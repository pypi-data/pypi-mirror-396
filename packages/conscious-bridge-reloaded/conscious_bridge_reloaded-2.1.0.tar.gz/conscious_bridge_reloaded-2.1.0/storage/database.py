"""
Database connection and management
"""

import sqlite3
from typing import Optional
from pathlib import Path
import json


class Database:
    """SQLite database manager"""
    
    def __init__(self, db_path: str = "conscious_bridges_reloaded.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
    def connect(self):
        """Connect to database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_schema(self):
        """Initialize database schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        conn = self.connect()
        conn.executescript(schema)
        conn.commit()
        self.close()
    
    def execute(self, query: str, params: tuple = ()):
        """Execute a query"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor
    
    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch one result"""
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all results"""
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def commit(self):
        """Commit transaction"""
        if self.connection:
            self.connection.commit()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is None:
            self.commit()
        self.close()