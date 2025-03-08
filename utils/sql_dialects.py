"""SQL dialect support and conversion utilities"""
from typing import Dict, Optional
import sqlparse

class SQLDialectConverter:
    """Handles conversion between different SQL dialects"""
    
    SUPPORTED_DIALECTS = {
        'mysql': 'MySQL',
        'postgresql': 'PostgreSQL',
        'sqlite': 'SQLite',
        'mssql': 'SQL Server'
    }

    def __init__(self):
        self.current_dialect = 'mysql'

    def convert_query(self, query: str, target_dialect: str) -> str:
        """Convert SQL query to target dialect"""
        if target_dialect not in self.SUPPORTED_DIALECTS:
            raise ValueError(f"Unsupported dialect: {target_dialect}")

        # Parse the SQL query
        parsed = sqlparse.parse(query)[0]

        # Apply dialect-specific transformations
        if target_dialect == 'postgresql':
            return self._to_postgresql(query)
        elif target_dialect == 'mysql':
            return self._to_mysql(query)
        elif target_dialect == 'sqlite':
            return self._to_sqlite(query)
        elif target_dialect == 'mssql':
            return self._to_mssql(query)
        
        return query

    def _to_postgresql(self, query: str) -> str:
        """Convert to PostgreSQL syntax"""
        query = query.replace('`', '"')  # Replace MySQL backticks with double quotes
        query = query.replace('IFNULL', 'COALESCE')
        return query

    def _to_mysql(self, query: str) -> str:
        """Convert to MySQL syntax"""
        query = query.replace('"', '`')  # Replace double quotes with backticks
        query = query.replace('COALESCE', 'IFNULL')
        return query

    def _to_sqlite(self, query: str) -> str:
        """Convert to SQLite syntax"""
        query = query.replace('`', '"')
        query = query.replace('TRUE', '1')
        query = query.replace('FALSE', '0')
        return query

    def _to_mssql(self, query: str) -> str:
        """Convert to MS SQL Server syntax"""
        query = query.replace('`', '[')
        query = query.replace('LIMIT', 'TOP')
        return query

    @staticmethod
    def get_supported_dialects() -> Dict[str, str]:
        """Get list of supported SQL dialects"""
        return SQLDialectConverter.SUPPORTED_DIALECTS
