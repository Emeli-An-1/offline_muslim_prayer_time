"""
Location Service - Handles location detection and management
FIXED: Added get_current_location() alias for compatibility
FIXED: Standardized method names
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class LocationService:
    """Manages user location for prayer time calculations"""
    
    KAABA_LAT = 21.4225
    KAABA_LON = 39.8262
    
    def __init__(self, storage_service=None):
        self.storage = storage_service
        self._current_location = None
        
        if self.storage:
            saved_location = self.storage.get("location", {})
            if saved_location.get("latitude") and saved_location.get("longitude"):
                self._current_location = saved_location
                logger.info(f"Loaded saved location: {saved_location.get('city', 'Unknown')}")
        
        logger.info("Location Service initialized")
    
    def get_location(self) -> Optional[Dict]:
        """Get current location"""
        return self._current_location
    
    def get_current_location(self) -> Optional[Dict]:  # FIXED: Added alias
        """Alias for get_location() - for compatibility with views"""
        return self.get_location()
    
    def set_location(
        self,
        latitude: float,
        longitude: float,
        city: str = None,
        country: str = None,
        timezone: str = None
    ) -> bool:
        """Set location manually"""
        try:
            if not (-90 <= latitude <= 90):
                raise ValueError(f"Invalid latitude: {latitude}")
            if not (-180 <= longitude <= 180):
                raise ValueError(f"Invalid longitude: {longitude}")
            
            if not timezone:
                timezone = self._estimate_timezone(longitude)
            
            location = {
                "latitude": latitude,
                "longitude": longitude,
                "city": city or "Manual Location",
                "country": country or "Unknown",
                "timezone": timezone,
                "updated_at": datetime.now().isoformat()
            }
            
            self._current_location = location
            
            if self.storage:
                self.storage.set("location", location)
            
            logger.info(f"Location set: {latitude}, {longitude} - {city}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting location: {e}")
            return False
    
    def _estimate_timezone(self, longitude: float) -> str:
        """Estimate timezone from longitude"""
        offset_hours = round(longitude / 15)
        timezone_map = {
            -5: "America/New_York", -6: "America/Chicago", -7: "America/Denver",
            -8: "America/Los_Angeles", 0: "Europe/London", 1: "Europe/Paris",
            2: "Europe/Athens", 3: "Asia/Riyadh", 4: "Asia/Dubai",
            5: "Asia/Karachi", 6: "Asia/Dhaka", 7: "Asia/Bangkok",
            8: "Asia/Singapore", 9: "Asia/Tokyo", 10: "Australia/Sydney"
        }
        return timezone_map.get(offset_hours, "UTC")
    
    def calculate_qibla_direction(
        self, latitude: Optional[float] = None, longitude: Optional[float] = None
    ) -> Dict[str, float]:
        """Calculate Qibla direction from current or specified location"""
        try:
            if latitude is None or longitude is None:
                if not self._current_location:
                    raise ValueError("No location available")
                latitude = self._current_location["latitude"]
                longitude = self._current_location["longitude"]
            
            import math
            lat1 = math.radians(latitude)
            lon1 = math.radians(longitude)
            lat2 = math.radians(self.KAABA_LAT)
            lon2 = math.radians(self.KAABA_LON)
            
            dlon = lon2 - lon1
            y = math.sin(dlon) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
            
            bearing = math.degrees(math.atan2(y, x))
            bearing = (bearing + 360) % 360
            
            dlat = lat2 - lat1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            distance_km = 6371 * c
            
            return {
                "qibla_direction": round(bearing, 2),
                "distance_km": round(distance_km, 2),
                "kaaba_lat": self.KAABA_LAT,
                "kaaba_lon": self.KAABA_LON
            }
        except Exception as e:
            logger.error(f"Error calculating Qibla: {e}")
            return {"qibla_direction": 0.0, "distance_km": 0.0, "error": str(e)}