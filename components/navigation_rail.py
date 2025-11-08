"""
Adaptive Navigation Component for PrayerOffline App
Provides NavigationRail for desktop and NavigationBar for mobile
"""

import flet as ft
from typing import Callable, List, Optional, Dict


class AppNavigationRail:
    """
    Adaptive navigation component that switches between NavigationRail (desktop)
    and NavigationBar (mobile) based on screen width.
    """
    
    def __init__(
        self,
        selected_index: int = 0,
        on_change: Optional[Callable] = None,
        destinations: Optional[List[Dict]] = None
    ):
        """
        Initialize the navigation component.
        
        Args:
            selected_index: Initially selected destination index
            on_change: Callback function when selection changes
            destinations: List of navigation destinations
        """
        self.selected_index = selected_index
        self.on_change = on_change
        self._destinations = destinations or self._default_destinations()
        self.current_component = None
        self.is_mobile = False
    
    def _default_destinations(self) -> List[Dict]:
        """Default navigation destinations"""
        return [
            {"icon": ft.Icons.HOME, "label": "Dashboard"},
            {"icon": ft.Icons.EXPLORE, "label": "Qibla"},
            {"icon": ft.Icons.BOOK, "label": "Du'ā"},
            {"icon": ft.Icons.CIRCLE_OUTLINED, "label": "Tasbih"},
            {"icon": ft.Icons.SETTINGS, "label": "Settings"},
        ]
    
    def build(self, page_width: int) -> ft.Control:
        """
        Build the appropriate navigation component based on screen width.
        
        Args:
            page_width: Current page width in pixels
            
        Returns:
            NavigationRail or NavigationBar based on screen size
        """
        self.is_mobile = page_width < 600
        
        if self.is_mobile:
            return self._build_navigation_bar()
        else:
            return self._build_navigation_rail()
    
    def _build_navigation_rail(self) -> ft.NavigationRail:
        """Build NavigationRail for desktop/tablet"""
        destinations = [
            ft.NavigationRailDestination(
                icon=dest["icon"],
                label=dest["label"]
            )
            for dest in self._destinations
        ]
        
        self.current_component = ft.NavigationRail(
            selected_index=self.selected_index,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=destinations,
            on_change=self._handle_change,
        )
        
        return self.current_component
    
    def _build_navigation_bar(self) -> ft.NavigationBar:
        """Build NavigationBar for mobile"""
        destinations = [
            ft.NavigationBarDestination(
                icon=dest["icon"],
                label=dest["label"]
            )
            for dest in self._destinations
        ]
        
        self.current_component = ft.NavigationBar(
            selected_index=self.selected_index,
            destinations=destinations,
            on_change=self._handle_change,
        )
        
        return self.current_component
    
    def _handle_change(self, e):
        """Handle navigation selection change"""
        self.selected_index = e.control.selected_index
        
        if self.on_change:
            self.on_change(e)
    
    def update_selected_index(self, index: int):
        """Update the selected index"""
        self.selected_index = index
        
        if self.current_component:
            self.current_component.selected_index = index
            if hasattr(self.current_component, 'update'):
                self.current_component.update()
    
    def get_selected_index(self) -> int:
        """Get current selected index"""
        return self.selected_index
    
    def get_selected_destination(self) -> Dict:
        """Get currently selected destination info"""
        if 0 <= self.selected_index < len(self._destinations):
            return self._destinations[self.selected_index]
        return self._destinations[0]


def create_navigation_rail(
    selected_index: int = 0,
    on_change: Optional[Callable] = None,
    page_width: int = 800
) -> ft.Control:
    """
    Helper function to create a navigation component.
    
    Args:
        selected_index: Initially selected index
        on_change: Change callback
        page_width: Current page width
        
    Returns:
        Navigation component (Rail or Bar)
    """
    nav = AppNavigationRail(selected_index, on_change)
    return nav.build(page_width)


def get_navigation_destinations() -> List[Dict]:
    """
    Get list of navigation destinations with icons and labels.
    
    Returns:
        List of destination dictionaries
    """
    return [
        {"icon": ft.Icons.HOME, "label": "Dashboard", "route": "/"},
        {"icon": ft.Icons.EXPLORE, "label": "Qibla", "route": "/qibla"},
        {"icon": ft.Icons.BOOK, "label": "Du'ā", "route": "/dua"},
        {"icon": ft.Icons.CIRCLE_OUTLINED, "label": "Tasbih", "route": "/tasbih"},
        {"icon": ft.Icons.SETTINGS, "label": "Settings", "route": "/settings"},
    ]