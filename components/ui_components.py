"""
Premium iOS-Inspired UI Components
Glassmorphism, Neumorphism, and Animated Components
"""

import flet as ft
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

# Import from current package
try:
    from .theme_manager import get_theme_manager
except ImportError:
    from theme_manager import get_theme_manager


class GlassCard(ft.Container):
    """Glassmorphism card with blur effect"""
    
    def __init__(
        self,
        content: Optional[ft.Control] = None,
        padding: int = 20,
        border_radius: int = 24,
        blur: int = 20,
        opacity: float = 0.8,
        width: Optional[int] = None,
        height: Optional[int] = None,
        elevation: int = 1,
        animate_scale: bool = False,
        **kwargs
    ):
        theme = get_theme_manager()
        
        super().__init__(
            content=content,
            padding=padding,
            border_radius=border_radius,
            bgcolor=f"{theme.get_color('surface')}CC",  # Semi-transparent
            border=ft.border.all(1, f"{theme.get_color('text')}10"),
            shadow=theme.get_shadow(elevation),
            width=width,
            height=height,
            blur=(blur, blur) if blur else None,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT) if animate_scale else None,
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT) if animate_scale else None,
            **kwargs
        )


class NeumorphicButton(ft.Container):
    """Neumorphic style button with depth effect"""
    
    def __init__(
        self,
        text: str = "",
        icon: Optional[str] = None,
        on_click: Optional[Callable] = None,
        width: int = 120,
        height: int = 50,
        primary: bool = False,
        **kwargs
    ):
        theme = get_theme_manager()
        
        # Button content
        content_list = []
        if icon:
            content_list.append(ft.Icon(icon, size=20, color=theme.get_color("primary" if primary else "text")))
        if text:
            content_list.append(
                ft.Text(
                    text,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=theme.get_color("primary" if primary else "text"),
                )
            )
        
        button_content = ft.Row(
            controls=content_list,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )
        
        super().__init__(
            content=button_content,
            width=width,
            height=height,
            border_radius=16,
            bgcolor=theme.get_color("surface"),
            shadow=theme.get_shadow(2),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            on_click=on_click,
            ink=True,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
            **kwargs
        )
        
        # Add hover effect
        self.scale = 1.0
    
    def _on_hover(self, e):
        """Handle hover animation"""
        self.scale = 1.05 if e.data == "true" else 1.0
        self.update()


class AnimatedIconButton(ft.Container):
    """Icon button with smooth animations"""
    
    def __init__(
        self,
        icon: str,
        on_click: Optional[Callable] = None,
        size: int = 50,
        icon_size: int = 24,
        tooltip: str = "",
        selected: bool = False,
        **kwargs
    ):
        theme = get_theme_manager()
        
        self.icon_control = ft.Icon(
            icon,
            size=icon_size,
            color=theme.get_color("primary" if selected else "text"),
        )
        
        super().__init__(
            content=self.icon_control,
            width=size,
            height=size,
            border_radius=size // 2,
            bgcolor=theme.get_color("primary") + "20" if selected else "transparent",
            on_click=on_click,
            ink=True,
            tooltip=tooltip,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(100, ft.AnimationCurve.BOUNCE_OUT),
            **kwargs
        )


class GradientText(ft.Container):
    """Text with gradient color effect"""
    
    def __init__(
        self,
        text: str,
        size: int = 24,
        weight: ft.FontWeight = ft.FontWeight.BOLD,
        gradient_colors: Optional[list] = None,
        **kwargs
    ):
        theme = get_theme_manager()
        
        if gradient_colors is None:
            gradient_colors = [theme.get_color("primary"), theme.get_color("accent")]
        
        text_control = ft.Text(
            text,
            size=size,
            weight=weight,
            color="transparent",  # Will be overridden by gradient
        )
        
        super().__init__(
            content=text_control,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=gradient_colors,
            ),
            **kwargs
        )


class ThemePreviewTile(ft.Container):
    """Theme preview tile for settings"""
    
    def __init__(
        self,
        theme_name: str,
        on_select: Optional[Callable] = None,
        selected: bool = False,
        **kwargs
    ):
        try:
            from .theme_manager import THEMES
        except ImportError:
            from theme_manager import THEMES
        
        theme_data = THEMES.get(theme_name, {})
        
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Container(
                        bgcolor=theme_data.get("bg", "#FFFFFF"),
                        height=60,
                        border_radius=12,
                        padding=10,
                        content=ft.Column(
                            controls=[
                                ft.Container(
                                    bgcolor=theme_data.get("primary", "#000000"),
                                    height=8,
                                    border_radius=4,
                                    width=40,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            bgcolor=theme_data.get("surface", "#FFFFFF"),
                                            height=20,
                                            width=20,
                                            border_radius=10,
                                        ),
                                        ft.Container(
                                            bgcolor=theme_data.get("accent", "#000000"),
                                            height=8,
                                            width=30,
                                            border_radius=4,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                            ],
                            spacing=8,
                        ),
                    ),
                    ft.Text(
                        theme_name,
                        size=12,
                        weight=ft.FontWeight.W_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=100,
            padding=10,
            border_radius=16,
            border=ft.border.all(2, theme_data.get("primary", "#000000") if selected else "transparent"),
            bgcolor=theme_data.get("surface", "#FFFFFF") + "40" if selected else "transparent",
            on_click=on_select,
            ink=True,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            **kwargs
        )


class ProgressRingWithText(ft.Stack):
    """Circular progress ring with centered text"""
    
    def __init__(
        self,
        progress: float = 0.0,
        size: int = 120,
        stroke_width: int = 8,
        text: str = "",
        text_size: int = 32,
        **kwargs
    ):
        theme = get_theme_manager()
        
        self.ring = ft.ProgressRing(
            value=progress,
            width=size,
            height=size,
            stroke_width=stroke_width,
            color=theme.get_color("primary"),
        )
        
        self.text_control = ft.Text(
            text,
            size=text_size,
            weight=ft.FontWeight.BOLD,
            color=theme.get_color("text"),
            text_align=ft.TextAlign.CENTER,
        )
        
        super().__init__(
            controls=[
                self.ring,
                ft.Container(
                    content=self.text_control,
                    alignment=ft.alignment.center,
                    width=size,
                    height=size,
                ),
            ],
            width=size,
            height=size,
            **kwargs
        )
    
    def update_progress(self, progress: float, text: str = None):
        """Update progress and text"""
        self.ring.value = progress
        if text is not None:
            self.text_control.value = text


class PrayerTimeCard(GlassCard):
    """Specialized card for prayer times with breathing animation"""
    
    def __init__(
        self,
        prayer_name: str,
        adhan_time: str,
        jamaat_time: Optional[str] = None,
        is_next: bool = False,
        icon: Optional[str] = None,
        **kwargs
    ):
        theme = get_theme_manager()
        
        # Prayer icon
        prayer_icons = {
            "Fajr": ft.Icons.BRIGHTNESS_5,
            "Sunrise": ft.Icons.WB_SUNNY,
            "Dhuhr": ft.Icons.WB_SUNNY_OUTLINED,
            "Asr": ft.Icons.BRIGHTNESS_6,
            "Maghrib": ft.Icons.BRIGHTNESS_3,
            "Isha": ft.Icons.BRIGHTNESS_2,
        }
        
        icon_name = icon or prayer_icons.get(prayer_name, ft.Icons.ACCESS_TIME)
        
        # Time display
        time_column = ft.Column(
            controls=[
                ft.Text(
                    prayer_name,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=theme.get_color("text"),
                ),
                ft.Text(
                    f"Adhan: {adhan_time}",
                    size=18,
                    weight=ft.FontWeight.W_500,
                    color=theme.get_color("primary" if is_next else "text"),
                ),
            ],
            spacing=4,
        )
        
        if jamaat_time:
            time_column.controls.append(
                ft.Text(
                    f"Jamaat: {jamaat_time}",
                    size=14,
                    color=theme.get_color("text_secondary"),
                )
            )
        
        content = ft.Row(
            controls=[
                ft.Icon(
                    icon_name,
                    size=40,
                    color=theme.get_color("primary" if is_next else "accent"),
                ),
                time_column,
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.START,
        )
        
        super().__init__(
            content=content,
            padding=16,
            border_radius=20,
            elevation=2 if is_next else 1,
            animate_scale=is_next,
            blur=25 if is_next else 20,
            **kwargs
        )
        
        # Add pulsing animation for next prayer
        if is_next:
            self.animate_opacity = ft.Animation(2000, ft.AnimationCurve.EASE_IN_OUT)


class FloatingActionButton(ft.Container):
    """iOS-style floating action button"""
    
    def __init__(
        self,
        icon: str,
        on_click: Optional[Callable] = None,
        size: int = 56,
        tooltip: str = "",
        **kwargs
    ):
        theme = get_theme_manager()
        
        super().__init__(
            content=ft.Icon(icon, size=28, color="#FFFFFF"),
            width=size,
            height=size,
            border_radius=size // 2,
            bgcolor=theme.get_color("primary"),
            shadow=theme.get_shadow(3),
            on_click=on_click,
            ink=True,
            tooltip=tooltip,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(150, ft.AnimationCurve.BOUNCE_OUT),
            **kwargs
        )


class SegmentedControl(ft.Container):
    """iOS-style segmented control"""
    
    def __init__(
        self,
        options: list,
        selected_index: int = 0,
        on_change: Optional[Callable] = None,
        **kwargs
    ):
        theme = get_theme_manager()
        self.on_change = on_change
        self.selected_index = selected_index
        
        self.buttons = []
        for idx, option in enumerate(options):
            btn = ft.Container(
                content=ft.Text(
                    option,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=theme.get_color("text") if idx == selected_index else theme.get_color("text_secondary"),
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                border_radius=12,
                bgcolor=theme.get_color("surface") if idx == selected_index else "transparent",
                on_click=lambda e, i=idx: self._on_select(i),
                ink=True,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            )
            self.buttons.append(btn)
        
        super().__init__(
            content=ft.Row(controls=self.buttons, spacing=4, tight=True),
            padding=4,
            border_radius=14,
            bgcolor=theme.get_color("bg"),
            border=ft.border.all(1, theme.get_color("text") + "10"),
            **kwargs
        )
    
    def _on_select(self, index: int):
        """Handle selection change"""
        theme = get_theme_manager()
        self.selected_index = index
        
        for idx, btn in enumerate(self.buttons):
            is_selected = idx == index
            btn.bgcolor = theme.get_color("surface") if is_selected else "transparent"
            btn.content.color = theme.get_color("text") if is_selected else theme.get_color("text_secondary")
            btn.content.weight = ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL
        
        if self.on_change:
            self.on_change(index)
        
        self.update()