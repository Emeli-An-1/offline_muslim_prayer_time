"""
Glassmorphic Dashboard View for PrayerOffline
Modern UI with blur effects, gradients, and transparency
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


class GlassmorphicDashboard(BaseView):
    """Glassmorphic dashboard with modern UI"""
    
    def __init__(self, page: ft.Page, storage, **kwargs):
        super().__init__(page, storage, **kwargs)
        
        self.notifier = kwargs.get('notifier')
        if not self.location_service:
            self.location_service = kwargs.get('location_service')
        
        self.prayer_calculator = PrayerTimesCalculator()
        
        self.current_prayer_times = None
        self.current_location = None
        self.show_jamaat_times = self.settings.get("show_jamaat_times", True)
        self.last_update = None
        
        self._initialize_data()
    
    def _initialize_data(self):
        """Initialize prayer times data"""
        try:
            if self.location_service:
                self.current_location = self.location_service.get_current_location()
            
            if not self.current_location:
                self.current_location = self.settings.get("location")
            
            if self.current_location:
                self._refresh_prayer_times()
            
            self.logger.info("Dashboard data initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard data: {e}")
    
    def _get_gradient_colors(self) -> tuple:
        """Get gradient colors based on theme"""
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        
        if is_dark:
            return (
                ft.colors.with_opacity(0.3, "#0f2027"),
                ft.colors.with_opacity(0.4, "#203a43"),
                ft.colors.with_opacity(0.3, "#2c5364")
            )
        else:
            return (
                ft.colors.with_opacity(0.4, "#a7c5bd"),
                ft.colors.with_opacity(0.5, "#c9dfd8"),
                ft.colors.with_opacity(0.4, "#e9d8a6")
            )
    
    def _create_glass_container(self, content, padding=20, border_radius=30):
        """Create a glassmorphic container"""
        return ft.Container(
            content=content,
            padding=padding,
            border_radius=border_radius,
            bgcolor=ft.colors.with_opacity(0.15, ft.colors.WHITE),
            border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.WHITE)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                offset=ft.Offset(0, 10)
            )
        )
    
    def build(self) -> ft.Control:
        """Build glassmorphic dashboard"""
        try:
            if not self.current_location:
                return self._build_no_location_view()
            
            gradient_colors = self._get_gradient_colors()
            
            return ft.Container(
                content=ft.Stack(
                    controls=[
                        # Gradient background
                        ft.Container(
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_left,
                                end=ft.alignment.bottom_right,
                                colors=list(gradient_colors)
                            ),
                            expand=True
                        ),
                        
                        # Main content
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    self._build_glass_header(),
                                    ft.Container(height=20),
                                    self._build_glass_countdown(),
                                    ft.Container(height=20),
                                    self._build_glass_prayer_cards(),
                                    ft.Container(height=20),
                                    self._build_glass_qibla_button(),
                                ],
                                scroll=ft.ScrollMode.AUTO,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=20,
                            expand=True
                        )
                    ]
                ),
                expand=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to build dashboard: {e}")
            return self._build_error_view(str(e))
    
    def _build_glass_header(self) -> ft.Control:
        """Build glassmorphic header"""
        today = datetime.now()
        
        hijri_text = ""
        if Gregorian:
            try:
                hijri_date = Gregorian(today.year, today.month, today.day).to_hijri()
                hijri_text = f"{hijri_date.day} {hijri_date.month_name()} {hijri_date.year} AH"
            except Exception:
                pass
        
        location_text = "Unknown Location"
        if self.current_location:
            city = self.current_location.get("city", "Unknown")
            country = self.current_location.get("country", "")
            location_text = f"{city}, {country}" if country else city
        
        return self._create_glass_container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.LOCATION_ON, size=20, color=ft.colors.WHITE),
                            ft.Text(
                                location_text,
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color=ft.colors.WHITE
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Text(
                        today.strftime("%A, %B %d, %Y"),
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        hijri_text,
                        size=14,
                        color=ft.colors.with_opacity(0.8, ft.colors.WHITE),
                        text_align=ft.TextAlign.CENTER
                    ) if hijri_text else ft.Container()
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            padding=20,
            border_radius=25
        )
    
    def _build_glass_countdown(self) -> ft.Control:
        """Build glassmorphic countdown section"""
        if not self.current_prayer_times:
            return ft.Container()
        
        next_prayer_info = self._get_next_prayer()
        
        if not next_prayer_info:
            return ft.Container()
        
        next_prayer, next_time, time_mode = next_prayer_info
        
        now = datetime.now()
        time_diff = next_time - now
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        seconds = int(time_diff.total_seconds() % 60)
        
        return self._create_glass_container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"Next: {next_prayer}",
                        size=18,
                        weight=ft.FontWeight.W_600,
                        color=ft.colors.WHITE,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                        size=48,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.icons.ACCESS_TIME, size=16, color=ft.colors.with_opacity(0.8, ft.colors.WHITE)),
                                ft.Text(
                                    "Time remaining",
                                    size=14,
                                    color=ft.colors.with_opacity(0.8, ft.colors.WHITE)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            padding=30,
            border_radius=30
        )
    
    def _build_glass_prayer_cards(self) -> ft.Control:
        """Build glassmorphic prayer cards"""
        if not self.current_prayer_times:
            return ft.Container()
        
        prayers = self.current_prayer_times.get("prayers", {})
        next_prayer_info = self._get_next_prayer()
        next_prayer_name = next_prayer_info[0] if next_prayer_info else None
        
        prayer_cards = []
        
        for prayer_name in PRAYER_NAMES:
            if prayer_name == "Sunrise":
                continue
            
            if prayer_name in prayers:
                prayer_data = prayers[prayer_name]
                is_next = prayer_name == next_prayer_name
                
                card = self._create_prayer_glass_card(prayer_name, prayer_data, is_next)
                prayer_cards.append(card)
        
        return ft.Column(
            controls=prayer_cards,
            spacing=12
        )
    
    def _create_prayer_glass_card(self, prayer_name: str, prayer_data: Dict, is_next: bool) -> ft.Control:
        """Create individual prayer glass card"""
        adhan_time = prayer_data.get("adhan", "N/A")
        jamaat_time = prayer_data.get("jamaat", "")
        
        # Highlight next prayer
        bg_opacity = 0.25 if is_next else 0.15
        border_opacity = 0.4 if is_next else 0.2
        glow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=20,
            color=ft.colors.with_opacity(0.3, ft.colors.PRIMARY)
        ) if is_next else None
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Prayer icon and name
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    self._get_prayer_icon(prayer_name),
                                    size=24,
                                    color=ft.colors.WHITE
                                ),
                                width=40,
                                height=40,
                                border_radius=20,
                                bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                                alignment=ft.alignment.center
                            ),
                            ft.Text(
                                prayer_name,
                                size=18,
                                weight=ft.FontWeight.BOLD if is_next else ft.FontWeight.W_500,
                                color=ft.colors.WHITE
                            )
                        ],
                        spacing=12,
                        expand=True
                    ),
                    
                    # Times
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("Adhan", size=10, color=ft.colors.with_opacity(0.7, ft.colors.WHITE)),
                                    ft.Text(adhan_time, size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Jamaat", size=10, color=ft.colors.with_opacity(0.7, ft.colors.WHITE)),
                                        ft.Text(jamaat_time if jamaat_time else "-", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2
                                ),
                                visible=self.show_jamaat_times
                            )
                        ],
                        spacing=20
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=20,
            border_radius=20,
            bgcolor=ft.colors.with_opacity(bg_opacity, ft.colors.WHITE),
            border=ft.border.all(1, ft.colors.with_opacity(border_opacity, ft.colors.WHITE)),
            shadow=glow if is_next else ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.colors.with_opacity(0.05, ft.colors.BLACK)
            )
        )
    
    def _get_prayer_icon(self, prayer_name: str) -> str:
        """Get icon for prayer"""
        icons = {
            "Fajr": ft.icons.BRIGHTNESS_5_OUTLINED,
            "Dhuhr": ft.icons.WB_SUNNY_OUTLINED,
            "Asr": ft.icons.WB_TWILIGHT,
            "Maghrib": ft.icons.BRIGHTNESS_3,
            "Isha": ft.icons.NIGHTS_STAY
        }
        return icons.get(prayer_name, ft.icons.ACCESS_TIME)
    
    def _build_glass_qibla_button(self) -> ft.Control:
        """Build glassmorphic Qibla direction button"""
        return ft.Container(
            content=ft.IconButton(
                icon=ft.icons.EXPLORE,
                icon_size=32,
                icon_color=ft.colors.WHITE,
                tooltip="Qibla Direction",
                on_click=lambda _: self.navigate_to("qibla")
            ),
            width=70,
            height=70,
            border_radius=35,
            bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
            border=ft.border.all(1, ft.colors.with_opacity(0.3, ft.colors.WHITE)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=ft.colors.with_opacity(0.2, ft.colors.PRIMARY)
            ),
            alignment=ft.alignment.center
        )
    
    def _build_no_location_view(self) -> ft.Control:
        """Glassmorphic no location view"""
        gradient_colors = self._get_gradient_colors()
        
        return ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Container(
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=list(gradient_colors)
                        ),
                        expand=True
                    ),
                    ft.Container(
                        content=self._create_glass_container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.icons.LOCATION_OFF, size=64, color=ft.colors.WHITE),
                                    ft.Text("Location Not Set", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                    ft.Text("Please set your location to view prayer times", size=14, color=ft.colors.with_opacity(0.8, ft.colors.WHITE), text_align=ft.TextAlign.CENTER),
                                    ft.Container(height=10),
                                    ft.ElevatedButton(
                                        "Open Settings",
                                        icon=ft.icons.SETTINGS,
                                        on_click=lambda _: self.navigate_to("settings"),
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                                            color=ft.colors.WHITE
                                        )
                                    )
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=15
                            ),
                            padding=40
                        ),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                ]
            ),
            expand=True
        )
    
    def _build_error_view(self, error_msg: str) -> ft.Control:
        """Glass error view"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=64, color=ft.colors.ERROR),
                    ft.Text("Error", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(error_msg, size=14)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            alignment=ft.alignment.center,
            expand=True
        )
    
    # Keep all helper methods from original dashboard
    def _get_next_prayer(self) -> Optional[Tuple[str, datetime, str]]:
        """Get next prayer - same as original"""
        try:
            if not self.current_prayer_times:
                return None
            
            prayers = self.current_prayer_times.get("prayers", {})
            now = datetime.now()
            current_date = now.date()
            
            for prayer_name in PRAYER_NAMES:
                if prayer_name == "Sunrise":
                    continue
                
                if prayer_name in prayers:
                    prayer_data = prayers[prayer_name]
                    
                    if self.show_jamaat_times and prayer_data.get("jamaat"):
                        jamaat_time_str = prayer_data["jamaat"]
                        try:
                            jamaat_time = datetime.strptime(jamaat_time_str, "%H:%M").time()
                            jamaat_datetime = datetime.combine(current_date, jamaat_time)
                            if jamaat_datetime > now:
                                return prayer_name, jamaat_datetime, "jamaat"
                        except Exception:
                            pass
                    
                    adhan_time_str = prayer_data.get("adhan")
                    if adhan_time_str:
                        try:
                            adhan_time = datetime.strptime(adhan_time_str, "%H:%M").time()
                            adhan_datetime = datetime.combine(current_date, adhan_time)
                            if adhan_datetime > now:
                                return prayer_name, adhan_datetime, "adhan"
                        except Exception:
                            pass
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to get next prayer: {e}")
            return None
    
    def _refresh_prayer_times(self):
        """Refresh prayer times - same as original"""
        try:
            if not self.current_location:
                return
            
            today = date.today()
            calc_settings = self.settings.get("calculation", {})
            method = calc_settings.get("method", "ISNA")
            asr_method = calc_settings.get("asr_method", "Standard")
            high_lat_rule = calc_settings.get("high_lat_rule", "None")
            
            prayer_times = self.prayer_calculator.calculate_prayer_times(
                latitude=self.current_location.get("latitude", self.current_location.get("lat")),
                longitude=self.current_location.get("longitude", self.current_location.get("lng")),
                calculation_date=today,
                timezone_name=self.current_location.get("timezone", "UTC"),
                method=method,
                asr_method=asr_method,
                high_lat_rule=high_lat_rule
            )
            
            jamaat_config = self.settings.get("jamaat_config", {})
            self.current_prayer_times = self.prayer_calculator.apply_jamaat_adjustments(
                prayer_times, jamaat_config
            )
            
            self.last_update = datetime.now()
            self.logger.info("Prayer times refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh prayer times: {e}")