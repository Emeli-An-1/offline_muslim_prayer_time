"""
Prayer Times Calculator - Offline Prayer Time Calculation Engine
FIXED: Class renamed from PrayerTimesService to PrayerTimesCalculator
FIXED: Method names to match dashboard_view.py expectations
FIXED: Return structure to match project spec
"""

import logging
import math
from datetime import datetime, timedelta, date, time as time_obj
from typing import Dict, Optional, Any
import pytz

logger = logging.getLogger(__name__)


class PrayerTimesCalculator:  # FIXED: Was PrayerTimesService
    """Calculate prayer times using astronomical formulas"""
    
    PRAYER_ORDER = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    
    METHODS = {
        "MWL": {"name": "Muslim World League", "fajr": 18.0, "isha": 17.0},
        "ISNA": {"name": "Islamic Society of North America", "fajr": 15.0, "isha": 15.0},
        "Egypt": {"name": "Egyptian General Authority", "fajr": 19.5, "isha": 17.5},
        "Makkah": {"name": "Umm Al-Qura", "fajr": 18.5, "isha": "90 min"},
        "Karachi": {"name": "University of Karachi", "fajr": 18.0, "isha": 18.0},
        "Tehran": {"name": "Institute of Geophysics", "fajr": 17.7, "isha": 14.0}
    }
    
    def __init__(self, storage_service=None):
        self.storage = storage_service
        logger.info("PrayerTimesCalculator initialized")
    
    def calculate_prayer_times(  # FIXED: Method name standardized
        self,
        latitude: float,
        longitude: float,
        calculation_date: date,
        timezone_name: str = "UTC",
        method: str = "ISNA",
        asr_method: str = "Standard",
        high_lat_rule: str = "None"
    ) -> Dict[str, Any]:
        """
        Calculate prayer times for specific date and location
        
        Returns:
            {
                "date": "2025-10-26",
                "location": {...},
                "method": "ISNA",
                "prayers": {
                    "Fajr": {"adhan": "05:30", "jamaat": None, "jamaat_mode": None},
                    ...
                }
            }
        """
        try:
            # Get timezone
            try:
                tz = pytz.timezone(timezone_name)
                local_dt = tz.localize(datetime.combine(calculation_date, datetime.min.time()))
                utc_offset = local_dt.utcoffset().total_seconds() / 3600
            except:
                tz = pytz.UTC
                utc_offset = 0
                logger.warning(f"Invalid timezone {timezone_name}, using UTC")
            
            # Get calculation parameters
            params = self.METHODS.get(method, self.METHODS["ISNA"])
            
            # Calculate times
            times = self._calculate_times(
                calculation_date, latitude, longitude, utc_offset, params, asr_method
            )
            
            # Build return structure
            result = {
                "date": calculation_date.isoformat(),
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone_name
                },
                "method": method,
                "prayers": {}
            }
            
            # Ensure all 6 prayers present in correct order
            for prayer_name in self.PRAYER_ORDER:
                prayer_time = times.get(prayer_name, "00:00")
                result["prayers"][prayer_name] = {
                    "adhan": prayer_time,
                    "jamaat": None,
                    "jamaat_mode": None
                }
            
            logger.info(f"Prayer times calculated for {calculation_date}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating prayer times: {e}", exc_info=True)
            raise
    
    def _calculate_times(
        self, date: date, lat: float, lng: float, offset: float, 
        params: Dict, asr_method: str
    ) -> Dict[str, str]:
        """Internal calculation using astronomical formulas"""
        # Julian date
        jd = self._julian_date(date.year, date.month, date.day)
        D = jd - 2451545.0
        
        # Sun position
        L = (280.460 + 0.9856474 * D) % 360
        g = (357.528 + 0.9856003 * D) % 360
        lambda_sun = (L + 1.915 * self._dsin(g) + 0.020 * self._dsin(2 * g)) % 360
        epsilon = 23.439 - 0.0000004 * D
        
        # Declination & Equation of Time
        declination = self._darcsin(self._dsin(epsilon) * self._dsin(lambda_sun))
        RA = self._darctan2(self._dcos(epsilon) * self._dsin(lambda_sun), self._dcos(lambda_sun))
        EqT = (L - RA) / 15.0
        if EqT > 12: EqT -= 24
        elif EqT < -12: EqT += 24
        
        times = {}
        
        # Dhuhr (Solar Noon)
        times["Dhuhr"] = self._time_to_string(12 + offset - (lng / 15.0) - EqT)
        
        # Sunrise
        sunrise_angle = 0.8333
        sunrise_time = self._sun_angle_time(declination, lat, sunrise_angle, True)
        times["Sunrise"] = self._time_to_string(sunrise_time + 12 + offset - (lng / 15.0) - EqT)
        
        # Maghrib (Sunset)
        sunset_time = self._sun_angle_time(declination, lat, sunrise_angle, False)
        times["Maghrib"] = self._time_to_string(sunset_time + 12 + offset - (lng / 15.0) - EqT)
        
        # Fajr
        fajr_angle = params["fajr"]
        fajr_time = self._sun_angle_time(declination, lat, fajr_angle, True)
        times["Fajr"] = self._time_to_string(fajr_time + 12 + offset - (lng / 15.0) - EqT)
        
        # Isha
        if isinstance(params.get("isha"), str):
            maghrib_minutes = self._time_to_minutes(times["Maghrib"])
            times["Isha"] = self._minutes_to_time(maghrib_minutes + 90)
        else:
            isha_angle = params.get("isha", 15.0)
            isha_time = self._sun_angle_time(declination, lat, isha_angle, False)
            times["Isha"] = self._time_to_string(isha_time + 12 + offset - (lng / 15.0) - EqT)
        
        # Asr
        shadow_factor = 2 if asr_method == "Hanafi" else 1
        asr_time = self._asr_time(declination, lat, shadow_factor)
        times["Asr"] = self._time_to_string(asr_time + 12 + offset - (lng / 15.0) - EqT)
        
        return times
    
    def apply_jamaat_adjustments(
        self, prayer_times: Dict[str, Any], jamaat_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply Jamaat time adjustments"""
        if not jamaat_config:
            logger.warning("No jamaat config provided")
            return prayer_times
        
        for prayer_name, prayer_data in prayer_times["prayers"].items():
            if prayer_name == "Sunrise":
                continue
            
            config = jamaat_config.get(prayer_name)
            if not config:
                continue
            
            if not config.get("enabled", False):
                continue
            
            mode = config.get("mode", "shift")
            adhan_time = prayer_data.get("adhan")
            
            if not adhan_time or not isinstance(adhan_time, str):
                logger.warning(f"Invalid adhan time for {prayer_name}: {adhan_time}")
                continue
            
            try:
                if mode == "fixed":
                    jamaat_time = config.get("time")
                    if jamaat_time and self._is_valid_time(jamaat_time):
                        prayer_data["jamaat"] = jamaat_time
                        prayer_data["jamaat_mode"] = "fixed"
                
                elif mode == "shift":
                    minutes = config.get("minutes")
                    if minutes is None:
                        minutes = 10
                    
                    adhan_minutes = self._time_to_minutes(adhan_time)
                    if adhan_minutes is not None:
                        prayer_data["jamaat"] = self._minutes_to_time(adhan_minutes + int(minutes))
                        prayer_data["jamaat_mode"] = "shift"
                    else:
                        logger.error(f"Failed to parse adhan time for {prayer_name}: {adhan_time}")
            
            except Exception as e:
                logger.error(f"Error applying Jamaat for {prayer_name}: {e}", exc_info=True)
        
        return prayer_times
    
    # Helper methods
    def _julian_date(self, year: int, month: int, day: int) -> float:
        if month <= 2:
            year -= 1
            month += 12
        A = math.floor(year / 100.0)
        B = 2 - A + math.floor(A / 4.0)
        return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5
    
    def _dsin(self, d: float) -> float:
        return math.sin(math.radians(d))
    
    def _dcos(self, d: float) -> float:
        return math.cos(math.radians(d))
    
    def _darcsin(self, x: float) -> float:
        return math.degrees(math.asin(max(-1, min(1, x))))
    
    def _darctan2(self, y: float, x: float) -> float:
        return math.degrees(math.atan2(y, x)) % 360
    
    def _sun_angle_time(self, declination: float, latitude: float, angle: float, morning: bool) -> float:
        try:
            cos_h = (self._dcos(90 + angle) - self._dsin(declination) * self._dsin(latitude)) / (
                self._dcos(declination) * self._dcos(latitude)
            )
            cos_h = max(-1, min(1, cos_h))
            hour_angle = math.degrees(math.acos(cos_h))
            return -hour_angle / 15.0 if morning else hour_angle / 15.0
        except:
            return -6 if morning else 6
    
    def _asr_time(self, declination: float, latitude: float, shadow_factor: int) -> float:
        try:
            t = shadow_factor + math.tan(math.radians(abs(latitude - declination)))
            if t <= 0: t = 0.01
            asr_altitude = math.degrees(math.atan(1.0 / t))
            cos_h = (self._dsin(asr_altitude) - self._dsin(declination) * self._dsin(latitude)) / (
                self._dcos(declination) * self._dcos(latitude)
            )
            cos_h = max(-1, min(1, cos_h))
            return math.degrees(math.acos(cos_h)) / 15.0
        except:
            return 3.0
    
    def _time_to_string(self, time_decimal: float) -> str:
        time_decimal = time_decimal % 24
        hours = int(time_decimal)
        minutes = int(round((time_decimal - hours) * 60))
        if minutes == 60:
            hours = (hours + 1) % 24
            minutes = 0
        return f"{hours:02d}:{minutes:02d}"
    
    def _time_to_minutes(self, time_str: str) -> Optional[int]:
        try:
            if not time_str:
                return None
            parts = time_str.split(":")
            if len(parts) != 2:
                return None
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return None
    
    def _minutes_to_time(self, total_minutes: int) -> str:
        total_minutes = total_minutes % (24 * 60)
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    
    def _is_valid_time(self, time_str: str) -> bool:
        try:
            parts = time_str.split(":")
            if len(parts) != 2: return False
            hours, minutes = int(parts[0]), int(parts[1])
            return 0 <= hours < 24 and 0 <= minutes < 60
        except:
            return False