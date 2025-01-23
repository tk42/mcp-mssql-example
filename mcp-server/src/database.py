import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyodbc
import os
from urllib.parse import quote_plus


class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv("MSSQL_HOST")
        self.port = os.getenv("MSSQL_PORT", "1433")
        self.database = os.getenv("MSSQL_DATABASE")
        self.username = os.getenv("MSSQL_USERNAME")
        self.password = os.getenv("MSSQL_PASSWORD")

    @property
    def connection_string(self) -> str:
        # PyODBCでの接続文字列
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.host},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            "TrustServerCertificate=yes;"
        )
        return conn_str

    @property
    def sqlalchemy_url(self) -> str:
        # SQLAlchemyでの接続URL
        conn_str = self.connection_string
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(conn_str)}"


class Database:
    def __init__(self):
        self.config = DatabaseConfig()
        self.engine = None
        self.SessionLocal = None
        
        self.init_db()

    def init_db(self):
        try:
            # エンジンの作成
            self.engine = create_engine(
                self.config.sqlalchemy_url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_pre_ping=True
            )
            
            # セッションファクトリの作成
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # 接続テスト
            for _ in range(3):
                if self.test_connection():
                    break
                time.sleep(5)
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")

    def get_session(self):
        """データベースセッションを取得"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def test_connection(self) -> bool:
        """接続テストを実行"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.scalar()  # 結果を取得
            return True
        except Exception:
            return False


# データベースインスタンスの作成
db = Database()
get_db = db.get_session

# モデルのベースクラス
Base = declarative_base()


# 接続テスト関数
def test_db_connection():
    """データベース接続のテストを実行"""
    try:
        # PyODBCでの直接接続テスト
        conn_str = DatabaseConfig().connection_string
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT @@version")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        # SQLAlchemyでの接続テスト
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.scalar()  # 結果を取得
        
        return {
            "status": "success",
            "message": "Database connection successful",
            "version": version
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }


print(test_db_connection())
