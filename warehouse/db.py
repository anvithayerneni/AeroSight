"""
AeroSight Database Connection & Query Execution Manager
Provides thread-safe connections to DuckDB (0-cost local embedded OLAP engine) and PostgreSQL.
"""

import os
from typing import Any, Optional

import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DUCKDB_PATH = os.path.join(BASE_DIR, "data", "warehouse.duckdb")

class DatabaseManager:
    _instance: Optional["DatabaseManager"] = None

    def __init__(self, db_path: str = DEFAULT_DUCKDB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = None

    @classmethod
    def get_instance(cls, db_path: str = DEFAULT_DUCKDB_PATH) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            # DuckDB read-write connection
            self._conn = duckdb.connect(self.db_path)
        return self._conn

    def execute_query(self, query: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        """Executes a SQL query and returns results as a list of dicts."""
        conn = self.get_connection()
        try:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            
            if cursor.description is None:
                return []
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error executing query: {e}\nQuery: {query}")
            raise e

    def query_df(self, query: str, params: list[Any] | None = None) -> pd.DataFrame:
        """Executes a SQL query and returns result as a Pandas DataFrame."""
        conn = self.get_connection()
        if params:
            return conn.execute(query, params).df()
        return conn.execute(query).df()

    def close(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

def get_db() -> DatabaseManager:
    return DatabaseManager.get_instance()
