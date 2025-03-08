"""User preferences and settings management"""
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class UserPreferences:
    def __init__(self, storage_file: str = "user_preferences.json"):
        self.storage_file = storage_file
        self.preferences = self.load_preferences()

    def load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from file"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "theme": "light",
                "dialect": "postgresql",
                "font_size": "medium",
                "show_line_numbers": True,
                "auto_complete": True,
                "connection_profiles": [],
                "recent_connections": [],
                "shared_queries": [],
                "performance_metrics": {
                    "total_queries": 0,
                    "successful_queries": 0,
                    "average_execution_time": 0.0,
                    "last_updated": datetime.now().isoformat()
                }
            }

    def save_preferences(self) -> None:
        """Save current preferences to file"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)

    def update_preference(self, key: str, value: Any) -> None:
        """Update a single preference"""
        self.preferences[key] = value
        self.save_preferences()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value"""
        return self.preferences.get(key, default)

    def add_connection_profile(self, profile: Dict[str, str]) -> None:
        """Add a new database connection profile"""
        if "connection_profiles" not in self.preferences:
            self.preferences["connection_profiles"] = []
        self.preferences["connection_profiles"].append(profile)
        self.save_preferences()

    def get_connection_profiles(self) -> List[Dict[str, str]]:
        """Get all saved connection profiles"""
        return self.preferences.get("connection_profiles", [])

    def add_shared_query(self, query: Dict[str, Any]) -> None:
        """Add a shared query with annotations"""
        if "shared_queries" not in self.preferences:
            self.preferences["shared_queries"] = []
        self.preferences["shared_queries"].append({
            **query,
            "shared_at": datetime.now().isoformat()
        })
        self.save_preferences()

    def get_shared_queries(self) -> List[Dict[str, Any]]:
        """Get all shared queries"""
        return self.preferences.get("shared_queries", [])

    def update_performance_metrics(self, execution_time: float, success: bool) -> None:
        """Update query performance metrics"""
        metrics = self.preferences.get("performance_metrics", {
            "total_queries": 0,
            "successful_queries": 0,
            "average_execution_time": 0.0,
            "last_updated": datetime.now().isoformat()
        })

        metrics["total_queries"] += 1
        if success:
            metrics["successful_queries"] += 1

        # Update running average
        prev_avg = metrics["average_execution_time"]
        total = metrics["total_queries"]
        metrics["average_execution_time"] = (prev_avg * (total - 1) + execution_time) / total
        metrics["last_updated"] = datetime.now().isoformat()

        self.preferences["performance_metrics"] = metrics
        self.save_preferences()