import sqlparse
from typing import Union

def validate_sql_query(query: str) -> Union[bool, str]:
    """
    Validate SQL query syntax and structure
    Returns True if valid, error message if invalid
    """
    try:
        # Basic SQL syntax validation
        parsed = sqlparse.parse(query)
        if not parsed:
            return False
            
        # Check for basic SQL injection patterns
        dangerous_keywords = [
            "DROP", "DELETE FROM", "TRUNCATE",
            "ALTER", "EXEC", "EXECUTE"
        ]
        
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
                
        return True
        
    except Exception as e:
        return False
