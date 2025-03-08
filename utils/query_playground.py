"""Interactive SQL Query Testing Playground"""
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from .database import Database
from .error_handler import SQLErrorHandler
from .sql_dialects import SQLDialectConverter
from .query_optimizer import QueryOptimizer

class QueryPlayground:
    def __init__(self):
        self.db = Database()
        self.dialect_converter = SQLDialectConverter()
        self.query_optimizer = QueryOptimizer()

    def execute_test_query(self, 
                         query: str,
                         dialect: str = 'postgresql',
                         limit_rows: int = 100) -> Tuple[Optional[pd.DataFrame], str, list]:
        """
        Execute a test query and return results with optimization suggestions
        Returns: (results_df, error_message, optimization_suggestions)
        """
        try:
            # Convert query to PostgreSQL dialect if needed
            if dialect != 'postgresql':
                query = self.dialect_converter.convert_query(query, 'postgresql')

            # Get optimization suggestions
            optimized_query, suggestions = self.query_optimizer.optimize_query(query)

            # Add LIMIT clause if not present
            if 'LIMIT' not in optimized_query.upper():
                optimized_query = f"{optimized_query} LIMIT {limit_rows}"

            # Execute query
            results = self.db.execute_query(optimized_query)
            
            # Convert to DataFrame
            if results:
                df = pd.DataFrame(results)
                return df, "", suggestions
            return pd.DataFrame(), "", suggestions

        except Exception as e:
            error_msg, color, suggestion = SQLErrorHandler.format_error(str(e))
            return None, error_msg, [suggestion]

    def get_table_preview(self, table_name: str, limit: int = 5) -> Optional[pd.DataFrame]:
        """Get a preview of table data"""
        try:
            if self.db.validate_table_exists(table_name):
                query = f"SELECT * FROM {table_name} LIMIT {limit}"
                results = self.db.execute_query(query)
                return pd.DataFrame(results) if results else pd.DataFrame()
        except Exception:
            return None
        return None

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get basic statistics about a table"""
        try:
            stats_query = f"""
            SELECT 
                (SELECT COUNT(*) FROM {table_name}) as row_count,
                (
                    SELECT json_object_agg(column_name, stats)
                    FROM (
                        SELECT 
                            column_name,
                            json_build_object(
                                'null_count', (
                                    SELECT COUNT(*) 
                                    FROM {table_name} 
                                    WHERE column_name IS NULL
                                ),
                                'distinct_count', (
                                    SELECT COUNT(DISTINCT column_name) 
                                    FROM {table_name}
                                )
                            ) as stats
                        FROM information_schema.columns
                        WHERE table_name = '{table_name}'
                    ) s
                ) as column_stats
            """
            results = self.db.execute_query(stats_query)
            return results[0] if results else {}
        except Exception:
            return {}
