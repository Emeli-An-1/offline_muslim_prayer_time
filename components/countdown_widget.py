"""
Countdown Widget for PrayerOffline
Real-time countdown display for next prayer time
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import flet as ft


class CountdownWidget(ft.Container):
    """Widget for displaying countdown to next prayer"""
    
    def __init__(self, prayer_name: str, target_time: datetime, 
                 time_mode: str = "adhan", previous_prayer_time: Optional[datetime] = None):
        self.prayer_name = prayer_name
        self.target_time = target_time
        self.time_mode = time_mode
        self.previous_prayer_time = previous_prayer_time
        self.logger = logging.getLogger(__name__)
        
        # UI Components
        self.prayer_title = None
        self.hours_text = None
        self.minutes_text = None
        self.seconds_text = None
        self.progress_ring = None
        self.time_remaining_text = None
        self.percentage_text = None
        
        super().__init__(
            content=self._build_content(),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            border_radius=16,
            padding=24
        )
    
    def _build_content(self) -> ft.Control:
        """Build the countdown widget content"""
        try:
            # Get prayer icon
            prayer_icon = self._get_prayer_icon(self.prayer_name)
            
            # Prayer title with icon
            self.prayer_title = ft.Row([
                ft.Icon(prayer_icon, size=32, color=ft.Colors.PRIMARY),
                ft.Column([
                    ft.Text(
                        f"Next: {self.prayer_name.title()}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_PRIMARY_CONTAINER
                    ),
                    ft.Text(
                        f"{self.time_mode.title()} at {self.target_time.strftime('%H:%M')}",
                        size=14,
                        color=ft.Colors.ON_PRIMARY_CONTAINER
                    )
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.CENTER)
            
            # Countdown display
            countdown_display = self._build_countdown_display()
            
            # Progress indicator
            progress_bar = self._build_progress_indicator()
            
            return ft.Column([
                self.prayer_title,
                ft.SizedBox(height=16),
                countdown_display,
                ft.SizedBox(height=16),
                progress_bar
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
        except Exception as e:
            self.logger.error(f"Failed to build countdown content: {e}")
            return ft.Text("Error loading countdown")
    
    def _get_prayer_icon(self, prayer_name: str) -> str:
        """Get icon for prayer"""
        icons = {
            "Fajr": ft.Icons.WB_TWILIGHT,
            "Sunrise": ft.Icons.WB_SUNNY,
            "Dhuhr": ft.Icons.LIGHT_MODE,
            "Asr": ft.Icons.BRIGHTNESS_6,
            "Maghrib": ft.Icons.BRIGHTNESS_4,
            "Isha": ft.Icons.BRIGHTNESS_2
        }
        return icons.get(prayer_name, ft.Icons.ACCESS_TIME)
    
    def _build_countdown_display(self) -> ft.Control:
        """Build the main countdown display"""
        try:
            # Calculate initial time remaining
            hours, minutes, seconds = self._calculate_time_remaining()
            
            # Create time display containers
            hours_container = ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"{hours:02d}",
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_PRIMARY_CONTAINER,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Hours",
                        size=12,
                        color=ft.Colors.ON_PRIMARY_CONTAINER,
                        text_align=ft.TextAlign.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.SURFACE_VARIANT,
                border_radius=8,
                padding=12,
                width=80
            )
            
            minutes_container = ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"{minutes:02d}",
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_PRIMARY_CONTAINER,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Minutes",
                        size=12,
                        color=ft.Colors.ON_PRIMARY_CONTAINER,
                        text_align=ft.TextAlign.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.SURFACE_VARIANT,
                border_radius=8,
                padding=12,
                width=80
            )
            
            seconds_container = ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"{seconds:02d}",
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_PRIMARY_CONTAINER,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Seconds",
                        size=12,
                        color=ft.Colors.ON_PRIMARY_CONTAINER,
                        text_align=ft.TextAlign.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=ft.Colors.SURFACE_VARIANT,
                border_radius=8,
                padding=12,
                width=80
            )
            
            # Store references for updates
            self.hours_text = hours_container.content.controls[0]
            self.minutes_text = minutes_container.content.controls[0]
            self.seconds_text = seconds_container.content.controls[0]
            
            return ft.Row([
                hours_container,
                ft.Text(":", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY_CONTAINER),
                minutes_container,
                ft.Text(":", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY_CONTAINER),
                seconds_container
            ], alignment=ft.MainAxisAlignment.CENTER)
            
        except Exception as e:
            self.logger.error(f"Failed to build countdown display: {e}")
            return ft.Text("00:00:00", size=32)
    
    def _build_progress_indicator(self) -> ft.Control:
        """Build circular progress indicator"""
        try:
            # Calculate progress (0.0 to 1.0)
            progress = self._calculate_progress()
            
            self.progress_ring = ft.ProgressRing(
                value=progress,
                stroke_width=8,
                color=ft.Colors.PRIMARY,
                bgcolor=ft.Colors.OUTLINE_VARIANT
            )
            
            # Percentage text
            self.percentage_text = ft.Text(
                f"{int(progress * 100)}%",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.ON_PRIMARY_CONTAINER
            )
            
            # Time remaining text
            hours, minutes, _ = self._calculate_time_remaining()
            total_minutes = hours * 60 + minutes
            
            self.time_remaining_text = ft.Text(
                f"{total_minutes} min remaining",
                size=12,
                color=ft.Colors.ON_PRIMARY_CONTAINER,
                text_align=ft.TextAlign.CENTER
            )
            
            return ft.Column([
                ft.Stack([
                    self.progress_ring,
                    ft.Container(
                        content=self.percentage_text,
                        alignment=ft.alignment.center,
                        width=60,
                        height=60
                    )
                ], width=60, height=60),
                ft.SizedBox(height=8),
                self.time_remaining_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
        except Exception as e:
            self.logger.error(f"Failed to build progress indicator: {e}")
            return ft.Container()
    
    def _calculate_time_remaining(self) -> tuple:
        """Calculate time remaining until target time"""
        try:
            now = datetime.now()
            
            # If target time has passed, it's for tomorrow
            target = self.target_time
            if target <= now:
                target += timedelta(days=1)
            
            time_diff = target - now
            
            hours = int(time_diff.total_seconds() // 3600)
            minutes = int((time_diff.total_seconds() % 3600) // 60)
            seconds = int(time_diff.total_seconds() % 60)
            
            return hours, minutes, seconds
            
        except Exception as e:
            self.logger.error(f"Failed to calculate time remaining: {e}")
            return 0, 0, 0
    
    def _calculate_progress(self) -> float:
        """Calculate progress from previous prayer to next prayer (0.0 to 1.0)"""
        try:
            now = datetime.now()
            
            # If target has passed, adjust for tomorrow
            target = self.target_time
            if target <= now:
                target += timedelta(days=1)
            
            # Determine previous prayer time
            if self.previous_prayer_time:
                # Use provided previous prayer time
                last_prayer = self.previous_prayer_time
                
                # If previous prayer is in the future (edge case), use 24h before
                if last_prayer >= now:
                    last_prayer = now - timedelta(hours=6)
            else:
                # Fallback: estimate based on average Islamic prayer intervals
                # Average interval between prayers is roughly 3-6 hours
                last_prayer = target - timedelta(hours=5)
            
            # Calculate progress
            total_seconds = (target - last_prayer).total_seconds()
            elapsed_seconds = (now - last_prayer).total_seconds()
            
            if total_seconds <= 0:
                return 0.0
            
            progress = elapsed_seconds / total_seconds
            
            # Ensure progress is between 0.0 and 1.0
            return max(0.0, min(1.0, progress))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate progress: {e}")
            return 0.0
    
    def update_countdown(self):
        """Update countdown display with current time"""
        try:
            # Calculate time remaining
            hours, minutes, seconds = self._calculate_time_remaining()
            
            # Update countdown display
            if self.hours_text:
                self.hours_text.value = f"{hours:02d}"
            if self.minutes_text:
                self.minutes_text.value = f"{minutes:02d}"
            if self.seconds_text:
                self.seconds_text.value = f"{seconds:02d}"
            
            # Update progress indicator
            if self.progress_ring:
                progress = self._calculate_progress()
                self.progress_ring.value = progress
                
                if self.percentage_text:
                    self.percentage_text.value = f"{int(progress * 100)}%"
            
            # Update remaining time text
            if self.time_remaining_text:
                total_minutes = hours * 60 + minutes
                self.time_remaining_text.value = f"{total_minutes} min remaining"
            
            # Add pulsing effect when close to prayer time
            if hours == 0 and minutes < 5:
                self.bgcolor = ft.Colors.ORANGE_CONTAINER if seconds % 2 else ft.Colors.PRIMARY_CONTAINER
            else:
                self.bgcolor = ft.Colors.PRIMARY_CONTAINER
            
            # Call parent update to refresh the UI
            super().update()
            
        except Exception as e:
            self.logger.error(f"Failed to update countdown: {e}")
    
    def update_target(self, prayer_name: str, target_time: datetime, 
                     time_mode: str = "adhan", previous_prayer_time: Optional[datetime] = None):
        """Update countdown target with new prayer information"""
        try:
            self.prayer_name = prayer_name
            self.target_time = target_time
            self.time_mode = time_mode
            self.previous_prayer_time = previous_prayer_time
            
            # Update prayer title
            if self.prayer_title and len(self.prayer_title.controls) > 1:
                prayer_icon = self._get_prayer_icon(prayer_name)
                self.prayer_title.controls[0].name = prayer_icon
                
                title_column = self.prayer_title.controls[1]
                if hasattr(title_column, 'controls'):
                    if len(title_column.controls) > 0:
                        title_column.controls[0].value = f"Next: {prayer_name.title()}"
                    if len(title_column.controls) > 1:
                        title_column.controls[1].value = f"{time_mode.title()} at {target_time.strftime('%H:%M')}"
            
            # Force update
            self.update_countdown()
            
        except Exception as e:
            self.logger.error(f"Failed to update countdown target: {e}")
    
    def update_time_mode(self, time_mode: str):
        """Update time mode (adhan/jamaat) without changing target"""
        try:
            self.time_mode = time_mode
            
            # Update subtitle
            if self.prayer_title and len(self.prayer_title.controls) > 1:
                title_column = self.prayer_title.controls[1]
                if hasattr(title_column, 'controls') and len(title_column.controls) > 1:
                    title_column.controls[1].value = f"{time_mode.title()} at {self.target_time.strftime('%H:%M')}"
                    super().update()
            
        except Exception as e:
            self.logger.error(f"Failed to update time mode: {e}")