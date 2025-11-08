"""
PrayerOffline - Main Application Class
Handles navigation, view management, and service coordination
"""

import flet as ft
import logging
from typing import Optional, Dict, Any
from theme_manager import theme_manager  # Import the global instance


logger = logging.getLogger(__name__)


class PrayerOfflineApp:
    """Main application class with navigation and view management"""
    
    def __init__(self, page: ft.Page, storage):
        """
        Initialize the application
        
        Args:
            page: Flet page instance
            storage: StorageService instance (pre-initialized)
        """
        self.page = page
        self.storage = storage
        self._initialized = False
        self.theme_manager = theme_manager  # ✅ Use global instance directly
        self._apply_theme()
        self.location_service = None
        self.audio_player = None
        self.notifier = None
        self.views = {}  # type: Dict[str, Any]
        self.current_view = "dashboard"

        # Navigation components
        self.nav_rail = None  # type: Optional[ft.NavigationRail]
        self.nav_bar = None  # type: Optional[ft.NavigationBar]
        self.content_container = None  # type: Optional[ft.Container]

        # Track initialization state
        self._initialized = False
        
        logger.info("PrayerOfflineApp instance created")

        # Handle page resize for responsive layout
        self.page.on_resize = self._on_page_resize

    def _on_page_resize(self, e):
        """Handle page resize for responsive layout"""
        try:
            # Rebuild layout if size category changed
            if self.page.width:
                was_mobile = self.page.width < 600
                # Rebuild if needed
                pass
        except Exception as ex:
            logger.error(f"Resize error: {ex}")
    
    def _apply_theme(self):
        """Apply theme from settings"""
        try:
            settings = self.storage.get('settings', {})
            theme_mode = settings.get("theme_mode", "System")
            
            if theme_mode == "Dark":
                self.page.theme_mode = ft.ThemeMode.DARK
            elif theme_mode == "Light":
                self.page.theme_mode = ft.ThemeMode.LIGHT
            else:
                self.page.theme_mode = ft.ThemeMode.SYSTEM
            
            logger.info(f"Applied theme: {theme_mode}")
        except Exception as e:
            logger.warning(f"Failed to apply theme, using system default: {e}")
            self.page.theme_mode = ft.ThemeMode.SYSTEM
    
    def initialize(self):
        """Initialize all services and views (synchronous)"""
        if self._initialized:
            logger.warning("App already initialized, skipping")
            return
        
        try:
            logger.info("Initializing PrayerOffline application...")
            
            # Initialize services
            self._initialize_services()
            
            # Initialize views
            self._initialize_views()
            
            # Build UI
            self._build_ui()
            
            self._initialized = True
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            self._show_error_screen(e)
            raise
    
    def _initialize_services(self):
        """Initialize all application services"""
        # Location service
        try:
            from services.location import LocationService
            self.location_service = LocationService()
            logger.info("✓ Location service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize location service: {e}")
            self.location_service = None
        
        # Audio player (optional)
        try:
            from services.audio_player import AudioPlayer
            self.audio_player = AudioPlayer()
            logger.info("✓ Audio player initialized")
        except Exception as e:
            logger.warning(f"Audio player not available: {e}")
            self.audio_player = None
        
        # Notifier service (optional)
        try:
            from services.notifier import NotificationService
            self.notifier = NotificationService()
            logger.info("✓ Notification service initialized")
        except Exception as e:
            logger.warning(f"Notification service not available: {e}")
            self.notifier = None
    
    def _initialize_views(self):
        """Initialize all view classes"""
        try:
            from views.dashboard_view_glass import GlassmorphicDashboard
            from views.qibla_view import QiblaView
            from views.dua_view import DuaView
            from views.tasbih_view import TasbihView
            from views.settings_view import SettingsView
            
            self.views = {
                "dashboard": GlassmorphicDashboard(
                    page=self.page,
                    storage=self.storage,
                    notifier=self.notifier,
                    location_service=self.location_service,
                    theme_manager=self.theme_manager  # ✅ Has theme support
                ),
                "qibla": QiblaView(
                    location_service=self.location_service,
                    i18n_strings={}
                    # ❌ No theme_manager - QiblaView doesn't support it yet
                ),
                "dua": DuaView(
                    page=self.page,
                    storage_service=self.storage,
                    audio_service=self.audio_player,
                    theme_manager=self.theme_manager  # ✅ NEW - Now has theme support!
                ),
                "tasbih": TasbihView(
                    page=self.page,
                    storage_service=self.storage,
                    audio_service=self.audio_player,
                    theme_manager=self.theme_manager  # ✅ NEW - Now has theme support!
                ),
                "settings": SettingsView(
                    page=self.page,
                    storage_service=self.storage,
                    location_service=self.location_service,
                    theme_manager=self.theme_manager,  # ✅ Has theme support
                    on_settings_changed=self._on_settings_changed
                )
            }
            logger.info("All views initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize views: {e}", exc_info=True)
            raise
    
    def _build_ui(self):
        """Build the main UI layout"""
        try:
            # Determine layout based on page width
            if self.page.width and self.page.width < 600:
                # Mobile layout with bottom navigation bar
                layout = self._build_mobile_layout()
            else:
                # Desktop layout with navigation rail
                layout = self._build_desktop_layout()
            
            self.page.add(layout)
            self.page.update()
            
            logger.info("UI built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build UI: {e}", exc_info=True)
            raise
    
    def _build_desktop_layout(self) -> ft.Control:
        """Build desktop layout with navigation rail"""
        # Create content container
        self.content_container = ft.Container(
            content=self._get_current_view(),
            expand=True,
            padding=20,
        )
        
        # Create navigation rail
        self.nav_rail = ft.NavigationRail(
            selected_index=self._get_view_index(self.current_view),
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=80,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.EXPLORE_OUTLINED,
                    selected_icon=ft.Icons.EXPLORE,
                    label="Qibla"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.BOOK_OUTLINED,
                    selected_icon=ft.Icons.BOOK,
                    label="Du'a"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.CIRCLE_OUTLINED,
                    selected_icon=ft.Icons.CIRCLE,
                    label="Tasbih"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings"
                ),
            ],
            on_change=self._on_navigation_change,
        )
        
        return ft.Row(
            controls=[
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content_container,
            ],
            spacing=0,
            expand=True,
        )
    
    def _build_mobile_layout(self) -> ft.Control:
        """Build mobile layout with bottom navigation bar"""
        # Create content container
        self.content_container = ft.Container(
            content=self._get_current_view(),
            expand=True,
            padding=10,
        )
        
        # Create navigation bar
        self.nav_bar = ft.NavigationBar(
            selected_index=self._get_view_index(self.current_view),
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Home"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.EXPLORE_OUTLINED,
                    selected_icon=ft.Icons.EXPLORE,
                    label="Qibla"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.BOOK_OUTLINED,
                    selected_icon=ft.Icons.BOOK,
                    label="Du'a"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.CIRCLE_OUTLINED,
                    selected_icon=ft.Icons.CIRCLE,
                    label="Tasbih"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings"
                ),
            ],
            on_change=self._on_navigation_change,
        )
        
        return ft.Column(
            controls=[
                self.content_container,
                self.nav_bar,
            ],
            spacing=0,
            expand=True,
        )
    
    def _get_current_view(self) -> ft.Control:
        """Get the current view's content"""
        if self.current_view in self.views:
            try:
                return self.views[self.current_view].build()
            except Exception as e:
                logger.error(f"Failed to build {self.current_view} view: {e}")
                return self._create_error_view(str(e))
        else:
            return ft.Text("View not found")
    
    def _create_error_view(self, error_msg: str) -> ft.Control:
        """Create an error view"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.ERROR),
                    ft.Text("Error loading view", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(error_msg, size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
    
    def _get_view_index(self, view_name: str) -> int:
        """Get index of view by name"""
        view_names = ["dashboard", "qibla", "dua", "tasbih", "settings"]
        return view_names.index(view_name) if view_name in view_names else 0
    
    def _get_view_name(self, index: int) -> str:
        """Get view name by index"""
        view_names = ["dashboard", "qibla", "dua", "tasbih", "settings"]
        return view_names[index] if 0 <= index < len(view_names) else "dashboard"
    
    def _on_navigation_change(self, e):
        """Handle navigation change"""
        try:
            index = e.control.selected_index
            view_name = self._get_view_name(index)
            
            if view_name != self.current_view:
                self.navigate_to(view_name)
                
        except Exception as ex:
            logger.error(f"Navigation error: {ex}", exc_info=True)
    
    def navigate_to(self, view_name: str):
        """Navigate to a specific view"""
        try:
            if view_name not in self.views:
                logger.error(f"View '{view_name}' not found")
                return
            
            self.current_view = view_name
            
            # Update navigation selection
            index = self._get_view_index(view_name)
            if self.nav_rail:
                self.nav_rail.selected_index = index
            if self.nav_bar:
                self.nav_bar.selected_index = index
            
            # Update content
            if self.content_container:
                self.content_container.content = self._get_current_view()
                self.page.update()
            
            logger.info(f"Navigated to: {view_name}")
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}", exc_info=True)
    
    def _on_theme_changed(self, theme_mode: str):
        """Handle theme change from settings"""
        try:
            if theme_mode == "Dark":
                self.page.theme_mode = ft.ThemeMode.DARK
            elif theme_mode == "Light":
                self.page.theme_mode = ft.ThemeMode.LIGHT
            else:
                self.page.theme_mode = ft.ThemeMode.SYSTEM
            
            self.page.update()
            logger.info(f"Theme changed to: {theme_mode}")
            
        except Exception as e:
            logger.error(f"Failed to change theme: {e}")
    
    def _show_error_screen(self, error: Exception):
        """Show error screen when initialization fails"""
        try:
            error_view = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.ERROR),
                        ft.Text(
                            "Failed to Start Application",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            str(error),
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            "Please check the logs for more details.",
                            size=12,
                            italic=True,
                            text_align=ft.TextAlign.CENTER
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                alignment=ft.alignment.center,
                expand=True,
                padding=40,
            )
            
            self.page.clean()
            self.page.add(error_view)
            self.page.update()
            
        except Exception as e:
            logger.error(f"Failed to show error screen: {e}")
    
    def _on_settings_changed(self, settings: Dict):
        """Handle settings change (FIXED)"""
        try:
            theme_mode = settings.get("theme_mode", "System")
            theme_name = settings.get("theme_name")
            if theme_name and theme_name in self.theme_manager.themes:
                self.theme_manager.settings = settings
                self._apply_theme()
                self._rebuild_layout()
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}", exc_info=True)