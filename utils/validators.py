"""
Input Validation Functions for PrayerOffline
Comprehensive validation for user inputs, settings, and data
"""

import re
import logging
from datetime import datetime, time
from typing import Optional, Tuple, Any, List, Dict
from pathlib import Path

# Import constants with fallback defaults
try:
    from utils.constants import (
        MIN_LATITUDE, MAX_LATITUDE,
        MIN_LONGITUDE, MAX_LONGITUDE,
        MIN_HOUR, MAX_HOUR,
        MIN_MINUTE, MAX_MINUTE,
        SUPPORTED_LANGUAGES,
        THEME_MODES
    )
except ImportError:
    # Fallback defaults if constants not available
    MIN_LATITUDE, MAX_LATITUDE = -90, 90
    MIN_LONGITUDE, MAX_LONGITUDE = -180, 180
    MIN_HOUR, MAX_HOUR = 0, 23
    MIN_MINUTE, MAX_MINUTE = 0, 59
    SUPPORTED_LANGUAGES = {"en": "English", "ar": "Arabic", "fr": "French", "ur": "Urdu"}
    THEME_MODES = ["light", "dark", "auto"]

logger = logging.getLogger(__name__)


# ============================================================================
# Validation Result Class
# ============================================================================

class ValidationResult:
    """Result of a validation operation"""
    
    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message
    
    def __bool__(self) -> bool:
        return self.is_valid
    
    def __repr__(self) -> str:
        return f"ValidationResult(valid={self.is_valid}, error='{self.error_message}')"


# ============================================================================
# Location Validators
# ============================================================================

def validate_latitude(latitude: Any) -> ValidationResult:
    """
    Validate latitude value
    
    Args:
        latitude: Value to validate
        
    Returns:
        ValidationResult
    """
    try:
        lat = float(latitude)
        if MIN_LATITUDE <= lat <= MAX_LATITUDE:
            return ValidationResult(True)
        else:
            return ValidationResult(
                False,
                f"Latitude must be between {MIN_LATITUDE} and {MAX_LATITUDE}"
            )
    except (ValueError, TypeError):
        return ValidationResult(False, "Latitude must be a valid number")


def validate_longitude(longitude: Any) -> ValidationResult:
    """
    Validate longitude value
    
    Args:
        longitude: Value to validate
        
    Returns:
        ValidationResult
    """
    try:
        lon = float(longitude)
        if MIN_LONGITUDE <= lon <= MAX_LONGITUDE:
            return ValidationResult(True)
        else:
            return ValidationResult(
                False,
                f"Longitude must be between {MIN_LONGITUDE} and {MAX_LONGITUDE}"
            )
    except (ValueError, TypeError):
        return ValidationResult(False, "Longitude must be a valid number")


def validate_coordinates(latitude: Any, longitude: Any) -> ValidationResult:
    """
    Validate latitude and longitude together
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        ValidationResult
    """
    lat_result = validate_latitude(latitude)
    if not lat_result:
        return lat_result
    
    lon_result = validate_longitude(longitude)
    if not lon_result:
        return lon_result
    
    return ValidationResult(True)


def validate_city_name(city: str) -> ValidationResult:
    """
    Validate city name
    
    Args:
        city: City name to validate
        
    Returns:
        ValidationResult
    """
    if not city or not isinstance(city, str):
        return ValidationResult(False, "City name is required")
    
    city = city.strip()
    
    if len(city) < 2:
        return ValidationResult(False, "City name must be at least 2 characters")
    
    if len(city) > 100:
        return ValidationResult(False, "City name is too long (max 100 characters)")
    
    # Allow letters, spaces, hyphens, apostrophes, and Arabic characters
    if not re.match(r"^[a-zA-Z\u0600-\u06FF\s\-']+$", city):
        return ValidationResult(
            False,
            "City name can only contain letters, spaces, hyphens, and apostrophes"
        )
    
    return ValidationResult(True)


# ============================================================================
# Time Validators
# ============================================================================

def validate_time_string(time_str: str) -> ValidationResult:
    """
    Validate time string format (HH:MM)
    
    Args:
        time_str: Time string to validate
        
    Returns:
        ValidationResult
    """
    if not time_str or not isinstance(time_str, str):
        return ValidationResult(False, "Time is required")
    
    # Check format HH:MM
    if not re.match(r'^\d{2}:\d{2}$', time_str):
        return ValidationResult(False, "Time must be in HH:MM format")
    
    try:
        parts = time_str.split(':')
        hour = int(parts[0])
        minute = int(parts[1])
        
        if not (MIN_HOUR <= hour <= MAX_HOUR):
            return ValidationResult(False, f"Hour must be between {MIN_HOUR} and {MAX_HOUR}")
        
        if not (MIN_MINUTE <= minute <= MAX_MINUTE):
            return ValidationResult(False, f"Minute must be between {MIN_MINUTE} and {MAX_MINUTE}")
        
        return ValidationResult(True)
        
    except (ValueError, IndexError):
        return ValidationResult(False, "Invalid time format")


def validate_time_object(time_obj: Any) -> ValidationResult:
    """
    Validate time object
    
    Args:
        time_obj: Time object to validate
        
    Returns:
        ValidationResult
    """
    if not isinstance(time_obj, time):
        return ValidationResult(False, "Must be a valid time object")
    
    if not (MIN_HOUR <= time_obj.hour <= MAX_HOUR):
        return ValidationResult(False, f"Hour must be between {MIN_HOUR} and {MAX_HOUR}")
    
    if not (MIN_MINUTE <= time_obj.minute <= MAX_MINUTE):
        return ValidationResult(False, f"Minute must be between {MIN_MINUTE} and {MAX_MINUTE}")
    
    return ValidationResult(True)


def validate_time_range(start_time: str, end_time: str) -> ValidationResult:
    """
    Validate that end_time is after start_time
    
    Args:
        start_time: Start time string (HH:MM)
        end_time: End time string (HH:MM)
        
    Returns:
        ValidationResult
    """
    start_result = validate_time_string(start_time)
    if not start_result:
        return start_result
    
    end_result = validate_time_string(end_time)
    if not end_result:
        return end_result
    
    try:
        start = datetime.strptime(start_time, "%H:%M").time()
        end = datetime.strptime(end_time, "%H:%M").time()
        
        if end <= start:
            return ValidationResult(False, "End time must be after start time")
        
        return ValidationResult(True)
        
    except ValueError:
        return ValidationResult(False, "Invalid time format")


# ============================================================================
# Jamaat Configuration Validators
# ============================================================================

def validate_jamaat_minutes(minutes: Any) -> ValidationResult:
    """
    Validate jamaat offset minutes
    
    Args:
        minutes: Minutes value to validate
        
    Returns:
        ValidationResult
    """
    try:
        mins = int(minutes)
        if -60 <= mins <= 120:
            return ValidationResult(True)
        else:
            return ValidationResult(
                False,
                "Jamaat offset must be between -60 and 120 minutes"
            )
    except (ValueError, TypeError):
        return ValidationResult(False, "Jamaat minutes must be a valid number")


def validate_jamaat_mode(mode: str) -> ValidationResult:
    """
    Validate jamaat mode
    
    Args:
        mode: Jamaat mode to validate
        
    Returns:
        ValidationResult
    """
    valid_modes = ["adhan_only", "fixed", "shift"]
    
    if mode not in valid_modes:
        return ValidationResult(
            False,
            f"Jamaat mode must be one of: {', '.join(valid_modes)}"
        )
    
    return ValidationResult(True)


def validate_jamaat_config(config: Dict[str, Any], mode: str) -> ValidationResult:
    """
    Validate complete jamaat configuration
    
    Args:
        config: Jamaat configuration dictionary
        mode: Jamaat mode
        
    Returns:
        ValidationResult
    """
    mode_result = validate_jamaat_mode(mode)
    if not mode_result:
        return mode_result
    
    # Validate based on mode
    if mode == "fixed":
        if "time" not in config:
            return ValidationResult(False, "Fixed mode requires 'time' field")
        return validate_time_string(config["time"])
    
    elif mode == "shift":
        if "minutes" not in config:
            return ValidationResult(False, "Shift mode requires 'minutes' field")
        return validate_jamaat_minutes(config["minutes"])
    
    return ValidationResult(True)


# ============================================================================
# Settings Validators
# ============================================================================

def validate_language(language: str) -> ValidationResult:
    """
    Validate language code
    
    Args:
        language: Language code to validate
        
    Returns:
        ValidationResult
    """
    if language not in SUPPORTED_LANGUAGES:
        return ValidationResult(
            False,
            f"Language must be one of: {', '.join(SUPPORTED_LANGUAGES.keys())}"
        )
    
    return ValidationResult(True)


def validate_theme_mode(theme_mode: str) -> ValidationResult:
    """
    Validate theme mode
    
    Args:
        theme_mode: Theme mode to validate
        
    Returns:
        ValidationResult
    """
    if theme_mode not in THEME_MODES:
        return ValidationResult(
            False,
            f"Theme mode must be one of: {', '.join(THEME_MODES)}"
        )
    
    return ValidationResult(True)


def validate_font_size(font_size: Any) -> ValidationResult:
    """
    Validate font size
    
    Args:
        font_size: Font size to validate
        
    Returns:
        ValidationResult
    """
    try:
        size = int(font_size)
        if 8 <= size <= 32:
            return ValidationResult(True)
        else:
            return ValidationResult(False, "Font size must be between 8 and 32")
    except (ValueError, TypeError):
        return ValidationResult(False, "Font size must be a valid number")


# ============================================================================
# Calculation Method Validators
# ============================================================================

def validate_calculation_method(method: str) -> ValidationResult:
    """
    Validate prayer calculation method (per project spec)
    
    Args:
        method: Calculation method to validate
        
    Returns:
        ValidationResult
    """
    valid_methods = ["ISNA", "MWL", "UMMALQURA", "EGYPTIAN", "KARACHI", "CUSTOM"]
    
    if method not in valid_methods:
        return ValidationResult(
            False,
            f"Calculation method must be one of: {', '.join(valid_methods)}"
        )
    
    return ValidationResult(True)


def validate_asr_method(method: str) -> ValidationResult:
    """
    Validate Asr calculation method (per project spec)
    
    Args:
        method: Asr method to validate
        
    Returns:
        ValidationResult
    """
    valid_methods = ["STANDARD", "HANAFI"]
    
    if method not in valid_methods:
        return ValidationResult(
            False,
            f"Asr method must be one of: {', '.join(valid_methods)}"
        )
    
    return ValidationResult(True)


def validate_high_latitude_rule(rule: str) -> ValidationResult:
    """
    Validate high latitude rule (per project spec)
    
    Args:
        rule: High latitude rule to validate
        
    Returns:
        ValidationResult
    """
    valid_rules = ["ANGLE_BASED", "MIDDLE_OF_NIGHT", "ONE_SEVENTH"]
    
    if rule not in valid_rules:
        return ValidationResult(
            False,
            f"High latitude rule must be one of: {', '.join(valid_rules)}"
        )
    
    return ValidationResult(True)


# ============================================================================
# String Validators
# ============================================================================

def validate_not_empty(value: str, field_name: str = "Field") -> ValidationResult:
    """
    Validate that string is not empty
    
    Args:
        value: String to validate
        field_name: Name of field for error message
        
    Returns:
        ValidationResult
    """
    if not value or not isinstance(value, str):
        return ValidationResult(False, f"{field_name} is required")
    
    if not value.strip():
        return ValidationResult(False, f"{field_name} cannot be empty")
    
    return ValidationResult(True)


def validate_string_length(value: str, min_length: int = 0, 
                          max_length: int = 1000,
                          field_name: str = "Field") -> ValidationResult:
    """
    Validate string length
    
    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length
        field_name: Name of field for error message
        
    Returns:
        ValidationResult
    """
    if not isinstance(value, str):
        return ValidationResult(False, f"{field_name} must be a string")
    
    length = len(value)
    
    if length < min_length:
        return ValidationResult(
            False,
            f"{field_name} must be at least {min_length} characters"
        )
    
    if length > max_length:
        return ValidationResult(
            False,
            f"{field_name} must be at most {max_length} characters"
        )
    
    return ValidationResult(True)


# ============================================================================
# Number Validators
# ============================================================================

def validate_positive_integer(value: Any, field_name: str = "Value") -> ValidationResult:
    """
    Validate positive integer
    
    Args:
        value: Value to validate
        field_name: Name of field for error message
        
    Returns:
        ValidationResult
    """
    try:
        num = int(value)
        if num > 0:
            return ValidationResult(True)
        else:
            return ValidationResult(False, f"{field_name} must be positive")
    except (ValueError, TypeError):
        return ValidationResult(False, f"{field_name} must be a valid integer")


def validate_number_range(value: Any, min_value: float, max_value: float,
                         field_name: str = "Value") -> ValidationResult:
    """
    Validate number is within range
    
    Args:
        value: Value to validate
        min_value: Minimum value
        max_value: Maximum value
        field_name: Name of field for error message
        
    Returns:
        ValidationResult
    """
    try:
        num = float(value)
        if min_value <= num <= max_value:
            return ValidationResult(True)
        else:
            return ValidationResult(
                False,
                f"{field_name} must be between {min_value} and {max_value}"
            )
    except (ValueError, TypeError):
        return ValidationResult(False, f"{field_name} must be a valid number")


# ============================================================================
# File & Path Validators
# ============================================================================

def validate_file_exists(path: str) -> ValidationResult:
    """
    Validate that file exists
    
    Args:
        path: File path to validate
        
    Returns:
        ValidationResult
    """
    try:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            return ValidationResult(True)
        else:
            return ValidationResult(False, f"File does not exist: {path}")
    except Exception as e:
        return ValidationResult(False, f"Invalid file path: {e}")


def validate_directory_exists(path: str) -> ValidationResult:
    """
    Validate that directory exists
    
    Args:
        path: Directory path to validate
        
    Returns:
        ValidationResult
    """
    try:
        dir_path = Path(path)
        if dir_path.exists() and dir_path.is_dir():
            return ValidationResult(True)
        else:
            return ValidationResult(False, f"Directory does not exist: {path}")
    except Exception as e:
        return ValidationResult(False, f"Invalid directory path: {e}")


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> ValidationResult:
    """
    Validate file extension
    
    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions (e.g., ['.txt', '.json'])
        
    Returns:
        ValidationResult
    """
    try:
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        if extension in allowed_extensions:
            return ValidationResult(True)
        else:
            return ValidationResult(
                False,
                f"File extension must be one of: {', '.join(allowed_extensions)}"
            )
    except Exception as e:
        return ValidationResult(False, f"Invalid filename: {e}")


# ============================================================================
# Email & URL Validators
# ============================================================================

def validate_email(email: str) -> ValidationResult:
    """
    Validate email address
    
    Args:
        email: Email address to validate
        
    Returns:
        ValidationResult
    """
    if not email or not isinstance(email, str):
        return ValidationResult(False, "Email is required")
    
    # RFC 5322 simplified email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return ValidationResult(True)
    else:
        return ValidationResult(False, "Invalid email address format")


def validate_url(url: str) -> ValidationResult:
    """
    Validate URL
    
    Args:
        url: URL to validate
        
    Returns:
        ValidationResult
    """
    if not url or not isinstance(url, str):
        return ValidationResult(False, "URL is required")
    
    # Simple URL regex pattern
    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    
    if re.match(pattern, url):
        return ValidationResult(True)
    else:
        return ValidationResult(False, "Invalid URL format")


# ============================================================================
# Composite Validators
# ============================================================================

def validate_location_data(location: Dict[str, Any]) -> ValidationResult:
    """
    Validate complete location data
    
    Args:
        location: Location dictionary
        
    Returns:
        ValidationResult
    """
    required_fields = ["latitude", "longitude"]
    
    for field in required_fields:
        if field not in location:
            return ValidationResult(False, f"Missing required field: {field}")
    
    # Validate coordinates
    coord_result = validate_coordinates(
        location["latitude"],
        location["longitude"]
    )
    if not coord_result:
        return coord_result
    
    # Validate city if present
    if "city" in location and location["city"]:
        city_result = validate_city_name(location["city"])
        if not city_result:
            return city_result
    
    return ValidationResult(True)


def validate_prayer_times_data(prayer_times: Dict[str, Any]) -> ValidationResult:
    """
    Validate prayer times data structure
    
    Args:
        prayer_times: Prayer times dictionary
        
    Returns:
        ValidationResult
    """
    if not isinstance(prayer_times, dict):
        return ValidationResult(False, "Prayer times must be a dictionary")
    
    if "prayers" not in prayer_times:
        return ValidationResult(False, "Missing 'prayers' key")
    
    prayers = prayer_times["prayers"]
    if not isinstance(prayers, dict):
        return ValidationResult(False, "Prayers must be a dictionary")
    
    # Validate each prayer time
    for prayer_name, prayer_data in prayers.items():
        if not isinstance(prayer_data, dict):
            return ValidationResult(False, f"{prayer_name} data must be a dictionary")
        
        if "adhan" not in prayer_data:
            return ValidationResult(False, f"{prayer_name} missing 'adhan' time")
        
        time_result = validate_time_string(prayer_data["adhan"])
        if not time_result:
            return ValidationResult(False, f"{prayer_name} adhan time invalid: {time_result.error_message}")
    
    return ValidationResult(True)


# ============================================================================
# Sanitization Functions
# ============================================================================

def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize string input (trim, limit length)
    
    Args:
        text: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        return ""
    
    # Trim whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def sanitize_number(value: Any, default: float = 0.0) -> float:
    """
    Sanitize number input
    
    Args:
        value: Value to sanitize
        default: Default value if conversion fails
        
    Returns:
        Sanitized number
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def sanitize_integer(value: Any, default: int = 0) -> int:
    """
    Sanitize integer input
    
    Args:
        value: Value to sanitize
        default: Default value if conversion fails
        
    Returns:
        Sanitized integer
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def sanitize_coordinates(latitude: Any, longitude: Any) -> Tuple[float, float]:
    """
    Sanitize and clamp coordinates
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        Tuple of (sanitized_latitude, sanitized_longitude)
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        # Clamp to valid ranges
        lat = max(MIN_LATITUDE, min(lat, MAX_LATITUDE))
        lon = max(MIN_LONGITUDE, min(lon, MAX_LONGITUDE))
        
        return lat, lon
    except (ValueError, TypeError):
        return 0.0, 0.0


# ============================================================================
# Batch Validation
# ============================================================================

def validate_all(validations: List[Tuple[Any, str, callable]]) -> ValidationResult:
    """
    Run multiple validations and return first failure
    
    Args:
        validations: List of (value, field_name, validator_function) tuples
        
    Returns:
        ValidationResult (first failure or success if all pass)
        
    Example:
        result = validate_all([
            (latitude, "Latitude", validate_latitude),
            (city, "City", validate_city_name),
            (time_str, "Time", validate_time_string)
        ])
    """
    for value, field_name, validator in validations:
        try:
            result = validator(value)
            if not result:
                return result
        except Exception as e:
            return ValidationResult(False, f"{field_name} validation error: {e}")
    
    return ValidationResult(True)


# ============================================================================
# Utility Functions
# ============================================================================

def get_validation_errors(validations: List[Tuple[Any, str, callable]]) -> List[str]:
    """
    Get all validation errors (doesn't stop at first failure)
    
    Args:
        validations: List of (value, field_name, validator_function) tuples
        
    Returns:
        List of error messages (empty if all valid)
    """
    errors = []
    
    for value, field_name, validator in validations:
        try:
            result = validator(value)
            if not result:
                errors.append(result.error_message)
        except Exception as e:
            errors.append(f"{field_name} validation error: {e}")
    
    return errors


def is_valid_dict_structure(data: Dict[str, Any], required_keys: List[str]) -> ValidationResult:
    """
    Validate dictionary has required keys
    
    Args:
        data: Dictionary to validate
        required_keys: List of required key names
        
    Returns:
        ValidationResult
    """
    if not isinstance(data, dict):
        return ValidationResult(False, "Data must be a dictionary")
    
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        return ValidationResult(
            False,
            f"Missing required keys: {', '.join(missing_keys)}"
        )
    
    return ValidationResult(True)