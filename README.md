# mscp-mssql-example


```
mcp-mssql-system/
├── docker-compose.yml
├── .env
├── mssql/
│   ├── Dockerfile
│   └── init/
│       ├── init.sql
│       └── configure.sql
├── mcp-server/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── processor.py
│       │   └── models.py
│       └── api/
│           ├── __init__.py
│           └── routes.py
├── llm-server/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── config.py
│       └── inference.py
└── streamlit-client/
    ├── Dockerfile
    ├── requirements.txt
    └── src/
        ├── main.py
        ├── config.py
        └── components/
            ├── chat.py
            └── results.py
```


## `curl` MCP Client
### ヘルスチェック
`./mcp_client.sh health`

### メタデータの取得
`./mcp_client.sh metadata`

### クエリの実行
`./mcp_client.sh query "show me sales data from last month"`

### クエリ履歴の取得
`./mcp_client.sh history`

### クエリの実行
```
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"text": "show me sales data from last month", "context_type": "SQL"}'
```
