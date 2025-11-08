"""
Components Package - Premium UI Components for PrayerOffline
"""

import logging

# ============================================================================
# PREMIUM COMPONENTS (Yeni Tasarım)
# ============================================================================
# Import theme manager from the repo root (module moved to project root)
from theme_manager import (
    ThemeManager,
    initialize_theme_manager,
    get_theme_manager,
    ThemeName,
    Spacing,
    BorderRadius,
)

from .styled_components import (
    PrayerCard,
    CountdownWidget,
    GlassCard,
    GradientButton,
    SectionHeader,
    InfoCard,
    StatCard,
    ToggleCard,
    EmptyState,
    LoadingIndicator,
    create_divider,
    create_spacer
)

from .navigation_components import (
    GlassNavigationBar,
    GlassNavigationRail,
    AdaptiveNavigation,
    get_standard_destinations,
    create_responsive_layout
)

# ============================================================================
# LEGACY COMPONENTS (Eski - Geriye uyumluluk için)
# ============================================================================
try:
    from .prayer_card import PrayerCard as LegacyPrayerCard, create_prayer_card
    from .countdown_widget import CountdownWidget as LegacyCountdownWidget
    from .navigation_rail import AppNavigationRail, create_navigation_rail, get_navigation_destinations
    LEGACY_AVAILABLE = True
except ImportError as e:
    LEGACY_AVAILABLE = False
    logging.warning(f"Legacy components not available: {e}")

# Configure logger
logger = logging.getLogger(__name__)

# ============================================================================
# PUBLIC API
# ============================================================================
__all__ = [
    # Theme System
    "ThemeManager",
    "initialize_theme_manager",
    "get_theme_manager",
    "ThemeName",
    "Spacing",
    "BorderRadius",
    
    # Premium Components
    "PrayerCard",
    "CountdownWidget",
    "GlassCard",
    "GradientButton",
    "SectionHeader",
    "InfoCard",
    "StatCard",
    "ToggleCard",
    "EmptyState",
    "LoadingIndicator",
    "create_divider",
    "create_spacer",
    
    # Navigation
    "GlassNavigationBar",
    "GlassNavigationRail",
    "AdaptiveNavigation",
    "get_standard_destinations",
    "create_responsive_layout",
]

# Add legacy components if available
if LEGACY_AVAILABLE:
    __all__.extend([
        "LegacyPrayerCard",
        "create_prayer_card",
        "LegacyCountdownWidget",
        "AppNavigationRail",
        "create_navigation_rail",
        "get_navigation_destinations",
    ])

__version__ = "2.0.0"

logger.info(f"✨ Components package loaded (v{__version__})")