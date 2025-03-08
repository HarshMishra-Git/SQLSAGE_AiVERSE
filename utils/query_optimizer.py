"""SQL query optimization utilities"""
import sqlparse
from typing import Dict, List, Tuple

class QueryOptimizer:
    """Optimizes SQL queries for better performance"""

    def __init__(self):
        self.optimization_rules = [
            self._optimize_select_columns,
            self._optimize_joins,
            self._optimize_where_conditions,
            self._add_indexes_hint
        ]

    def optimize_query(self, query: str, schema: Dict = None) -> Tuple[str, List[str]]:
        """
        Optimize the given SQL query
        Returns: (optimized_query, list of optimization suggestions)
        """
        suggestions = []
        optimized = query

        # Apply each optimization rule
        for rule in self.optimization_rules:
            optimized, rule_suggestions = rule(optimized, schema)
            suggestions.extend(rule_suggestions)

        return optimized, suggestions

    def _optimize_select_columns(self, query: str, schema: Dict) -> Tuple[str, List[str]]:
        """Optimize SELECT clause"""
        suggestions = []
        
        if 'SELECT *' in query.upper():
            suggestions.append("Consider selecting specific columns instead of SELECT *")
        
        return query, suggestions

    def _optimize_joins(self, query: str, schema: Dict) -> Tuple[str, List[str]]:
        """Optimize JOIN operations"""
        suggestions = []
        
        # Check for proper join conditions
        if 'JOIN' in query.upper() and 'ON' not in query.upper():
            suggestions.append("Add proper JOIN conditions using ON clause")
            
        return query, suggestions

    def _optimize_where_conditions(self, query: str, schema: Dict) -> Tuple[str, List[str]]:
        """Optimize WHERE conditions"""
        suggestions = []
        
        if 'LIKE' in query.upper():
            suggestions.append("Consider using exact matching instead of LIKE when possible")
            
        return query, suggestions

    def _add_indexes_hint(self, query: str, schema: Dict) -> Tuple[str, List[str]]:
        """Suggest indexes based on query patterns"""
        suggestions = []
        
        if schema and 'WHERE' in query.upper():
            # Extract columns used in WHERE clause
            # Suggest indexes for frequently filtered columns
            suggestions.append("Consider adding indexes for columns used in WHERE clause")
            
        return query, suggestions
