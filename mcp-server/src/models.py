from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, List, Optional

Base = declarative_base()

class DatabaseContext:
    def __init__(
        self,
        tables: Dict[str, List[dict]],
        database_type: str,
        version: str
    ):
        self.tables = tables
        self.database_type = database_type
        self.version = version

class QueryLog(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    original_query = Column(Text)
    transformed_query = Column(Text)
    execution_result = Column(Text)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("query_history.id"))
    cpu_time = Column(Integer)
    elapsed_time = Column(Integer)
    logical_reads = Column(Integer)
    physical_reads = Column(Integer)
    row_count = Column(Integer)
    execution_plan = Column(Text)
    created_at = Column(DateTime, default=func.now())

class MCPMetadata(Base):
    __tablename__ = "mcp_metadata"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(128))
    column_name = Column(String(128))
    data_type = Column(String(128))
    description = Column(Text, nullable=True)
    sample_values = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())