"""SQL error handling and formatting"""
from typing import Tuple, Optional
import sqlparse
import re

class SQLErrorHandler:
    """Handles SQL error formatting and suggestions"""
    
    ERROR_PATTERNS = {
        'syntax': (r'syntax error', 'red'),
        'missing_table': (r'table .* does not exist', 'orange'),
        'missing_column': (r'column .* does not exist', 'yellow'),
        'ambiguous': (r'ambiguous column', 'purple'),
        'data_type': (r'data type mismatch', 'blue')
    }

    @staticmethod
    def format_error(error_message: str) -> Tuple[str, str, str]:
        """
        Format error message with color coding and suggestions
        Returns: (formatted_message, color, suggestion)
        """
        error_type = 'unknown'
        color = 'gray'
        suggestion = "No specific suggestion available"

        # Match error patterns
        for err_type, (pattern, err_color) in SQLErrorHandler.ERROR_PATTERNS.items():
            if re.search(pattern, error_message.lower()):
                error_type = err_type
                color = err_color
                suggestion = SQLErrorHandler._get_suggestion(err_type)
                break

        return error_message, color, suggestion

    @staticmethod
    def _get_suggestion(error_type: str) -> str:
        """Get suggestion based on error type"""
        suggestions = {
            'syntax': "Check for missing semicolons, brackets, or keywords",
            'missing_table': "Verify table name and ensure it exists in the database",
            'missing_column': "Verify column name and check table schema",
            'ambiguous': "Specify table name for ambiguous column references",
            'data_type': "Ensure data types match in comparisons and assignments"
        }
        return suggestions.get(error_type, "Review the query syntax and schema")

    @staticmethod
    def validate_query_segment(segment: str) -> Optional[str]:
        """Validate a specific segment of the SQL query"""
        try:
            parsed = sqlparse.parse(segment)[0]
            return None  # No error
        except Exception as e:
            return str(e)
