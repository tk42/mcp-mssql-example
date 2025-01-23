import os
from dataclasses import dataclass


@dataclass
class Settings:
    max_concurrent_connections: int = int(os.getenv("MAX_CONCURRENT_CONNECTIONS", 10))
    llm_server_url: str = os.getenv("LLM_SERVER_URL", "http://llm-server:8080")
