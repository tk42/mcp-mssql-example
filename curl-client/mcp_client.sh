#!/bin/bash

# 設定
API_HOST="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

# カラーコード
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ヘルスチェック
health_check() {
    echo -e "${BLUE}Checking API health...${NC}"
    curl -s -X GET "${API_HOST}/health"
    echo
}

# メタデータの取得
get_metadata() {
    echo -e "${BLUE}Getting database metadata...${NC}"
    curl -s -X GET "${API_HOST}/metadata"
    echo
}

# 自然言語クエリの実行
execute_query() {
    local query_text="$1"
    echo -e "${BLUE}Executing query: ${query_text}${NC}"
    curl -s -X POST "${API_HOST}/query" \
        -H "${CONTENT_TYPE}" \
        -d "{
            \"text\": \"${query_text}\",
            \"context_type\": \"SQL\"
        }"
    echo
}

# クエリ履歴の取得
get_query_history() {
    echo -e "${BLUE}Getting query history...${NC}"
    curl -s -X GET "${API_HOST}/history"
    echo
}

# メイン処理
main() {
    case "$1" in
        "health")
            health_check
            ;;
        "metadata")
            get_metadata
            ;;
        "query")
            if [ -z "$2" ]; then
                echo "Usage: $0 query 'your query text'"
                exit 1
            fi
            execute_query "$2"
            ;;
        "history")
            get_query_history
            ;;
        *)
            echo "Usage: $0 {health|metadata|query|history}"
            echo "Examples:"
            echo "  $0 health"
            echo "  $0 metadata"
            echo "  $0 query 'show me all sales from last month'"
            echo "  $0 history"
            exit 1
            ;;
    esac
}

# スクリプトの実行
main "$@"