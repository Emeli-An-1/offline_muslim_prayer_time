"""
Views Package - Contains all application view implementations

This package organizes all UI views for the PrayerOffline application:
- Dashboard: Main prayer time display with real-time countdown
- Qibla: Compass and direction to Kaaba
- Settings: Comprehensive app configuration
- Dua: Supplications library with search and bookmarks
- Tasbih: Islamic counter with statistics
"""

import logging
from typing import Type, Dict, Optional, Any

# Import all view classes
from .base_view import BaseView, SnackBarType
from .dashboard_view import DashboardView
from .qibla_view import QiblaView
from .settings_view import SettingsView
from .dua_view import DuaView
from .tasbih_view import TasbihView

# Configure package logger
logger = logging.getLogger(__name__)

# Public API exports
__all__ = [
    "BaseView",
    "SnackBarType",
    "DashboardView",
    "QiblaView",
    "SettingsView",
    "DuaView",
    "TasbihView",
    "ViewRegistry",
    "get_view_class",
    "create_view"
]

# Version for package
__version__ = "1.0.0"


class ViewRegistry:
    """
    Registry for all available views in the application
    Enables dynamic view creation and management
    """
    
    _registry: Dict[str, Type[BaseView]] = {
        "dashboard": DashboardView,
        "qibla": QiblaView,
        "settings": SettingsView,
        "dua": DuaView,
        "tasbih": TasbihView
    }
    
    @classmethod
    def register(cls, name: str, view_class: Type[BaseView]) -> None:
        """
        Register a new view class
        
        Args:
            name: Unique view identifier
            view_class: View class (must extend BaseView)
            
        Raises:
            TypeError: If view_class doesn't extend BaseView
            ValueError: If name already registered
        """
        if not issubclass(view_class, BaseView):
            raise TypeError(f"{view_class} must extend BaseView")
        
        if name in cls._registry:
            logger.warning(f"View '{name}' already registered, overwriting")
        
        cls._registry[name] = view_class
        logger.info(f"View registered: {name} -> {view_class.__name__}")
    
    @classmethod
    def unregister(cls, name: str) -> bool:
        """
        Unregister a view class
        
        Args:
            name: View identifier to remove
            
        Returns:
            True if view was registered and removed, False otherwise
        """
        if name in cls._registry:
            del cls._registry[name]
            logger.info(f"View unregistered: {name}")
            return True
        return False
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseView]]:
        """
        Get view class by name
        
        Args:
            name: View identifier
            
        Returns:
            View class or None if not found
        """
        return cls._registry.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, Type[BaseView]]:
        """
        Get all registered views
        
        Returns:
            Dictionary of view_name -> view_class
        """
        return cls._registry.copy()
    
    @classmethod
    def list_views(cls) -> list:
        """
        List all available view names
        
        Returns:
            List of registered view names
        """
        return list(cls._registry.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if view is registered
        
        Args:
            name: View identifier
            
        Returns:
            True if view is registered
        """
        return name in cls._registry


def get_view_class(view_name: str) -> Optional[Type[BaseView]]:
    """
    Get view class by name using registry
    
    Args:
        view_name: View identifier (e.g., "dashboard", "settings")
        
    Returns:
        View class or None if not found
        
    Example:
        DashboardView = get_view_class("dashboard")
    """
    view_class = ViewRegistry.get(view_name)
    if not view_class:
        logger.error(f"View not found: {view_name}")
        logger.debug(f"Available views: {ViewRegistry.list_views()}")
    return view_class


def create_view(
    view_name: str,
    page: Any,
    storage_service: Any,
    location_service: Optional[Any] = None,
    audio_service: Optional[Any] = None,
    on_navigation: Optional[Any] = None,
    **kwargs
) -> Optional[BaseView]:
    """
    Factory function to create view instances
    
    Args:
        view_name: View identifier (e.g., "dashboard", "settings")
        page: Flet page instance
        storage_service: Storage service for persistence
        location_service: Optional location service
        audio_service: Optional audio service
        on_navigation: Optional navigation callback
        **kwargs: Additional view-specific arguments
        
    Returns:
        View instance or None if view not found
        
    Raises:
        Exception: If view creation fails
        
    Example:
        dashboard = create_view(
            "dashboard",
            page=page,
            storage_service=storage,
            on_navigation=handle_navigation
        )
    """
    try:
        view_class = ViewRegistry.get(view_name)
        
        if not view_class:
            logger.error(f"Cannot create view '{view_name}': not registered")
            return None
        
        # Create view instance with provided services
        view = view_class(
            page=page,
            storage_service=storage_service,
            location_service=location_service,
            audio_service=audio_service,
            on_navigation=on_navigation,
            **kwargs
        )
        
        logger.info(f"View created successfully: {view_name}")
        return view
    
    except TypeError as e:
        logger.error(f"View creation failed - invalid arguments: {e}")
        raise
    except Exception as e:
        logger.error(f"View creation failed for '{view_name}': {e}")
        raise


# Initialize logging for views package
def setup_logging(level=logging.INFO):
    """
    Setup logging for views package
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


# Log package initialization
logger.info(f"Views package initialized (v{__version__})")
logger.debug(f"Available views: {ViewRegistry.list_views()}")