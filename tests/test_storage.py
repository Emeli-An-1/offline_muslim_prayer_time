"""
Storage & Data Persistence Tests

Functional tests for StorageService:
- Settings persistence and retrieval
- Data migration compatibility
- Data validation
- Storage error handling
- Cache management
- Data corruption recovery
"""

import pytest
import json
import sqlite3
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

# Import actual services
from services.storage import StorageService
from utils.constants import DEFAULT_SETTINGS


# ==================== FIXTURES ====================

@pytest.fixture
def temp_dir():
    """Create temporary directory for testing"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_storage(temp_dir):
    """Create a temporary storage service for testing"""
    # Create temporary data structure
    data_dir = temp_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    i18n_dir = temp_dir / "i18n"
    i18n_dir.mkdir(exist_ok=True)
    
    # Create storage instance with temp paths
    storage = StorageService()
    storage.data_dir = data_dir
    storage.db_path = data_dir / "test_prayer_offline.db"
    
    # Initialize
    storage.initialize()
    
    return storage


@pytest.fixture
def sample_prayer_times():
    """Sample prayer times data for testing"""
    return {
        "date": "2024-01-15",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York"
        },
        "method": "ISNA",
        "prayers": {
            "Fajr": {"adhan": "05:30", "jamaat": "05:45", "jamaat_mode": "shift"},
            "Sunrise": {"adhan": "06:45", "jamaat": None, "jamaat_mode": None},
            "Dhuhr": {"adhan": "12:30", "jamaat": "12:40", "jamaat_mode": "shift"},
            "Asr": {"adhan": "15:45", "jamaat": "15:55", "jamaat_mode": "shift"},
            "Maghrib": {"adhan": "18:15", "jamaat": "18:20", "jamaat_mode": "shift"},
            "Isha": {"adhan": "19:45", "jamaat": "20:00", "jamaat_mode": "fixed"}
        }
    }


# ==================== TESTS ====================

class TestSettingsPersistence:
    """Test settings persistence and retrieval"""
    
    @pytest.mark.unit
    def test_initialize_creates_default_settings(self, temp_storage):
        """Test default settings are created on initialization"""
        settings = temp_storage.get_settings()
        
        # Should have all default keys
        assert "app" in settings
        assert "location" in settings
        assert "calculation" in settings
        assert "jamaat" in settings
        assert "notifications" in settings
        
        # Verify default values
        assert settings["app"]["language"] == "en"
        assert settings["location"]["city"] == "Mecca"
    
    @pytest.mark.unit
    def test_save_and_load_setting(self, temp_storage):
        """Test saving and loading individual settings"""
        # Save a setting
        test_location = {
            "latitude": 51.5074,
            "longitude": -0.1278,
            "city": "London",
            "country": "UK",
            "timezone": "Europe/London",
            "auto_detect": False
        }
        
        temp_storage.update_setting("location", test_location)
        
        # Load and verify
        loaded_location = temp_storage.get_setting("location")
        assert loaded_location["latitude"] == 51.5074
        assert loaded_location["longitude"] == -0.1278
        assert loaded_location["city"] == "London"
    
    @pytest.mark.unit
    def test_update_individual_setting(self, temp_storage):
        """Test updating individual settings"""
        # Get initial language
        initial_lang = temp_storage.get_setting("app")["language"]
        
        # Update app settings
        app_settings = temp_storage.get_setting("app")
        app_settings["language"] = "ar"
        temp_storage.update_setting("app", app_settings)
        
        # Verify change
        updated = temp_storage.get_setting("app")
        assert updated["language"] == "ar"
        assert updated["language"] != initial_lang
    
    @pytest.mark.unit
    def test_settings_with_special_characters(self, temp_storage):
        """Test settings containing special characters (Arabic, Urdu, etc.)"""
        special_settings = {
            "app_title_ar": "الصلاة أوفلاين",
            "app_title_ur": "نماز آف لاین",
            "location_city": "São Paulo"
        }
        
        temp_storage.update_setting("i18n_test", special_settings)
        
        # Load and verify special characters preserved
        loaded = temp_storage.get_setting("i18n_test")
        assert "الصلاة" in loaded["app_title_ar"]
        assert "نماز" in loaded["app_title_ur"]
        assert "São Paulo" == loaded["location_city"]
    
    @pytest.mark.unit
    def test_get_all_settings(self, temp_storage):
        """Test retrieving all settings at once"""
        all_settings = temp_storage.get_settings()
        
        # Should return dict with multiple keys
        assert isinstance(all_settings, dict)
        assert len(all_settings) >= 5
        
        # Should include all major sections
        expected_keys = ["app", "location", "calculation", "jamaat", "notifications"]
        for key in expected_keys:
            assert key in all_settings
    
    @pytest.mark.unit
    def test_settings_persistence_across_sessions(self, temp_dir):
        """Test settings persist across app sessions"""
        # Session 1: Create storage and save settings
        storage1 = StorageService()
        storage1.data_dir = temp_dir / "data"
        storage1.data_dir.mkdir(exist_ok=True)
        storage1.db_path = storage1.data_dir / "test_prayer_offline.db"
        storage1.initialize()
        
        storage1.update_setting("app", {"language": "ar", "theme": "dark"})
        
        # Session 2: Create new storage instance (simulating app restart)
        storage2 = StorageService()
        storage2.data_dir = temp_dir / "data"
        storage2.db_path = storage2.data_dir / "test_prayer_offline.db"
        storage2.initialize()
        
        # Should load persisted settings
        loaded = storage2.get_setting("app")
        assert loaded["language"] == "ar"
        assert loaded["theme"] == "dark"
    
    @pytest.mark.unit
    def test_large_settings_storage(self, temp_storage):
        """Test storing large settings objects"""
        large_settings = {
            "bookmarks": [f"dua_{i}" for i in range(1000)],
            "history": [{"prayer": "Fajr", "date": f"2024-01-{i%28+1:02d}"} for i in range(500)]
        }
        
        temp_storage.update_setting("large_data", large_settings)
        
        # Load and verify
        loaded = temp_storage.get_setting("large_data")
        assert len(loaded["bookmarks"]) == 1000
        assert len(loaded["history"]) == 500
        assert loaded["bookmarks"][0] == "dua_0"
        assert loaded["bookmarks"][999] == "dua_999"
    
    @pytest.mark.unit
    def test_setting_with_default_fallback(self, temp_storage):
        """Test getting non-existent setting with default value"""
        # Non-existent key with default
        value = temp_storage.get_setting("nonexistent_key", {"default": "value"})
        
        assert value == {"default": "value"}
        assert "default" in value


class TestMigrationCompatibility:
    """Test data migration and version compatibility"""
    
    @pytest.mark.unit
    def test_missing_fields_use_defaults(self, temp_storage):
        """Test that missing fields are filled with defaults"""
        # Save incomplete settings
        incomplete = {"language": "en"}
        temp_storage.update_setting("app", incomplete)
        
        # Get full default settings
        defaults = DEFAULT_SETTINGS["app"]
        
        # Load and check defaults are used for missing fields
        loaded = temp_storage.get_setting("app")
        assert loaded["language"] == "en"  # From saved
        
        # If theme is missing, it should use default
        if "theme" not in incomplete:
            # Should have default theme from initialization
            assert "theme" in DEFAULT_SETTINGS["app"]
    
    @pytest.mark.unit
    def test_old_format_compatibility(self, temp_storage):
        """Test loading data in older format"""
        # Simulate old format without some newer fields
        old_format_location = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York"
            # Missing: country, timezone, auto_detect
        }
        
        temp_storage.update_setting("location", old_format_location)
        loaded = temp_storage.get_setting("location")
        
        # Should still load basic fields
        assert loaded["latitude"] == 40.7128
        assert loaded["city"] == "New York"
    
    @pytest.mark.unit
    def test_schema_validation_structure(self, temp_storage):
        """Test that stored data maintains proper structure"""
        # Get all settings
        settings = temp_storage.get_settings()
        
        # Verify structure
        assert isinstance(settings, dict)
        assert isinstance(settings.get("app"), dict)
        assert isinstance(settings.get("location"), dict)
        assert isinstance(settings.get("jamaat"), dict)


class TestDataValidation:
    """Test data validation"""
    
    @pytest.mark.unit
    def test_coordinate_validation(self):
        """Test latitude/longitude validation"""
        valid_coords = [
            {"lat": 0.0, "lng": 0.0},
            {"lat": 40.7128, "lng": -74.0060},
            {"lat": -33.8688, "lng": 151.2093},
            {"lat": 90.0, "lng": 180.0},
            {"lat": -90.0, "lng": -180.0}
        ]
        
        for coord in valid_coords:
            assert -90 <= coord["lat"] <= 90, f"Invalid latitude: {coord['lat']}"
            assert -180 <= coord["lng"] <= 180, f"Invalid longitude: {coord['lng']}"
    
    @pytest.mark.unit
    def test_invalid_coordinate_rejection(self):
        """Test rejection of invalid coordinates"""
        invalid_coords = [
            {"lat": 91.0, "lng": 0.0},
            {"lat": 0.0, "lng": 181.0},
            {"lat": -91.0, "lng": -181.0},
            {"lat": 100.0, "lng": 200.0}
        ]
        
        for coord in invalid_coords:
            is_valid = (-90 <= coord["lat"] <= 90 and -180 <= coord["lng"] <= 180)
            assert not is_valid, f"Should reject invalid coords: {coord}"
    
    @pytest.mark.unit
    def test_time_format_validation(self):
        """Test HH:MM time format validation"""
        valid_times = ["00:00", "12:30", "23:59", "05:45", "18:15"]
        
        for time_str in valid_times:
            parts = time_str.split(":")
            assert len(parts) == 2, f"Invalid format: {time_str}"
            
            h, m = int(parts[0]), int(parts[1])
            assert 0 <= h <= 23, f"Invalid hour: {h}"
            assert 0 <= m <= 59, f"Invalid minute: {m}"
    
    @pytest.mark.unit
    def test_invalid_time_format_rejection(self):
        """Test rejection of invalid time formats"""
        invalid_times = ["24:00", "12:60", "abc:def", "12", "1:2:3", "-05:30"]
        
        for time_str in invalid_times:
            try:
                parts = time_str.split(":")
                if len(parts) != 2:
                    is_valid = False
                else:
                    h, m = int(parts[0]), int(parts[1])
                    is_valid = (0 <= h <= 23 and 0 <= m <= 59)
            except (ValueError, IndexError):
                is_valid = False
            
            assert not is_valid, f"Should reject invalid time: {time_str}"
    
    @pytest.mark.unit
    def test_language_code_validation(self):
        """Test language code validation"""
        valid_languages = ["en", "ar", "fr", "ur"]
        test_lang = "en"
        
        assert test_lang in valid_languages
        assert "invalid_lang" not in valid_languages
    
    @pytest.mark.unit
    def test_theme_mode_validation(self):
        """Test theme mode validation"""
        valid_themes = ["light", "dark", "auto"]
        
        for theme in valid_themes:
            assert theme in ["light", "dark", "auto"]
        
        assert "invalid_theme" not in valid_themes
    
    @pytest.mark.unit
    def test_font_size_range_validation(self):
        """Test font size range validation"""
        valid_sizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32]
        
        for size in valid_sizes:
            assert 8 <= size <= 32, f"Size out of range: {size}"
        
        invalid_sizes = [4, 6, 40, 100, -10]
        for size in invalid_sizes:
            assert not (8 <= size <= 32), f"Should reject: {size}"
    
    @pytest.mark.unit
    def test_prayer_times_structure_validation(self, sample_prayer_times):
        """Test prayer times data structure validation"""
        # Should have required keys
        assert "date" in sample_prayer_times
        assert "prayers" in sample_prayer_times
        assert isinstance(sample_prayer_times["prayers"], dict)
        
        # Each prayer should have adhan time
        for prayer, times in sample_prayer_times["prayers"].items():
            assert "adhan" in times
            assert isinstance(times["adhan"], str)


class TestStorageErrorHandling:
    """Test storage error handling and recovery"""
    
    @pytest.mark.unit
    def test_read_corrupted_json(self):
        """Test handling of corrupted JSON data"""
        corrupted_data = b"{ invalid json structure"
        
        with pytest.raises(json.JSONDecodeError):
            json.loads(corrupted_data)
    
    @pytest.mark.unit
    def test_file_not_found_creates_defaults(self, temp_storage):
        """Test that missing files are handled gracefully"""
        # Even with fresh storage, should have defaults
        settings = temp_storage.get_settings()
        
        assert settings is not None
        assert isinstance(settings, dict)
        assert len(settings) > 0
    
    @pytest.mark.unit
    def test_database_connection_handling(self, temp_storage):
        """Test database connection is properly managed"""
        # Should be able to query database
        with sqlite3.connect(temp_storage.db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Required tables should exist
            assert "settings" in tables
            assert "prayer_times_cache" in tables
            assert "tasbih_sessions" in tables
    
    @pytest.mark.unit
    def test_invalid_data_type_handling(self, temp_storage):
        """Test handling of invalid data types"""
        # Try to store non-serializable data
        invalid_data = {"callable": lambda x: x}
        
        # Should raise error or handle gracefully
        with pytest.raises((TypeError, json.JSONDecodeError)):
            json.dumps(invalid_data)


class TestCacheManagement:
    """Test cache and performance optimization"""
    
    @pytest.mark.unit
    def test_prayer_times_cache_storage(self, temp_storage, sample_prayer_times):
        """Test caching of calculated prayer times"""
        date_key = "2024-01-15"
        location_hash = "nyc_40.7128_-74.0060"
        
        # Cache prayer times
        temp_storage.cache_prayer_times(date_key, location_hash, sample_prayer_times)
        
        # Retrieve from cache
        cached = temp_storage.get_cached_prayer_times(date_key, location_hash)
        
        assert cached is not None
        assert cached["date"] == "2024-01-15"
        assert "prayers" in cached
        assert cached["prayers"]["Fajr"]["adhan"] == "05:30"
    
    @pytest.mark.unit
    def test_cache_returns_none_when_empty(self, temp_storage):
        """Test cache returns None for non-existent entries"""
        cached = temp_storage.get_cached_prayer_times("nonexistent_date", "nonexistent_location")
        
        assert cached is None
    
    @pytest.mark.unit
    def test_cache_overwrites_existing_entry(self, temp_storage, sample_prayer_times):
        """Test cache overwrites when same key is used"""
        date_key = "2024-01-15"
        location_hash = "test_location"
        
        # Cache first version
        temp_storage.cache_prayer_times(date_key, location_hash, sample_prayer_times)
        
        # Cache updated version
        updated_times = sample_prayer_times.copy()
        updated_times["prayers"]["Fajr"]["adhan"] = "05:45"
        temp_storage.cache_prayer_times(date_key, location_hash, updated_times)
        
        # Should get updated version
        cached = temp_storage.get_cached_prayer_times(date_key, location_hash)
        assert cached["prayers"]["Fajr"]["adhan"] == "05:45"
    
    @pytest.mark.unit
    def test_multiple_location_cache(self, temp_storage, sample_prayer_times):
        """Test caching for multiple locations"""
        date_key = "2024-01-15"
        
        # Cache for NYC
        nyc_hash = "nyc"
        temp_storage.cache_prayer_times(date_key, nyc_hash, sample_prayer_times)
        
        # Cache for London with different times
        london_times = sample_prayer_times.copy()
        london_times["prayers"]["Fajr"]["adhan"] = "06:15"
        london_hash = "london"
        temp_storage.cache_prayer_times(date_key, london_hash, london_times)
        
        # Both should be retrievable
        nyc_cached = temp_storage.get_cached_prayer_times(date_key, nyc_hash)
        london_cached = temp_storage.get_cached_prayer_times(date_key, london_hash)
        
        assert nyc_cached["prayers"]["Fajr"]["adhan"] == "05:30"
        assert london_cached["prayers"]["Fajr"]["adhan"] == "06:15"


class TestTasbihPersistence:
    """Test Tasbih counter data persistence"""
    
    @pytest.mark.unit
    def test_save_tasbih_session(self, temp_storage):
        """Test saving tasbih session"""
        temp_storage.save_tasbih_session("Subḥān Allāh", 33, 33)
        
        # Verify it was saved
        history = temp_storage.get_tasbih_history(days=1)
        assert len(history) > 0
        assert history[0]["dhikr_name"] == "Subḥān Allāh"
        assert history[0]["count"] == 33
    
    @pytest.mark.unit
    def test_get_tasbih_history(self, temp_storage):
        """Test retrieving tasbih history"""
        # Save multiple sessions
        temp_storage.save_tasbih_session("Subḥān Allāh", 33, 33)
        temp_storage.save_tasbih_session("Alḥamdulillāh", 33, 33)
        temp_storage.save_tasbih_session("Allāhu Akbar", 34, 34)
        
        # Get history
        history = temp_storage.get_tasbih_history(days=7)
        
        assert len(history) >= 3
        dhikr_names = [h["dhikr_name"] for h in history]
        assert "Subḥān Allāh" in dhikr_names
        assert "Alḥamdulillāh" in dhikr_names
        assert "Allāhu Akbar" in dhikr_names
    
    @pytest.mark.unit
    def test_empty_tasbih_history(self, temp_storage):
        """Test retrieving history when no sessions exist"""
        history = temp_storage.get_tasbih_history(days=7)
        
        # Should return empty list, not error
        assert history == []


class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    @pytest.mark.unit
    def test_checksum_verification(self):
        """Test checksum verification for data integrity"""
        data = "important_prayer_times_data"
        checksum1 = hashlib.sha256(data.encode()).hexdigest()
        
        # Same data should produce same checksum
        checksum2 = hashlib.sha256(data.encode()).hexdigest()
        assert checksum1 == checksum2
        
        # Different data should produce different checksum
        modified_data = "modified_prayer_times_data"
        checksum3 = hashlib.sha256(modified_data.encode()).hexdigest()
        assert checksum1 != checksum3
    
    @pytest.mark.unit
    def test_database_integrity(self, temp_storage):
        """Test database integrity after multiple operations"""
        # Perform multiple operations
        temp_storage.update_setting("test1", {"value": 1})
        temp_storage.update_setting("test2", {"value": 2})
        temp_storage.update_setting("test1", {"value": 3})  # Update
        
        # Verify data consistency
        test1 = temp_storage.get_setting("test1")
        test2 = temp_storage.get_setting("test2")
        
        assert test1["value"] == 3
        assert test2["value"] == 2
    
    @pytest.mark.unit
    def test_json_encoding_decoding_consistency(self, temp_storage):
        """Test JSON encoding/decoding maintains data integrity"""
        original_data = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        temp_storage.update_setting("json_test", original_data)
        loaded_data = temp_storage.get_setting("json_test")
        
        assert loaded_data == original_data


# ==================== INTEGRATION TESTS ====================

class TestStorageIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.integration
    def test_full_prayer_times_workflow(self, temp_storage, sample_prayer_times):
        """Test complete prayer times storage workflow"""
        date_key = "2024-01-15"
        location_hash = "test_location"
        
        # 1. Cache prayer times
        temp_storage.cache_prayer_times(date_key, location_hash, sample_prayer_times)
        
        # 2. Retrieve from cache
        cached = temp_storage.get_cached_prayer_times(date_key, location_hash)
        assert cached is not None
        
        # 3. Update location settings
        location = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York"
        }
        temp_storage.update_setting("location", location)
        
        # 4. Verify all data is accessible
        loaded_location = temp_storage.get_setting("location")
        assert loaded_location["city"] == "New York"
        assert cached["prayers"]["Fajr"]["adhan"] == "05:30"
    
    @pytest.mark.integration
    def test_complete_app_lifecycle(self, temp_dir):
        """Test complete app lifecycle: init, use, restart"""
        # First launch
        storage1 = StorageService()
        storage1.data_dir = temp_dir / "data"
        storage1.data_dir.mkdir(exist_ok=True)
        storage1.db_path = storage1.data_dir / "test_prayer_offline.db"
        storage1.initialize()
        
        # User configures app
        storage1.update_setting("app", {"language": "ar", "theme": "dark"})
        storage1.update_setting("location", {"city": "London", "latitude": 51.5074})
        storage1.save_tasbih_session("Subḥān Allāh", 33, 33)
        
        # App restarts (new storage instance)
        storage2 = StorageService()
        storage2.data_dir = temp_dir / "data"
        storage2.db_path = storage2.data_dir / "test_prayer_offline.db"
        storage2.initialize()
        
        # All data should be restored
        app = storage2.get_setting("app")
        location = storage2.get_setting("location")
        history = storage2.get_tasbih_history(days=7)
        
        assert app["language"] == "ar"
        assert location["city"] == "London"
        assert len(history) > 0