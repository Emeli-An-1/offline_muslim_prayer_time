"""
PrayerOffline - Main Entry Point with Full View Integration (FIXED)
Privacy-first offline Muslim Prayer Time application
"""

import flet as ft
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
log_file = project_root / 'prayer_offline.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SimpleStorageService:
    """Simple in-memory storage service for development with error handling"""
    def __init__(self):
        self.data = {}
        logger.info("Storage service initialized")
    
    def get(self, key: str, default=None):
        try:
            return self.data.get(key, default)
        except Exception as e:
            logger.error(f"Storage get error for key '{key}': {e}")
            return default
    
    def set(self, key: str, value):
        try:
            self.data[key] = value
            logger.debug(f"Storage set: {key}")
        except Exception as e:
            logger.error(f"Storage set error for key '{key}': {e}")
    
    def cache_prayer_times(self, date: str, times: dict):
        try:
            if "prayer_cache" not in self.data:
                self.data["prayer_cache"] = {}
            self.data["prayer_cache"][date] = times
        except Exception as e:
            logger.error(f"Prayer cache error: {e}")
    
    def get_cached_prayer_times(self, date: str):
        try:
            if "prayer_cache" not in self.data:
                return None
            return self.data["prayer_cache"].get(date)
        except Exception as e:
            logger.error(f"Get cached prayer times error: {e}")
            return None


class SimpleLocationService:
    """Simple location service for development with validation"""
    def __init__(self, storage=None):
        self.storage = storage
        self.current_location = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "city": "New York",
            "timezone": "America/New_York"
        }
        if storage:
            try:
                stored = storage.get("location", {})
                if stored.get("latitude"):
                    self.current_location = stored
                    logger.info(f"Loaded location: {stored.get('city')}")
            except Exception as e:
                logger.error(f"Location load error: {e}")
    
    def get_current_location(self) -> Dict[str, Any]:
        return self.current_location.copy()
    
    def set_location(self, lat: float, lng: float, city: str, timezone: str = "UTC") -> bool:
        """Set location with validation. Returns True on success."""
        try:
            if not (-90 <= lat <= 90):
                logger.warning(f"Invalid latitude: {lat}")
                return False
            if not (-180 <= lng <= 180):
                logger.warning(f"Invalid longitude: {lng}")
                return False
            
            self.current_location = {
                "latitude": lat,
                "longitude": lng,
                "city": city,
                "timezone": timezone
            }
            if self.storage:
                self.storage.set("location", self.current_location)
            logger.info(f"Location updated: {city} ({lat}, {lng})")
            return True
        except Exception as e:
            logger.error(f"Set location error: {e}")
            return False


def main(page: ft.Page):
    """Main application entry point"""
    
    try:
        # Services
        storage = SimpleStorageService()
        location_service = SimpleLocationService(storage)
        
        # Initialize default settings
        if not storage.get("settings"):
            storage.set("settings", {
                "location": location_service.get_current_location(),
                "calculation_method": "ISNA",
                "asr_school": "STANDARD",
                "high_latitude_rule": "ANGLE_BASED",
                "theme": "auto",
                "language": "en",
                "font_size": 14,
                "notifications_enabled": True,
                "vibration_enabled": True,
            })
        
        if not storage.get("jamaat_config"):
            storage.set("jamaat_config", {
                "Fajr": {"mode": "fixed", "time": "05:45", "minutes": None, "enabled": True},
                "Dhuhr": {"mode": "shift", "time": None, "minutes": 10, "enabled": True},
                "Asr": {"mode": "shift", "time": None, "minutes": 15, "enabled": True},
                "Maghrib": {"mode": "shift", "time": None, "minutes": 5, "enabled": True},
                "Isha": {"mode": "fixed", "time": "20:30", "minutes": None, "enabled": True}
            })
        
        # Configure page
        page.title = "PrayerOffline - Muslim Prayer Times"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.spacing = 0
        
        # Window configuration with error handling
        try:
            page.window.width = 400
            page.window.height = 700
            page.window.min_width = 350
            page.window.min_height = 500
            page.window.resizable = True
        except AttributeError:
            logger.info("Window sizing not available (web mode)")
        except Exception as e:
            logger.warning(f"Window configuration error: {e}")
        
        logger.info("Starting PrayerOffline application...")
        
        # State management
        app_state = {
            "current_view": 0,
            "nav_buttons": {}
        }
        main_content_area = ft.Container(expand=True)
        
        def show_snackbar(message: str, error: bool = False):
            """Helper to show snackbar messages"""
            try:
                page.snack_bar = ft.SnackBar(
                    ft.Text(message),
                    bgcolor=ft.Colors.ERROR_CONTAINER if error else None
                )
                page.snack_bar.open = True
                page.update()
            except Exception as e:
                logger.error(f"Snackbar error: {e}")
        
        def update_nav_highlight(view_index: int):
            """Update navigation button highlighting"""
            try:
                for idx, btn in app_state["nav_buttons"].items():
                    if idx == view_index:
                        btn.bgcolor = ft.Colors.PRIMARY_CONTAINER
                    else:
                        btn.bgcolor = ft.Colors.TRANSPARENT
                app_state["current_view"] = view_index
                page.update()
            except Exception as e:
                logger.error(f"Nav highlight error: {e}")
        
        def show_dashboard(e=None):
            """Show dashboard with prayer times"""
            try:
                update_nav_highlight(0)
                main_content_area.content = None
                
                # TODO: Replace with actual prayer time calculation
                # For now, using sample data
                prayer_times = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "prayers": {
                        "Fajr": {"adhan": "05:30", "jamaat": "05:45"},
                        "Sunrise": {"adhan": "06:45", "jamaat": None},
                        "Dhuhr": {"adhan": "12:30", "jamaat": "12:45"},
                        "Asr": {"adhan": "15:45", "jamaat": "16:00"},
                        "Maghrib": {"adhan": "18:15", "jamaat": "18:20"},
                        "Isha": {"adhan": "19:45", "jamaat": "20:00"}
                    }
                }
                
                date_obj = datetime.strptime(prayer_times["date"], "%Y-%m-%d")
                formatted_date = date_obj.strftime("%A, %B %d, %Y")
                
                prayer_icons = {
                    "Fajr": ft.Icons.BRIGHTNESS_5,
                    "Sunrise": ft.Icons.WB_SUNNY,
                    "Dhuhr": ft.Icons.WB_SUNNY_OUTLINED,
                    "Asr": ft.Icons.BRIGHTNESS_6,
                    "Maghrib": ft.Icons.BRIGHTNESS_3,
                    "Isha": ft.Icons.BRIGHTNESS_2
                }
                
                prayer_cards = []
                for prayer_name, times in prayer_times["prayers"].items():
                    adhan_time = times.get("adhan", "N/A")
                    jamaat_time = times.get("jamaat")
                    
                    time_display = ft.Column(
                        controls=[
                            ft.Text(prayer_name, size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Adhan: {adhan_time}", size=18, weight=ft.FontWeight.W_500)
                        ],
                        spacing=2
                    )
                    
                    if jamaat_time:
                        time_display.controls.append(
                            ft.Text(f"Jamaat: {jamaat_time}", size=14, color=ft.Colors.OUTLINE)
                        )
                    
                    card = ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(
                                        prayer_icons.get(prayer_name, ft.Icons.ACCESS_TIME),
                                        size=30,
                                        color=ft.Colors.PRIMARY
                                    ),
                                    time_display
                                ],
                                spacing=20
                            ),
                            padding=15
                        )
                    )
                    prayer_cards.append(card)
                
                location_info = storage.get("location", {})
                city = location_info.get("city", "Unknown")
                
                dashboard = ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Today's Prayer Times", size=24, weight=ft.FontWeight.BOLD),
                                    ft.Text(formatted_date, size=14, color=ft.Colors.OUTLINE),
                                    ft.Text(f"📍 {city}", size=12, color=ft.Colors.OUTLINE)
                                ],
                                spacing=5
                            ),
                            padding=ft.padding.only(left=20, right=20, top=20, bottom=10)
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=prayer_cards,
                                spacing=10,
                                scroll=ft.ScrollMode.AUTO
                            ),
                            padding=20,
                            expand=True
                        )
                    ],
                    spacing=0,
                    expand=True
                )
                
                main_content_area.content = dashboard
                page.update()
                logger.debug("Dashboard view loaded")
                
            except Exception as e:
                logger.error(f"Dashboard error: {e}", exc_info=True)
                show_snackbar("Error loading dashboard", error=True)
        
        def show_qibla(e=None):
            """Show Qibla compass"""
            try:
                update_nav_highlight(1)
                main_content_area.content = None
                
                loc = storage.get("location", {})
                lat = loc.get("latitude", 40.7128)
                lng = loc.get("longitude", -74.0060)
                
                # TODO: Replace with actual Qibla calculation using qibla_service
                # Simple approximation for demo
                import math
                
                # Kaaba coordinates
                kaaba_lat = 21.4225
                kaaba_lng = 39.8262
                
                # Simple bearing calculation
                lat_diff = math.radians(kaaba_lat - lat)
                lng_diff = math.radians(kaaba_lng - lng)
                
                y = math.sin(lng_diff) * math.cos(math.radians(kaaba_lat))
                x = math.cos(math.radians(lat)) * math.sin(math.radians(kaaba_lat)) - \
                    math.sin(math.radians(lat)) * math.cos(math.radians(kaaba_lat)) * math.cos(lng_diff)
                
                qibla_bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
                
                # Distance calculation (Haversine)
                R = 6371  # Earth radius in km
                dlat = math.radians(kaaba_lat - lat)
                dlng = math.radians(kaaba_lng - lng)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * \
                    math.cos(math.radians(kaaba_lat)) * math.sin(dlng/2)**2
                c = 2 * math.asin(math.sqrt(a))
                distance = R * c
                
                qibla = ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Text("Qibla Compass", size=24, weight=ft.FontWeight.BOLD),
                            padding=16
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.COMPASS_CALIBRATION, size=120, color=ft.Colors.PRIMARY),
                                    ft.Text(
                                        f"Qibla Direction: {qibla_bearing:.1f}° from North",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.Text(
                                        f"Distance to Kaaba: {distance:,.0f} km",
                                        size=14,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.Divider(),
                                    ft.Text("Your Location:", size=12, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Latitude: {lat:.4f}°", size=12),
                                    ft.Text(f"Longitude: {lng:.4f}°", size=12),
                                    ft.Divider(),
                                    ft.Text("Instructions:", size=12, weight=ft.FontWeight.BOLD),
                                    ft.Text("1. Hold device level", size=11),
                                    ft.Text("2. Rotate to align with arrow", size=11),
                                    ft.Text("3. Arrow points toward Mecca", size=11),
                                ],
                                spacing=12,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=16,
                            border=ft.border.all(1, ft.Colors.OUTLINE),
                            border_radius=12,
                            margin=16
                        ),
                        ft.Container(expand=True)
                    ],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO
                )
                
                main_content_area.content = qibla
                page.update()
                logger.debug("Qibla view loaded")
                
            except Exception as e:
                logger.error(f"Qibla error: {e}", exc_info=True)
                show_snackbar("Error loading Qibla", error=True)
        
        def show_dua(e=None):
            """Show Dua/Supplications"""
            try:
                update_nav_highlight(2)
                main_content_area.content = None
                
                # Sample duas with proper RTL support
                duas = [
                    {
                        "title": "Morning Supplication",
                        "arabic": "الحمد لله حمداً كثيراً طيباً مباركاً",
                        "transliteration": "Al-hamdu lillahi hamdan kathiran tayyiban mubarakan",
                        "translation": "All praise is due to Allah with much good and blessed praise."
                    },
                    {
                        "title": "Before Sleep",
                        "arabic": "بسم الله أموت وأحيا",
                        "transliteration": "Bismillah amutu wa ahya",
                        "translation": "In the name of Allah I die and I live."
                    },
                    {
                        "title": "Upon Waking",
                        "arabic": "الحمد لله الذي أحيانا بعد ما أماتنا وإليه النشور",
                        "transliteration": "Al-hamdu lillahi alladhi ahyana ba'da ma amitana wa ilayhi an-nushor",
                        "translation": "All praise is due to Allah who gave us life after death and to Him is the return."
                    }
                ]
                
                dua_cards = []
                for dua in duas:
                    card = ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(dua["title"], size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        dua["arabic"],
                                        size=18,
                                        color=ft.Colors.PRIMARY,
                                        text_align=ft.TextAlign.RIGHT,
                                        rtl=True
                                    ),
                                    ft.Text(dua["transliteration"], size=10, italic=True),
                                    ft.Text(dua["translation"], size=11),
                                ],
                                spacing=8
                            ),
                            padding=12
                        )
                    )
                    dua_cards.append(card)
                
                dua_view = ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Text("Supplications (Dua)", size=24, weight=ft.FontWeight.BOLD),
                            padding=16
                        ),
                        ft.Container(
                            content=ft.TextField(
                                label="Search Dua",
                                prefix_icon=ft.Icons.SEARCH,
                                width=250
                            ),
                            padding=16,
                            alignment=ft.alignment.center
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=dua_cards,
                                spacing=8,
                                scroll=ft.ScrollMode.AUTO
                            ),
                            padding=16,
                            expand=True
                        )
                    ],
                    expand=True,
                    spacing=0
                )
                
                main_content_area.content = dua_view
                page.update()
                logger.debug("Dua view loaded")
                
            except Exception as e:
                logger.error(f"Dua error: {e}", exc_info=True)
                show_snackbar("Error loading Duas", error=True)
        
        def show_tasbih(e=None):
            """Show Tasbih counter"""
            try:
                update_nav_highlight(3)
                main_content_area.content = None
                
                counter_state = {"count": 0, "target": 33}
                
                def increment_counter(e):
                    counter_state["count"] += 1
                    if counter_state["count"] > counter_state["target"]:
                        counter_state["count"] = 0
                    update_tasbih_display()
                
                def reset_counter(e):
                    counter_state["count"] = 0
                    update_tasbih_display()
                
                count_text = ft.Text(
                    f"{counter_state['count']}/{counter_state['target']}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                )
                
                # Fix: Prevent division by zero
                initial_progress = 0.0 if counter_state['target'] == 0 else \
                                   counter_state['count'] / counter_state['target']
                
                progress_ring = ft.ProgressRing(
                    value=initial_progress,
                    stroke_width=8,
                    width=150,
                    height=150,
                    color=ft.Colors.PRIMARY
                )
                
                def update_tasbih_display():
                    try:
                        count_text.value = f"{counter_state['count']}/{counter_state['target']}"
                        if counter_state['target'] > 0:
                            progress_ring.value = min(1.0, counter_state['count'] / counter_state['target'])
                        else:
                            progress_ring.value = 0.0
                        page.update()
                    except Exception as e:
                        logger.error(f"Tasbih display update error: {e}")
                
                tasbih = ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Text("Tasbih Counter", size=24, weight=ft.FontWeight.BOLD),
                            padding=16
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "سبحان الله",
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER,
                                        color=ft.Colors.PRIMARY,
                                        rtl=True
                                    ),
                                    ft.Container(
                                        content=ft.Stack(
                                            controls=[
                                                progress_ring,
                                                ft.Container(
                                                    content=count_text,
                                                    alignment=ft.alignment.center,
                                                    width=150,
                                                    height=150
                                                )
                                            ],
                                            width=150,
                                            height=150
                                        ),
                                        alignment=ft.alignment.center,
                                        padding=20
                                    ),
                                    ft.Container(
                                        content=ft.IconButton(
                                            icon=ft.Icons.ADD_CIRCLE,
                                            icon_size=80,
                                            icon_color=ft.Colors.PRIMARY,
                                            on_click=increment_counter
                                        ),
                                        alignment=ft.alignment.center,
                                        padding=16
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.IconButton(icon=ft.Icons.ARROW_BACK, tooltip="Previous"),
                                            ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Reset", on_click=reset_counter),
                                            ft.IconButton(icon=ft.Icons.ARROW_FORWARD, tooltip="Next"),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=16
                                    ),
                                ],
                                spacing=12,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=16,
                            border=ft.border.all(1, ft.Colors.OUTLINE),
                            border_radius=12,
                            margin=16
                        ),
                        ft.Container(expand=True)
                    ],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO
                )
                
                main_content_area.content = tasbih
                page.update()
                logger.debug("Tasbih view loaded")
                
            except Exception as e:
                logger.error(f"Tasbih error: {e}", exc_info=True)
                show_snackbar("Error loading Tasbih", error=True)
        
        def show_settings(e=None):
            """Show Settings"""
            try:
                update_nav_highlight(4)
                main_content_area.content = None
                
                loc = storage.get("location", {})
                lat_field = ft.TextField(
                    label="Latitude",
                    value=str(loc.get("latitude", 40.7128)),
                    width=150,
                    keyboard_type=ft.KeyboardType.NUMBER
                )
                lng_field = ft.TextField(
                    label="Longitude",
                    value=str(loc.get("longitude", -74.0060)),
                    width=150,
                    keyboard_type=ft.KeyboardType.NUMBER
                )
                city_field = ft.TextField(
                    label="City",
                    value=loc.get("city", "New York"),
                    width=250
                )
                
                def save_location(e):
                    try:
                        lat = float(lat_field.value)
                        lng = float(lng_field.value)
                        city = city_field.value.strip()
                        
                        if not city:
                            show_snackbar("City name is required", error=True)
                            return
                        
                        if location_service.set_location(lat, lng, city):
                            storage.set("location_configured", True)
                            show_snackbar("✓ Location saved successfully!")
                            logger.info(f"Location saved: {city}")
                        else:
                            show_snackbar("Invalid coordinates. Lat: -90 to 90, Lng: -180 to 180", error=True)
                            
                    except ValueError:
                        show_snackbar("Invalid number format", error=True)
                        logger.warning("Invalid location input")
                    except Exception as e:
                        show_snackbar(f"Error saving location: {str(e)}", error=True)
                        logger.error(f"Location save error: {e}")
                
                settings = ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                            padding=16
                        ),
                        
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Location Settings", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        f"Current: {loc.get('city', 'Unknown')}",
                                        size=12,
                                        color=ft.Colors.OUTLINE
                                    ),
                                    ft.Row(
                                        controls=[lat_field, lng_field],
                                        spacing=10
                                    ),
                                    city_field,
                                    ft.ElevatedButton(
                                        "Save Location",
                                        icon=ft.Icons.CHECK,
                                        on_click=save_location
                                    ),
                                ],
                                spacing=8
                            ),
                            padding=16,
                            border=ft.border.all(1, ft.Colors.OUTLINE),
                            border_radius=8,
                            margin=16
                        ),
                        
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Calculation Settings", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Dropdown(
                                        label="Calculation Method",
                                        options=[
                                            ft.dropdown.Option("ISNA"),
                                            ft.dropdown.Option("MWL"),
                                            ft.dropdown.Option("EGYPTIAN"),
                                            ft.dropdown.Option("KARACHI"),
                                            ft.dropdown.Option("UMM_AL_QURA")
                                        ],
                                        value="ISNA",
                                        expand=True
                                    ),
                                    ft.Dropdown(
                                        label="Asr School",
                                        options=[
                                            ft.dropdown.Option("STANDARD"),
                                            ft.dropdown.Option("HANAFI")
                                        ],
                                        value="STANDARD",
                                        expand=True
                                    ),
                                ],
                                spacing=8
                            ),
                            padding=16,
                            border=ft.border.all(1, ft.Colors.OUTLINE),
                            border_radius=8,
                            margin=16
                        ),
                        
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("App Information", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text("Version: 0.1.0-alpha", size=12),
                                    ft.Text("Privacy-first • Offline-first • Open Source", size=11),
                                ],
                                spacing=4
                            ),
                            padding=16,
                            border=ft.border.all(1, ft.Colors.OUTLINE),
                            border_radius=8,
                            margin=16
                        ),
                        
                        ft.Container(expand=True)
                    ],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO
                )
                
                main_content_area.content = settings
                page.update()
                logger.debug("Settings view loaded")
                
            except Exception as e:
                logger.error(f"Settings error: {e}", exc_info=True)
                show_snackbar("Error loading Settings", error=True)
        
        # Create navigation bar
        nav_items = [
            ("Dashboard", ft.Icons.HOME, show_dashboard),
            ("Qibla", ft.Icons.COMPASS_CALIBRATION, show_qibla),
            ("Dua", ft.Icons.BOOK, show_dua),
            ("Tasbih", ft.Icons.CIRCLE, show_tasbih),
            ("Settings", ft.Icons.SETTINGS, show_settings),
        ]
        
        nav_buttons_list = []
        for idx, (label, icon, handler) in enumerate(nav_items):
            btn = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(icon, size=24),
                        ft.Text(label, size=10)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2
                ),
                padding=8,
                on_click=handler,
                expand=True,
                bgcolor=ft.Colors.PRIMARY_CONTAINER if idx == 0 else ft.Colors.TRANSPARENT,
                border_radius=8,
                ink=True
            )
            app_state["nav_buttons"][idx] = btn
            nav_buttons_list.append(btn)
        
        nav_bar = ft.Container(
            content=ft.Row(controls=nav_buttons_list, spacing=4),
            padding=8,
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
            bgcolor=ft.Colors.SURFACE
        )
        
        # Main layout
        page.add(
            ft.Column(
                controls=[main_content_area, nav_bar],
                spacing=0,
                expand=True
            )
        )
        
        # Show initial view
        show_dashboard()
        logger.info("Application started successfully")
        
    except Exception as e:
        logger.critical(f"Fatal application error: {e}", exc_info=True)
        # Show error dialog
        try:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Application Error"),
                content=ft.Text(f"Failed to start application:\n{str(e)}"),
                actions=[
                    ft.TextButton("Close", on_click=lambda e: sys.exit(1))
                ]
            )
            page.dialog.open = True
            page.update()
        except:
            print(f"CRITICAL ERROR: {e}")
            sys.exit(1)


if __name__ == '__main__':
    try:
        logger.info("Launching PrayerOffline...")
        ft.app(target=main, name="PrayerOffline")
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Startup error: {e}", exc_info=True)
        print(f"\n❌ Failed to start PrayerOffline: {e}")
        print(f"Check log file: prayer_offline.log")
        sys.exit(1)