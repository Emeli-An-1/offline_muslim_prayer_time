"""
Constants for PrayerOffline Application
Centralized configuration values, enums, and defaults
"""

from enum import Enum
from typing import Dict, List


# ============================================================================
# Application Metadata
# ============================================================================

APP_NAME = "PrayerOffline"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Privacy-first offline Muslim Prayer Time app"
APP_AUTHOR = "PrayerOffline Team"


# ============================================================================
# Prayer Configuration
# ============================================================================

PRAYER_NAMES: List[str] = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]

# Prayer names in Arabic
PRAYER_NAMES_ARABIC: Dict[str, str] = {
    "Fajr": "الفجر",
    "Sunrise": "الشروق",
    "Dhuhr": "الظهر",
    "Asr": "العصر",
    "Maghrib": "المغرب",
    "Isha": "العشاء"
}

# Default jamaat time offsets (minutes after adhan)
DEFAULT_JAMAAT_OFFSETS: Dict[str, int] = {
    "Fajr": 15,
    "Dhuhr": 10,
    "Asr": 10,
    "Maghrib": 5,
    "Isha": 10
}


# ============================================================================
# Calculation Methods
# ============================================================================

class CalculationMethod(Enum):
    """Islamic prayer time calculation methods"""
    MWL = "MWL"  # Muslim World League
    ISNA = "ISNA"  # Islamic Society of North America
    EGYPT = "Egypt"  # Egyptian General Authority of Survey
    MAKKAH = "Makkah"  # Umm Al-Qura University, Makkah
    KARACHI = "Karachi"  # University of Islamic Sciences, Karachi
    TEHRAN = "Tehran"  # Institute of Geophysics, University of Tehran
    JAFARI = "Jafari"  # Shia Ithna-Ashari, Leva Institute, Qum


# Calculation method descriptions
CALCULATION_METHOD_DESCRIPTIONS: Dict[str, str] = {
    "MWL": "Muslim World League (Default for most regions)",
    "ISNA": "Islamic Society of North America (USA/Canada)",
    "Egypt": "Egyptian General Authority of Survey",
    "Makkah": "Umm Al-Qura University, Makkah (Saudi Arabia)",
    "Karachi": "University of Islamic Sciences, Karachi (Pakistan)",
    "Tehran": "Institute of Geophysics, University of Tehran (Iran)",
    "Jafari": "Shia Ithna-Ashari, Leva Institute, Qum"
}


class AsrMethod(Enum):
    """Asr prayer calculation methods"""
    STANDARD = "Standard"  # Shafi, Maliki, Hanbali (shadow = object length)
    HANAFI = "Hanafi"  # Hanafi school (shadow = 2x object length)


class HighLatitudeRule(Enum):
    """High latitude adjustment rules"""
    NONE = "None"  # No adjustment
    MIDDLE_OF_NIGHT = "MiddleOfNight"  # Middle of the night
    ONE_SEVENTH = "OneSeventh"  # 1/7th of the night
    ANGLE_BASED = "AngleBased"  # Angle-based method


# High latitude threshold (degrees)
HIGH_LATITUDE_THRESHOLD = 48.0


# ============================================================================
# Jamaat Configuration
# ============================================================================

class JamaatMode(Enum):
    """Jamaat time configuration modes"""
    ADHAN_ONLY = "adhan_only"  # No jamaat, only adhan
    FIXED = "fixed"  # Fixed time (e.g., always at 13:00)
    SHIFT = "shift"  # Minutes after adhan (e.g., +10 minutes)


# ============================================================================
# Qibla Configuration
# ============================================================================

# Kaaba coordinates (Mecca, Saudi Arabia)
KAABA_LAT = 21.4225
KAABA_LNG = 39.8262
KAABA_LOCATION = {"latitude": KAABA_LAT, "longitude": KAABA_LNG, "name": "Kaaba"}


# ============================================================================
# Tasbih/Dhikr Configuration
# ============================================================================

DHIKR_TYPES: Dict[str, str] = {
    "subhanallah": "سُبْحَانَ اللَّهِ",
    "alhamdulillah": "الْحَمْدُ لِلَّهِ",
    "allahu_akbar": "اللَّهُ أَكْبَرُ",
    "la_ilaha_illallah": "لَا إِلَٰهَ إِلَّا ٱللَّٰهُ",
    "astaghfirullah": "أَسْتَغْفِرُ ٱللَّٰهَ"
}

DHIKR_NAMES_ENGLISH: Dict[str, str] = {
    "subhanallah": "SubhanAllah (Glory be to Allah)",
    "alhamdulillah": "Alhamdulillah (Praise be to Allah)",
    "allahu_akbar": "Allahu Akbar (Allah is the Greatest)",
    "la_ilaha_illallah": "La ilaha illallah (There is no god but Allah)",
    "astaghfirullah": "Astaghfirullah (I seek forgiveness from Allah)"
}

# Common dhikr targets
DHIKR_TARGETS: List[int] = [33, 99, 100, 500, 1000]


# ============================================================================
# UI Configuration
# ============================================================================

# Theme modes
THEME_MODES: List[str] = ["Light", "Dark", "System"]

# Supported languages
SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "English",
    "ar": "العربية (Arabic)",
    "ur": "اردو (Urdu)",
    "fr": "Français (French)"
}

# RTL languages
RTL_LANGUAGES: List[str] = ["ar", "ur", "fa", "he"]

# Font sizes
FONT_SIZES: Dict[str, int] = {
    "small": 12,
    "medium": 14,
    "large": 16,
    "xlarge": 18
}

# Color scheme
COLORS: Dict[str, str] = {
    "primary": "#4CAF50",
    "secondary": "#2196F3",
    "error": "#F44336",
    "warning": "#FF9800",
    "success": "#4CAF50",
    "info": "#2196F3"
}


# ============================================================================
# Notification Configuration
# ============================================================================

class NotificationType(Enum):
    """Notification types"""
    ADHAN = "adhan"
    JAMAAT = "jamaat"
    REMINDER = "reminder"


# Notification priorities
NOTIFICATION_PRIORITIES: Dict[str, str] = {
    "high": "High",
    "default": "Default",
    "low": "Low"
}

# Default notification lead times (minutes before prayer)
NOTIFICATION_LEAD_TIMES: List[int] = [0, 5, 10, 15, 30]


# ============================================================================
# Time & Date Configuration
# ============================================================================

# Time format patterns
TIME_FORMAT_12H = "%I:%M %p"
TIME_FORMAT_24H = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default time format
DEFAULT_TIME_FORMAT = TIME_FORMAT_24H


# ============================================================================
# Storage Configuration
# ============================================================================

# Database file name
DATABASE_FILE = "prayer_offline.db"

# Cache duration (days)
PRAYER_TIMES_CACHE_DURATION = 30


# ============================================================================
# Default Settings
# ============================================================================

DEFAULT_SETTINGS: Dict = {
    "location": {
        "latitude": 21.4225,
        "longitude": 39.8262,
        "city": "Mecca",
        "country": "Saudi Arabia",
        "timezone": "Asia/Riyadh"
    },
    "calculation": {
        "method": "ISNA",
        "asr_method": "Standard",
        "high_lat_rule": "None"
    },
    "theme_mode": "System",
    "language": "en",
    "font_size": 14,
    "time_format": "24h",
    "show_jamaat_times": True,
    "show_hijri_date": True,
    "jamaat_config": {
        "Fajr": {
            "mode": "shift",
            "minutes": 15,
            "enabled": True
        },
        "Dhuhr": {
            "mode": "shift",
            "minutes": 10,
            "enabled": True
        },
        "Asr": {
            "mode": "shift",
            "minutes": 10,
            "enabled": True
        },
        "Maghrib": {
            "mode": "shift",
            "minutes": 5,
            "enabled": True
        },
        "Isha": {
            "mode": "shift",
            "minutes": 10,
            "enabled": True
        }
    },
    "notifications": {
        "enabled": True,
        "adhan_enabled": True,
        "jamaat_enabled": True,
        "sound_enabled": True,
        "vibration_enabled": True
    }
}


# ============================================================================
# API & Network Configuration
# ============================================================================

# User agent for any network requests (if needed)
USER_AGENT = f"{APP_NAME}/{APP_VERSION}"

# Request timeout (seconds)
REQUEST_TIMEOUT = 10


# ============================================================================
# Validation Rules
# ============================================================================

# Location validation
MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0

# Time validation
MIN_HOUR = 0
MAX_HOUR = 23
MIN_MINUTE = 0
MAX_MINUTE = 59


# ============================================================================
# Error Messages
# ============================================================================

ERROR_MESSAGES: Dict[str, str] = {
    "location_not_set": "Location not set. Please configure your location in Settings.",
    "calculation_failed": "Failed to calculate prayer times. Please check your settings.",
    "storage_error": "Storage error occurred. Please restart the application.",
    "permission_denied": "Permission denied. Please grant the required permissions.",
    "invalid_input": "Invalid input. Please check your entry.",
    "network_error": "Network error. Please check your connection.",
}


# ============================================================================
# Feature Flags
# ============================================================================

FEATURES: Dict[str, bool] = {
    "enable_qibla": True,
    "enable_tasbih": True,
    "enable_dua": True,
    "enable_audio": True,
    "enable_notifications": True,
    "enable_widgets": True,
    "enable_export": True,
}


# ============================================================================
# Development Configuration
# ============================================================================

# Debug mode (set via environment variable)
import os
DEBUG_MODE = os.getenv("PRAYER_OFFLINE_DEBUG", "false").lower() == "true"

# Log level
LOG_LEVEL = "DEBUG" if DEBUG_MODE else "INFO"