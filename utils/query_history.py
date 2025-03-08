"""Query history management"""
import json
from datetime import datetime
from typing import List, Dict, Optional

class QueryHistory:
    """Manages SQL query history and favorites"""
    
    def __init__(self, storage_file: str = "query_history.json"):
        self.storage_file = storage_file
        self.history: List[Dict] = []
        self.load_history()

    def add_query(self, 
                 natural_query: str, 
                 sql_query: str, 
                 dialect: str = "mysql",
                 tags: List[str] = None) -> None:
        """Add a query to history"""
        query_record = {
            "timestamp": datetime.now().isoformat(),
            "natural_query": natural_query,
            "sql_query": sql_query,
            "dialect": dialect,
            "tags": tags or [],
            "favorite": False
        }
        self.history.append(query_record)
        self.save_history()

    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """Get recent queries"""
        return sorted(
            self.history,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]

    def get_favorite_queries(self) -> List[Dict]:
        """Get favorite queries"""
        return [q for q in self.history if q.get("favorite", False)]

    def toggle_favorite(self, query_timestamp: str) -> bool:
        """Toggle favorite status of a query"""
        for query in self.history:
            if query["timestamp"] == query_timestamp:
                query["favorite"] = not query.get("favorite", False)
                self.save_history()
                return query["favorite"]
        return False

    def search_queries(self, 
                      keyword: str, 
                      dialect: Optional[str] = None) -> List[Dict]:
        """Search queries by keyword and dialect"""
        results = []
        for query in self.history:
            if (keyword.lower() in query["natural_query"].lower() or
                keyword.lower() in query["sql_query"].lower()):
                if not dialect or query["dialect"] == dialect:
                    results.append(query)
        return results

    def save_history(self) -> None:
        """Save query history to file"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def load_history(self) -> None:
        """Load query history from file"""
        try:
            with open(self.storage_file, 'r') as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.history = []
