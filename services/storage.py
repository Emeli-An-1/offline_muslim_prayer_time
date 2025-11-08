"""
Storage Service - Data Persistence with Migration Support
Handles settings, prayer times cache, and user preferences
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StorageService:
    """Manages persistent storage for app settings and data"""

    def __init__(self, app_dir: Optional[Path] = None):
        """
        Initialize storage service
        
        Args:
            app_dir: Application directory for data storage
        """
        if app_dir is None:
            app_dir = Path.home() / ".prayer_offline"
        
        self.app_dir = Path(app_dir)
        self.app_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.app_dir / "prayer_offline.db"
        self.settings_file = self.app_dir / "settings.json"
        
        # Initialize database
        self._init_database()
        
        # Load settings into memory for fast access
        self._settings_cache: Dict[str, Any] = {}
        self._load_settings()
        
        logger.info(f"Storage initialized at: {self.app_dir}")

    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Prayer times cache - FIXED: Added location_hash column
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prayer_times_cache (
                    date TEXT NOT NULL,
                    location_hash TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (date, location_hash)
                )
            """)
            
            # Tasbih history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasbih_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dhikr_type TEXT NOT NULL,
                    count INTEGER NOT NULL,
                    target INTEGER,
                    completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Dua bookmarks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dua_bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dua_id TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Notification log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prayer_name TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    scheduled_time TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def _load_settings(self):
        """Load settings from JSON file into cache"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self._settings_cache = json.load(f)
                logger.info(f"Loaded {len(self._settings_cache)} settings from file")
            else:
                # Initialize with default settings
                self._settings_cache = self._get_default_settings()
                self._save_settings()
                logger.info("Initialized default settings")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self._settings_cache = self._get_default_settings()

    def _save_settings(self):
        """Save settings cache to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings_cache, f, indent=2, ensure_ascii=False)
            logger.debug("Settings saved successfully")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def _get_default_settings(self) -> Dict[str, Any]:
        """Return default application settings"""
        return {
            "location_configured": False,
            "location": {
                "latitude": None,
                "longitude": None,
                "city": None,
                "country": None,
                "timezone": "UTC"
            },
            "calculation_method": "ISNA",
            "asr_method": "Standard",
            "high_latitude_rule": "AngleBased",
            "language": "en",
            "theme_mode": "System",  # Changed from "system"
            "theme_name": "islamic_prayer",  # NEW - add this line
            "notifications_enabled": True,
            "notification_sound": "adhan",
            "vibration_enabled": True,
            "jamaat_config": {
                "Fajr": {
                    "mode": "fixed",
                    "time": "05:45",
                    "minutes": None,
                    "enabled": True
                },
                "Dhuhr": {
                    "mode": "shift",
                    "time": None,
                    "minutes": 10,
                    "enabled": True
                },
                "Asr": {
                    "mode": "shift",
                    "time": None,
                    "minutes": 10,
                    "enabled": True
                },
                "Maghrib": {
                    "mode": "shift",
                    "time": None,
                    "minutes": 5,
                    "enabled": True
                },
                "Isha": {
                    "mode": "fixed",
                    "time": "20:00",
                    "minutes": None,
                    "enabled": True
                }
            },
            "adhan_notifications": {
                "Fajr": True,
                "Dhuhr": True,
                "Asr": True,
                "Maghrib": True,
                "Isha": True
            },
            "jamaat_notifications": {
                "Fajr": True,
                "Dhuhr": True,
                "Asr": True,
                "Maghrib": True,
                "Isha": True
            },
            "font_size": "medium",
            "show_seconds": True,
            "24_hour_format": False,
            "first_launch": True
        }

    # Public API methods
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        try:
            # Support dot notation for nested keys
            keys = key.split('.')
            value = self._settings_cache
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except Exception as e:
            logger.error(f"Error getting setting '{key}': {e}")
            return default

    def set(self, key: str, value: Any) -> bool:
        """
        Set a setting value
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Support dot notation for nested keys
            keys = key.split('.')
            
            if len(keys) == 1:
                # Simple key
                self._settings_cache[key] = value
            else:
                # Nested key - navigate to parent
                current = self._settings_cache
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                
                # Set the final value
                current[keys[-1]] = value
            
            # Save to file
            self._save_settings()
            logger.debug(f"Setting '{key}' updated")
            return True
            
        except Exception as e:
            logger.error(f"Error setting '{key}': {e}")
            return False

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary"""
        return self._settings_cache.copy()

    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update multiple settings at once
        
        Args:
            settings: Dictionary of settings to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._settings_cache.update(settings)
            self._save_settings()
            logger.info(f"Updated {len(settings)} settings")
            return True
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return False

    def reset_settings(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self._settings_cache = self._get_default_settings()
            self._save_settings()
            logger.info("Settings reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            return False

    # Prayer times cache methods - FIXED: Added location_hash parameter
    
    def cache_prayer_times(self, date: str, location_hash: str, data: Dict[str, Any]) -> bool:
        """
        Cache prayer times for a specific date and location
        
        Args:
            date: Date string (YYYY-MM-DD)
            location_hash: Location identifier hash
            data: Prayer times data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO prayer_times_cache (date, location_hash, data)
                VALUES (?, ?, ?)
            """, (date, location_hash, json.dumps(data)))
            
            conn.commit()
            conn.close()
            logger.debug(f"Cached prayer times for {date} at {location_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching prayer times: {e}")
            return False

    def get_cached_prayer_times(self, date: str, location_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached prayer times for a specific date and location
        
        Args:
            date: Date string (YYYY-MM-DD)
            location_hash: Location identifier hash
            
        Returns:
            Prayer times data or None if not found
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data FROM prayer_times_cache 
                WHERE date = ? AND location_hash = ?
            """, (date, location_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached prayer times: {e}")
            return None

    # Tasbih methods
    
    def save_tasbih_session(self, dhikr_type: str, count: int, 
                           target: Optional[int] = None, 
                           completed: bool = False) -> bool:
        """Save a tasbih counting session"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tasbih_history (dhikr_type, count, target, completed)
                VALUES (?, ?, ?, ?)
            """, (dhikr_type, count, target, 1 if completed else 0))
            
            conn.commit()
            conn.close()
            logger.debug(f"Saved tasbih session: {dhikr_type} - {count}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tasbih session: {e}")
            return False

    def get_tasbih_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent tasbih history"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tasbih_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting tasbih history: {e}")
            return []

    def get_tasbih_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get tasbih statistics for the last N days"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get total count per dhikr type
            cursor.execute("""
                SELECT dhikr_type, SUM(count) as total_count, COUNT(*) as sessions
                FROM tasbih_history
                WHERE created_at >= datetime('now', '-' || ? || ' days')
                GROUP BY dhikr_type
            """, (days,))
            
            results = cursor.fetchall()
            conn.close()
            
            stats = {}
            for row in results:
                stats[row[0]] = {
                    "total_count": row[1],
                    "sessions": row[2]
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting tasbih stats: {e}")
            return {}

    # Dua bookmarks
    
    def add_dua_bookmark(self, dua_id: str) -> bool:
        """Add a dua to bookmarks"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO dua_bookmarks (dua_id)
                VALUES (?)
            """, (dua_id,))
            
            conn.commit()
            conn.close()
            logger.debug(f"Bookmarked dua: {dua_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error bookmarking dua: {e}")
            return False

    def remove_dua_bookmark(self, dua_id: str) -> bool:
        """Remove a dua from bookmarks"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM dua_bookmarks WHERE dua_id = ?
            """, (dua_id,))
            
            conn.commit()
            conn.close()
            logger.debug(f"Removed bookmark: {dua_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing bookmark: {e}")
            return False

    def get_dua_bookmarks(self) -> List[str]:
        """Get all bookmarked dua IDs"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT dua_id FROM dua_bookmarks
                ORDER BY created_at DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            return [row[0] for row in results]
            
        except Exception as e:
            logger.error(f"Error getting bookmarks: {e}")
            return []

    def is_dua_bookmarked(self, dua_id: str) -> bool:
        """Check if a dua is bookmarked"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM dua_bookmarks WHERE dua_id = ?
            """, (dua_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking bookmark: {e}")
            return False

    # Cleanup methods
    
    def clear_old_cache(self, days: int = 30) -> bool:
        """Clear prayer times cache older than N days"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM prayer_times_cache
                WHERE created_at < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleared {deleted} old cache entries")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def export_data(self, export_path: Path) -> bool:
        """Export all user data to JSON file"""
        try:
            data = {
                "settings": self._settings_cache,
                "tasbih_history": self.get_tasbih_history(limit=1000),
                "dua_bookmarks": self.get_dua_bookmarks(),
                "export_date": datetime.now().isoformat()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

    def import_data(self, import_path: Path) -> bool:
        """Import user data from JSON file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Import settings
            if "settings" in data:
                self._settings_cache = data["settings"]
                self._save_settings()
            
            # Import tasbih history
            if "tasbih_history" in data:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                for session in data["tasbih_history"]:
                    cursor.execute("""
                        INSERT INTO tasbih_history 
                        (dhikr_type, count, target, completed, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        session.get("dhikr_type"),
                        session.get("count"),
                        session.get("target"),
                        session.get("completed"),
                        session.get("created_at")
                    ))
                
                conn.commit()
                conn.close()
            
            # Import bookmarks
            if "dua_bookmarks" in data:
                for dua_id in data["dua_bookmarks"]:
                    self.add_dua_bookmark(dua_id)
            
            logger.info(f"Data imported from {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return False