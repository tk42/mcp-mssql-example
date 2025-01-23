# server.py
import logging
import os
from typing import Any, Optional
from pydantic import BaseModel, Field

import pyodbc
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

# ロギングの設定
logger = get_logger(__name__)
logging.basicConfig(level=logging.INFO)

# データベース接続情報を環境変数から取得
DB_CONNECTION_STRING = os.getenv(
    "MSSQL_CONNECTION_STRING",
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=mssql;"
    "DATABASE=master;"
    "UID=sa;"
    "PWD=YourStrongPassword123;"
    "TrustServerCertificate=yes;"
)


class QueryResult(BaseModel):
    columns: list[str] = Field(description="Result set column names")
    rows: list[list[Any]] = Field(description="Result set rows")
    row_count: int = Field(description="Number of rows affected or returned")
    error: Optional[str] = Field(default=None, description="Error message if query failed")


class DatabaseTools:
    def __init__(self):
        self.conn = pyodbc.connect(DB_CONNECTION_STRING)

    def execute_query(self, query: str) -> QueryResult:
        """Execute a SQL query and return the results."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            
            # SELECT文の場合は結果を取得
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                row_count = len(rows)
                # pyodbcのRowオブジェクトを通常のリストに変換
                rows = [list(row) for row in rows]
            else:
                # INSERT/UPDATE/DELETE文の場合
                columns = []
                rows = []
                row_count = cursor.rowcount
            
            cursor.close()
            return QueryResult(
                columns=columns,
                rows=rows,
                row_count=row_count
            )
        
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                error=str(e)
            )

# MCPサーバーの初期化
mcp = FastMCP("SQL Query Server")
db_tools = DatabaseTools()

@mcp.tool()
def execute_sql_query(query: str) -> QueryResult:
    """
    Execute a SQL query on the MSSQL database.
    
    Parameters:
        query: SQL query to execute
    
    Returns:
        QueryResult containing columns, rows, and row count or error message
    """
    logger.info(f"Executing SQL query: {query}")
    return db_tools.execute_query(query)

@mcp.tool()
def get_table_info(table_name: str) -> QueryResult:
    """
    Get information about a specific table including its schema.
    
    Parameters:
        table_name: Name of the table to inspect
    
    Returns:
        QueryResult containing table schema information
    """
    query = f"""
    SELECT 
        c.name AS column_name,
        t.name AS data_type,
        c.max_length,
        c.is_nullable
    FROM sys.columns c
    JOIN sys.types t ON c.user_type_id = t.user_type_id
    WHERE c.object_id = OBJECT_ID('{table_name}')
    """
    return db_tools.execute_query(query)

@mcp.tool()
def list_tables() -> QueryResult:
    """
    Get a list of all tables in the database.
    
    Returns:
        QueryResult containing list of table names
    """
    query = """
    SELECT 
        s.name AS schema_name,
        t.name AS table_name
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    ORDER BY s.name, t.name
    """
    return db_tools.execute_query(query)

def main():
    """Start the MCP server"""
    try:
        # サーバー設定を行い、起動
        mcp.run()
    except Exception as e:
        logger.error(f"Error starting MCP server: {str(e)}")
        raise

if __name__ == "__main__":
    main()