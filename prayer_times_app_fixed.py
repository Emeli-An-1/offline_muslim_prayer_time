"""
Complete Prayer Times App - Flet Implementation (FIXED - Timer Issue Resolved)
Following Design Spec: Offline Muslim Prayer Time — Design System & UI/UX Specification
"""

import flet as ft
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import threading

# ============================================================================
# DESIGN SYSTEM - Section 3: Visual System
# ============================================================================

class DesignTokens:
    """Design tokens from specification Section 3"""
    
    # Light mode colors
    PRIMARY = "#0B6B63"
    PRIMARY_CONTAINER = "#E6F7F2"
    SECONDARY = "#D9BBA7"
    BACKGROUND = "#FCFEFF"
    SURFACE = "#FFFFFF"
    TEXT_PRIMARY = "#062524"
    TEXT_SECONDARY = "#6B7773"
    ERROR = "#C94A4A"
    ACCENT = "#F2C94C"
    DIVIDER = "#ECECEC"
    
    # Dark mode colors
    DARK_BACKGROUND = "#0A0F0E"
    DARK_SURFACE = "#0E1615"
    DARK_TEXT_PRIMARY = "#E6F7F2"
    DARK_TEXT_MUTED = "#9AA8A3"
    
    # Typography
    FONT_SIZE_H1 = 32
    FONT_WEIGHT_H1 = ft.FontWeight.BOLD
    FONT_SIZE_H2 = 22
    FONT_WEIGHT_H2 = ft.FontWeight.W_600
    FONT_SIZE_BODY = 16
    FONT_SIZE_CAPTION = 12
    
    # Spacing (4pt baseline grid)
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    SPACING_XXL = 32
    
    # Border radius
    RADIUS_SM = 12
    RADIUS_MD = 16
    RADIUS_LG = 20
    RADIUS_XL = 25
    RADIUS_XXL = 30
    
    @staticmethod
    def get_gradient(is_dark=False):
        """Get gradient colors based on theme"""
        if is_dark:
            return ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#0f2027", "#203a43", "#2c5364"]
            )
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#0B6B63", "#0FA88E"]
        )


# ============================================================================
# PRAYER DATA
# ============================================================================

class PrayerData:
    """Prayer times data structure"""
    
    PRAYERS = [
        {"name": "Fajr", "adhan": "05:30", "jamaat": "05:45", "icon": ft.Icons.BRIGHTNESS_5_OUTLINED},
        {"name": "Dhuhr", "adhan": "12:45", "jamaat": "13:00", "icon": ft.Icons.WB_SUNNY_OUTLINED},
        {"name": "Asr", "adhan": "15:30", "jamaat": "15:45", "icon": ft.Icons.WB_TWILIGHT},
        {"name": "Maghrib", "adhan": "18:15", "jamaat": "18:20", "icon": ft.Icons.BRIGHTNESS_3},
        {"name": "Isha", "adhan": "19:45", "jamaat": "20:00", "icon": ft.Icons.NIGHTS_STAY},
    ]
    
    @staticmethod
    def get_next_prayer() -> Optional[Dict]:
        """Find next prayer based on current time"""
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute
        
        for prayer in PrayerData.PRAYERS:
            h, m = map(int, prayer["adhan"].split(":"))
            prayer_minutes = h * 60 + m
            if prayer_minutes > current_minutes:
                return prayer
        
        return PrayerData.PRAYERS[0]
    
    @staticmethod
    def get_time_remaining(target_time: str) -> Dict[str, int]:
        """Calculate time remaining until target"""
        now = datetime.now()
        h, m = map(int, target_time.split(":"))
        target = datetime(now.year, now.month, now.day, h, m)
        
        if target < now:
            target += timedelta(days=1)
        
        diff = target - now
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        seconds = int(diff.total_seconds() % 60)
        
        return {"hours": hours, "minutes": minutes, "seconds": seconds}


# ============================================================================
# GLASSMORPHIC COMPONENTS
# ============================================================================

class GlassContainer(ft.Container):
    """Glassmorphic container with blur and transparency"""
    
    def __init__(
        self,
        content: ft.Control,
        padding: int = 20,
        border_radius: int = 30,
        **kwargs
    ):
        bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.WHITE)
        border = ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE))
        shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 10)
        )
        
        super().__init__(
            content=content,
            padding=padding,
            border_radius=border_radius,
            bgcolor=bgcolor,
            border=border,
            shadow=shadow,
            **kwargs
        )


# ============================================================================
# PRAYER CARD COMPONENT
# ============================================================================

class PrayerCard(ft.Container):
    """Individual prayer time card"""
    
    def __init__(self, prayer: Dict, is_next: bool, show_jamaat: bool):
        bg_opacity = 0.25 if is_next else 0.15
        border_opacity = 0.4 if is_next else 0.2
        
        icon_container = ft.Container(
            content=ft.Icon(
                prayer["icon"],
                size=24,
                color=ft.Colors.WHITE
            ),
            width=40,
            height=40,
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            alignment=ft.alignment.center
        )
        
        prayer_name = ft.Text(
            prayer["name"],
            size=18,
            weight=ft.FontWeight.BOLD if is_next else ft.FontWeight.W_500,
            color=ft.Colors.WHITE
        )
        
        adhan_display = ft.Column(
            controls=[
                ft.Text("Adhan", size=10, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                ft.Text(prayer["adhan"], size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2
        )
        
        jamaat_display = ft.Column(
            controls=[
                ft.Text("Jamaat", size=10, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                ft.Text(prayer["jamaat"] or "-", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
            visible=show_jamaat
        )
        
        card_content = ft.Row(
            controls=[
                ft.Row(
                    controls=[icon_container, prayer_name],
                    spacing=12,
                    expand=True
                ),
                ft.Row(
                    controls=[adhan_display, jamaat_display],
                    spacing=20
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        shadow = None
        if is_next:
            shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.3, DesignTokens.PRIMARY)
            )
        
        super().__init__(
            content=card_content,
            padding=20,
            border_radius=DesignTokens.RADIUS_LG,
            bgcolor=ft.Colors.with_opacity(bg_opacity, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(border_opacity, ft.Colors.WHITE)),
            shadow=shadow
        )


# ============================================================================
# COUNTDOWN WIDGET
# ============================================================================

class CountdownWidget(ft.Container):
    """Hero countdown widget with working timer"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.next_prayer = PrayerData.get_next_prayer()
        self.running = True
        
        self.countdown_text = ft.Text(
            "00:00:00",
            size=48,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER
        )
        
        content = ft.Column(
            controls=[
                ft.Text(
                    f"Next: {self.next_prayer['name']}",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=10),
                self.countdown_text,
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ACCESS_TIME, size=16, 
                               color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)),
                        ft.Text(
                            "Time remaining",
                            size=14,
                            color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )
        
        super().__init__(
            content=content,
            padding=30,
            border_radius=DesignTokens.RADIUS_XXL,
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 10)
            )
        )
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()
    
    def _run_timer(self):
        """Timer thread that updates countdown"""
        while self.running:
            try:
                time_data = PrayerData.get_time_remaining(self.next_prayer["adhan"])
                self.countdown_text.value = f"{time_data['hours']:02d}:{time_data['minutes']:02d}:{time_data['seconds']:02d}"
                
                if self.page:
                    self.page.update()
                
                time.sleep(1)
            except:
                break
    
    def stop_timer(self):
        """Stop the countdown timer"""
        self.running = False


# ============================================================================
# DASHBOARD VIEW
# ============================================================================

class DashboardView(ft.Column):
    """Main dashboard view"""
    
    def __init__(self, page: ft.Page, show_jamaat: bool = True):
        self.page = page
        self.show_jamaat = show_jamaat
        self.next_prayer = PrayerData.get_next_prayer()
        
        # Header
        header = self._build_header()
        
        # Countdown
        self.countdown = CountdownWidget(page)
        
        # Prayer cards
        prayer_cards = self._build_prayer_cards()
        
        # Qibla button
        qibla_button = self._build_qibla_button()
        
        super().__init__(
            controls=[
                header,
                ft.Container(height=20),
                self.countdown,
                ft.Container(height=20),
                prayer_cards,
                ft.Container(height=20),
                qibla_button,
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        )
    
    def _build_header(self) -> ft.Control:
        """Build header with date and location"""
        today = datetime.now()
        
        return GlassContainer(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOCATION_ON, size=20, color=ft.Colors.WHITE),
                            ft.Text(
                                "New York, USA",
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.WHITE
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Text(
                        today.strftime("%A, %B %d, %Y"),
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "15 Jumada Al-Awwal 1446 AH",
                        size=14,
                        color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            padding=20,
            border_radius=DesignTokens.RADIUS_XL
        )
    
    def _build_prayer_cards(self) -> ft.Control:
        """Build prayer time cards"""
        cards = []
        
        for prayer in PrayerData.PRAYERS:
            is_next = prayer["name"] == self.next_prayer["name"]
            card = PrayerCard(prayer, is_next, self.show_jamaat)
            cards.append(card)
        
        return ft.Column(
            controls=cards,
            spacing=12
        )
    
    def _build_qibla_button(self) -> ft.Control:
        """Build floating Qibla button"""
        return ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.EXPLORE,
                icon_size=32,
                icon_color=ft.Colors.WHITE,
                tooltip="Qibla Direction"
            ),
            width=70,
            height=70,
            border_radius=35,
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.2, DesignTokens.PRIMARY)
            ),
            alignment=ft.alignment.center
        )
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'countdown'):
            self.countdown.stop_timer()


# ============================================================================
# QIBLA VIEW
# ============================================================================

class QiblaView(ft.Container):
    """Qibla compass view"""
    
    def __init__(self):
        content = GlassContainer(
            content=ft.Column(
                controls=[
                    ft.Text("Qibla Compass", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(height=20),
                    
                    # Compass visual
                    ft.Container(
                        content=ft.Stack(
                            controls=[
                                # Compass circle
                                ft.Container(
                                    width=250,
                                    height=250,
                                    border_radius=125,
                                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                    border=ft.border.all(2, ft.Colors.with_opacity(0.3, ft.Colors.WHITE))
                                ),
                                # Direction markers
                                ft.Container(
                                    content=ft.Text("N", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                    top=10,
                                    left=118
                                ),
                                ft.Container(
                                    content=ft.Text("E", color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                                    top=118,
                                    right=10
                                ),
                                ft.Container(
                                    content=ft.Text("S", color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                                    bottom=10,
                                    left=118
                                ),
                                ft.Container(
                                    content=ft.Text("W", color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                                    top=118,
                                    left=10
                                ),
                                # Qibla indicator
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("☪️", size=40),
                                            ft.Text("Ka'bah", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=4
                                    ),
                                    top=80,
                                    left=90
                                ),
                            ],
                            width=250,
                            height=250
                        ),
                        alignment=ft.alignment.center
                    ),
                    
                    ft.Container(height=20),
                    
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.EXPLORE, color=ft.Colors.WHITE, size=20),
                            ft.Text("58.7° from North", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8
                    ),
                    
                    ft.Text(
                        "Distance to Kaaba: ~9,850 km",
                        size=14,
                        color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
                        text_align=ft.TextAlign.CENTER
                    ),
                    
                    ft.Container(height=10),
                    
                    ft.Text(
                        "Point your device horizontally for accurate direction",
                        size=12,
                        color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                        text_align=ft.TextAlign.CENTER,
                        italic=True
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=40
        )
        
        super().__init__(
            content=content,
            alignment=ft.alignment.center,
            expand=True
        )


# ============================================================================
# SETTINGS VIEW
# ============================================================================

class SettingsView(ft.Container):
    """Settings view"""
    
    def __init__(self, on_jamaat_toggle, on_theme_change, current_theme_mode):
        self.on_jamaat_toggle = on_jamaat_toggle
        self.on_theme_change = on_theme_change
        
        content = ft.Column(
            controls=[
                GlassContainer(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.SETTINGS, size=24, color=ft.Colors.WHITE),
                                    ft.Text("Settings", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                                ],
                                spacing=12
                            ),
                            
                            ft.Container(height=20),
                            
                            # Theme Mode Dropdown
                            ft.Row(
                                controls=[
                                    ft.Text("Theme Mode", size=16, color=ft.Colors.WHITE, expand=True),
                                    ft.Dropdown(
                                        value=current_theme_mode,
                                        options=[
                                            ft.dropdown.Option("Light", "Light"),
                                            ft.dropdown.Option("Dark", "Dark"),
                                            ft.dropdown.Option("System", "System"),
                                        ],
                                        on_change=on_theme_change,
                                        width=150,
                                        text_style=ft.TextStyle(color=ft.Colors.WHITE),
                                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                                        border_color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            
                            ft.Divider(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                            
                            # Jamaat toggle
                            ft.Row(
                                controls=[
                                    ft.Text("Show Jamaat Times", size=16, color=ft.Colors.WHITE, expand=True),
                                    ft.Switch(
                                        value=True,
                                        on_change=self.on_jamaat_toggle,
                                        active_color=DesignTokens.ACCENT
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            
                            ft.Divider(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                            
                            # Settings info
                            ft.Column(
                                controls=[
                                    self._setting_row("📍 Location", "New York, USA"),
                                    self._setting_row("🧮 Method", "ISNA"),
                                    self._setting_row("🌙 Asr School", "Standard (Shafi)"),
                                    self._setting_row("🌍 Timezone", "America/New_York"),
                                    self._setting_row("🔔 Notifications", "Enabled"),
                                ],
                                spacing=12
                            ),
                            
                            ft.Container(height=20),
                            
                            ft.Text(
                                "Prayer Times v1.0 • Offline-First",
                                size=12,
                                color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                                text_align=ft.TextAlign.CENTER
                            )
                        ],
                        spacing=12
                    ),
                    padding=24
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0
        )
        
        super().__init__(
            content=content,
            padding=20,
            expand=True
        )
    
    def _setting_row(self, label: str, value: str) -> ft.Control:
        """Create a settings row"""
        return ft.Row(
            controls=[
                ft.Text(label, size=14, color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE), expand=True),
                ft.Text(value, size=14, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE))
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )


# ============================================================================
# MAIN APP
# ============================================================================

class PrayerTimesApp:
    """Main application"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Prayer Times"
        self.page.padding = 0
        
        self.current_view = "home"
        self.show_jamaat = True
        self.theme_mode = "Light"
        self.current_dashboard = None
        
        self.build()
    
    def build(self):
        """Build main app UI"""
        is_dark = self.theme_mode == "Dark" or (self.theme_mode == "System" and self.page.theme_mode == ft.ThemeMode.DARK)
        
        # Gradient background
        self.background = ft.Container(
            gradient=DesignTokens.get_gradient(is_dark),
            expand=True
        )
        
        # Content area
        self.current_dashboard = DashboardView(self.page, self.show_jamaat)
        self.content_area = ft.Container(
            content=self.current_dashboard,
            padding=20,
            expand=True
        )
        
        # Bottom navigation
        self.nav_bar = self._build_nav_bar()
        
        # Stack everything
        main_stack = ft.Stack(
            controls=[
                self.background,
                ft.Column(
                    controls=[
                        self.content_area,
                        self.nav_bar
                    ],
                    spacing=0,
                    expand=True
                )
            ],
            expand=True
        )
        
        self.page.add(main_stack)
    
    def _build_nav_bar(self) -> ft.Control:
        """Build bottom navigation bar"""
        
        def nav_button(icon, label, view_name):
            is_active = self.current_view == view_name
            
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            icon,
                            size=24,
                            color=ft.Colors.WHITE if is_active else ft.Colors.with_opacity(0.6, ft.Colors.WHITE)
                        ),
                        ft.Text(
                            label,
                            size=12,
                            color=ft.Colors.WHITE if is_active else ft.Colors.with_opacity(0.6, ft.Colors.WHITE)
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4
                ),
                on_click=lambda e, v=view_name: self.switch_view(v),
                padding=8
            )
        
        nav_content = ft.Row(
            controls=[
                nav_button(ft.Icons.HOME, "Home", "home"),
                nav_button(ft.Icons.EXPLORE, "Qibla", "qibla"),
                nav_button(ft.Icons.CALENDAR_MONTH, "Calendar", "calendar"),
                nav_button(ft.Icons.SETTINGS, "Settings", "settings"),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND
        )
        
        return GlassContainer(
            content=nav_content,
            padding=12,
            border_radius=DesignTokens.RADIUS_XL
        )
    
    def switch_view(self, view_name: str):
        """Switch between views"""
        # Clean up previous dashboard if switching away from home
        if self.current_view == "home" and view_name != "home" and self.current_dashboard:
            self.current_dashboard.cleanup()
            self.current_dashboard = None
        
        self.current_view = view_name
        
        if view_name == "home":
            self.current_dashboard = DashboardView(self.page, self.show_jamaat)
            self.content_area.content = self.current_dashboard
        elif view_name == "qibla":
            self.content_area.content = QiblaView()
        elif view_name == "calendar":
            self.content_area.content = self._build_placeholder("Calendar", ft.Icons.CALENDAR_MONTH)
        elif view_name == "settings":
            self.content_area.content = SettingsView(
                self._on_jamaat_toggle, 
                self._on_theme_change,
                self.theme_mode
            )
        
        self.page.update()
    
    def _on_theme_change(self, e):
        """Handle theme change"""
        self.theme_mode = e.control.value
        
        # Update background gradient
        is_dark = self.theme_mode == "Dark" or (self.theme_mode == "System" and self.page.theme_mode == ft.ThemeMode.DARK)
        self.background.gradient = DesignTokens.get_gradient(is_dark)
        
        # Update page theme mode
        if self.theme_mode == "Light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif self.theme_mode == "Dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
        
        # Show snackbar
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"Theme changed to {self.theme_mode}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.with_opacity(0.8, DesignTokens.PRIMARY)
            )
        )
        
        self.page.update()
    
    def _on_jamaat_toggle(self, e):
        """Handle Jamaat toggle"""
        self.show_jamaat = e.control.value
        if self.current_view == "home":
            # Clean up old dashboard
            if self.current_dashboard:
                self.current_dashboard.cleanup()
            
            # Create new dashboard
            self.current_dashboard = DashboardView(self.page, self.show_jamaat)
            self.content_area.content = self.current_dashboard
            self.page.update()
    
    def _build_placeholder(self, title: str, icon) -> ft.Control:
        """Build placeholder view"""
        return ft.Container(
            content=GlassContainer(
                content=ft.Column(
                    controls=[
                        ft.Icon(icon, size=64, color=ft.Colors.WHITE),
                        ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Coming soon...", size=14, color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE))
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16
                ),
                padding=40
            ),
            alignment=ft.alignment.center,
            expand=True
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main(page: ft.Page):
    """Main entry point"""
    app = PrayerTimesApp(page)


if __name__ == "__main__":
    ft.app(target=main)