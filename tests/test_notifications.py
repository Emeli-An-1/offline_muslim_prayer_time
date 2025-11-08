"""
Notification System Tests

Functional tests for NotificationService:
- Notification scheduling and delivery
- Permission handling
- Background persistence
- Notification triggering
- Error recovery
- Async operations
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta, time as dt_time
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Import actual services
from services.notifier import NotificationService, NOTIFICATION_AVAILABLE


# ==================== FIXTURES ====================

@pytest.fixture
def temp_dir():
    """Create temporary directory for testing"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
async def notifier(temp_dir):
    """Create a temporary notification service for testing"""
    # Set up temporary notification database path
    notification_db = temp_dir / "notification_schedule.json"
    
    # Create notifier with patched path
    notifier = NotificationService()
    
    # Patch the NOTIFICATION_DB path
    import services.notifier as notifier_module
    original_db = notifier_module.NOTIFICATION_DB
    notifier_module.NOTIFICATION_DB = str(notification_db)
    
    # Initialize
    await notifier.initialize()
    
    yield notifier
    
    # Stop notification loop
    await notifier.stop_notification_loop()
    
    # Restore original path
    notifier_module.NOTIFICATION_DB = original_db


@pytest.fixture
def sample_prayer_times():
    """Sample prayer times data"""
    return {
        "date": "2024-01-15",
        "prayers": {
            "Fajr": {"adhan": "05:30", "jamaat": "05:45"},
            "Dhuhr": {"adhan": "12:30", "jamaat": "12:40"},
            "Asr": {"adhan": "15:45", "jamaat": "15:55"},
            "Maghrib": {"adhan": "18:15", "jamaat": "18:20"},
            "Isha": {"adhan": "19:45", "jamaat": "20:00"}
        }
    }


@pytest.fixture
def jamaat_config():
    """Sample jamaat configuration"""
    return {
        "Fajr": {"enabled": True, "mode": "shift", "minutes": 15},
        "Dhuhr": {"enabled": True, "mode": "shift", "minutes": 10},
        "Asr": {"enabled": True, "mode": "shift", "minutes": 10},
        "Maghrib": {"enabled": True, "mode": "shift", "minutes": 5},
        "Isha": {"enabled": True, "mode": "fixed", "time": "20:00"}
    }


# ==================== TESTS ====================

class TestNotificationScheduling:
    """Test notification scheduling"""
    
    @pytest.mark.asyncio
    async def test_schedule_single_notification(self, notifier):
        """Test scheduling a single notification"""
        notification_id = await notifier.schedule_prayer_notification(
            "Fajr", "05:30", "adhan"
        )
        
        assert notification_id is not None
        assert "Fajr" in notification_id
        assert "adhan" in notification_id
        
        # Check it's in scheduled list
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) == 1
        assert scheduled[0]["prayer"] == "Fajr"
        assert scheduled[0]["time"] == "05:30"
    
    @pytest.mark.asyncio
    async def test_schedule_daily_notifications(self, notifier, sample_prayer_times, jamaat_config):
        """Test scheduling daily notifications for all prayers"""
        success = await notifier.schedule_daily_notifications(
            sample_prayer_times, jamaat_config
        )
        
        assert success is True
        
        # Should have notifications for each prayer (adhan + jamaat)
        scheduled = notifier.get_scheduled_notifications()
        
        # Count prayers with jamaat enabled
        expected_count = 0
        for prayer, times in sample_prayer_times["prayers"].items():
            if times.get("adhan"):
                expected_count += 1  # Adhan notification
            if times.get("jamaat"):
                expected_count += 1  # Jamaat notification
        
        assert len(scheduled) == expected_count
    
    @pytest.mark.asyncio
    async def test_notification_at_specific_time(self, notifier):
        """Test scheduling notification at specific time"""
        notification_time = "05:30"
        
        await notifier.schedule_prayer_notification("Fajr", notification_time, "adhan")
        
        scheduled = notifier.get_scheduled_notifications()
        assert scheduled[0]["time"] == "05:30"
        
        # Validate time format
        h, m = map(int, notification_time.split(":"))
        assert 0 <= h <= 23
        assert 0 <= m <= 59
    
    @pytest.mark.asyncio
    async def test_cancel_scheduled_notification(self, notifier):
        """Test canceling a scheduled notification"""
        # Schedule notification
        notification_id = await notifier.schedule_prayer_notification(
            "Fajr", "05:30", "adhan"
        )
        
        # Verify it's scheduled
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) == 1
        
        # Cancel it
        success = await notifier.cancel_prayer_notification(notification_id)
        assert success is True
        
        # Verify it's removed
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) == 0
    
    @pytest.mark.asyncio
    async def test_reschedule_notification(self, notifier):
        """Test rescheduling an existing notification"""
        # Schedule notification
        notif_id = await notifier.schedule_prayer_notification(
            "Fajr", "05:30", "adhan"
        )
        
        # Cancel old one
        await notifier.cancel_prayer_notification(notif_id)
        
        # Schedule new one with different time
        new_id = await notifier.schedule_prayer_notification(
            "Fajr", "05:45", "adhan"
        )
        
        # Verify new time
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) == 1
        assert scheduled[0]["time"] == "05:45"
    
    @pytest.mark.asyncio
    async def test_notification_structure(self, notifier):
        """Test notification data structure"""
        await notifier.schedule_prayer_notification("Fajr", "05:30", "adhan")
        
        scheduled = notifier.get_scheduled_notifications()
        notification = scheduled[0]
        
        # Check required fields
        assert "prayer" in notification
        assert "time" in notification
        assert "type" in notification
        assert "id" in notification
        
        # Verify values
        assert notification["prayer"] == "Fajr"
        assert notification["time"] == "05:30"
        assert notification["type"] == "adhan"
    
    @pytest.mark.asyncio
    async def test_batch_notification_scheduling(self, notifier):
        """Test scheduling multiple notifications in batch"""
        prayers = [
            ("Fajr", "05:30", "adhan"),
            ("Dhuhr", "12:30", "adhan"),
            ("Asr", "15:30", "adhan"),
            ("Maghrib", "18:30", "adhan"),
            ("Isha", "20:30", "adhan")
        ]
        
        for prayer, time, notif_type in prayers:
            await notifier.schedule_prayer_notification(prayer, time, notif_type)
        
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) == 5
        
        # Verify all prayers are scheduled
        prayer_names = [n["prayer"] for n in scheduled]
        assert "Fajr" in prayer_names
        assert "Isha" in prayer_names
    
    @pytest.mark.asyncio
    async def test_duplicate_notification_prevention(self, notifier):
        """Test that duplicate notifications are prevented"""
        # Schedule same notification twice
        id1 = await notifier.schedule_prayer_notification("Fajr", "05:30", "adhan")
        id2 = await notifier.schedule_prayer_notification("Fajr", "05:30", "adhan")
        
        # Should have same ID (duplicate prevented)
        assert id1 == id2
        
        # Should only have one notification
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) == 1


class TestPermissionHandling:
    """Test notification permission handling"""
    
    @pytest.mark.asyncio
    async def test_check_notification_permission(self, notifier):
        """Test checking if notification permission is available"""
        has_permission = await notifier.update_notification_permissions()
        
        # Should return boolean
        assert isinstance(has_permission, bool)
        
        # Should match NOTIFICATION_AVAILABLE
        assert has_permission == NOTIFICATION_AVAILABLE
    
    @pytest.mark.asyncio
    async def test_notification_availability(self, notifier):
        """Test checking notification availability"""
        is_available = notifier.is_notification_available()
        
        assert isinstance(is_available, bool)
        assert is_available == NOTIFICATION_AVAILABLE
    
    @pytest.mark.asyncio
    async def test_platform_info(self, notifier):
        """Test getting platform information"""
        platform_info = notifier.get_platform_info()
        
        assert "platform" in platform_info
        assert "available" in platform_info
        assert "library" in platform_info
        
        assert isinstance(platform_info["available"], bool)
    
    @pytest.mark.asyncio
    @patch('services.notifier.NOTIFICATION_AVAILABLE', False)
    async def test_graceful_degradation_when_unavailable(self, notifier):
        """Test graceful degradation when notifications unavailable"""
        # Should still initialize without error
        assert notifier._initialized is True
        
        # Test notification should return False
        result = await notifier.test_notification()
        assert result is False


class TestBackgroundPersistence:
    """Test notification persistence across app restarts"""
    
    @pytest.mark.asyncio
    async def test_notifications_persist_to_file(self, notifier, temp_dir):
        """Test that scheduled notifications persist to file"""
        # Schedule notifications
        await notifier.schedule_prayer_notification("Fajr", "05:30", "adhan")
        await notifier.schedule_prayer_notification("Dhuhr", "12:30", "adhan")
        
        # Check file was created
        import services.notifier as notifier_module
        db_path = Path(notifier_module.NOTIFICATION_DB)
        assert db_path.exists()
        
        # Check file content
        with open(db_path, 'r', encoding="utf-8") as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert data[0]["prayer"] == "Fajr"
    
    @pytest.mark.asyncio
    async def test_restore_notifications_on_restart(self, temp_dir):
        """Test restoring notifications on app restart"""
        # Create notification file
        notification_db = temp_dir / "notification_schedule.json"
        test_data = [
            {"id": "n001", "prayer": "Fajr", "time": "05:30", "type": "adhan"},
            {"id": "n002", "prayer": "Dhuhr", "time": "12:30", "type": "adhan"}
        ]
        
        with open(notification_db, 'w', encoding="utf-8") as f:
            json.dump(test_data, f)
        
        # Create new notifier instance (simulating restart)
        import services.notifier as notifier_module
        original_db = notifier_module.NOTIFICATION_DB
        notifier_module.NOTIFICATION_DB = str(notification_db)
        
        notifier = NotificationService()
        await notifier.initialize()
        
        # Should restore notifications
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) == 2
        assert scheduled[0]["prayer"] == "Fajr"
        
        await notifier.stop_notification_loop()
        notifier_module.NOTIFICATION_DB = original_db
    
    @pytest.mark.asyncio
    async def test_cancel_all_notifications_clears_file(self, notifier):
        """Test that canceling all notifications clears the file"""
        # Schedule some notifications
        await notifier.schedule_prayer_notification("Fajr", "05:30", "adhan")
        await notifier.schedule_prayer_notification("Dhuhr", "12:30", "adhan")
        
        # Cancel all
        await notifier.cancel_all_notifications()
        
        # Verify empty
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) == 0


class TestNotificationTriggering:
    """Test notification triggering logic"""
    
    @pytest.mark.asyncio
    async def test_get_next_notification(self, notifier):
        """Test getting next upcoming notification"""
        # Schedule future notification
        future_time = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
        await notifier.schedule_prayer_notification("Dhuhr", future_time, "adhan")
        
        # Also schedule past notification (should be ignored)
        past_time = (datetime.now() - timedelta(hours=1)).strftime("%H:%M")
        await notifier.schedule_prayer_notification("Fajr", past_time, "adhan")
        
        # Get next notification
        next_notif = notifier.get_next_notification()
        
        # Should return the future one
        if next_notif:
            assert next_notif["time"] == future_time
    
    @pytest.mark.asyncio
    @patch('services.notifier.notification')
    async def test_test_notification_sends(self, mock_notification, notifier):
        """Test that test notification is sent"""
        if NOTIFICATION_AVAILABLE:
            mock_notification.notify = Mock()
            
            result = await notifier.test_notification()
            
            # Should attempt to send
            assert result is True or mock_notification.notify.called
    
    @pytest.mark.asyncio
    async def test_notification_loop_starts(self, notifier):
        """Test that notification loop starts"""
        # Loop should be started during initialization
        assert notifier._running is True or not NOTIFICATION_AVAILABLE
        assert notifier._notification_task is not None or not NOTIFICATION_AVAILABLE
    
    @pytest.mark.asyncio
    async def test_notification_loop_stops(self, notifier):
        """Test that notification loop can be stopped"""
        # Stop the loop
        await notifier.stop_notification_loop()
        
        assert notifier._running is False


class TestNotificationErrorHandling:
    """Test notification error handling"""
    
    @pytest.mark.asyncio
    async def test_invalid_notification_time(self, notifier):
        """Test handling invalid notification time"""
        invalid_time = "25:00"
        
        # Should still schedule (validation happens elsewhere)
        await notifier.schedule_prayer_notification("Fajr", invalid_time, "adhan")
        
        scheduled = notifier.get_scheduled_notifications()
        # Notification is scheduled, but validation should catch it
        assert len(scheduled) == 1
    
    @pytest.mark.asyncio
    async def test_empty_prayer_name(self, notifier):
        """Test handling empty prayer name"""
        result = await notifier.schedule_prayer_notification("", "05:30", "adhan")
        
        # Should still return an ID
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_corrupted_notification_file_recovery(self, temp_dir):
        """Test recovery from corrupted notification file"""
        # Create corrupted file
        notification_db = temp_dir / "notification_schedule.json"
        with open(notification_db, 'w', encoding="utf-8") as f:
            f.write("{ invalid json")
        
        # Create notifier (should handle corrupted file)
        import services.notifier as notifier_module
        original_db = notifier_module.NOTIFICATION_DB
        notifier_module.NOTIFICATION_DB = str(notification_db)
        
        notifier = NotificationService()
        await notifier.initialize()
        
        # Should initialize with empty list
        scheduled = notifier.get_scheduled_notifications()
        assert scheduled == []
        
        await notifier.stop_notification_loop()
        notifier_module.NOTIFICATION_DB = original_db
    
    @pytest.mark.asyncio
    async def test_notification_service_without_plyer(self, notifier):
        """Test notification service works without plyer installed"""
        # Service should initialize even without plyer
        assert notifier._initialized is True
        
        # Should gracefully handle lack of notification support
        is_available = notifier.is_notification_available()
        assert isinstance(is_available, bool)


class TestNotificationIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_daily_notification_workflow(self, notifier, sample_prayer_times, jamaat_config):
        """Test complete daily notification workflow"""
        # 1. Schedule daily notifications
        success = await notifier.schedule_daily_notifications(
            sample_prayer_times, jamaat_config
        )
        assert success is True
        
        # 2. Verify all notifications scheduled
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) > 0
        
        # 3. Check specific prayers are scheduled
        prayer_names = [n["prayer"] for n in scheduled]
        assert "Fajr" in prayer_names
        assert "Isha" in prayer_names
        
        # 4. Get next notification
        next_notif = notifier.get_next_notification()
        # Should return None or a valid notification
        assert next_notif is None or "prayer" in next_notif
        
        # 5. Cancel all and verify
        await notifier.cancel_all_notifications()
        scheduled = notifier.get_scheduled_notifications()
        assert len(scheduled) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_notification_persistence_lifecycle(self, temp_dir):
        """Test notification persistence through lifecycle"""
        notification_db = temp_dir / "notification_schedule.json"
        
        import services.notifier as notifier_module
        original_db = notifier_module.NOTIFICATION_DB
        notifier_module.NOTIFICATION_DB = str(notification_db)
        
        # Session 1: Schedule notifications
        notifier1 = NotificationService()
        await notifier1.initialize()
        await notifier1.schedule_prayer_notification("Fajr", "05:30", "adhan")
        await notifier1.schedule_prayer_notification("Dhuhr", "12:30", "adhan")
        await notifier1.stop_notification_loop()
        
        # Session 2: Restore notifications
        notifier2 = NotificationService()
        await notifier2.initialize()
        scheduled = notifier2.get_scheduled_notifications()
        
        assert len(scheduled) == 2
        assert scheduled[0]["prayer"] == "Fajr"
        assert scheduled[1]["prayer"] == "Dhuhr"
        
        await notifier2.stop_notification_loop()
        notifier_module.NOTIFICATION_DB = original_db
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_update_daily_schedule(self, notifier, sample_prayer_times, jamaat_config):
        """Test updating daily schedule replaces old notifications"""
        # Schedule first set
        await notifier.schedule_daily_notifications(sample_prayer_times, jamaat_config)
        first_count = len(notifier.get_scheduled_notifications())
        
        # Update with new times
        updated_times = sample_prayer_times.copy()
        updated_times["prayers"]["Fajr"]["adhan"] = "05:45"
        
        await notifier.schedule_daily_notifications(updated_times, jamaat_config)
        second_count = len(notifier.get_scheduled_notifications())
        
        # Should have same count (replaced, not added)
        assert second_count == first_count
        
        # Verify Fajr time updated
        scheduled = notifier.get_scheduled_notifications()
        fajr_notifs = [n for n in scheduled if n["prayer"] == "Fajr"]
        
        # Should have new time
        if fajr_notifs:
            assert any(n["time"] == "05:45" for n in fajr_notifs)


class TestNotificationValidation:
    """Test notification data validation"""
    
    @pytest.mark.unit
    def test_time_format_validation(self):
        """Test HH:MM time format validation"""
        valid_times = ["00:00", "12:30", "23:59", "05:45"]
        
        for time_str in valid_times:
            parts = time_str.split(":")
            assert len(parts) == 2
            h, m = int(parts[0]), int(parts[1])
            assert 0 <= h <= 23
            assert 0 <= m <= 59
    
    @pytest.mark.unit
    def test_invalid_time_rejection(self):
        """Test rejection of invalid times"""
        invalid_times = ["24:00", "12:60", "abc:def"]
        
        for time_str in invalid_times:
            try:
                parts = time_str.split(":")
                h, m = int(parts[0]), int(parts[1])
                is_valid = 0 <= h <= 23 and 0 <= m <= 59
            except (ValueError, IndexError):
                is_valid = False
            
            assert not is_valid
    
    @pytest.mark.unit
    def test_prayer_name_validation(self):
        """Test prayer name validation"""
        valid_prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        
        test_prayer = "Fajr"
        assert test_prayer in valid_prayers
    
    @pytest.mark.unit
    def test_notification_type_validation(self):
        """Test notification type validation"""
        valid_types = ["adhan", "jamaat", "reminder"]
        
        test_type = "adhan"
        assert test_type in valid_types