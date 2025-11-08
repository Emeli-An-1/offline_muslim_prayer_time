"""Navigation components compatibility shim

This module provides premium/backwards-compatible names for navigation
components by re-exporting implementations from `navigation_rail.py`.
"""

import flet as ft
from typing import List, Dict, Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)

# Import from current package
try:
    from .theme_manager import ThemeManager, Spacing, BorderRadius
except ImportError:
    # Fallback for direct imports
    from theme_manager import ThemeManager, Spacing, BorderRadius


# ============================================================================
# GLASS NAVIGATION BAR (Mobile - Bottom)
# ============================================================================

class GlassNavigationBar(ft.Container):
    """
    Glassmorphism navigation bar for mobile (bottom navigation)
    
    Example:
        destinations = [
            {"icon": ft.icons.HOME_OUTLINED, "selected_icon": ft.icons.HOME, "label": "Home"},
            {"icon": ft.icons.EXPLORE_OUTLINED, "selected_icon": ft.icons.EXPLORE, "label": "Qibla"},
            {"icon": ft.icons.BOOK_OUTLINED, "selected_icon": ft.icons.BOOK, "label": "Dua"},
            {"icon": ft.icons.CIRCLE_OUTLINED, "selected_icon": ft.icons.CIRCLE, "label": "Tasbih"},
            {"icon": ft.icons.SETTINGS_OUTLINED, "selected_icon": ft.icons.SETTINGS, "label": "Settings"}
        ]
        
        nav_bar = GlassNavigationBar(
            destinations=destinations,
            selected_index=0,
            on_change=lambda idx: print(f"Selected: {idx}"),
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        destinations: List[Dict[str, Any]],
        selected_index: int = 0,
        on_change: Optional[Callable[[int], None]] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        self.destinations = destinations
        self.selected_index = selected_index
        self.on_change = on_change
        self.theme = theme_manager
        
        # Create navigation items
        self.nav_items = []
        self._build_nav_items()
        
        # Glass styling
        glass_style = self.theme.get_glassmorphism_style(blur=30, opacity=0.95)
        
        # Main content
        content = ft.Row(
            controls=self.nav_items,
            spacing=0,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        super().__init__(
            content=content,
            bgcolor=glass_style["bgcolor"],
            blur=glass_style["blur"],
            border=ft.border.only(
                top=ft.BorderSide(1, self.theme.get_color("outline_variant"))
            ),
            padding=ft.padding.symmetric(horizontal=Spacing.SM, vertical=Spacing.MD),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color="#00000015",
                offset=ft.Offset(0, -4)
            ),
            **kwargs
        )
    
    def _build_nav_items(self):
        """Build navigation item controls"""
        self.nav_items = []
        
        for idx, dest in enumerate(self.destinations):
            is_selected = idx == self.selected_index
            
            # Get icons
            icon = dest.get("selected_icon" if is_selected else "icon")
            label = dest.get("label", "")
            
            # Create nav item
            item = self._create_nav_item(
                icon=icon,
                label=label,
                is_selected=is_selected,
                index=idx
            )
            
            self.nav_items.append(item)
    
    def _create_nav_item(self, icon: str, label: str, is_selected: bool, index: int) -> ft.Container:
        """Create a single navigation item"""
        
        # Colors based on selection
        if is_selected:
            icon_color = self.theme.get_color("primary")
            text_color = self.theme.get_color("primary")
            text_weight = ft.FontWeight.W_600
            bg_color = f"{self.theme.get_color('primary')}15"
        else:
            icon_color = self.theme.get_color("text_secondary")
            text_color = self.theme.get_color("text_secondary")
            text_weight = ft.FontWeight.NORMAL
            bg_color = "transparent"
        
        # Item content
        item_content = ft.Column(
            controls=[
                ft.Icon(
                    icon,
                    size=24,
                    color=icon_color
                ),
                ft.Text(
                    label,
                    size=11,
                    weight=text_weight,
                    color=text_color
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.XS
        )
        
        return ft.Container(
            content=item_content,
            padding=ft.padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.SM),
            border_radius=BorderRadius.MD,
            bgcolor=bg_color,
            on_click=lambda e: self._handle_click(index),
            ink=True,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            expand=True
        )
    
    def _handle_click(self, index: int):
        """Handle navigation item click"""
        if index != self.selected_index:
            self.selected_index = index
            self._build_nav_items()
            
            # Update controls
            self.content.controls = self.nav_items
            self.update()
            
            # Call callback
            if self.on_change:
                try:
                    self.on_change(index)
                except Exception as e:
                    logger.error(f"Navigation callback error: {e}")
    
    def set_selected_index(self, index: int):
        """Programmatically set selected index"""
        if 0 <= index < len(self.destinations):
            self.selected_index = index
            self._build_nav_items()
            self.content.controls = self.nav_items
            self.update()


# ============================================================================
# GLASS NAVIGATION RAIL (Desktop - Side)
# ============================================================================

class GlassNavigationRail(ft.Container):
    """
    Glassmorphism navigation rail for desktop (side navigation)
    
    Example:
        destinations = [
            {"icon": ft.icons.HOME_OUTLINED, "selected_icon": ft.icons.HOME, "label": "Dashboard"},
            {"icon": ft.icons.EXPLORE_OUTLINED, "selected_icon": ft.icons.EXPLORE, "label": "Qibla"},
            ...
        ]
        
        nav_rail = GlassNavigationRail(
            destinations=destinations,
            selected_index=0,
            on_change=lambda idx: print(f"Selected: {idx}"),
            theme_manager=theme_manager,
            extended=True  # Show labels
        )
    """
    
    def __init__(
        self,
        destinations: List[Dict[str, Any]],
        selected_index: int = 0,
        on_change: Optional[Callable[[int], None]] = None,
        theme_manager: Optional[ThemeManager] = None,
        extended: bool = False,
        width: int = 80,
        extended_width: int = 200,
        **kwargs
    ):
        self.destinations = destinations
        self.selected_index = selected_index
        self.on_change = on_change
        self.theme = theme_manager
        self.extended = extended
        self.width = extended_width if extended else width
        
        # Create navigation items
        self.nav_items = []
        self._build_nav_items()
        
        # Glass styling
        glass_style = self.theme.get_glassmorphism_style(blur=30, opacity=0.95)
        
        # Main content - vertical column
        content = ft.Column(
            controls=self.nav_items,
            spacing=Spacing.SM,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER if not extended else ft.CrossAxisAlignment.START
        )
        
        super().__init__(
            content=content,
            width=self.width,
            bgcolor=glass_style["bgcolor"],
            blur=glass_style["blur"],
            border=ft.border.only(
                right=ft.BorderSide(1, self.theme.get_color("outline_variant"))
            ),
            padding=Spacing.MD,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color="#00000015",
                offset=ft.Offset(4, 0)
            ),
            **kwargs
        )
    
    def _build_nav_items(self):
        """Build navigation rail item controls"""
        self.nav_items = []
        
        for idx, dest in enumerate(self.destinations):
            is_selected = idx == self.selected_index
            
            # Get icons
            icon = dest.get("selected_icon" if is_selected else "icon")
            label = dest.get("label", "")
            
            # Create nav item
            item = self._create_nav_item(
                icon=icon,
                label=label,
                is_selected=is_selected,
                index=idx
            )
            
            self.nav_items.append(item)
    
    def _create_nav_item(self, icon: str, label: str, is_selected: bool, index: int) -> ft.Container:
        """Create a single navigation rail item"""
        
        # Colors based on selection
        if is_selected:
            icon_color = self.theme.get_color("primary")
            text_color = self.theme.get_color("primary")
            text_weight = ft.FontWeight.W_600
            bg_color = f"{self.theme.get_color('primary')}15"
        else:
            icon_color = self.theme.get_color("text_secondary")
            text_color = self.theme.get_color("text_secondary")
            text_weight = ft.FontWeight.NORMAL
            bg_color = "transparent"
        
        # Item content based on extended mode
        if self.extended:
            # Extended: Icon + Label in row
            item_content = ft.Row(
                controls=[
                    ft.Icon(
                        icon,
                        size=24,
                        color=icon_color
                    ),
                    ft.Text(
                        label,
                        size=14,
                        weight=text_weight,
                        color=text_color
                    )
                ],
                spacing=Spacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
            padding = ft.padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.MD)
        else:
            # Compact: Icon + Label in column
            item_content = ft.Column(
                controls=[
                    ft.Icon(
                        icon,
                        size=24,
                        color=icon_color
                    ),
                    ft.Text(
                        label,
                        size=10,
                        weight=text_weight,
                        color=text_color,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.XS
            )
            padding = ft.padding.symmetric(horizontal=Spacing.SM, vertical=Spacing.MD)
        
        return ft.Container(
            content=item_content,
            padding=padding,
            border_radius=BorderRadius.MD,
            bgcolor=bg_color,
            on_click=lambda e: self._handle_click(index),
            ink=True,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            width=self.width - (Spacing.MD * 2)
        )
    
    def _handle_click(self, index: int):
        """Handle navigation item click"""
        if index != self.selected_index:
            self.selected_index = index
            self._build_nav_items()
            
            # Update controls
            self.content.controls = self.nav_items
            self.update()
            
            # Call callback
            if self.on_change:
                try:
                    self.on_change(index)
                except Exception as e:
                    logger.error(f"Navigation callback error: {e}")
    
    def set_selected_index(self, index: int):
        """Programmatically set selected index"""
        if 0 <= index < len(self.destinations):
            self.selected_index = index
            self._build_nav_items()
            self.content.controls = self.nav_items
            self.update()
    
    def toggle_extended(self):
        """Toggle between compact and extended mode"""
        self.extended = not self.extended
        self.width = 200 if self.extended else 80
        self._build_nav_items()
        self.content.controls = self.nav_items
        self.update()


# ============================================================================
# ADAPTIVE NAVIGATION (Auto-switches based on screen size)
# ============================================================================

class AdaptiveNavigation:
    """
    Adaptive navigation that switches between bar and rail based on screen size
    
    Example:
        nav = AdaptiveNavigation(
            destinations=destinations,
            selected_index=0,
            on_change=handle_navigation,
            theme_manager=theme_manager,
            page=page
        )
        
        # Get appropriate navigation component
        nav_component = nav.get_navigation_component()
    """
    
    def __init__(
        self,
        destinations: List[Dict[str, Any]],
        selected_index: int = 0,
        on_change: Optional[Callable[[int], None]] = None,
        theme_manager: Optional[ThemeManager] = None,
        page: Optional[ft.Page] = None,
        mobile_breakpoint: int = 600
    ):
        self.destinations = destinations
        self.selected_index = selected_index
        self.on_change = on_change
        self.theme = theme_manager
        self.page = page
        self.mobile_breakpoint = mobile_breakpoint
        
        self._nav_bar = None
        self._nav_rail = None
    
    def get_navigation_component(self) -> ft.Control:
        """Get appropriate navigation component based on screen size"""
        if self.page and self.page.width:
            is_mobile = self.page.width < self.mobile_breakpoint
        else:
            is_mobile = True  # Default to mobile
        
        if is_mobile:
            return self._get_nav_bar()
        else:
            return self._get_nav_rail()
    
    def _get_nav_bar(self) -> GlassNavigationBar:
        """Get or create navigation bar"""
        if self._nav_bar is None:
            self._nav_bar = GlassNavigationBar(
                destinations=self.destinations,
                selected_index=self.selected_index,
                on_change=self._handle_change,
                theme_manager=self.theme
            )
        return self._nav_bar
    
    def _get_nav_rail(self) -> GlassNavigationRail:
        """Get or create navigation rail"""
        if self._nav_rail is None:
            self._nav_rail = GlassNavigationRail(
                destinations=self.destinations,
                selected_index=self.selected_index,
                on_change=self._handle_change,
                theme_manager=self.theme,
                extended=False
            )
        return self._nav_rail
    
    def _handle_change(self, index: int):
        """Handle navigation change from either component"""
        self.selected_index = index
        
        # Sync both components
        if self._nav_bar:
            self._nav_bar.set_selected_index(index)
        if self._nav_rail:
            self._nav_rail.set_selected_index(index)
        
        # Call user callback
        if self.on_change:
            self.on_change(index)
    
    def set_selected_index(self, index: int):
        """Set selected index on active component"""
        self.selected_index = index
        if self._nav_bar:
            self._nav_bar.set_selected_index(index)
        if self._nav_rail:
            self._nav_rail.set_selected_index(index)


# ============================================================================
# HELPER: Standard App Destinations
# ============================================================================

def get_standard_destinations() -> List[Dict[str, Any]]:
    """
    Get standard PrayerOffline navigation destinations
    
    Returns:
        List of destination dictionaries
    
    Example:
        destinations = get_standard_destinations()
        nav_bar = GlassNavigationBar(
            destinations=destinations,
            ...
        )
    """
    return [
        {
            "icon": ft.Icons.HOME_OUTLINED,
            "selected_icon": ft.Icons.HOME,
            "label": "Dashboard"
        },
        {
            "icon": ft.Icons.EXPLORE_OUTLINED,
            "selected_icon": ft.Icons.EXPLORE,
            "label": "Qibla"
        },
        {
            "icon": ft.Icons.BOOK_OUTLINED,
            "selected_icon": ft.Icons.BOOK,
            "label": "Du'a"
        },
        {
            "icon": ft.Icons.CIRCLE_OUTLINED,
            "selected_icon": ft.Icons.CIRCLE,
            "label": "Tasbih"
        },
        {
            "icon": ft.Icons.SETTINGS_OUTLINED,
            "selected_icon": ft.Icons.SETTINGS,
            "label": "Settings"
        }
    ]


# ============================================================================
# HELPER: Create Responsive Layout
# ============================================================================

def create_responsive_layout(
    content: ft.Control,
    navigation: AdaptiveNavigation,
    page: ft.Page
) -> ft.Control:
    """
    Create responsive layout with adaptive navigation
    
    Args:
        content: Main content area
        navigation: AdaptiveNavigation instance
        page: Flet Page
        
    Returns:
        Complete layout with navigation
    
    Example:
        nav = AdaptiveNavigation(...)
        layout = create_responsive_layout(
            content=main_content,
            navigation=nav,
            page=page
        )
        page.add(layout)
    """
    nav_component = navigation.get_navigation_component()
    
    if page.width and page.width >= 600:
        # Desktop: Side navigation + content
        return ft.Row(
            controls=[
                nav_component,
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=content,
                    expand=True
                )
            ],
            spacing=0,
            expand=True
        )
    else:
        # Mobile: Content + bottom navigation
        return ft.Column(
            controls=[
                ft.Container(
                    content=content,
                    expand=True
                ),
                nav_component
            ],
            spacing=0,
            expand=True
        )


# Backwards-compatible alias: provide a simple NavigationRail name expected by some callers
NavigationRail = GlassNavigationRail

__all__ = [
    "GlassNavigationBar",
    "GlassNavigationRail",
    "NavigationRail",
    "AdaptiveNavigation",
    "get_standard_destinations",
    "create_responsive_layout",
]