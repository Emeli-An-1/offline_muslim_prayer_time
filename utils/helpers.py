"""
Helper Functions for PrayerOffline
Utility functions for time, date, formatting, and calculations
"""

import math
import logging
from datetime import datetime, date, time, timedelta
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path

try:
    from hijri_converter import Gregorian, Hijri
    HIJRI_AVAILABLE = True
except ImportError:
    HIJRI_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# Time & Date Helpers
# ============================================================================

def format_time(time_obj: time, format_24h: bool = True) -> str:
    """
    Format time object to string
    
    Args:
        time_obj: Time object to format
        format_24h: Use 24-hour format (True) or 12-hour format (False)
        
    Returns:
        Formatted time string
    """
    try:
        if format_24h:
            return time_obj.strftime("%H:%M")
        else:
            return time_obj.strftime("%I:%M %p")
    except Exception as e:
        logger.error(f"Failed to format time: {e}")
        return "N/A"


def parse_time(time_str: str) -> Optional[time]:
    """
    Parse time string to time object
    
    Args:
        time_str: Time string (HH:MM or HH:MM:SS)
        
    Returns:
        Time object or None if parsing fails
    """
    try:
        # Try HH:MM format
        if len(time_str) == 5:
            return datetime.strptime(time_str, "%H:%M").time()
        # Try HH:MM:SS format
        elif len(time_str) == 8:
            return datetime.strptime(time_str, "%H:%M:%S").time()
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to parse time '{time_str}': {e}")
        return None


def time_to_minutes(time_obj: time) -> int:
    """
    Convert time to minutes since midnight
    
    Args:
        time_obj: Time object
        
    Returns:
        Minutes since midnight
    """
    return time_obj.hour * 60 + time_obj.minute


def minutes_to_time(minutes: int) -> time:
    """
    Convert minutes since midnight to time object
    
    Args:
        minutes: Minutes since midnight
        
    Returns:
        Time object
    """
    hours = minutes // 60
    mins = minutes % 60
    return time(hour=hours % 24, minute=mins)


def add_minutes_to_time(time_obj: time, minutes: int) -> time:
    """
    Add minutes to a time object
    
    Args:
        time_obj: Original time
        minutes: Minutes to add (can be negative)
        
    Returns:
        New time object
    """
    total_minutes = time_to_minutes(time_obj) + minutes
    # Handle day overflow
    total_minutes = total_minutes % (24 * 60)
    return minutes_to_time(total_minutes)


def time_difference(time1: time, time2: time) -> int:
    """
    Calculate difference between two times in minutes
    
    Args:
        time1: First time
        time2: Second time
        
    Returns:
        Difference in minutes (time1 - time2)
    """
    minutes1 = time_to_minutes(time1)
    minutes2 = time_to_minutes(time2)
    return minutes1 - minutes2


def get_time_remaining(target_time: datetime) -> Tuple[int, int, int]:
    """
    Calculate time remaining until target time
    
    Args:
        target_time: Target datetime
        
    Returns:
        Tuple of (hours, minutes, seconds)
    """
    now = datetime.now()
    
    # If target is in the past, assume it's for tomorrow
    if target_time <= now:
        target_time += timedelta(days=1)
    
    time_diff = target_time - now
    hours = int(time_diff.total_seconds() // 3600)
    minutes = int((time_diff.total_seconds() % 3600) // 60)
    seconds = int(time_diff.total_seconds() % 60)
    
    return hours, minutes, seconds


def format_time_remaining(hours: int, minutes: int, seconds: int = 0, 
                         show_seconds: bool = False) -> str:
    """
    Format time remaining as string
    
    Args:
        hours: Hours
        minutes: Minutes
        seconds: Seconds
        show_seconds: Include seconds in output
        
    Returns:
        Formatted string (e.g., "2h 30m" or "2:30:45")
    """
    if show_seconds:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


# ============================================================================
# Hijri Date Helpers
# ============================================================================

def get_hijri_date(gregorian_date: date = None) -> Optional[str]:
    """
    Convert Gregorian date to Hijri date string
    
    Args:
        gregorian_date: Date to convert (defaults to today)
        
    Returns:
        Formatted Hijri date string or None if conversion fails
    """
    if not HIJRI_AVAILABLE:
        logger.warning("hijri-converter not available")
        return None
    
    try:
        if gregorian_date is None:
            gregorian_date = date.today()
        
        hijri = Gregorian(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day
        ).to_hijri()
        
        # Format: "15 Ramadan 1445 AH"
        return f"{hijri.day} {hijri.month_name()} {hijri.year} AH"
        
    except Exception as e:
        logger.error(f"Failed to convert to Hijri date: {e}")
        return None


def get_hijri_components(gregorian_date: date = None) -> Optional[Dict[str, Any]]:
    """
    Get Hijri date components
    
    Args:
        gregorian_date: Date to convert (defaults to today)
        
    Returns:
        Dictionary with day, month, year, month_name or None
    """
    if not HIJRI_AVAILABLE:
        return None
    
    try:
        if gregorian_date is None:
            gregorian_date = date.today()
        
        hijri = Gregorian(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day
        ).to_hijri()
        
        return {
            "day": hijri.day,
            "month": hijri.month,
            "year": hijri.year,
            "month_name": hijri.month_name(),
            "formatted": f"{hijri.day} {hijri.month_name()} {hijri.year} AH"
        }
        
    except Exception as e:
        logger.error(f"Failed to get Hijri components: {e}")
        return None


# ============================================================================
# Qibla Calculation Helpers
# ============================================================================

def calculate_qibla_direction(latitude: float, longitude: float,
                              kaaba_lat: float = 21.4225,
                              kaaba_lng: float = 39.8262) -> float:
    """
    Calculate Qibla direction from given location
    
    Args:
        latitude: Current location latitude
        longitude: Current location longitude
        kaaba_lat: Kaaba latitude (default: Mecca)
        kaaba_lng: Kaaba longitude (default: Mecca)
        
    Returns:
        Qibla direction in degrees (0-360, where 0 is North)
    """
    try:
        # Convert to radians
        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        lat2 = math.radians(kaaba_lat)
        lon2 = math.radians(kaaba_lng)
        
        # Calculate using great circle formula
        delta_lon = lon2 - lon1
        
        y = math.sin(delta_lon) * math.cos(lat2)
        x = (math.cos(lat1) * math.sin(lat2) - 
             math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))
        
        # Calculate bearing
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        
        # Normalize to 0-360
        bearing = (bearing + 360) % 360
        
        return bearing
        
    except Exception as e:
        logger.error(f"Failed to calculate Qibla direction: {e}")
        return 0.0


def calculate_distance_to_kaaba(latitude: float, longitude: float,
                                kaaba_lat: float = 21.4225,
                                kaaba_lng: float = 39.8262) -> float:
    """
    Calculate distance to Kaaba using Haversine formula
    
    Args:
        latitude: Current location latitude
        longitude: Current location longitude
        kaaba_lat: Kaaba latitude
        kaaba_lng: Kaaba longitude
        
    Returns:
        Distance in kilometers
    """
    try:
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1 = math.radians(latitude)
        lon1 = math.radians(longitude)
        lat2 = math.radians(kaaba_lat)
        lon2 = math.radians(kaaba_lng)
        
        # Differences
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Haversine formula
        a = (math.sin(dlat / 2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        
        return distance
        
    except Exception as e:
        logger.error(f"Failed to calculate distance to Kaaba: {e}")
        return 0.0


def format_distance(distance_km: float) -> str:
    """
    Format distance with appropriate unit
    
    Args:
        distance_km: Distance in kilometers
        
    Returns:
        Formatted distance string
    """
    if distance_km < 1:
        return f"{int(distance_km * 1000)} meters"
    elif distance_km < 100:
        return f"{distance_km:.1f} km"
    else:
        return f"{int(distance_km)} km"


def get_compass_direction(degrees: float) -> str:
    """
    Convert degrees to compass direction (N, NE, E, etc.)
    
    Args:
        degrees: Direction in degrees (0-360)
        
    Returns:
        Compass direction string
    """
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    ]
    
    index = round(degrees / 22.5) % 16
    return directions[index]


# ============================================================================
# Location Helpers
# ============================================================================

def format_coordinates(latitude: float, longitude: float, 
                      precision: int = 4) -> str:
    """
    Format coordinates as string
    
    Args:
        latitude: Latitude
        longitude: Longitude
        precision: Decimal places
        
    Returns:
        Formatted coordinates (e.g., "40.7128° N, 74.0060° W")
    """
    lat_dir = "N" if latitude >= 0 else "S"
    lon_dir = "E" if longitude >= 0 else "W"
    
    return f"{abs(latitude):.{precision}f}° {lat_dir}, {abs(longitude):.{precision}f}° {lon_dir}"


def is_valid_coordinates(latitude: float, longitude: float) -> bool:
    """
    Check if coordinates are valid
    
    Args:
        latitude: Latitude to check
        longitude: Longitude to check
        
    Returns:
        True if valid
    """
    return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)


# ============================================================================
# String Helpers
# ============================================================================

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_string(text: str) -> str:
    """
    Clean string (trim whitespace, normalize)
    
    Args:
        text: String to clean
        
    Returns:
        Cleaned string
    """
    return " ".join(text.split())


def is_arabic(text: str) -> bool:
    """
    Check if text contains Arabic characters
    
    Args:
        text: Text to check
        
    Returns:
        True if contains Arabic
    """
    return any('\u0600' <= char <= '\u06FF' for char in text)


# ============================================================================
# File Helpers
# ============================================================================

def ensure_directory(path: Path) -> bool:
    """
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
        
    Returns:
        True if directory exists or was created
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def get_file_size(path: Path) -> int:
    """
    Get file size in bytes
    
    Args:
        path: File path
        
    Returns:
        File size in bytes, or 0 if error
    """
    try:
        return path.stat().st_size if path.exists() else 0
    except Exception as e:
        logger.error(f"Failed to get file size for {path}: {e}")
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# ============================================================================
# Number Helpers
# ============================================================================

def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def lerp(start: float, end: float, t: float) -> float:
    """
    Linear interpolation between start and end
    
    Args:
        start: Start value
        end: End value
        t: Interpolation factor (0-1)
        
    Returns:
        Interpolated value
    """
    return start + (end - start) * clamp(t, 0.0, 1.0)


def map_range(value: float, in_min: float, in_max: float,
              out_min: float, out_max: float) -> float:
    """
    Map value from one range to another
    
    Args:
        value: Input value
        in_min: Input range minimum
        in_max: Input range maximum
        out_min: Output range minimum
        out_max: Output range maximum
        
    Returns:
        Mapped value
    """
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


# ============================================================================
# Debug Helpers
# ============================================================================

def log_dict(data: Dict, title: str = "Dictionary", level: str = "INFO"):
    """
    Log dictionary contents in readable format
    
    Args:
        data: Dictionary to log
        title: Log title
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"{title}:")
    for key, value in data.items():
        log_func(f"  {key}: {value}")


def format_exception(exception: Exception) -> str:
    """
    Format exception for user display
    
    Args:
        exception: Exception to format
        
    Returns:
        User-friendly error message
    """
    error_type = type(exception).__name__
    error_msg = str(exception)
    return f"{error_type}: {error_msg}"


# ============================================================================
# List Helpers
# ============================================================================

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """
    Safely get dictionary value with default
    
    Args:
        dictionary: Dictionary to query
        key: Key to get
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    try:
        return dictionary.get(key, default)
    except Exception:
        return default