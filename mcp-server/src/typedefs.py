from typing import List, Optional, Dict
from pydantic import BaseModel


# データモデルの定義
class QueryRequest(BaseModel):
    text: str
    parameters: Optional[Dict] = None


class QueryResponse(BaseModel):
    sql: str
    result: str
    execution_time: float


class DatabaseMetadata(BaseModel):
    tables: Dict[str, List[dict]]
    database_type: str
    version: str


class ModelProvider(BaseModel):
    name: str
    endpoint: str
    api_key: Optional[str] = None


class DatabaseContext(BaseModel):
    tables: Dict[str, List[dict]]
    database_type: str
    version: str

