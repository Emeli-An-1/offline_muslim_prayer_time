"""
PrayerOffline - Complete Theme Manager
Implements the full design specification with calm, spiritual aesthetics
Based on design_prompt.md specifications
"""

import flet as ft
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# CONSTANTS - Design System Foundation
# ============================================================================

class Spacing:
    """4pt baseline grid system"""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    XXXL = 48


class BorderRadius:
    """Consistent border radius values"""
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    CARD = 12  # Standard card radius from spec
    BUTTON = 12  # Standard button radius from spec


class Elevation:
    """Shadow elevation levels"""
    NONE = 0
    LOW = 2
    MEDIUM = 4
    HIGH = 8


class FontSize:
    """Typography scale from design spec"""
    DISPLAY = 32  # H1: 28-34sp
    TITLE = 22    # H2: 20-24sp
    BODY = 16     # Body: 14-16sp
    CAPTION = 12  # Small/captions: 12sp
    BUTTON = 16   # Button text: 14-16sp
    QURANIC = 20  # Arabic/Quranic text: 16-22sp


class FontWeight:
    """Font weight tokens"""
    REGULAR = ft.FontWeight.W_400
    MEDIUM = ft.FontWeight.W_600
    BOLD = ft.FontWeight.W_700


class ThemeName(Enum):
    """Available theme presets"""
    SPIRITUAL_LIGHT = "spiritual_light"  # Main theme from design spec
    SPIRITUAL_DARK = "spiritual_dark"    # Dark mode equivalent
    MINIMAL_TEAL = "minimal_teal"        # Alternative clean theme
    WARM_SAND = "warm_sand"              # Warm alternative


# ============================================================================
# COLOR PALETTE DATA STRUCTURES
# ============================================================================

@dataclass
class ThemeColors:
    """Complete color palette following design specification"""
    
    # Primary Brand Colors (Deep Teal)
    primary: str              # #0B6B63 - Deep Teal
    primary_container: str    # #E6F7F2 - Soft Mint
    on_primary: str
    on_primary_container: str
    
    # Secondary Colors (Warm Sand)
    secondary: str            # #D9BBA7 - Warm Sand
    secondary_container: str
    on_secondary: str
    on_secondary_container: str
    
    # Accent/Success
    accent: str               # #F2C94C - Gold Accent
    success: str              # For success states
    on_accent: str
    
    # Surfaces
    background: str           # #FCFEFF - Off-white
    surface: str              # #FFFFFF - White
    surface_variant: str      # Subtle variant
    on_background: str        # #062524 - Near-black teal
    on_surface: str
    on_surface_variant: str
    
    # Text
    text_primary: str         # #062524
    text_secondary: str       # #6B7773 - Muted
    text_tertiary: str
    
    # Status Colors
    error: str                # #C94A4A - Clay Red
    warning: str
    info: str
    on_error: str
    
    # UI Elements
    divider: str              # #ECECEC
    outline: str
    outline_variant: str
    shadow: str
    
    # Prayer-specific gradients (calm, spiritual)
    fajr_start: str
    fajr_end: str
    dhuhr_start: str
    dhuhr_end: str
    asr_start: str
    asr_end: str
    maghrib_start: str
    maghrib_end: str
    isha_start: str
    isha_end: str


@dataclass
class ThemeConfig:
    """Complete theme configuration"""
    name: str
    display_name: str
    colors: ThemeColors
    
    # Typography
    font_family: str
    font_family_arabic: str  # Separate Arabic font
    
    # Layout tokens
    spacing_base: int
    border_radius_base: int
    elevation_base: int
    
    # Visual effects
    card_blur: float
    glass_opacity: float
    use_shadows: bool
    use_gradients: bool
    use_glassmorphism: bool
    pattern_opacity: float  # For Islamic geometric patterns


# ============================================================================
# THEME MANAGER CLASS
# ============================================================================

class ThemeManager:
    """
    Comprehensive theme management system
    Implements design specification with spiritual, calm aesthetics
    """
    
    def __init__(self):
        self.themes = self._create_themes()
        self.current_theme_name = "spiritual_light"
        self.settings = {}
    
    # ========================================================================
    # THEME DEFINITIONS - Following Design Specification
    # ========================================================================
    
    def _create_themes(self) -> Dict[str, ThemeConfig]:
        """Create all theme variants"""
        return {
            "spiritual_light": self._create_spiritual_light_theme(),
            "spiritual_dark": self._create_spiritual_dark_theme(),
            "minimal_teal": self._create_minimal_teal_theme(),
            "warm_sand": self._create_warm_sand_theme(),
        }
    
    def _create_spiritual_light_theme(self) -> ThemeConfig:
        """
        Main theme following design specification
        Deep Teal primary, calm and spiritual
        """
        return ThemeConfig(
            name="spiritual_light",
            display_name="Spiritual Light",
            colors=ThemeColors(
                # Primary (Deep Teal - Design Spec)
                primary="#0B6B63",
                primary_container="#E6F7F2",
                on_primary="#FFFFFF",
                on_primary_container="#062524",
                
                # Secondary (Warm Sand - Design Spec)
                secondary="#D9BBA7",
                secondary_container="#F5EDE5",
                on_secondary="#3E2723",
                on_secondary_container="#3E2723",
                
                # Accent (Gold - Design Spec)
                accent="#F2C94C",
                success="#0FA88E",  # Teal variant for success
                on_accent="#3E2723",
                
                # Surfaces (Design Spec)
                background="#FCFEFF",
                surface="#FFFFFF",
                surface_variant="#F5F9F8",
                on_background="#062524",
                on_surface="#062524",
                on_surface_variant="#3E4A47",
                
                # Text (Design Spec)
                text_primary="#062524",
                text_secondary="#6B7773",
                text_tertiary="#9AA8A3",
                
                # Status (Design Spec)
                error="#C94A4A",
                warning="#F2994A",
                info="#0B6B63",
                on_error="#FFFFFF",
                
                # UI Elements (Design Spec)
                divider="#ECECEC",
                outline="#DBDFE0",
                outline_variant="#E8ECEB",
                shadow="#06252410",
                
                # Prayer Gradients (Calm, Spiritual - Based on Spec)
                fajr_start="#1565C0",      # Dawn blue
                fajr_end="#0B6B63",        # Deep teal
                dhuhr_start="#F2994A",     # Warm orange
                dhuhr_end="#F2C94C",       # Gold
                asr_start="#D9BBA7",       # Warm sand
                asr_end="#C9A689",         # Deeper sand
                maghrib_start="#C94A4A",   # Clay red
                maghrib_end="#E67E73",     # Softer red
                isha_start="#2C3E50",      # Deep navy
                isha_end="#0B6B63",        # Deep teal
            ),
            font_family="Inter",
            font_family_arabic="Noto Naskh Arabic",
            spacing_base=Spacing.LG,
            border_radius_base=BorderRadius.CARD,
            elevation_base=Elevation.LOW,
            card_blur=10.0,
            glass_opacity=0.95,
            use_shadows=True,
            use_gradients=True,
            use_glassmorphism=True,
            pattern_opacity=0.03,
        )
    
    def _create_spiritual_dark_theme(self) -> ThemeConfig:
        """
        Dark mode following design specification
        Maintains calm, spiritual feel in dark mode
        """
        return ThemeConfig(
            name="spiritual_dark",
            display_name="Spiritual Dark",
            colors=ThemeColors(
                # Primary (Adjusted for dark)
                primary="#0FA88E",
                primary_container="#0B4A43",
                on_primary="#FFFFFF",
                on_primary_container="#E6F7F2",
                
                # Secondary
                secondary="#D9BBA7",
                secondary_container="#4A3A2F",
                on_secondary="#FFFFFF",
                on_secondary_container="#F5EDE5",
                
                # Accent
                accent="#F2C94C",
                success="#0FA88E",
                on_accent="#062524",
                
                # Surfaces (Dark - Design Spec)
                background="#0A0F0E",
                surface="#0E1615",
                surface_variant="#1A2524",
                on_background="#E6F7F2",
                on_surface="#E6F7F2",
                on_surface_variant="#C5D4D0",
                
                # Text (Dark - Design Spec)
                text_primary="#E6F7F2",
                text_secondary="#9AA8A3",
                text_tertiary="#6B7773",
                
                # Status
                error="#EF9A9A",
                warning="#FFCC80",
                info="#0FA88E",
                on_error="#3E2723",
                
                # UI Elements
                divider="#2A3736",
                outline="#3E4A47",
                outline_variant="#2A3736",
                shadow="#00000040",
                
                # Prayer Gradients (Luminous in dark)
                fajr_start="#1E88E5",
                fajr_end="#0FA88E",
                dhuhr_start="#FFB74D",
                dhuhr_end="#F2C94C",
                asr_start="#BCAAA4",
                asr_end="#8D6E63",
                maghrib_start="#EF5350",
                maghrib_end="#E67E73",
                isha_start="#42A5F5",
                isha_end="#0FA88E",
            ),
            font_family="Inter",
            font_family_arabic="Noto Naskh Arabic",
            spacing_base=Spacing.LG,
            border_radius_base=BorderRadius.CARD,
            elevation_base=Elevation.MEDIUM,
            card_blur=15.0,
            glass_opacity=0.85,
            use_shadows=True,
            use_gradients=True,
            use_glassmorphism=True,
            pattern_opacity=0.05,
        )
    
    def _create_minimal_teal_theme(self) -> ThemeConfig:
        """Minimal clean theme with teal accent"""
        return ThemeConfig(
            name="minimal_teal",
            display_name="Minimal Teal",
            colors=ThemeColors(
                primary="#00897B",
                primary_container="#B2DFDB",
                on_primary="#FFFFFF",
                on_primary_container="#004D40",
                secondary="#90A4AE",
                secondary_container="#CFD8DC",
                on_secondary="#FFFFFF",
                on_secondary_container="#263238",
                accent="#FFA726",
                success="#66BB6A",
                on_accent="#FFFFFF",
                background="#FAFAFA",
                surface="#FFFFFF",
                surface_variant="#F5F5F5",
                on_background="#212121",
                on_surface="#212121",
                on_surface_variant="#616161",
                text_primary="#212121",
                text_secondary="#757575",
                text_tertiary="#9E9E9E",
                error="#E57373",
                warning="#FFB74D",
                info="#64B5F6",
                on_error="#FFFFFF",
                divider="#E0E0E0",
                outline="#BDBDBD",
                outline_variant="#E0E0E0",
                shadow="#00000020",
                fajr_start="#0097A7",
                fajr_end="#00BCD4",
                dhuhr_start="#FFA726",
                dhuhr_end="#FF7043",
                asr_start="#AB47BC",
                asr_end="#8E24AA",
                maghrib_start="#F06292",
                maghrib_end="#E91E63",
                isha_start="#5C6BC0",
                isha_end="#3F51B5",
            ),
            font_family="Inter",
            font_family_arabic="Cairo",
            spacing_base=Spacing.LG,
            border_radius_base=BorderRadius.MD,
            elevation_base=Elevation.LOW,
            card_blur=0.0,
            glass_opacity=1.0,
            use_shadows=True,
            use_gradients=False,
            use_glassmorphism=False,
            pattern_opacity=0.0,
        )
    
    def _create_warm_sand_theme(self) -> ThemeConfig:
        """Warm, earthy theme with sand tones"""
        return ThemeConfig(
            name="warm_sand",
            display_name="Warm Sand",
            colors=ThemeColors(
                primary="#8D6E63",
                primary_container="#D7CCC8",
                on_primary="#FFFFFF",
                on_primary_container="#3E2723",
                secondary="#BF8F6E",
                secondary_container="#EFEBE9",
                on_secondary="#FFFFFF",
                on_secondary_container="#4E342E",
                accent="#FFC107",
                success="#7CB342",
                on_accent="#3E2723",
                background="#FFF8E1",
                surface="#FFFFFF",
                surface_variant="#FFF3E0",
                on_background="#3E2723",
                on_surface="#3E2723",
                on_surface_variant="#5D4037",
                text_primary="#3E2723",
                text_secondary="#6D4C41",
                text_tertiary="#8D6E63",
                error="#D32F2F",
                warning="#F57C00",
                info="#1976D2",
                on_error="#FFFFFF",
                divider="#D7CCC8",
                outline="#BCAAA4",
                outline_variant="#D7CCC8",
                shadow="#3E272320",
                fajr_start="#5D4037",
                fajr_end="#795548",
                dhuhr_start="#FFA726",
                dhuhr_end="#FF8A65",
                asr_start="#A1887F",
                asr_end="#8D6E63",
                maghrib_start="#EF5350",
                maghrib_end="#F44336",
                isha_start="#6D4C41",
                isha_end="#4E342E",
            ),
            font_family="Inter",
            font_family_arabic="Amiri",
            spacing_base=Spacing.XL,
            border_radius_base=BorderRadius.LG,
            elevation_base=Elevation.LOW,
            card_blur=5.0,
            glass_opacity=0.9,
            use_shadows=True,
            use_gradients=True,
            use_glassmorphism=False,
            pattern_opacity=0.04,
        )
    
    # ========================================================================
    # CORE METHODS
    # ========================================================================
    
    def get_theme(self, theme_name: Optional[str] = None) -> ThemeConfig:
        """Get theme configuration"""
        name = theme_name or self.current_theme_name
        return self.themes.get(name, self.themes["spiritual_light"])
    
    def set_theme(self, theme_name: str) -> bool:
        """Set active theme"""
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            return True
        return False
    
    def get_all_themes(self) -> List[str]:
        """Get all theme names"""
        return list(self.themes.keys())
    
    def get_theme_display_names(self) -> Dict[str, str]:
        """Get theme name to display name mapping"""
        return {
            name: config.display_name
            for name, config in self.themes.items()
        }
    
    # ========================================================================
    # COLOR GETTERS - Component API
    # ========================================================================
    
    def get_color(self, color_name: str, theme_name: Optional[str] = None) -> str:
        """
        Get color by name with smart fallbacks
        
        Args:
            color_name: Color key (supports aliases)
            theme_name: Optional theme override
            
        Returns:
            Hex color string
        """
        theme = self.get_theme(theme_name)
        colors = theme.colors
        
        # Normalized color name
        name = color_name.lower().replace("-", "_").replace(" ", "_")
        
        # Direct match
        if hasattr(colors, name):
            return getattr(colors, name)
        
        # Common aliases
        aliases = {
            "bg": "background",
            "text": "text_primary",
            "muted": "text_secondary",
            "disabled": "text_tertiary",
            "border": "outline",
            "card": "surface",
        }
        
        if name in aliases:
            return getattr(colors, aliases[name])
        
        # Fallback to primary
        return colors.primary
    
    def get_gradient(
        self,
        prayer_name: Optional[str] = None,
        theme_name: Optional[str] = None
    ) -> ft.LinearGradient:
        """
        Get prayer-specific gradient or default gradient
        
        Args:
            prayer_name: Prayer name (Fajr, Dhuhr, etc.) or None for default
            theme_name: Optional theme override
            
        Returns:
            LinearGradient object
        """
        theme = self.get_theme(theme_name)
        colors = theme.colors
        
        if prayer_name:
            prayer = prayer_name.lower()
            start_key = f"{prayer}_start"
            end_key = f"{prayer}_end"
            
            if hasattr(colors, start_key) and hasattr(colors, end_key):
                return ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[
                        getattr(colors, start_key),
                        getattr(colors, end_key)
                    ]
                )
        
        # Default gradient (primary to accent)
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[colors.primary, colors.accent]
        )
    
    def get_glassmorphism_style(
        self,
        blur: int = 20,
        opacity: float = 0.9,
        theme_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get glassmorphism card style
        
        Args:
            blur: Blur amount
            opacity: Background opacity
            theme_name: Optional theme override
            
        Returns:
            Style dictionary for Container
        """
        theme = self.get_theme(theme_name)
        colors = theme.colors
        
        if not theme.use_glassmorphism:
            # Fallback to solid surface
            return {
                "bgcolor": colors.surface,
                "border": ft.border.all(1, colors.outline_variant),
                "border_radius": theme.border_radius_base,
            }
        
        # Glass effect
        bg_color = colors.surface
        if len(bg_color) == 7:  # #RRGGBB
            bg_color = f"{bg_color}{int(opacity * 255):02X}"
        
        return {
            "bgcolor": bg_color,
            "blur": (blur, blur),
            "border": ft.border.all(1, f"{colors.outline}40"),
            "border_radius": theme.border_radius_base,
        }
    
    def get_shadow(
        self,
        elevation: int = 2,
        theme_name: Optional[str] = None
    ) -> ft.BoxShadow:
        """
        Get shadow based on elevation
        
        Args:
            elevation: Shadow level (0-8)
            theme_name: Optional theme override
            
        Returns:
            BoxShadow object
        """
        theme = self.get_theme(theme_name)
        
        if not theme.use_shadows or elevation == 0:
            return None
        
        # Shadow intensity based on elevation
        blur_radius = elevation * 2
        spread_radius = max(0, elevation - 2)
        offset_y = elevation
        
        return ft.BoxShadow(
            spread_radius=spread_radius,
            blur_radius=blur_radius,
            color=theme.colors.shadow,
            offset=ft.Offset(0, offset_y)
        )
    
    # ========================================================================
    # STYLE GENERATORS - Complete Component Styles
    # ========================================================================
    
    def get_card_style(
        self,
        elevated: bool = True,
        glass: bool = False,
        theme_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get complete card style"""
        theme = self.get_theme(theme_name)
        
        if glass:
            return self.get_glassmorphism_style(
                blur=int(theme.card_blur),
                opacity=theme.glass_opacity,
                theme_name=theme_name
            )
        
        style = {
            "bgcolor": theme.colors.surface,
            "border_radius": theme.border_radius_base,
            "padding": theme.spacing_base,
        }
        
        if elevated:
            style["shadow"] = self.get_shadow(
                elevation=theme.elevation_base,
                theme_name=theme_name
            )
        
        return style
    
    def get_button_style(
        self,
        variant: str = "filled",  # filled, outlined, text
        theme_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get button style"""
        theme = self.get_theme(theme_name)
        colors = theme.colors
        
        styles = {
            "filled": {
                "bgcolor": colors.primary,
                "color": colors.on_primary,
                "border": None,
                "elevation": theme.elevation_base if theme.use_shadows else 0,
            },
            "outlined": {
                "bgcolor": None,
                "color": colors.primary,
                "border": ft.border.all(2, colors.primary),
                "elevation": 0,
            },
            "text": {
                "bgcolor": None,
                "color": colors.primary,
                "border": None,
                "elevation": 0,
            }
        }
        
        base_style = styles.get(variant, styles["filled"])
        base_style["border_radius"] = BorderRadius.BUTTON
        
        return base_style
    
    def get_text_style(
        self,
        variant: str = "body",  # display, title, body, caption, button
        theme_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get text style following design spec typography"""
        theme = self.get_theme(theme_name)
        colors = theme.colors
        
        styles = {
            "display": {
                "size": FontSize.DISPLAY,
                "weight": FontWeight.BOLD,
                "color": colors.text_primary,
            },
            "title": {
                "size": FontSize.TITLE,
                "weight": FontWeight.MEDIUM,
                "color": colors.text_primary,
            },
            "body": {
                "size": FontSize.BODY,
                "weight": FontWeight.REGULAR,
                "color": colors.text_primary,
            },
            "caption": {
                "size": FontSize.CAPTION,
                "weight": FontWeight.REGULAR,
                "color": colors.text_secondary,
            },
            "button": {
                "size": FontSize.BUTTON,
                "weight": FontWeight.MEDIUM,
                "color": colors.on_primary,
            }
        }
        
        return styles.get(variant, styles["body"])
    
    def apply_to_page(
        self,
        page: ft.Page,
        theme_mode: str = "system"
    ):
        """Apply theme to Flet page"""
        theme = self.get_theme()
        
        # Set theme mode
        if theme_mode.lower() == "dark":
            page.theme_mode = ft.ThemeMode.DARK
            if "dark" not in self.current_theme_name:
                self.set_theme("spiritual_dark")
        elif theme_mode.lower() == "light":
            page.theme_mode = ft.ThemeMode.LIGHT
            if "dark" in self.current_theme_name:
                self.set_theme("spiritual_light")
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM
        
        # Apply theme colors
        page.theme = ft.Theme(
            color_scheme_seed=theme.colors.primary,
            font_family=theme.font_family,
        )
        
        page.bgcolor = theme.colors.background
        page.update()


# ============================================================================
# GLOBAL INSTANCE & HELPER FUNCTIONS
# ============================================================================

# Global singleton instance
_theme_manager_instance: Optional[ThemeManager] = None


def initialize_theme_manager() -> ThemeManager:
    """Initialize global theme manager"""
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance


def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance"""
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance


# Legacy compatibility
theme_manager = get_theme_manager()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "ThemeManager",
    "ThemeConfig",
    "ThemeColors",
    "ThemeName",
    "Spacing",
    "BorderRadius",
    "Elevation",
    "FontSize",
    "FontWeight",
    "initialize_theme_manager",
    "get_theme_manager",
    "theme_manager",
]