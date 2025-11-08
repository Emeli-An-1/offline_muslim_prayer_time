"""
Notification Service for PrayerOffline
Handles local notifications with persistent scheduling
"""
import logging
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

try:
    from plyer import notification
    NOTIFICATION_AVAILABLE = True
except ImportError:
    notification = None
    NOTIFICATION_AVAILABLE = False


class NotificationService:
    """Service for handling prayer time notifications"""
    
    def __init__(self, storage_service=None):
        """
        Initialize notification service
        
        Args:
            storage_service: StorageService instance
        """
        self.storage = storage_service
        self.logger = logging.getLogger(__name__)
        self.scheduled_notifications = []
        self._initialized = False
        self._notification_thread = None
        self._stop_event = threading.Event()
    
    def initialize(self):
        """Initialize notification service"""
        try:
            # Load scheduled notifications from storage
            if self.storage:
                self.scheduled_notifications = self.storage.get("scheduled_notifications", [])
            
            # Start background notification checker
            self._start_notification_thread()
            
            self._initialized = True
            self.logger.info(f"Notification service initialized (available: {NOTIFICATION_AVAILABLE})")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize notifier: {e}")
    
    def _start_notification_thread(self):
        """Start background thread to check and send notifications"""
        if self._notification_thread and self._notification_thread.is_alive():
            return
        
        self._stop_event.clear()
        self._notification_thread = threading.Thread(
            target=self._notification_loop,
            daemon=True
        )
        self._notification_thread.start()
        self.logger.info("Notification background thread started")
    
    def _notification_loop(self):
        """Background loop to check and send notifications"""
        while not self._stop_event.is_set():
            try:
                current_time = datetime.now()
                current_time_str = current_time.strftime("%H:%M")
                
                # Check each scheduled notification
                for notif in self.scheduled_notifications.copy():
                    if notif.get("time") == current_time_str and not notif.get("sent_today", False):
                        # Check if notification is enabled
                        if not notif.get("enabled", True):
                            continue
                        
                        # Send the notification
                        self._send_notification(
                            title=notif.get("title", "Prayer Time"),
                            message=notif.get("message", ""),
                            sound_file=notif.get("sound_file")
                        )
                        
                        # Mark as sent today
                        notif["sent_today"] = True
                        notif["last_sent"] = current_time.isoformat()
                
                # Reset sent flags at midnight
                if current_time.hour == 0 and current_time.minute == 0:
                    for notif in self.scheduled_notifications:
                        notif["sent_today"] = False
                    
                    # Save reset state
                    if self.storage:
                        self.storage.set("scheduled_notifications", self.scheduled_notifications)
                
                # Sleep for 30 seconds before next check
                self._stop_event.wait(30)
                
            except Exception as e:
                self.logger.error(f"Error in notification loop: {e}")
                self._stop_event.wait(60)  # Wait longer on error
    
    def schedule_daily_notifications(self, prayer_times: Dict[str, Any], 
                                    jamaat_config: Dict[str, Any] = None) -> bool:
        """
        Schedule notifications for all prayers
        
        Args:
            prayer_times: Prayer times dictionary from calculator
            jamaat_config: Jamaat configuration (optional)
            
        Returns:
            True if scheduling successful
        """
        try:
            # Clear old notifications
            self.cancel_all_notifications()
            
            prayers = prayer_times.get("prayers", {})
            
            # Get notification settings
            adhan_enabled = self.storage.get("notifications_enabled", True) if self.storage else True
            adhan_notifs = self.storage.get("adhan_notifications", {}) if self.storage else {}
            jamaat_notifs = self.storage.get("jamaat_notifications", {}) if self.storage else {}
            
            scheduled_count = 0
            
            for prayer_name, prayer_data in prayers.items():
                if prayer_name == "Sunrise":
                    continue  # Skip sunrise notifications
                
                # Schedule adhan notification
                if adhan_enabled and adhan_notifs.get(prayer_name, True):
                    adhan_time = prayer_data.get("adhan")
                    if adhan_time:
                        self._schedule_notification(
                            prayer_name=prayer_name,
                            time=adhan_time,
                            notification_type="adhan",
                            sound_file="adhan"
                        )
                        scheduled_count += 1
                
                # Schedule jamaat notification
                if adhan_enabled and jamaat_notifs.get(prayer_name, True):
                    jamaat_time = prayer_data.get("jamaat")
                    if jamaat_time:
                        self._schedule_notification(
                            prayer_name=prayer_name,
                            time=jamaat_time,
                            notification_type="jamaat",
                            sound_file="notification"
                        )
                        scheduled_count += 1
            
            # Save to storage
            if self.storage:
                self.storage.set("scheduled_notifications", self.scheduled_notifications)
            
            self.logger.info(f"Scheduled {scheduled_count} notifications")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule notifications: {e}", exc_info=True)
            return False
    
    def _schedule_notification(self, prayer_name: str, time: str, 
                              notification_type: str, sound_file: str = "default"):
        """
        Schedule a single notification
        
        Args:
            prayer_name: Name of the prayer (Fajr, Dhuhr, etc.)
            time: Time in HH:MM format
            notification_type: Type (adhan/jamaat)
            sound_file: Sound file to play
        """
        try:
            notification_id = f"{prayer_name}_{notification_type}_{time}"
            
            # Check for duplicates
            if any(n.get("id") == notification_id for n in self.scheduled_notifications):
                return
            
            # Create notification entry
            if notification_type == "adhan":
                title = f"{prayer_name} Adhan"
                message = f"It's time for {prayer_name} prayer"
            else:
                title = f"{prayer_name} Jamaat"
                message = f"Jamaat for {prayer_name} is starting"
            
            notification_entry = {
                "id": notification_id,
                "prayer": prayer_name,
                "time": time,
                "type": notification_type,
                "title": title,
                "message": message,
                "sound_file": sound_file,
                "sent_today": False,
                "enabled": True,
                "created_at": datetime.now().isoformat()
            }
            
            self.scheduled_notifications.append(notification_entry)
            self.logger.debug(f"Scheduled notification: {notification_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to schedule notification: {e}")
    
    def _send_notification(self, title: str, message: str, 
                          sound_file: Optional[str] = None):
        """
        Send a notification now
        
        Args:
            title: Notification title
            message: Notification message
            sound_file: Optional sound file to play
        """
        try:
            if not NOTIFICATION_AVAILABLE or not notification:
                self.logger.warning("Notifications not available")
                return
            
            # Check if notifications are enabled
            notifications_enabled = self.storage.get("notifications_enabled", True) if self.storage else True
            if not notifications_enabled:
                self.logger.info("Notifications disabled in settings")
                return
            
            # Send notification
            notification.notify(
                title=title,
                message=message,
                app_name="PrayerOffline",
                timeout=10
            )
            
            self.logger.info(f"Notification sent: {title}")
            
            # Play sound if enabled and sound file provided
            notification_sound = self.storage.get("notification_sound", "adhan") if self.storage else "adhan"
            if notification_sound != "none" and sound_file:
                self._play_notification_sound(sound_file)
            
            # Vibrate if enabled
            vibration_enabled = self.storage.get("vibration_enabled", True) if self.storage else True
            if vibration_enabled:
                self._vibrate()
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
    
    def _play_notification_sound(self, sound_file: str):
        """Play notification sound"""
        try:
            # Import audio player
            from services.audio_player import AudioPlayer
            
            audio_player = AudioPlayer()
            
            if sound_file == "adhan":
                audio_player.play_adhan()
            elif sound_file == "notification":
                audio_player.play_notification_sound()
            else:
                # Try to play custom file
                audio_player.play_file(sound_file)
                
        except Exception as e:
            self.logger.error(f"Failed to play notification sound: {e}")
    
    def _vibrate(self):
        """Trigger device vibration"""
        try:
            from plyer import vibrator
            vibrator.vibrate(0.5)  # Vibrate for 0.5 seconds
        except Exception:
            pass  # Vibration not available on this platform
    
    def cancel_all_notifications(self) -> bool:
        """Cancel all scheduled notifications"""
        try:
            self.scheduled_notifications.clear()
            if self.storage:
                self.storage.set("scheduled_notifications", [])
            self.logger.info("All notifications cancelled")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel notifications: {e}")
            return False
    
    def cancel_notification(self, notification_id: str) -> bool:
        """Cancel a specific notification"""
        try:
            self.scheduled_notifications = [
                n for n in self.scheduled_notifications 
                if n.get("id") != notification_id
            ]
            if self.storage:
                self.storage.set("scheduled_notifications", self.scheduled_notifications)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel notification: {e}")
            return False
    
    def get_scheduled_notifications(self) -> List[Dict[str, Any]]:
        """Get list of scheduled notifications"""
        return self.scheduled_notifications.copy()
    
    def test_notification(self) -> bool:
        """Send a test notification"""
        try:
            self._send_notification(
                title="PrayerOffline Test",
                message="Notifications are working correctly!",
                sound_file="notification"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Test notification failed: {e}")
            return False
    
    def check_permissions(self) -> bool:
        """Check if notification permissions are granted"""
        # On desktop platforms, notifications are usually available
        # On mobile, this would check actual permissions
        return NOTIFICATION_AVAILABLE
    
    def update_notification_permissions(self) -> bool:
        """Request notification permissions (mainly for mobile)"""
        # This is platform-specific
        # For now, just return current availability
        return self.check_permissions()
    
    def enable_notification(self, notification_id: str) -> bool:
        """Enable a specific notification"""
        try:
            for notif in self.scheduled_notifications:
                if notif.get("id") == notification_id:
                    notif["enabled"] = True
                    if self.storage:
                        self.storage.set("scheduled_notifications", self.scheduled_notifications)
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to enable notification: {e}")
            return False
    
    def disable_notification(self, notification_id: str) -> bool:
        """Disable a specific notification"""
        try:
            for notif in self.scheduled_notifications:
                if notif.get("id") == notification_id:
                    notif["enabled"] = False
                    if self.storage:
                        self.storage.set("scheduled_notifications", self.scheduled_notifications)
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to disable notification: {e}")
            return False
    
    def cleanup(self):
        """Cleanup notification service"""
        try:
            # Stop the background thread
            self._stop_event.set()
            
            if self._notification_thread and self._notification_thread.is_alive():
                self._notification_thread.join(timeout=2.0)
            
            self.logger.info("Notification service cleaned up")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup notification service: {e}")
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        try:
            total = len(self.scheduled_notifications)
            enabled = sum(1 for n in self.scheduled_notifications if n.get("enabled", True))
            sent_today = sum(1 for n in self.scheduled_notifications if n.get("sent_today", False))
            
            return {
                "total_scheduled": total,
                "enabled": enabled,
                "disabled": total - enabled,
                "sent_today": sent_today,
                "pending_today": enabled - sent_today,
                "available": NOTIFICATION_AVAILABLE
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get notification stats: {e}")
            return {}
    
    def reschedule_notification(self, notification_id: str, new_time: str) -> bool:
        """Reschedule a notification to a new time"""
        try:
            for notif in self.scheduled_notifications:
                if notif.get("id") == notification_id:
                    notif["time"] = new_time
                    notif["sent_today"] = False  # Reset sent flag
                    
                    # Update ID to reflect new time
                    prayer = notif.get("prayer")
                    notif_type = notif.get("type")
                    notif["id"] = f"{prayer}_{notif_type}_{new_time}"
                    
                    if self.storage:
                        self.storage.set("scheduled_notifications", self.scheduled_notifications)
                    
                    self.logger.info(f"Rescheduled notification {notification_id} to {new_time}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to reschedule notification: {e}")
            return False