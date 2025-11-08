"""
Base View for PrayerOffline App - FIXED
Provides common functionality for all views
"""

import flet as ft
import logging
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


class SnackBarType:
    """Snackbar message types"""
    ERROR = "error"
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"


class BaseView:
    """
    Base class for all views in the application.
    Provides common functionality and structure.
    """
    
    def __init__(self, page: ft.Page, storage, **kwargs):
        """
        Initialize base view.
        
        Args:
            page: Flet page instance
            storage: Storage service instance
            **kwargs: Additional services (location_service, notifier, etc.)
        """
        self.page = page
        self.storage = storage
        
        # Setup logger for this view
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Extract common services from kwargs
        self.location_service = kwargs.get('location_service')
        self.notifier = kwargs.get('notifier')
        self.audio_player = kwargs.get('audio_player')
        self.audio_service = kwargs.get('audio_service')  # Alternative name
        self.on_navigation = kwargs.get('on_navigation')
        self.i18n_strings = kwargs.get('i18n_strings', {})
        
        # View state
        self.is_mounted = False
        self.container = None
        
        # Load settings
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict:
        """Load settings from storage"""
        try:
            # Try different storage methods
            if hasattr(self.storage, 'get_all_settings'):
                return self.storage.get_all_settings()
            elif hasattr(self.storage, 'get_settings'):
                return self.storage.get_settings()
            elif hasattr(self.storage, 'get'):
                # Get from nested 'settings' key or return entire storage
                settings = self.storage.get('settings')
                if settings and isinstance(settings, dict):
                    return settings
                # Otherwise, return a dict with common keys
                return {
                    'location': self.storage.get('location', {}),
                    'calculation_method': self.storage.get('calculation_method', 'ISNA'),
                    'theme_mode': self.storage.get('theme_mode', 'System'),
                    'language': self.storage.get('language', 'en'),
                }
            else:
                self.logger.warning("Storage service has no recognized get method")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            return {}
    
    def build(self) -> ft.Control:
        """
        Build the view UI. Override this in subclasses.
        
        Returns:
            ft.Control: The main control for this view
        """
        return ft.Container(
            content=ft.Text("Base View - Override build() method"),
            padding=20
        )
    
    def did_mount(self):
        """Called when view is mounted to the page"""
        self.is_mounted = True
        self.logger.debug(f"{self.__class__.__name__} mounted")
    
    def will_unmount(self):
        """Called when view is about to be unmounted"""
        self.is_mounted = False
        self.logger.debug(f"{self.__class__.__name__} unmounting")
    
    def update(self):
        """Update the view"""
        try:
            if self.container and hasattr(self.container, 'update'):
                self.container.update()
            elif self.page:
                self.page.update()
        except Exception as e:
            self.logger.error(f"Failed to update view: {e}")
    
    def get_string(self, key: str, default: str = "") -> str:
        """
        Get translated string for current language.
        
        Args:
            key: Translation key (e.g., "prayers.fajr")
            default: Default value if translation not found
            
        Returns:
            Translated string
        """
        try:
            # Get language from settings
            language = self.settings.get('language', 'en')
            
            # Navigate through nested keys
            keys = key.split('.')
            value = self.i18n_strings.get(language, {})
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default or key
            
            return value if value else (default or key)
        except Exception as e:
            self.logger.debug(f"Translation lookup failed for '{key}': {e}")
            return default or key
    
    def get_translation(self, key: str, default: str = "") -> str:
        """Alias for get_string for backward compatibility"""
        return self.get_string(key, default)
    
    def show_snackbar(self, message: str, bgcolor: str = None):
        """
        Show a snackbar message.
        
        Args:
            message: Message to display
            bgcolor: Background color (optional)
        """
        try:
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=bgcolor
                )
                self.page.snack_bar = snackbar
                snackbar.open = True
                self.page.update()
        except Exception as e:
            self.logger.error(f"Failed to show snackbar: {e}")
    
    def show_error(self, message: str):
        """Show error message"""
        self.show_snackbar(message, bgcolor=ft.Colors.RED_700)
    
    def show_success(self, message: str):
        """Show success message"""
        self.show_snackbar(message, bgcolor=ft.Colors.GREEN_700)
    
    def show_info(self, message: str):
        """Show info message"""
        self.show_snackbar(message, bgcolor=ft.Colors.BLUE_700)
    
    def show_warning(self, message: str):
        """Show warning message"""
        self.show_snackbar(message, bgcolor=ft.Colors.ORANGE_700)
    
    def show_dialog(self, title: str, content: str, actions: list = None):
        """
        Show a dialog.
        
        Args:
            title: Dialog title
            content: Dialog content text
            actions: List of dialog actions (buttons)
        """
        try:
            if not actions:
                actions = [
                    ft.TextButton("OK", on_click=lambda e: self.close_dialog())
                ]
            
            dialog = ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Text(content),
                actions=actions,
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        except Exception as e:
            self.logger.error(f"Failed to show dialog: {e}")
    
    def close_dialog(self):
        """Close any open dialogs"""
        try:
            if self.page and hasattr(self.page, 'dialog') and self.page.dialog:
                self.page.dialog.open = False
                self.page.update()
        except Exception as e:
            self.logger.error(f"Failed to close dialog: {e}")
    
    def navigate_to(self, route: str):
        """
        Navigate to a different route/view.
        
        Args:
            route: Route path (e.g., 'dashboard', 'settings')
        """
        try:
            if self.on_navigation:
                self.on_navigation(route)
            elif hasattr(self.page, 'go'):
                self.page.go(route)
            else:
                self.logger.warning(f"Cannot navigate to '{route}' - no navigation handler")
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value from storage.
        
        Args:
            key: Setting key (supports nested keys with dots, e.g., 'location.city')
            default: Default value if not found
            
        Returns:
            Setting value
        """
        try:
            # Support nested keys
            keys = key.split('.')
            value = self.settings
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
            
            return value if value is not None else default
        except Exception as e:
            self.logger.error(f"Failed to get setting '{key}': {e}")
            return default
    
    def save_setting(self, key: str, value: Any) -> bool:
        """
        Save a setting value to storage.
        
        Args:
            key: Setting key
            value: Value to save
            
        Returns:
            True if saved successfully
        """
        try:
            # Update local settings
            self.settings[key] = value
            
            # Persist to storage - try multiple methods
            if hasattr(self.storage, 'update_setting'):
                return self.storage.update_setting(key, value)
            elif hasattr(self.storage, 'set'):
                self.storage.set(key, value)
                return True
            else:
                self.logger.warning("Storage service has no update_setting or set method")
                return False
        except Exception as e:
            self.logger.error(f"Failed to save setting '{key}': {e}")
            return False
    
    def refresh(self):
        """
        Refresh the view (can be overridden by subclasses)
        """
        try:
            # Reload settings
            self.settings = self._load_settings()
            
            # Update the view
            self.update()
        except Exception as e:
            self.logger.error(f"Failed to refresh view: {e}")


class ViewContainer(ft.Container):
    """
    Container wrapper for views that need to be used as controls.
    Use this when you need to add a view directly to the page.
    """
    
    def __init__(self, view: BaseView, **kwargs):
        """
        Initialize view container.
        
        Args:
            view: BaseView instance
            **kwargs: Additional Container properties
        """
        self.view = view
        
        # Build the view content
        content = view.build()
        
        # Initialize container with view content
        super().__init__(
            content=content,
            expand=True,
            **kwargs
        )
        
        # Store reference in view
        view.container = self
        
        # Mark view as mounted
        view.did_mount()