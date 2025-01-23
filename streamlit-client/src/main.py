import streamlit as st
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
from typing import Optional, Dict, Any


class MCPStreamlitClient:
    def __init__(self, server_file: str):
        self.server_params = StdioServerParameters(
            command="python",
            args=[server_file],
            env=None
        )
        self.session: Optional[ClientSession] = None
        
    async def initialize_session(self):
        """MCPセッションを初期化"""
        if not hasattr(self, 'client_context'):
            self.client_context = stdio_client(self.server_params)
            read, write = await self.client_context.__aenter__()
            self.session = ClientSession(read, write)
            await self.session.__aenter__()
            await self.session.initialize()

    async def close_session(self):
        """セッションをクリーンアップ"""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'client_context'):
            await self.client_context.__aexit__(None, None, None)

    async def execute_query(self, sql: str) -> str:
        """SQLクエリを実行"""
        if not self.session:
            await self.initialize_session()
        return await self.session.call_tool("query_data", {"sql": sql})

    async def get_schema(self) -> Dict[str, Any]:
        """スキーマ情報を取得"""
        if not self.session:
            await self.initialize_session()
        schema_json = await self.session.read_resource("schema://main")
        return json.loads(schema_json)

def main():
    st.set_page_config(page_title="SQL Server Explorer", layout="wide")
    st.title("SQL Server Explorer")

    # MCPクライアントの初期化
    if 'mcp_client' not in st.session_state:
        st.session_state.mcp_client = MCPStreamlitClient("sql_server_explorer.py")

    # 左サイドバーにスキーマ情報を表示
    with st.sidebar:
        st.header("Database Schema")
        if st.button("Refresh Schema"):
            schema = asyncio.run(st.session_state.mcp_client.get_schema())
            st.session_state.schema = schema

        if 'schema' in st.session_state:
            for table_name, columns in st.session_state.schema.items():
                with st.expander(table_name):
                    for column in columns:
                        st.text(f"{column['column']} ({column['type']})")

    # メイン画面にクエリエディタを表示
    st.header("SQL Query Editor")
    query = st.text_area("Enter your SQL query", height=200)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        execute = st.button("Execute")
    with col2:
        if execute and query:
            with st.spinner("Executing query..."):
                try:
                    result = asyncio.run(st.session_state.mcp_client.execute_query(query))
                    st.success("Query executed successfully")
                    st.text_area("Results", result, height=300)
                except Exception as e:
                    st.error(f"Error executing query: {str(e)}")

    # セッションの終了処理
    if st.button("Close Connection"):
        asyncio.run(st.session_state.mcp_client.close_session())
        st.success("Connection closed successfully")


if __name__ == "__main__":
    main()
