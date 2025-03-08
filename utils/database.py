"""Database utility functions"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any, Union

# Load environment variables from .env file
load_dotenv()

class Database:
    """Database connection and query execution handler"""

    def __init__(self):
        self.conn_params = {
            'dbname': os.getenv('PGDATABASE'),
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
            'host': os.getenv('PGHOST'),
            'port': os.getenv('PGPORT')
        }

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as a list of dictionaries"""
        try:
            with psycopg2.connect(**self.conn_params) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    if cur.description:  # If query returns data
                        return cur.fetchall()
                    return []
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def test_query(self, query: str) -> bool:
        """Test if a query is valid without executing it"""
        try:
            with psycopg2.connect(**self.conn_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("EXPLAIN " + query)
                    return True
        except Exception:
            return False

    def get_table_schema(self) -> Dict[str, Any]:
        """Get the database schema information"""
        schema_query = """
        WITH relationships AS (
            SELECT
                tc.table_name as table_name,
                kcu.column_name as column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
        )
        SELECT 
            t.table_name,
            json_build_object(
                'columns', json_object_agg(
                    c.column_name,
                    json_build_object(
                        'type', c.data_type,
                        'nullable', c.is_nullable = 'YES',
                        'default', c.column_default,
                        'is_primary', EXISTS (
                            SELECT 1 FROM information_schema.key_column_usage kcu
                            WHERE kcu.table_name = c.table_name 
                            AND kcu.column_name = c.column_name
                            AND EXISTS (
                                SELECT 1 FROM information_schema.table_constraints tc
                                WHERE tc.constraint_name = kcu.constraint_name
                                AND tc.constraint_type = 'PRIMARY KEY'
                            )
                        )
                    )
                ),
                'relationships', (
                    SELECT json_agg(
                        json_build_object(
                            'column', r.column_name,
                            'references_table', r.foreign_table_name,
                            'references_column', r.foreign_column_name
                        )
                    )
                    FROM relationships r
                    WHERE r.table_name = t.table_name
                )
            ) as table_info
        FROM 
            information_schema.tables t
            JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE 
            t.table_schema = 'public'
        GROUP BY 
            t.table_name;
        """
        try:
            results = self.execute_query(schema_query)
            schema = {}
            for row in results:
                schema[row['table_name']] = row['table_info']
            return schema
        except Exception as e:
            raise Exception(f"Error getting schema: {str(e)}")

    def get_query_explain_plan(self, query: str) -> List[Dict[str, Any]]:
        """Get query execution plan for optimization"""
        try:
            return self.execute_query(f"EXPLAIN (FORMAT JSON) {query}")
        except Exception as e:
            raise Exception(f"Error getting query plan: {str(e)}")

    def validate_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            result = self.execute_query("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            return result[0]['exists'] if result else False
        except Exception:
            return False