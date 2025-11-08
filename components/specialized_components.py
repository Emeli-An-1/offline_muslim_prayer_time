"""
Specialized Components for PrayerOffline Views
Compass, FlipCard, and Animated Counter with premium iOS design
"""

import flet as ft
from typing import Optional, Callable
from theme_manager import get_theme_manager
import math


class GlassCompass(ft.Stack):
    """Glass-style compass for Qibla direction with glow effect"""
    
    def __init__(
        self,
        direction: float = 0.0,  # 0-360 degrees
        size: int = 200,
        on_calibrate: Optional[Callable] = None,
        **kwargs
    ):
        theme = get_theme_manager()
        self.direction = direction
        self.size = size
        
        # Compass background (glass disc)
        self.compass_bg = ft.Container(
            width=size,
            height=size,
            border_radius=size // 2,
            bgcolor=f"{theme.get_color('surface')}CC",
            border=ft.border.all(2, f"{theme.get_color('primary')}40"),
            shadow=theme.get_shadow(3),
            blur=(30, 30),
        )
        
        # Kaaba direction indicator (glowing line)
        self.kaaba_line = ft.Container(
            width=4,
            height=size // 2 - 40,
            bgcolor=theme.get_color("primary"),
            border_radius=2,
            shadow=ft.BoxShadow(
                spread_radius=8,
                blur_radius=20,
                color=f"{theme.get_color('primary')}60",
            ),
            animate_rotation=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
        )
        
        # North indicator
        self.north_indicator = ft.Text(
            "N",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=theme.get_color("accent"),
        )
        
        # Direction text
        self.direction_text = ft.Text(
            f"{int(direction)}°",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=theme.get_color("text"),
            text_align=ft.TextAlign.CENTER,
        )
        
        # Compass content stack
        compass_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=20),
                    self.north_indicator,
                    ft.Container(expand=True),
                    self.kaaba_line,
                    ft.Container(expand=True),
                    self.direction_text,
                    ft.Container(height=20),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=size,
            height=size,
            alignment=ft.alignment.center,
        )
        
        super().__init__(
            controls=[
                self.compass_bg,
                compass_content,
            ],
            width=size,
            height=size,
            **kwargs
        )
    
    def set_direction(self, degrees: float):
        """Update compass direction with animation"""
        self.direction = degrees
        self.kaaba_line.rotate = ft.Rotate(math.radians(degrees))
        self.direction_text.value = f"{int(degrees)}°"


class FlipCard(ft.Stack):
    """Flip card with rotation animation for Du'a"""
    
    def __init__(
        self,
        front_content: ft.Control,
        back_content: ft.Control,
        width: int = 300,
        height: int = 200,
        **kwargs
    ):
        theme = get_theme_manager()
        self.is_flipped = False
        
        # Front card (Arabic)
        self.front = ft.Container(
            content=front_content,
            width=width,
            height=height,
            bgcolor=f"{theme.get_color('surface')}F0",
            border_radius=20,
            padding=20,
            shadow=theme.get_shadow(2),
            border=ft.border.all(1, f"{theme.get_color('primary')}30"),
            blur=(20, 20),
            visible=True,
        )
        
        # Back card (Translation)
        self.back = ft.Container(
            content=back_content,
            width=width,
            height=height,
            bgcolor=f"{theme.get_color('surface')}F0",
            border_radius=20,
            padding=20,
            shadow=theme.get_shadow(2),
            border=ft.border.all(1, f"{theme.get_color('accent')}30"),
            blur=(20, 20),
            visible=False,
        )
        
        # Flip button
        self.flip_btn = ft.IconButton(
            icon=ft.Icons.FLIP,
            icon_size=20,
            tooltip="Flip card",
            on_click=self._flip,
            icon_color=theme.get_color("primary"),
        )
        
        super().__init__(
            controls=[
                self.front,
                self.back,
                ft.Container(
                    content=self.flip_btn,
                    alignment=ft.alignment.bottom_right,
                    width=width,
                    height=height,
                ),
            ],
            width=width,
            height=height,
            **kwargs
        )
    
    def _flip(self, e):
        """Flip the card with animation"""
        self.is_flipped = not self.is_flipped
        
        # Simple visibility toggle (Flet doesn't support 3D transforms yet)
        # In a real app, you'd use CSS transforms or animate opacity
        self.front.visible = not self.is_flipped
        self.back.visible = self.is_flipped
        
        self.update()


class AnimatedCounter(ft.Container):
    """Liquid-style animated counter for Tasbih"""
    
    def __init__(
        self,
        count: int = 0,
        target: int = 33,
        dhikr_text: str = "سُبْحَانَ اللهِ",
        on_increment: Optional[Callable] = None,
        on_reset: Optional[Callable] = None,
        **kwargs
    ):
        theme = get_theme_manager()
        self.count = count
        self.target = target
        self.on_increment = on_increment
        self.on_reset = on_reset
        
        # Dhikr text (Arabic)
        self.dhikr = ft.Text(
            dhikr_text,
            size=36,
            weight=ft.FontWeight.BOLD,
            color=theme.get_color("primary"),
            text_align=ft.TextAlign.CENTER,
        )
        
        # Progress ring with count
        self.progress_ring = ft.ProgressRing(
            value=count / target if target > 0 else 0,
            width=180,
            height=180,
            stroke_width=12,
            color=theme.get_color("primary"),
        )
        
        self.count_text = ft.Text(
            f"{count}/{target}",
            size=56,
            weight=ft.FontWeight.BOLD,
            color=theme.get_color("text"),
            text_align=ft.TextAlign.CENTER,
        )
        
        # Progress stack
        progress_stack = ft.Stack(
            controls=[
                self.progress_ring,
                ft.Container(
                    content=self.count_text,
                    alignment=ft.alignment.center,
                    width=180,
                    height=180,
                ),
            ],
            width=180,
            height=180,
        )
        
        # Increment button (main action)
        self.increment_btn = ft.Container(
            content=ft.Icon(
                ft.Icons.ADD_CIRCLE,
                size=80,
                color=theme.get_color("primary"),
            ),
            on_click=self._increment,
            ink=True,
            animate_scale=ft.Animation(100, ft.AnimationCurve.BOUNCE_OUT),
        )
        
        # Control buttons
        control_buttons = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_size=32,
                    tooltip="Reset",
                    on_click=self._reset,
                    icon_color=theme.get_color("text"),
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_size=32,
                    tooltip="Settings",
                    icon_color=theme.get_color("text"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=40,
        )
        
        # Build counter layout
        counter_content = ft.Column(
            controls=[
                self.dhikr,
                ft.Container(height=20),
                progress_stack,
                ft.Container(height=30),
                self.increment_btn,
                ft.Container(height=20),
                control_buttons,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        super().__init__(
            content=counter_content,
            bgcolor=f"{theme.get_color('surface')}CC",
            border_radius=24,
            padding=30,
            shadow=theme.get_shadow(3),
            border=ft.border.all(1, f"{theme.get_color('primary')}20"),
            blur=(25, 25),
            **kwargs
        )
    
    def _increment(self, e):
        """Increment counter with animation"""
        self.count += 1
        
        # Reset if target reached
        if self.count > self.target:
            self.count = 0
        
        # Update UI
        self._update_display()
        
        # Animate button
        self.increment_btn.scale = 1.2
        self.update()
        
        # Reset scale
        self.increment_btn.scale = 1.0
        self.update()
        
        # Callback
        if self.on_increment:
            self.on_increment(self.count)
    
    def _reset(self, e):
        """Reset counter"""
        self.count = 0
        self._update_display()
        
        if self.on_reset:
            self.on_reset()
    
    def _update_display(self):
        """Update counter display"""
        self.count_text.value = f"{self.count}/{self.target}"
        self.progress_ring.value = self.count / self.target if self.target > 0 else 0
        self.update()
    
    def set_dhikr(self, arabic_text: str, target: int = 33):
        """Change dhikr type"""
        self.dhikr.value = arabic_text
        self.target = target
        self.count = 0
        self._update_display()


class HijriDateCard(ft.Container):
    """Beautiful Hijri date display with blur capsule"""
    
    def __init__(
        self,
        hijri_date: str = "15 Ramadan 1446 AH",
        gregorian_date: str = "March 15, 2025",
        **kwargs
    ):
        theme = get_theme_manager()
        
        content = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "Hijri",
                            size=10,
                            color=theme.get_color("text_secondary"),
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            hijri_date,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=theme.get_color("primary"),
                        ),
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.VerticalDivider(width=1, color=f"{theme.get_color('text')}20"),
                ft.Column(
                    controls=[
                        ft.Text(
                            "Gregorian",
                            size=10,
                            color=theme.get_color("text_secondary"),
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(
                            gregorian_date,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=theme.get_color("text"),
                        ),
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )
        
        super().__init__(
            content=content,
            bgcolor=f"{theme.get_color('surface')}DD",
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            shadow=theme.get_shadow(1),
            blur=(20, 20),
            **kwargs
        )


class CountdownTimer(ft.Container):
    """Countdown timer for next prayer with glow effect"""
    
    def __init__(
        self,
        hours: int = 2,
        minutes: int = 30,
        seconds: int = 45,
        **kwargs
    ):
        theme = get_theme_manager()
        
        # Time units
        def create_time_unit(value: int, label: str):
            return ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            f"{value:02d}",
                            size=48,
                            weight=ft.FontWeight.BOLD,
                            color=theme.get_color("primary"),
                            text_align=ft.TextAlign.CENTER,
                        ),
                        bgcolor=f"{theme.get_color('surface')}EE",
                        border_radius=16,
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        shadow=theme.get_shadow(2),
                        width=80,
                    ),
                    ft.Text(
                        label,
                        size=12,
                        color=theme.get_color("text_secondary"),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            )
        
        timer_display = ft.Row(
            controls=[
                create_time_unit(hours, "Hours"),
                ft.Text(":", size=48, color=theme.get_color("text")),
                create_time_unit(minutes, "Minutes"),
                ft.Text(":", size=48, color=theme.get_color("text")),
                create_time_unit(seconds, "Seconds"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )
        
        super().__init__(
            content=timer_display,
            **kwargs
        )


class LocationDisplay(ft.Container):
    """Location display with icon and formatted coordinates"""
    
    def __init__(
        self,
        city: str = "Mecca",
        country: str = "Saudi Arabia",
        latitude: float = 21.4225,
        longitude: float = 39.8262,
        **kwargs
    ):
        theme = get_theme_manager()
        
        content = ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.LOCATION_ON,
                    size=20,
                    color=theme.get_color("primary"),
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            f"{city}, {country}",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=theme.get_color("text"),
                        ),
                        ft.Text(
                            f"{latitude:.4f}°, {longitude:.4f}°",
                            size=10,
                            color=theme.get_color("text_secondary"),
                        ),
                    ],
                    spacing=2,
                ),
            ],
            spacing=8,
        )
        
        super().__init__(
            content=content,
            bgcolor=f"{theme.get_color('surface')}CC",
            border_radius=16,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            shadow=theme.get_shadow(1),
            blur=(15, 15),
            **kwargs
        )