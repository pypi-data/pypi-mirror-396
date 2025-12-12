import os
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Dict, Any, Optional, List
import httpx
import hmac
import base64
import time
from datetime import datetime
from hashlib import sha256
from pydantic import Field, BaseModel, ConfigDict
from mcp.server.fastmcp import FastMCP
import json



# --- Global Logger ---
logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self):
        self.base_url = "http://api.idb4.alibaba-inc.com"
        self.access_key = os.getenv('ACCESS_KEY_ID')
        self.access_secret = os.getenv('ACCESS_KEY_SECRET')

    def _generate_signature(self, content: str) -> str:
        """生成签名"""
        key = self.access_secret.encode('utf-8')
        message = content.encode('utf-8')
        signature = hmac.new(key, message, sha256).digest()
        return base64.b64encode(signature).decode('utf-8')

    def _build_sign_content(self, method: str, path: str, timestamp: str) -> str:
        """构建签名内容"""
        return f"{method}\n{path}\n{timestamp}\n"

    async def request(self, method: str, path: str, **kwargs) -> str:
        """发送HTTP请求"""
        # 构建完整URL
        url = f"{self.base_url}{path}"

        # 生成时间戳
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # 构建签名内容并生成签名
        sign_content = self._build_sign_content(method, path, timestamp)
        signature = self._generate_signature(sign_content)

        # 设置认证头
        headers = kwargs.get('headers', {})
        headers.update({
            'X-Access-Key': self.access_key,
            'X-Signature': signature,
            'X-Timestamp': timestamp,
            'Content-Type': 'application/json'
        })
        kwargs['headers'] = headers

        # 创建新的client并发送请求
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def get(self, path: str, **kwargs) -> httpx.Response:
        return await self.request('GET', path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        return await self.request('POST', path, **kwargs)


# --- Pydantic Models ---
class MyBaseModel(BaseModel):
    model_config = ConfigDict(json_dumps_params={'ensure_ascii': False})

class DatabaseDetail(MyBaseModel):
    dbId: Any = Field(description="Unique database identifier in DMS", default=None)
    schemaName: Any = Field(description="Name of the database schema", default=None)
    dbType: Any = Field(description="Database Engine type", default=None)
    alias: Any = Field(description="Instance alias in DMS", default=None)
    instanceId: Any = Field(description="Instance identifier in DMS", default=None)
    state: Any = Field(description="Current operational status", default=None)
    dbaName: Any = Field(description="Current DBA name", default=None)
    description: Any = Field(description="Description of the database", default=None)
    envType: Any = Field(description="EnvType of the database", default=None)
    host: Any = Field(description="Hostname or IP address of the database instance")
    port: Any = Field(description="Connection port number")

class InstanceDetail(MyBaseModel):
    id: Any = Field(description="Unique instance identifier in DMS", default=None)
    host: Any = Field(description="Hostname or IP address of the database instance")
    port: Any = Field(description="Connection port number")
    state: Any = Field(description="Current operational status", default=None)
    alias: Any = Field(description="Instance alias in DMS", default=None)
    dbType: Any = Field(description="Database Engine type", default=None)
    dbaName: Any = Field(description="Current DBA name", default=None)
    envType: Any = Field(description="EnvType of the instance", default=None)
    ddlOnline: Any = Field(description="Whether to use DDLOnline（无锁变更开关）, -1: Prohibited, 0: Not used, 1: Native Online DDL takes priority, 2: DMS OnlineDDL takes priority", default=None)

class TableDetail(MyBaseModel):
    columns: Any = Field(description="List of column metadata", default=None)
    indexes: Any = Field(description="List of index metadata", default=None)

class ResultSet(MyBaseModel):
    ColumnNames: List[str] = Field(description="Ordered list of column names")
    RowCount: int = Field(description="Number of rows returned")
    Rows: List[Dict[str, Any]] = Field(description="List of rows, where each row is a dictionary of column_name: value")
    # MarkdownTable: Optional[str] = Field(default=None, description="Data formatted as a Markdown table string")
    Success: bool = Field(description="Whether this result set was successfully retrieved")
    Message: str = Field(description="Additional message returned")

class ExecuteScriptResult(MyBaseModel):
    RequestId: str = Field(description="Unique request identifier")
    Results: List[ResultSet] = Field(description="List of result sets from executed script")
    Success: bool = Field(description="Overall operation success status")
    Message: str = Field(default="", description="Overall error message if execution failed")

    def __str__(self) -> str:
        if not self.Success:
            msg = self.Message.strip()
            if not msg:
                for rs in self.Results:
                    if rs.Message.strip():
                        msg = rs.Message.strip()
                        break
            return f"Error: {msg}" if msg else "Script execution failed with no detailed error."
        output = {
            "success": True,
            "requestId": self.RequestId,
            "results": []
        }
        for rs in self.Results:
            if rs.Success:
                output["results"].append({
                    "columnNames": rs.ColumnNames,
                    "rowCount": rs.RowCount,
                    "rows": rs.Rows  # ← 完整 rows 列表
                })
            else:
                output["results"].append({
                    "success": False,
                    "message": rs.Message
                })
        return json.dumps(output, ensure_ascii=False, indent=2)


async def get_instance(
        host: str = Field(description="The hostname of the database instance"),
        port: str = Field(description="The connection port number"),
        sid: Optional[str] = Field(default=None, description="Required for Oracle like databases")
) -> InstanceDetail:
    client = ApiClient()
    data = {"host": host, "port": port, "sid": sid}

    try:
        resp = await client.post('/mcp/api/meta/getInstance', json=data)
        if not isinstance(resp, dict):
            logger.warning("Unexpected response type from getInstance")
            return None
        instance_data = resp.get("root")
        return InstanceDetail(**instance_data)

    except Exception as e:
        logger.error(f"Error in get_instance: {e}")
        raise

async def search_database(
        schema_name: str = Field(description="Name of the database schema to search for."),
        env_type: Optional[str]  = Field(default=None, description="Environment type of the database, such as 'production', 'development', 'test', etc."),
        db_type: Optional[str] = Field(default=None, description="Type of the database, such as 'MySQL', 'Redis', etc.")
) -> Dict[str, Any]:
    client = ApiClient()
    try:
        data = {"schemaName": schema_name, "envType": env_type, "dbTypeStr": db_type}
        resp = await client.post('/mcp/api/meta/searchDatabase', json=data)
        return resp.get("root") if resp and resp.get("root") else {}
        # return DatabaseDetail(**db_data)
    except Exception as e:
        logger.error(f"Error in search_database: {e}")
        raise

async def search_logic_database(
        schema_name: str = Field(description="Name of the logic database"),
        env_type: Optional[str]  = Field(default=None, description="EnvType of the logic database."),
        db_type: Optional[str] = Field(default=None, description="DbType of the logic database")
) -> Dict[str, Any]:
    client = ApiClient()
    try:
        data = {"schemaName": schema_name, "envType": env_type, "dbTypeStr": db_type}
        resp = await client.post('/mcp/api/meta/searchLogicDatabase', json=data)
        return resp.get("root") if resp and resp.get("root") else {}
        # return DatabaseDetail(**db_data)
    except Exception as e:
        logger.error(f"Error in search_logic_database: {e}")
        raise

async def get_database(
        host: str = Field(description="Hostname or IP of the database instance"),
        port: str = Field(description="Connection port number"),
        schema_name: str = Field(description="Name of the database schema"),
        sid: Optional[str] = Field(default=None, description="Required for Oracle like databases")
) -> DatabaseDetail:
    client = ApiClient()
    try:
        data = {"host": host, "port": port, "sid":sid, "schemaName": schema_name}
        resp = await client.post('/mcp/api/meta/getDatabase', json=data)
        if not isinstance(resp, dict):
            logger.warning("Unexpected response type from getDatabase")
            return None
        db_data = resp.get("root")
        # return resp
        return DatabaseDetail(**db_data)
    except Exception as e:
        logger.error(f"Error in get_database: {e}")
        raise

async def list_logic_tables(  # Renamed from listTable to follow convention
        database_id: str = Field(description="DMS logic databaseId"),
        search_name: Optional[str] = Field(default=None, description="Optional: Search keyword for table names"),
        page_number: int = Field(default=1, description="Pagination page number"),
        page_size: int = Field(default=200, description="Results per page (max 200)")
) -> Dict[str, Any]:
    client = ApiClient()
    try:
        if not search_name:
            search_name = "%"
        data = {"dbId": database_id, "searchName": search_name, "page": page_number, "rows":page_size, "returnGuid":True}
        resp = await client.post('/mcp/api/meta/listLogicTables', json=data)
        return resp.get("root") if resp and resp.get("root") else {}
        # return resp.root if resp and resp.root else {}
    except Exception as e:
        logger.error(f"Error in list_tables: {e}")
        raise

async def list_tables(  # Renamed from listTable to follow convention
        database_id: str = Field(description="DMS databaseId"),
        search_name: Optional[str] = Field(default=None, description="Optional: Search keyword for table names"),
        page_number: int = Field(default=1, description="Pagination page number"),
        page_size: int = Field(default=200, description="Results per page (max 200)")
) -> Dict[str, Any]:
    client = ApiClient()
    try:
        if not search_name:
            search_name = "%"
        data = {"dbId": database_id, "searchName": search_name, "page": page_number, "rows":page_size, "returnGuid":True}
        resp = await client.post('/mcp/api/meta/listTables', json=data)
        if not isinstance(resp, dict):
            logger.warning("Unexpected response type from getDatabase")
            return None
        return resp.get("root") if resp and resp.get("root") else {}
    except Exception as e:
        logger.error(f"Error in list_tables: {e}")
        raise

async def get_meta_table_detail_info(
        table_guid: str = Field(description="Unique table identifier (format: dmsTableId.schemaName.tableName)")
) -> TableDetail:
    client = ApiClient()
    try:
        data = {"guid": table_guid}
        resp = await client.post('/mcp/api/meta/getTableDetailInfo', json=data)
        if not isinstance(resp, dict):
            logger.warning("Unexpected response type from getMetaTableDetailInfo")
            return None
        table_data = resp.get("root")
        return TableDetail(**table_data)
    except Exception as e:
        logger.error(f"Error in get_meta_table_detail_info: {e}")
        raise

async def query_security_columns(
        table_guid: str = Field(description="Unique table identifier (format: dmsTableId.schemaName.tableName)")
) -> Dict[str, Any]:
    client = ApiClient()
    try:
        data = {"guid": table_guid}
        resp = await client.post('/mcp/api/meta/querySecurityColumns', json=data)
        if not isinstance(resp, dict):
            logger.warning("Unexpected response type from querySecurityColumns")
            return None
        return resp.get("root") if resp and resp.get("root") else {}
    except Exception as e:
        logger.error(f"Error in query_security_columns: {e}")
        raise

# def _format_as_markdown_table(column_names: List[str], rows: List[Dict[str, Any]]) -> str:
#     if not column_names: return ""
#     header = "| " + " | ".join(column_names) + " |"
#     separator = "| " + " | ".join(["---"] * len(column_names)) + " |"
#     table_rows_str = [header, separator]
#     for row_data in rows:
#         row_values = [str(row_data.get(col, "")) for col in column_names]
#         table_rows_str.append("| " + " | ".join(row_values) + " |")
#     return "\n".join(table_rows_str)

async def execute_script(
        database_id: str = Field(description="DMS databaseId"),
        script: str = Field(description="SQL script to execute"),
        logic: bool = Field(default=False, description="Whether to use logical execution mode")
) -> ExecuteScriptResult:  # Return the object, __str__ will be used by wrapper if needed
    client = ApiClient()
    try:
        data = {"dbId": database_id, "script": script, "logic": logic}
        resp = await client.post('/mcp/api/meta/executeScript', json=data)

        if not isinstance(resp, dict):
            warning_msg = "Unexpected response type from executeScript"
            logger.warning(warning_msg)
            return ExecuteScriptResult(RequestId="", Results=[], Success=False,
                Message=warning_msg)

        overall_success = resp.get('success', False)
        request_id = resp.get('traceId', "")
        overall_message = ""

        if not overall_success:
            overall_message = resp.get('message') or resp.get('errorMsg') or "Script execution failed."
        processed_results = []

        if overall_success and resp.get('root'):
            for res_item in resp.get('root', []):
                if res_item.get('success'):
                    column_names = res_item.get('columnNames', [])
                    rows_data = res_item.get('rows', [])
                    # markdown_table = _format_as_markdown_table(column_names, rows_data)
                    # processed_results.append(
                    #     ResultSet(ColumnNames=column_names, RowCount=res_item.get('count', 0), Rows=rows_data,
                    #               MarkdownTable=markdown_table, Success=True, Message=''))
                    processed_results.append(
                        ResultSet(ColumnNames=column_names, RowCount=res_item.get('count', 0), Rows=rows_data,
                                 Success=True, Message=''))
                else:
                    processed_results.append(
                        ResultSet(ColumnNames=[], RowCount=0, Rows=[], MarkdownTable=None, Success=False, Message=res_item.get('message')))
        elif not overall_success and resp.get('root'):
            for res_item in resp.get('root', []):
                processed_results.append(
                    ResultSet(
                        ColumnNames=[],
                        RowCount=0,
                        Rows=[],
                        Success=False,
                        Message=res_item.get('message', "")
                    )
                )
        return ExecuteScriptResult(RequestId=request_id, Results=processed_results,
                                   Success=overall_success,
                                   Message=overall_message)
    except Exception as e:
        error_msg = f"Exception during script execution: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return ExecuteScriptResult(
            RequestId="",
            Results=[],
            Success=False,
            Message=error_msg
        )

# --- ToolRegistry Class ---
class ToolRegistry:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.default_database_id: Optional[str] = getattr(self.mcp.state, 'default_database_id', None)

    def register_tools(self) -> FastMCP:
        if self.default_database_id:
            logger.info(f"DATABASE_ID is set ('{self.default_database_id}'). Registering configured toolset.")
            self._register_configured_db_toolset()
        else:
            logger.info("DATABASE_ID not set. Registering full toolset.")
            self._register_full_toolset()
        return self.mcp

    def _register_configured_db_toolset(self):
        @self.mcp.tool(name="listTables",
                       description="Lists tables in the database. Search by name is supported.",
                       annotations={"title": "List Tables (Pre-configured DB)", "readOnlyHint": True})
        async def list_tables_configured(
                search_name: Optional[str] = Field(
                    description="Optional: A string used as the search keyword to match table names."),
                page_number: int = Field(description="Pagination page number", default=1),
                page_size: int = Field(description="Number of results per page", default=200)
        ) -> Dict[str, Any]:
            return await list_tables(database_id=self.default_database_id, search_name=search_name,
                                     page_number=page_number, page_size=page_size)

        self.mcp.tool(name="getTableDetailInfo",
                      description="Retrieve detailed metadata information about a specific database table including "
                                  "schema and index details. If you don't know the table_guid parameter, retrieve it using listTables.",
                      annotations={"title": "Get Table Details", "readOnlyHint": True})(get_meta_table_detail_info)
        @self.mcp.tool(name="executeScript",
                       description="Executes an SQL script against the pre-configured database.",
                       annotations={"title": "Execute SQL (Pre-configured DB)", "readOnlyHint": False,
                                    "destructiveHint": True})
        async def execute_script_configured(
                script: str = Field(description="SQL script to execute"),
                logic: bool = Field(description="Whether to use logical execution mode", default=False)
        ) -> str:
            result_obj = await execute_script(database_id=self.default_database_id, script=script, logic=logic)
            return str(result_obj)
        self.mcp.tool(name="listSecurityColumns",
                      description="Retrieve the list of security columns under the table. "
                                  "If you don't know the table_guid parameter, retrieve it using listTables.",
                      annotations={"title": "List Security Columns", "readOnlyHint": True})(query_security_columns)
    def _register_full_toolset(self):
        self.mcp.tool(name="getInstance",
                      description="Retrieve detailed instance information from DMS using the host and port.",
                      annotations={"title": "获取DMS实例详情", "readOnlyHint": True})(get_instance)
        self.mcp.tool(name="searchDatabase",
                      description="Search and retrieve detailed information about databases registered in the DMS.",
                      annotations={"title": "搜索DMS中的数据库信息", "readOnlyHint": True})(search_database)
        self.mcp.tool(name="searchLogicDatabase",
                      description="Retrieve detailed information about logic databases DMS.",
                      annotations={"title": "获取DMS逻辑库信息", "readOnlyHint": True})(search_logic_database)
        self.mcp.tool(name="getDatabase",
                      description="Obtain detailed information about a specific database in DMS when the host and port are provided.",
                      annotations={"title": "获取DMS数据库详情", "readOnlyHint": True})(get_database)
        self.mcp.tool(name="listLogicTables",
                      description="Search for logic tables by databaseId and (optional) table name. "
                                  "If you don't know the logic databaseId, first use searchLogicDatabase to retrieve it."
                                  "Note: searchLogicDatabase may return multiple logic databases. In this case, let the user choose which one to use.",
                      annotations={"title": "列出DMS逻辑表", "readOnlyHint": True})(list_logic_tables)
        self.mcp.tool(name="listTables",
                      description="Search for tables by databaseId and (optional) table name. If the user mentions a logical database or logical table, please use the tool with 'logic' in its name."
                                  "If you don't know the databaseId, first use getDatabase to retrieve it."
                                  "If you don't have enough information for getDatabase tool, ask the user to provide the necessary details.",
                      annotations={"title": "列出DMS表", "readOnlyHint": True})(list_tables)
        self.mcp.tool(name="getTableDetailInfo",
                      description="Retrieve detailed metadata information about a specific database table including "
                                  "schema and index details. If you don't know the table_guid parameter, retrieve it using listTables.",
                      annotations={"title": "获取DMS表详细信息", "readOnlyHint": True})(get_meta_table_detail_info)
        @self.mcp.tool(name="executeScript",
                       description="Execute SQL script against a database in DMS and return structured results.",
                       annotations={"title": "在DMS中执行SQL脚本", "readOnlyHint": False, "destructiveHint": True})
        async def execute_script_full_wrapper(
                database_id: str = Field(description="Required DMS databaseId. Obtained via getDatabase tool"),
                script: str = Field(description="SQL script to execute"),
                logic: bool = Field(description="Whether to use logical execution mode", default=False)
        ) -> str:  # Return string representation
            result_obj = await execute_script(database_id=database_id, script=script, logic=logic)
            return str(result_obj)
        self.mcp.tool(name="listSecurityColumns",
                      description="Retrieve the list of security columns under the table. "
                                  "If you don't know the table_guid parameter, retrieve it using listTables.",
                      annotations={"title": "List Security Columns", "readOnlyHint": True})(query_security_columns)
# --- Lifespan Function ---
@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncGenerator[None, None]:
    logger.info("Initializing DMS MCP Server via lifespan")

    # Ensure app.state exists
    if not hasattr(app, 'state') or app.state is None:
        class AppState: pass

        app.state = AppState()

    app.state.default_database_id = None  # Initialize default_database_id

    dms_connection_string = os.getenv("CONNECTION_STRING")
    if dms_connection_string:
        logger.info(f"CONNECTION_STRING environment variable found: {dms_connection_string}")
        db_host, db_port, db_name_path, catalog_name = None, None, None, None
        try:
            # Expected formats:
            # 1. catalog@host:port:schema  (PG, full)
            # 2. database@host:port      (MySQL, database is schema-like)
            # 3. host:port:schema          (No catalog, with schema)
            # 4. host:port                 (No catalog, no schema)

            parts = dms_connection_string.split('@')

            potential_catalog_or_db_name = None
            main_part = ""

            if len(parts) > 1:  # Contains '@'
                potential_catalog_or_db_name = parts[0]
                main_part = parts[1]
            else:  # No '@'
                main_part = parts[0]

            main_part_components = main_part.split(':')

            if len(main_part_components) == 3:  # host:port:schema
                db_host = main_part_components[0]
                db_port = main_part_components[1]
                db_name_path = main_part_components[2]  # This is schema
                if potential_catalog_or_db_name:  # Format 1: catalog@host:port:schema
                    catalog_name = potential_catalog_or_db_name
                # else Format 3: host:port:schema (catalog_name remains None)

            elif len(main_part_components) == 2:  # host:port
                db_host = main_part_components[0]
                db_port = main_part_components[1]
                if potential_catalog_or_db_name:  # Format 2: database@host:port
                    # Here, potential_catalog_or_db_name is the database/schema
                    db_name_path = potential_catalog_or_db_name
                    # For MySQL-like, catalog is not explicit in this way, so catalog_name remains None or is not used as such.
                # else Format 4: host:port (db_name_path and catalog_name remain None)

            else:
                raise ValueError(
                    f"Invalid format for host:port or host:port:schema part: '{main_part}' in CONNECTION_STRING '{dms_connection_string}'.")

            if not (db_host and db_port):  # This check might be redundant if ValueError above catches it.
                logger.error(
                    f"CONNECTION_STRING '{dms_connection_string}' is incomplete. Missing host or port. Expected formats: catalog@host:port:schema, database@host:port, host:port:schema, host:port")
            else:
                logger.info(f"Verifying instance from CONNECTION_STRING: {db_host}:{db_port}")
                try:
                    instance_details = await get_instance(host=db_host, port=str(db_port), sid=None)
                    if not instance_details or not instance_details.id:
                        logger.warning(
                            f"Instance {db_host}:{db_port} not found or no valid id returned by get_instance. Cannot use this CONNECTION_STRING.")
                    else:
                        logger.info(f"Instance {db_host}:{db_port} verified. InstanceId: {instance_details.id}")

                        if db_name_path or catalog_name:  # We need either a schema or a catalog to search
                            search_term_for_db = catalog_name if catalog_name else db_name_path
                            sid_name = None
                            if catalog_name and db_name_path:
                                sid_name = db_name_path
                                logger.info(
                                    f"Searching for database with catalog '{catalog_name}' and schema '{db_name_path}' associated with instance {db_host}:{db_port}")
                            elif db_name_path:
                                logger.info(
                                    f"Searching for database schema '{db_name_path}' associated with instance {db_host}:{db_port}")
                            elif catalog_name:
                                logger.info(
                                    f"Searching for database catalog '{catalog_name}' associated with instance {db_host}:{db_port}")

                            database = await get_database(host=db_host,
                                                          port=db_port, schema_name=search_term_for_db, sid=sid_name)
                            if not database or database.dbId is None:
                                logger.warning(
                                    f"No database found for {search_term_for_db} at {db_host}:{db_port} after processing CONNECTION_STRING.")
                                database = await get_database(host=db_host, port=db_port, schema_name=search_term_for_db, sid=None)
                            found_db_id = None
                            if database:
                                found_db_id = database.dbId

                            if found_db_id:
                                app.state.default_database_id = found_db_id
                                logger.info(
                                    f"Successfully configured default_database_id to {found_db_id} using CONNECTION_STRING.")
                            else:
                                current_search_criteria = f"catalog '{catalog_name}', schema '{db_name_path}'" if catalog_name and db_name_path else f"schema '{db_name_path}'" if db_name_path else f"catalog '{catalog_name}'"
                                logger.warning(
                                    f"Could not find a matching database for {current_search_criteria} at {db_host}:{db_port} after processing CONNECTION_STRING.")
                        else:
                            logger.info(
                                f"Instance {db_host}:{db_port} verified, but no catalog or schema provided in CONNECTION_STRING. No default database_id will be set from this DSN.")

                except Exception as instance_e:
                    logger.error(
                        f"Error during instance verification or database search for CONNECTION_STRING '{dms_connection_string}': {instance_e}")

        except ValueError as ve:
            logger.error(
                f"Invalid CONNECTION_STRING format '{dms_connection_string}': {ve}. Expected formats: catalog@host:port:schema, database@host:port, host:port:schema, or host:port")
        except Exception as e:
            logger.error(f"Error parsing CONNECTION_STRING '{dms_connection_string}': {e}")
    else:
        logger.info("CONNECTION_STRING environment variable not found.")

    if app.state.default_database_id:
        logger.info(f"Final default_database_id to be used (from CONNECTION_STRING): {app.state.default_database_id}")
    else:
        logger.info("No default database ID configured from CONNECTION_STRING. Full toolset will be registered.")

    registry = ToolRegistry(mcp=app)
    registry.register_tools()

    yield

    logger.info("Shutting down DMS MCP Server via lifespan")
    if hasattr(app.state, 'default_database_id'):
        delattr(app.state, 'default_database_id')

# --- FastMCP Instance Creation & Server Run ---
mcp = FastMCP(
    "DatabaseManagementAssistant_INNER",
    lifespan=lifespan,
    instructions="Database Management Assistant (DMS) is a toolkit designed to assist users in managing and "
                 "interacting with databases."
)

def run_server():
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level_str, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info(f"Starting DMS MCP server with log level {log_level_str}")
    mcp.run(transport=os.getenv('SERVER_TRANSPORT', 'stdio'))

if __name__ == "__main__":
    run_server()
