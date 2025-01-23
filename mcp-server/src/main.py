from mcp.server.fastmcp import FastMCP
import pyodbc
from typing import Optional, List, Tuple
import json
from database import db
from mcp.server.fastmcp import FastMCP
from sqlalchemy import text
from typing import Generator
from contextlib import contextmanager


class SQLServerExplorer:
    def __init__(self, database_instance):
        self.db = database_instance
        self.mcp = FastMCP("SQL Server Explorer")
        self.setup_resources()
    
    @contextmanager
    def get_connection(self) -> Generator:
        """データベース接続のコンテキストマネージャ"""
        with self.db.engine.connect() as connection:
            yield connection
    
    def setup_resources(self):
        @self.mcp.resource("schema://main")
        def get_schema() -> str:
            """データベーススキーマを取得するリソース"""
            try:
                with self.get_connection() as conn:
                    schema_query = text("""
                        SELECT 
                            t.name AS table_name,
                            c.name AS column_name,
                            ty.name AS data_type,
                            c.max_length,
                            c.is_nullable
                        FROM sys.tables t
                        INNER JOIN sys.columns c ON t.object_id = c.object_id
                        INNER JOIN sys.types ty ON c.user_type_id = ty.user_type_id
                        ORDER BY t.name, c.column_id
                    """)
                    
                    result = conn.execute(schema_query)
                    schema_info = result.fetchall()
                    
                    # スキーマ情報をJSONフォーマットで整形
                    schema_dict = {}
                    for row in schema_info:
                        table_name = row[0]
                        if table_name not in schema_dict:
                            schema_dict[table_name] = []
                        
                        schema_dict[table_name].append({
                            "column": row[1],
                            "type": row[2],
                            "length": row[3],
                            "nullable": row[4]
                        })
                    
                    return json.dumps(schema_dict, indent=2)
                    
            except Exception as e:
                return f"Error: {str(e)}"

        @self.mcp.tool()
        def query_data(sql: str) -> str:
            """SQLクエリを安全に実行するツール"""
            try:
                with self.get_connection() as conn:
                    result = conn.execute(text(sql))
                    rows = result.fetchall()
                    return "\n".join(str(row) for row in rows)
            except Exception as e:
                return f"Error: {str(e)}"


def create_explorer() -> SQLServerExplorer:
    """SQLServerExplorerのインスタンスを作成"""
    return SQLServerExplorer(db)


if __name__ == "__main__":
    explorer = create_explorer()
    explorer.mcp.run()
