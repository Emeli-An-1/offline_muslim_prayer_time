"""
Premium Styled Components for PrayerOffline
Modern, iOS-inspired UI components with glassmorphism and animations

Usage:
    from styled_components import PrayerCard, CountdownWidget, GlassCard
    from theme_manager import get_theme_manager
    
    theme = get_theme_manager()
    
    # Create a prayer card
    card = PrayerCard(
        prayer_name="Fajr",
        adhan_time="05:30",
        jamaat_time="05:45",
        is_next=True,
        theme_manager=theme
    )
"""

import flet as ft
from typing import Optional, Callable, List, Any, Dict
import logging

logger = logging.getLogger(__name__)

# Import from current package
try:
    from .theme_manager import ThemeManager, Spacing, BorderRadius
except ImportError:
    # Fallback for direct imports
    from theme_manager import ThemeManager, Spacing, BorderRadius


# ============================================================================
# PRAYER CARD - Premium prayer time card with gradient
# ============================================================================

class PrayerCard(ft.Container):
    """
    Premium prayer time card with gradient and glow effects
    
    Example:
        card = PrayerCard(
            prayer_name="Fajr",
            adhan_time="05:30",
            jamaat_time="05:45",
            is_next=True,
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        prayer_name: str,
        adhan_time: str,
        jamaat_time: Optional[str] = None,
        is_next: bool = False,
        is_current: bool = False,
        theme_manager: Optional[ThemeManager] = None,
        on_click: Optional[Callable] = None,
        show_icon: bool = True,
        **kwargs
    ):
        # Prayer icons mapping
        self.prayer_icons = {
            "Fajr": ft.Icons.BRIGHTNESS_5,
            "Sunrise": ft.Icons.WB_SUNNY,
            "Dhuhr": ft.Icons.WB_SUNNY_OUTLINED,
            "Asr": ft.Icons.BRIGHTNESS_6,
            "Maghrib": ft.Icons.BRIGHTNESS_3,
            "Isha": ft.Icons.BRIGHTNESS_2
        }
        
        theme = theme_manager
        icon = self.prayer_icons.get(prayer_name, ft.Icons.ACCESS_TIME)
        
        # Build card content
        controls = []
        
        # Icon (optional)
        if show_icon:
            icon_container = ft.Container(
                content=ft.Icon(
                    icon,
                    size=28,
                    color=theme.get_color("primary") if is_next else theme.get_color("text")
                ),
                width=44,
                height=44,
                border_radius=BorderRadius.MD,
                bgcolor=f"{theme.get_color('primary')}15" if is_next else theme.get_color("surface_variant"),
                alignment=ft.alignment.center
            )
            controls.append(icon_container)
        
        # Prayer info column
        prayer_info = ft.Column(
            controls=[
                ft.Text(
                    prayer_name,
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=theme.get_color("text")
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            adhan_time,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=theme.get_color("primary") if is_next else theme.get_color("text")
                        ),
                        ft.Text(
                            f"• {jamaat_time}" if jamaat_time else "",
                            size=14,
                            color=theme.get_color("text_secondary"),
                            visible=bool(jamaat_time)
                        ),
                    ],
                    spacing=Spacing.SM
                )
            ],
            spacing=Spacing.XS,
            expand=True
        )
        controls.append(prayer_info)
        
        # Next indicator
        if is_next:
            controls.append(
                ft.Icon(
                    ft.Icons.ARROW_FORWARD_IOS_ROUNDED,
                    size=16,
                    color=theme.get_color("primary")
                )
            )
        
        card_content = ft.Row(
            controls=controls,
            spacing=Spacing.MD,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        # Styling based on state
        if is_next or is_current:
            # Highlighted card with gradient
            bgcolor = None
            gradient = theme.get_gradient(prayer_name)
            shadow = theme.get_shadow(elevation=3)
            border = ft.border.all(2, theme.get_color("primary"))
        else:
            # Normal card
            bgcolor = theme.get_color("surface")
            gradient = None
            shadow = theme.get_shadow(elevation=1)
            border = ft.border.all(1, theme.get_color("outline_variant"))
        
        super().__init__(
            content=card_content,
            bgcolor=bgcolor,
            gradient=gradient,
            border=border,
            border_radius=BorderRadius.LG,
            padding=Spacing.MD,
            shadow=shadow,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            on_click=on_click,
            ink=True,
            **kwargs
        )


# ============================================================================
# COUNTDOWN WIDGET - Circular countdown with progress ring
# ============================================================================

class CountdownWidget(ft.Container):
    """
    Circular countdown widget with animated progress ring
    
    Example:
        countdown = CountdownWidget(
            next_prayer="Dhuhr",
            time_remaining="02:15:30",
            progress=0.65,
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        next_prayer: str,
        time_remaining: str,
        progress: float = 0.0,
        size: int = 200,
        theme_manager: Optional[ThemeManager] = None,
        show_label: bool = True,
        **kwargs
    ):
        theme = theme_manager
        
        # Progress ring
        progress_ring = ft.ProgressRing(
            value=max(0.0, min(1.0, progress)),
            width=size,
            height=size,
            stroke_width=10,
            color=theme.get_color("primary"),
            bgcolor=f"{theme.get_color('primary')}20"
        )
        
        # Time display overlay
        time_controls = [
            ft.Text(
                time_remaining,
                size=36,
                weight=ft.FontWeight.BOLD,
                color=theme.get_color("primary"),
                text_align=ft.TextAlign.CENTER
            )
        ]
        
        if show_label:
            time_controls.insert(0, ft.Text(
                f"Next: {next_prayer}",
                size=14,
                weight=ft.FontWeight.W_500,
                color=theme.get_color("text_secondary"),
                text_align=ft.TextAlign.CENTER
            ))
            time_controls.append(ft.Text(
                "remaining",
                size=12,
                color=theme.get_color("text_secondary"),
                text_align=ft.TextAlign.CENTER
            ))
        
        time_overlay = ft.Column(
            controls=time_controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.XS
        )
        
        # Stack progress ring with time
        content = ft.Stack(
            controls=[
                ft.Container(
                    content=progress_ring,
                    alignment=ft.alignment.center
                ),
                ft.Container(
                    content=time_overlay,
                    width=size,
                    height=size,
                    alignment=ft.alignment.center
                )
            ],
            width=size,
            height=size
        )
        
        super().__init__(
            content=content,
            alignment=ft.alignment.center,
            **kwargs
        )


# ============================================================================
# GLASS CARD - Glassmorphism container
# ============================================================================

class GlassCard(ft.Container):
    """
    Glassmorphism card with blur effect
    
    Example:
        card = GlassCard(
            content=ft.Text("Content"),
            theme_manager=theme_manager,
            blur=25,
            padding=20
        )
    """
    
    def __init__(
        self,
        content: ft.Control,
        theme_manager: Optional[ThemeManager] = None,
        blur: int = 20,
        opacity: float = 0.9,
        padding: int = Spacing.MD,
        elevation: int = 2,
        **kwargs
    ):
        theme = theme_manager
        glass_style = theme.get_glassmorphism_style(blur=blur, opacity=opacity)
        
        super().__init__(
            content=content,
            bgcolor=glass_style["bgcolor"],
            blur=glass_style["blur"],
            border=glass_style["border"],
            border_radius=glass_style["border_radius"],
            padding=padding,
            shadow=theme.get_shadow(elevation=elevation),
            **kwargs
        )


# ============================================================================
# GRADIENT BUTTON - Premium button with gradient
# ============================================================================

class GradientButton(ft.Container):
    """
    Premium gradient button with hover effects
    
    Example:
        button = GradientButton(
            text="Save",
            icon=ft.Icons.SAVE,
            on_click=lambda e: print("Clicked"),
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        text: str,
        icon: Optional[str] = None,
        on_click: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        variant: str = "primary",  # "primary", "secondary", "outlined"
        expand: bool = False,
        width: Optional[int] = None,
        **kwargs
    ):
        theme = theme_manager
        
        # Build button content
        controls = []
        
        if variant == "outlined":
            text_color = theme.get_color("primary")
            icon_color = theme.get_color("primary")
        else:
            text_color = "#FFFFFF"
            icon_color = "#FFFFFF"
        
        if icon:
            controls.append(
                ft.Icon(icon, size=20, color=icon_color)
            )
        
        controls.append(
            ft.Text(
                text,
                size=16,
                weight=ft.FontWeight.W_600,
                color=text_color
            )
        )
        
        button_content = ft.Row(
            controls=controls,
            spacing=Spacing.SM,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True
        )
        
        # Styling based on variant
        if variant == "primary":
            bgcolor = None
            gradient = theme.get_gradient()
            border = None
        elif variant == "secondary":
            bgcolor = theme.get_color("surface_variant")
            gradient = None
            border = None
        else:  # outlined
            bgcolor = None
            gradient = None
            border = ft.border.all(2, theme.get_color("primary"))
        
        super().__init__(
            content=button_content,
            bgcolor=bgcolor,
            gradient=gradient,
            border=border,
            border_radius=BorderRadius.LG,
            padding=ft.padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
            shadow=theme.get_shadow(elevation=2) if variant != "outlined" else None,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_click=on_click,
            ink=True,
            expand=expand,
            width=width,
            **kwargs
        )


# ============================================================================
# SECTION HEADER - Styled section header
# ============================================================================

class SectionHeader(ft.Container):
    """
    Section header with optional action button
    
    Example:
        header = SectionHeader(
            title="Prayer Times",
            subtitle="Today's schedule",
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        title: str,
        subtitle: Optional[str] = None,
        action_icon: Optional[str] = None,
        on_action: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        theme = theme_manager
        
        # Title and subtitle
        title_column = ft.Column(
            controls=[
                ft.Text(
                    title,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=theme.get_color("text")
                ),
                ft.Text(
                    subtitle,
                    size=14,
                    color=theme.get_color("text_secondary")
                ) if subtitle else ft.Container()
            ],
            spacing=Spacing.XS,
            expand=True
        )
        
        # Action button (optional)
        controls = [title_column]
        
        if action_icon and on_action:
            action_btn = ft.IconButton(
                icon=action_icon,
                icon_size=24,
                icon_color=theme.get_color("primary"),
                on_click=on_action
            )
            controls.append(action_btn)
        
        content = ft.Row(
            controls=controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START
        )
        
        super().__init__(
            content=content,
            padding=ft.padding.only(
                left=Spacing.MD,
                right=Spacing.MD,
                top=Spacing.LG,
                bottom=Spacing.SM
            ),
            **kwargs
        )


# ============================================================================
# INFO CARD - Simple info display card
# ============================================================================

class InfoCard(ft.Container):
    """
    Simple info display card
    
    Example:
        card = InfoCard(
                icon=ft.Icons.LOCATION_ON,
            title="Location",
            value="New York, USA",
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        icon: str,
        title: str,
        value: str,
        theme_manager: Optional[ThemeManager] = None,
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        theme = theme_manager
        
        content = ft.Row(
            controls=[
                ft.Icon(
                    icon,
                    size=24,
                    color=theme.get_color("primary")
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            title,
                            size=12,
                            color=theme.get_color("text_secondary")
                        ),
                        ft.Text(
                            value,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=theme.get_color("text")
                        )
                    ],
                    spacing=Spacing.XS,
                    expand=True
                )
            ],
            spacing=Spacing.MD
        )
        
        super().__init__(
            content=content,
            bgcolor=theme.get_color("surface_variant"),
            border_radius=BorderRadius.MD,
            padding=Spacing.MD,
            on_click=on_click,
            ink=True if on_click else False,
            **kwargs
        )


# ============================================================================
# STAT CARD - Statistics display card
# ============================================================================

class StatCard(ft.Container):
    """
    Statistics display card with icon
    
    Example:
        card = StatCard(
            icon=ft.Icons.CIRCLE,
            label="Total Count",
            value="1,234",
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        icon: str,
        label: str,
        value: str,
        theme_manager: Optional[ThemeManager] = None,
        gradient_bg: bool = False,
        **kwargs
    ):
        theme = theme_manager
        
        content = ft.Column(
            controls=[
                ft.Icon(
                    icon,
                    size=32,
                    color="#FFFFFF" if gradient_bg else theme.get_color("primary")
                ),
                ft.Text(
                    value,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF" if gradient_bg else theme.get_color("text")
                ),
                ft.Text(
                    label,
                    size=12,
                    color="#FFFFFFCC" if gradient_bg else theme.get_color("text_secondary")
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.SM
        )
        
        if gradient_bg:
            bgcolor = None
            gradient = theme.get_gradient()
        else:
            bgcolor = theme.get_color("surface")
            gradient = None
        
        super().__init__(
            content=content,
            bgcolor=bgcolor,
            gradient=gradient,
            border_radius=BorderRadius.LG,
            padding=Spacing.LG,
            shadow=theme.get_shadow(elevation=2),
            **kwargs
        )


# ============================================================================
# TOGGLE CARD - Card with toggle switch
# ============================================================================

class ToggleCard(ft.Container):
    """
    Card with toggle switch for settings
    
    Example:
        card = ToggleCard(
            icon=ft.Icons.NOTIFICATIONS,
            title="Notifications",
            subtitle="Enable prayer notifications",
            value=True,
            on_change=lambda e: print(e.control.value),
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        icon: str,
        title: str,
        subtitle: Optional[str] = None,
        value: bool = False,
        on_change: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        theme = theme_manager
        
        # Icon
        icon_container = ft.Container(
            content=ft.Icon(icon, size=24, color=theme.get_color("primary")),
            width=40,
            height=40,
            bgcolor=f"{theme.get_color('primary')}15",
            border_radius=BorderRadius.SM,
            alignment=ft.alignment.center
        )
        
        # Text column
        text_controls = [
            ft.Text(
                title,
                size=16,
                weight=ft.FontWeight.W_600,
                color=theme.get_color("text")
            )
        ]
        
        if subtitle:
            text_controls.append(
                ft.Text(
                    subtitle,
                    size=12,
                    color=theme.get_color("text_secondary")
                )
            )
        
        text_column = ft.Column(
            controls=text_controls,
            spacing=Spacing.XS,
            expand=True
        )
        
        # Toggle switch
        toggle = ft.Switch(
            value=value,
            active_color=theme.get_color("primary"),
            on_change=on_change
        )
        
        content = ft.Row(
            controls=[
                icon_container,
                text_column,
                toggle
            ],
            spacing=Spacing.MD,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        super().__init__(
            content=content,
            bgcolor=theme.get_color("surface"),
            border=ft.border.all(1, theme.get_color("outline_variant")),
            border_radius=BorderRadius.MD,
            padding=Spacing.MD,
            **kwargs
        )


# ============================================================================
# EMPTY STATE - Empty state display
# ============================================================================

class EmptyState(ft.Container):
    """
    Empty state display with icon and message
    
    Example:
        empty = EmptyState(
            icon=ft.Icons.INBOX,
            title="No data yet",
            message="Start by adding some content",
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        icon: str,
        title: str,
        message: Optional[str] = None,
        action_text: Optional[str] = None,
        on_action: Optional[Callable] = None,
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        theme = theme_manager
        
        controls = [
            ft.Icon(
                icon,
                size=64,
                color=theme.get_color("text_secondary")
            ),
            ft.Text(
                title,
                size=18,
                weight=ft.FontWeight.BOLD,
                color=theme.get_color("text"),
                text_align=ft.TextAlign.CENTER
            )
        ]
        
        if message:
            controls.append(
                ft.Text(
                    message,
                    size=14,
                    color=theme.get_color("text_secondary"),
                    text_align=ft.TextAlign.CENTER
                )
            )
        
        if action_text and on_action:
            controls.append(
                ft.ElevatedButton(
                    text=action_text,
                    on_click=on_action
                )
            )
        
        content = ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.MD
        )
        
        super().__init__(
            content=content,
            alignment=ft.alignment.center,
            padding=Spacing.XXL,
            **kwargs
        )


# ============================================================================
# LOADING INDICATOR - Custom loading indicator
# ============================================================================

class LoadingIndicator(ft.Container):
    """
    Custom loading indicator
    
    Example:
        loading = LoadingIndicator(
            message="Loading prayer times...",
            theme_manager=theme_manager
        )
    """
    
    def __init__(
        self,
        message: str = "Loading...",
        theme_manager: Optional[ThemeManager] = None,
        **kwargs
    ):
        theme = theme_manager
        
        content = ft.Column(
            controls=[
                ft.ProgressRing(
                    width=48,
                    height=48,
                    color=theme.get_color("primary")
                ),
                ft.Text(
                    message,
                    size=14,
                    color=theme.get_color("text_secondary"),
                    text_align=ft.TextAlign.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.MD
        )
        
        super().__init__(
            content=content,
            alignment=ft.alignment.center,
            padding=Spacing.XXL,
            **kwargs
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_divider(theme_manager: ThemeManager, thickness: int = 1) -> ft.Divider:
    """Create a themed divider"""
    return ft.Divider(
        height=thickness,
        color=theme_manager.get_color("outline_variant")
    )


def create_spacer(height: int = Spacing.MD) -> ft.Container:
    """Create a vertical spacer"""
    return ft.Container(height=height)