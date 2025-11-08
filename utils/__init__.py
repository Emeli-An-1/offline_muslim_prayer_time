"""
Utils Package - Utility functions, constants, and validators for PrayerOffline

This package contains:
- constants: Application constants, enums, and defaults
- helpers: Helper functions for time, dates, calculations, and formatting
- validators: Input validation and sanitization functions
"""

import logging

# Import all constants
from .constants import (
    # Application metadata
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    
    # Prayer configuration
    PRAYER_NAMES,
    PRAYER_NAMES_ARABIC,
    DEFAULT_JAMAAT_OFFSETS,
    
    # Enums
    CalculationMethod,
    AsrMethod,
    HighLatitudeRule,
    JamaatMode,
    NotificationType,
    
    # Qibla
    KAABA_LAT,
    KAABA_LNG,
    KAABA_LOCATION,
    
    # Dhikr
    DHIKR_TYPES,
    DHIKR_NAMES_ENGLISH,
    DHIKR_TARGETS,
    
    # UI
    THEME_MODES,
    SUPPORTED_LANGUAGES,
    RTL_LANGUAGES,
    FONT_SIZES,
    COLORS,
    
    # Time formats
    TIME_FORMAT_12H,
    TIME_FORMAT_24H,
    DATE_FORMAT,
    DATETIME_FORMAT,
    
    # Defaults
    DEFAULT_SETTINGS,
    
    # Validation
    MIN_LATITUDE,
    MAX_LATITUDE,
    MIN_LONGITUDE,
    MAX_LONGITUDE,
    
    # Error messages
    ERROR_MESSAGES,
    
    # Features
    FEATURES,
)

# Import commonly used helpers
from .helpers import (
    # Time helpers
    format_time,
    parse_time,
    add_minutes_to_time,
    get_time_remaining,
    format_time_remaining,
    
    # Hijri helpers
    get_hijri_date,
    get_hijri_components,
    
    # Qibla helpers
    calculate_qibla_direction,
    calculate_distance_to_kaaba,
    format_distance,
    get_compass_direction,
    
    # Location helpers
    format_coordinates,
    is_valid_coordinates,
    
    # String helpers
    truncate_string,
    clean_string,
    is_arabic,
    
    # File helpers
    ensure_directory,
    format_file_size,
    
    # Number helpers
    clamp,
    lerp,
    map_range,
    
    # Debug helpers
    log_dict,
    format_exception,
)

# Import validators
from .validators import (
    # Validation result class
    ValidationResult,
    
    # Location validators
    validate_latitude,
    validate_longitude,
    validate_coordinates,
    validate_city_name,
    
    # Time validators
    validate_time_string,
    validate_time_object,
    validate_time_range,
    
    # Jamaat validators
    validate_jamaat_minutes,
    validate_jamaat_mode,
    validate_jamaat_config,
    
    # Settings validators
    validate_language,
    validate_theme_mode,
    validate_font_size,
    
    # Calculation validators
    validate_calculation_method,
    validate_asr_method,
    validate_high_latitude_rule,
    
    # String validators
    validate_not_empty,
    validate_string_length,
    
    # Number validators
    validate_positive_integer,
    validate_number_range,
    
    # File validators
    validate_file_exists,
    validate_directory_exists,
    
    # Composite validators
    validate_location_data,
    validate_prayer_times_data,
    
    # Sanitization
    sanitize_string,
    sanitize_number,
    sanitize_integer,
    sanitize_coordinates,
    
    # Batch validation
    validate_all,
    get_validation_errors,
)

# Configure package logger
logger = logging.getLogger(__name__)

# Public API exports
__all__ = [
    # Constants
    "APP_NAME",
    "APP_VERSION",
    "APP_DESCRIPTION",
    "PRAYER_NAMES",
    "PRAYER_NAMES_ARABIC",
    "DEFAULT_JAMAAT_OFFSETS",
    "CalculationMethod",
    "AsrMethod",
    "HighLatitudeRule",
    "JamaatMode",
    "NotificationType",
    "KAABA_LAT",
    "KAABA_LNG",
    "KAABA_LOCATION",
    "DHIKR_TYPES",
    "DHIKR_NAMES_ENGLISH",
    "DHIKR_TARGETS",
    "THEME_MODES",
    "SUPPORTED_LANGUAGES",
    "RTL_LANGUAGES",
    "FONT_SIZES",
    "COLORS",
    "TIME_FORMAT_12H",
    "TIME_FORMAT_24H",
    "DATE_FORMAT",
    "DATETIME_FORMAT",
    "DEFAULT_SETTINGS",
    "MIN_LATITUDE",
    "MAX_LATITUDE",
    "MIN_LONGITUDE",
    "MAX_LONGITUDE",
    "ERROR_MESSAGES",
    "FEATURES",
    
    # Helpers
    "format_time",
    "parse_time",
    "add_minutes_to_time",
    "get_time_remaining",
    "format_time_remaining",
    "get_hijri_date",
    "get_hijri_components",
    "calculate_qibla_direction",
    "calculate_distance_to_kaaba",
    "format_distance",
    "get_compass_direction",
    "format_coordinates",
    "is_valid_coordinates",
    "truncate_string",
    "clean_string",
    "is_arabic",
    "ensure_directory",
    "format_file_size",
    "clamp",
    "lerp",
    "map_range",
    "log_dict",
    "format_exception",
    
    # Validators
    "ValidationResult",
    "validate_latitude",
    "validate_longitude",
    "validate_coordinates",
    "validate_city_name",
    "validate_time_string",
    "validate_time_object",
    "validate_time_range",
    "validate_jamaat_minutes",
    "validate_jamaat_mode",
    "validate_jamaat_config",
    "validate_language",
    "validate_theme_mode",
    "validate_font_size",
    "validate_calculation_method",
    "validate_asr_method",
    "validate_high_latitude_rule",
    "validate_not_empty",
    "validate_string_length",
    "validate_positive_integer",
    "validate_number_range",
    "validate_file_exists",
    "validate_directory_exists",
    "validate_location_data",
    "validate_prayer_times_data",
    "sanitize_string",
    "sanitize_number",
    "sanitize_integer",
    "sanitize_coordinates",
    "validate_all",
    "get_validation_errors",
]

# Version
__version__ = "1.0.0"

logger.debug(f"Utils package initialized (v{__version__})")