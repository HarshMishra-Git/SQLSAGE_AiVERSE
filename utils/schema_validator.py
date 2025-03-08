from typing import Dict, Any

def validate_schema(schema: Dict[str, Any]) -> bool:
    """
    Validate uploaded database schema format
    """
    try:
        # Check if schema has required structure
        if not isinstance(schema, dict):
            return False
            
        # Check if schema has tables
        if 'tables' not in schema:
            return False
            
        # Validate each table has required fields
        for table_name, table_info in schema['tables'].items():
            if not isinstance(table_info, dict):
                return False
                
            if 'columns' not in table_info:
                return False
                
            # Validate column structure
            for column_name, column_info in table_info['columns'].items():
                if 'type' not in column_info:
                    return False
                    
        return True
        
    except Exception:
        return False
