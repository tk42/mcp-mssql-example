FROM --platform=linux/amd64 python:3.13-bookworm

WORKDIR /app

# 基本的なパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージの依存関係インストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# アプリケーションコードのコピー
COPY ./src .

# Streamlitの設定ファイル用ディレクトリ作成
RUN mkdir -p /root/.streamlit

# Streamlit設定ファイルのコピー
COPY config.toml /root/.streamlit/config.toml

# 8501ポートを公開
EXPOSE 8501

# コンテナ起動時のコマンド
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]