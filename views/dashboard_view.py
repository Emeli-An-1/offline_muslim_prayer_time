"""
Dashboard View for PrayerOffline
Displays prayer times, countdown, and current status
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, Tuple
import flet as ft

try:
    from hijri_converter import Gregorian
except ImportError:
    Gregorian = None

from views.base_view import BaseView
from utils.constants import PRAYER_NAMES, JamaatMode
from services.praytimes import PrayerTimesCalculator


class DashboardView(BaseView):
    """Dashboard view for displaying prayer times and status"""
    
    def __init__(self, page: ft.Page, storage, **kwargs):
        """
        Initialize dashboard view
        
        Args:
            page: Flet page instance
            storage: Storage service
            **kwargs: Additional services (notifier, location_service, etc.)
        """
        super().__init__(page, storage, **kwargs)
        
        # Extract services from kwargs
        self.notifier = kwargs.get('notifier')
        if not self.location_service:
            self.location_service = kwargs.get('location_service')
        
        # Initialize prayer calculator
        self.prayer_calculator = PrayerTimesCalculator()
        
        # Data
        self.current_prayer_times = None
        self.current_location = None
        
        # UI Components (will be created in build())
        self.date_display = None
        self.location_display = None
        self.countdown_container = None
        self.prayer_cards_column = None
        self.jamaat_toggle = None
        self.refresh_button = None
        
        # State
        self.show_jamaat_times = self.settings.get("show_jamaat_times", True)
        self.last_update = None
        
        # Initialize data
        self._initialize_data()
    
    def _initialize_data(self):
        """Initialize prayer times data"""
        try:
            # Get current location
            if self.location_service:
                self.current_location = self.location_service.get_current_location()
            
            if not self.current_location:
                # Try to load from settings
                self.current_location = self.settings.get("location")
            
            # Load today's prayer times
            if self.current_location:
                self._refresh_prayer_times()
            
            self.logger.info("Dashboard data initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard data: {e}")
    
    def build(self) -> ft.Control:
        """Build the dashboard view UI"""
        try:
            # Check if location is set
            if not self.current_location:
                return self._build_no_location_view()
            
            # Build main content
            return ft.Container(
                content=ft.Column(
                    controls=[
                        self._build_header(),
                        ft.Divider(height=1),
                        self._build_countdown_section(),
                        ft.Divider(height=1),
                        self._build_prayer_times_section(),
                        ft.Divider(height=1),
                        self._build_quick_actions(),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                expand=True,
            )
            
        except Exception as e:
            self.logger.error(f"Failed to build dashboard view: {e}")
            return self._build_error_view(str(e))
    
    def _build_no_location_view(self) -> ft.Control:
        """Build view when no location is set"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.LOCATION_OFF, size=64, color=ft.Colors.OUTLINE),
                    ft.Text(
                        "Location Not Set",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Please set your location in Settings to view prayer times",
                        size=14,
                        color=ft.colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.ElevatedButton(
                        "Open Settings",
                        icon=ft.Icons.SETTINGS,
                        on_click=lambda _: self.navigate_to("settings")
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def _build_error_view(self, error_msg: str) -> ft.Control:
        """Build error view"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.colors.ERROR),
                    ft.Text("Failed to Load Dashboard", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(error_msg, size=14, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.ElevatedButton("Retry", on_click=lambda _: self._on_retry()),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def _build_header(self) -> ft.Control:
        """Build the header section with date and location"""
        # Current date
        today = datetime.now()
        
        # Hijri date
        hijri_text = ""
        if Gregorian:
            try:
                hijri_date = Gregorian(today.year, today.month, today.day).to_hijri()
                hijri_text = f"{hijri_date.day} {hijri_date.month_name()} {hijri_date.year} AH"
            except Exception:
                hijri_text = "Hijri date unavailable"
        
        self.date_display = ft.Column(
            controls=[
                ft.Text(
                    today.strftime("%A, %B %d, %Y"),
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    hijri_text,
                    size=14,
                        color=ft.colors.OUTLINE,
                    text_align=ft.TextAlign.CENTER
                ) if hijri_text else ft.Container(),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )
        
        # Location display
        location_text = "Unknown Location"
        if self.current_location:
            city = self.current_location.get("city", "Unknown")
            country = self.current_location.get("country", "")
            location_text = f"{city}, {country}" if country else city
        
        self.location_display = ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOCATION_ON, size=16),
                ft.Text(location_text, size=14),
                ft.IconButton(
                    icon=ft.Icons.EDIT_LOCATION,
                    icon_size=16,
                    tooltip="Change location",
                    on_click=lambda _: self.navigate_to("settings")
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[self.date_display, self.location_display],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.padding.only(bottom=16),
        )
    
    def _build_countdown_section(self) -> ft.Control:
        """Build the countdown section"""
        if not self.current_prayer_times:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ACCESS_TIME, size=48, color=ft.Colors.OUTLINE),
                        ft.Text("Prayer times not available", text_align=ft.TextAlign.CENTER),
                        ft.ElevatedButton("Refresh", on_click=lambda _: self._on_refresh()),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                padding=20,
                alignment=ft.alignment.center,
            )
        
        # Get next prayer
        next_prayer_info = self._get_next_prayer()
        
        if not next_prayer_info:
            next_prayer_text = "No upcoming prayers today"
            time_remaining_text = ""
        else:
            next_prayer, next_time, time_mode = next_prayer_info
            next_prayer_text = f"Next: {next_prayer}"
            
            # Calculate time remaining
            now = datetime.now()
            time_diff = next_time - now
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            seconds = int(time_diff.total_seconds() % 60)
            
            time_remaining_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Jamaat toggle
        self.jamaat_toggle = ft.Switch(
            label="Show Jamaat Times",
            value=self.show_jamaat_times,
            on_change=self._on_jamaat_toggle_change,
        )
        
        self.countdown_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        next_prayer_text,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        time_remaining_text,
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ) if time_remaining_text else ft.Container(),
                    ft.Container(height=8),
                    self.jamaat_toggle,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
                bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=12,
            padding=20,
            margin=ft.margin.symmetric(vertical=12),
        )
        
        return self.countdown_container
    
    def _build_prayer_times_section(self) -> ft.Control:
        """Build the prayer times section"""
        if not self.current_prayer_times:
            return ft.Container()
        
        prayers = self.current_prayer_times.get("prayers", {})
        
        # Create prayer time cards
        prayer_cards = []
        for prayer_name in PRAYER_NAMES:
            if prayer_name == "Sunrise":
                continue  # Skip sunrise in main list
            
            if prayer_name in prayers:
                prayer_data = prayers[prayer_name]
                card = self._create_prayer_card(prayer_name, prayer_data)
                prayer_cards.append(card)
        
        self.prayer_cards_column = ft.Column(
            controls=[
                ft.Text(
                    self.get_string("prayers.today_schedule", "Today's Prayer Times"),
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=8),
                *prayer_cards,
            ],
            spacing=8,
        )
        
        return self.prayer_cards_column
    
    def _create_prayer_card(self, prayer_name: str, prayer_data: Dict) -> ft.Control:
        """Create a prayer time card"""
        adhan_time = prayer_data.get("adhan", "N/A")
        jamaat_time = prayer_data.get("jamaat", "")
        
        # Determine if this is the current/next prayer
        is_active = False
        next_prayer_info = self._get_next_prayer()
        if next_prayer_info:
            next_prayer, _, _ = next_prayer_info
            is_active = prayer_name == next_prayer
        
        card_content = ft.Row(
            controls=[
                # Prayer name
                ft.Container(
                    content=ft.Text(
                        prayer_name,
                        size=16,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                    ),
                    expand=True,
                ),
                # Adhan time
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Adhan", size=10, color=ft.Colors.OUTLINE),
                            ft.Text(adhan_time, size=14, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=2,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=80,
                ),
                # Jamaat time (if enabled)
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Jamaat", size=10, color=ft.Colors.OUTLINE),
                            ft.Text(
                                jamaat_time if jamaat_time else "-",
                                size=14,
                                weight=ft.FontWeight.BOLD
                            ),
                        ],
                        spacing=2,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=80,
                    visible=self.show_jamaat_times,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        return ft.Container(
            content=card_content,
                bgcolor=ft.colors.PRIMARY_CONTAINER if is_active else ft.colors.SURFACE_VARIANT,
            border=ft.border.all(2, ft.colors.PRIMARY) if is_active else None,
            border_radius=8,
            padding=16,
        )
    
    def _build_quick_actions(self) -> ft.Control:
        """Build quick actions section"""
        self.refresh_button = ft.ElevatedButton(
            text=self.get_string("actions.refresh", "Refresh Times"),
            icon=ft.Icons.REFRESH,
            on_click=lambda _: self._on_refresh(),
        )
        
        test_notification_button = ft.ElevatedButton(
            text=self.get_string("actions.test_notification", "Test Notification"),
            icon=ft.Icons.NOTIFICATIONS,
            on_click=lambda _: self._on_test_notification(),
        )
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    self.refresh_button,
                    test_notification_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
            padding=ft.padding.symmetric(vertical=16),
        )
    
    # Helper Methods
    
    def _get_next_prayer(self) -> Optional[Tuple[str, datetime, str]]:
        """
        Get next prayer information
        
        Returns:
            Tuple of (prayer_name, prayer_time, time_mode) or None
        """
        try:
            if not self.current_prayer_times:
                return None
            
            prayers = self.current_prayer_times.get("prayers", {})
            now = datetime.now()
            current_date = now.date()
            
            # Find next prayer
            for prayer_name in PRAYER_NAMES:
                if prayer_name == "Sunrise":
                    continue  # Skip sunrise
                
                if prayer_name in prayers:
                    prayer_data = prayers[prayer_name]
                    
                    # Try jamaat time first if enabled
                    if self.show_jamaat_times and prayer_data.get("jamaat"):
                        jamaat_time_str = prayer_data["jamaat"]
                        try:
                            jamaat_time = datetime.strptime(jamaat_time_str, "%H:%M").time()
                            jamaat_datetime = datetime.combine(current_date, jamaat_time)
                            
                            if jamaat_datetime > now:
                                return prayer_name, jamaat_datetime, "jamaat"
                        except Exception:
                            pass
                    
                    # Try adhan time
                    adhan_time_str = prayer_data.get("adhan")
                    if adhan_time_str:
                        try:
                            adhan_time = datetime.strptime(adhan_time_str, "%H:%M").time()
                            adhan_datetime = datetime.combine(current_date, adhan_time)
                            
                            if adhan_datetime > now:
                                return prayer_name, adhan_datetime, "adhan"
                        except Exception:
                            pass
            
            # If no prayer found for today, get first prayer of tomorrow
            tomorrow = current_date + timedelta(days=1)
            first_prayer = "Fajr"
            if first_prayer in prayers:
                prayer_data = prayers[first_prayer]
                adhan_time_str = prayer_data.get("adhan")
                if adhan_time_str:
                    try:
                        adhan_time = datetime.strptime(adhan_time_str, "%H:%M").time()
                        adhan_datetime = datetime.combine(tomorrow, adhan_time)
                        return first_prayer, adhan_datetime, "adhan"
                    except Exception:
                        pass
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get next prayer: {e}")
            return None
    
    def _refresh_prayer_times(self):
        """Refresh prayer times for current location and date"""
        try:
            if not self.current_location:
                self.logger.warning("No location available for prayer time calculation")
                return
            
            today = date.today()
            
            # Get calculation settings
            calc_settings = self.settings.get("calculation", {})
            method = calc_settings.get("method", "ISNA")
            asr_method = calc_settings.get("asr_method", "Standard")
            high_lat_rule = calc_settings.get("high_lat_rule", "None")
            
            # Calculate prayer times
            prayer_times = self.prayer_calculator.calculate_prayer_times(
                latitude=self.current_location.get("latitude", self.current_location.get("lat")),
                longitude=self.current_location.get("longitude", self.current_location.get("lng")),
                calculation_date=today,
                timezone_name=self.current_location.get("timezone", "UTC"),
                method=method,
                asr_method=asr_method,
                high_lat_rule=high_lat_rule
            )
            
            # Apply jamaat adjustments
            jamaat_config = self.settings.get("jamaat_config", {})
            self.current_prayer_times = self.prayer_calculator.apply_jamaat_adjustments(
                prayer_times, jamaat_config
            )
            
            # Cache prayer times
            location_hash = f"{self.current_location['latitude']},{self.current_location['longitude']}"
            self.storage.cache_prayer_times(
                today.isoformat(), location_hash, self.current_prayer_times
            )
            
            self.last_update = datetime.now()
            self.logger.info("Prayer times refreshed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh prayer times: {e}")
            
            # Try to load from cache
            try:
                today = date.today()
                location_hash = f"{self.current_location['latitude']},{self.current_location['longitude']}"
                cached_times = self.storage.get_cached_prayer_times(
                    today.isoformat(), location_hash
                )
                
                if cached_times:
                    self.current_prayer_times = cached_times
                    self.logger.info("Loaded prayer times from cache")
                    
            except Exception as cache_error:
                self.logger.error(f"Failed to load cached prayer times: {cache_error}")
    
    # Event Handlers
    
    def _on_jamaat_toggle_change(self, e):
        """Handle jamaat toggle change"""
        try:
            self.show_jamaat_times = e.control.value
            # Save to settings
            self.storage.update_setting("show_jamaat_times", self.show_jamaat_times)
            # Rebuild only the prayer cards section
            if self.prayer_cards_column:
                prayers = self.current_prayer_times.get("prayers", {})
                prayer_cards = []
                for prayer_name in PRAYER_NAMES:
                    if prayer_name == "Sunrise":
                        continue
                    if prayer_name in prayers:
                        prayer_data = prayers[prayer_name]
                        card = self._create_prayer_card(prayer_name, prayer_data)
                        prayer_cards.append(card)
                # Update controls
                self.prayer_cards_column.controls = [
                    ft.Text("Today's Prayer Times", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=8),
                    *prayer_cards,
                ]
            self.page.update()
            self.show_info("Display mode updated")
        except Exception as e:
            self.logger.error(f"Failed to handle jamaat toggle: {e}")
            self.show_error("Failed to update display mode")

    def _on_refresh(self):
        """Handle refresh button click"""
        try:
            # Disable button during refresh
            if self.refresh_button:
                self.refresh_button.disabled = True
                self.refresh_button.text = "Refreshing..."
                self.page.update()
            # Refresh data
            self._refresh_prayer_times()
            # Rebuild countdown and prayer times sections
            if self.countdown_container and self.current_prayer_times:
                # Update countdown
                new_countdown = self._build_countdown_section()
                # Update prayer cards
                prayers = self.current_prayer_times.get("prayers", {})
                prayer_cards = []
                for prayer_name in PRAYER_NAMES:
                    if prayer_name == "Sunrise":
                        continue
                    if prayer_name in prayers:
                        prayer_data = prayers[prayer_name]
                        card = self._create_prayer_card(prayer_name, prayer_data)
                        prayer_cards.append(card)
                if self.prayer_cards_column:
                    self.prayer_cards_column.controls = [
                        ft.Text("Today's Prayer Times", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=8),
                        *prayer_cards,
                    ]
            self.page.update()
            self.show_success("Prayer times refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh: {e}")
            self.show_error("Failed to refresh prayer times")
        finally:
            # Re-enable button
            if self.refresh_button:
                self.refresh_button.disabled = False
                self.refresh_button.text = "Refresh Times"
                self.page.update()
    
    def _on_retry(self):
        """Handle retry button click"""
        try:
            self._initialize_data()
            self.page.clean()
            self.page.add(self.build())
            self.page.update()
        except Exception as e:
            self.logger.error(f"Retry failed: {e}")
            self.show_error("Retry failed")
    
    def _on_test_notification(self):
        """Handle test notification button click"""
        try:
            if self.notifier:
                success = self.notifier.test_notification()
                if success:
                    self.show_success("Test notification sent!")
                else:
                    self.show_warning("Notification sent, but may not be visible")
            else:
                self.show_warning("Notification service not available")
                
        except Exception as e:
            self.logger.error(f"Failed to send test notification: {e}")
            self.show_error("Failed to send notification")
    
    # Public Methods
    
    def update_countdown(self):
        """
        Update countdown display (should be called periodically)
        Can be called by app timer
        """
        try:
            if self.countdown_container:
                # Rebuild countdown section
                new_countdown = self._build_countdown_section()
                # Replace old countdown with new one
                # Note: Full implementation would need component reference tracking
                self.page.update()
                
        except Exception as e:
            self.logger.error(f"Failed to update countdown: {e}")
    
    def on_view_activated(self):
        """Called when view becomes active"""
        try:
            # Refresh if data is stale (> 1 hour)
            if (not self.last_update or 
                (datetime.now() - self.last_update).total_seconds() > 3600):
                self._refresh_prayer_times()
                
        except Exception as e:
            self.logger.error(f"Error in view activation: {e}")