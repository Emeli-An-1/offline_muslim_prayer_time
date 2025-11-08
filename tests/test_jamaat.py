"""Tests for Jamaat time adjustment functionality"""
import pytest
from datetime import date
from services.praytimes import PrayerTimesCalculator


class TestJamaatAdjustments:
    """Test jamaat time adjustments"""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance"""
        return PrayerTimesCalculator()
    
    @pytest.fixture
    def base_prayer_times(self, calculator):
        """Get base prayer times for testing"""
        return calculator.calculate_prayer_times(
            latitude=40.7128,
            longitude=-74.0060,
            calculation_date=date(2025, 1, 1),
            timezone_name="America/New_York",
            method="ISNA"
        )
    
    def test_shift_mode_adjustment(self, calculator, base_prayer_times):
        """Test shift mode jamaat adjustment (minutes after adhan)"""
        jamaat_config = {
            "Fajr": {"mode": "shift", "minutes": 15, "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        fajr = result["prayers"]["Fajr"]
        assert fajr["jamaat"] is not None
        assert fajr["jamaat_mode"] == "shift"
        
        # Verify 15 minutes added
        adhan_parts = fajr["adhan"].split(":")
        jamaat_parts = fajr["jamaat"].split(":")
        
        adhan_mins = int(adhan_parts[0]) * 60 + int(adhan_parts[1])
        jamaat_mins = int(jamaat_parts[0]) * 60 + int(jamaat_parts[1])
        
        assert jamaat_mins - adhan_mins == 15
    
    def test_shift_mode_all_prayers(self, calculator, base_prayer_times):
        """Test shift mode for all prayers"""
        jamaat_config = {
            "Fajr": {"mode": "shift", "minutes": 15, "enabled": True},
            "Dhuhr": {"mode": "shift", "minutes": 10, "enabled": True},
            "Asr": {"mode": "shift", "minutes": 10, "enabled": True},
            "Maghrib": {"mode": "shift", "minutes": 5, "enabled": True},
            "Isha": {"mode": "shift", "minutes": 10, "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        # Check all prayers have jamaat times
        for prayer_name in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            prayer = result["prayers"][prayer_name]
            assert prayer["jamaat"] is not None
            assert prayer["jamaat_mode"] == "shift"
    
    def test_fixed_mode_adjustment(self, calculator, base_prayer_times):
        """Test fixed mode jamaat adjustment"""
        jamaat_config = {
            "Isha": {"mode": "fixed", "time": "20:30", "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        isha = result["prayers"]["Isha"]
        assert isha["jamaat"] == "20:30"
        assert isha["jamaat_mode"] == "fixed"
    
    def test_fixed_mode_different_times(self, calculator, base_prayer_times):
        """Test fixed mode with different times for multiple prayers"""
        jamaat_config = {
            "Fajr": {"mode": "fixed", "time": "05:45", "enabled": True},
            "Dhuhr": {"mode": "fixed", "time": "13:00", "enabled": True},
            "Isha": {"mode": "fixed", "time": "20:30", "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        assert result["prayers"]["Fajr"]["jamaat"] == "05:45"
        assert result["prayers"]["Dhuhr"]["jamaat"] == "13:00"
        assert result["prayers"]["Isha"]["jamaat"] == "20:30"
    
    def test_disabled_jamaat(self, calculator, base_prayer_times):
        """Test disabled jamaat"""
        jamaat_config = {
            "Dhuhr": {"mode": "shift", "minutes": 10, "enabled": False}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        dhuhr = result["prayers"]["Dhuhr"]
        assert dhuhr["jamaat"] is None
    
    def test_mixed_modes(self, calculator, base_prayer_times):
        """Test mixed jamaat modes"""
        jamaat_config = {
            "Fajr": {"mode": "fixed", "time": "05:45", "enabled": True},
            "Dhuhr": {"mode": "shift", "minutes": 10, "enabled": True},
            "Asr": {"mode": "shift", "minutes": 15, "enabled": True},
            "Maghrib": {"mode": "fixed", "time": "18:25", "enabled": True},
            "Isha": {"mode": "shift", "minutes": 10, "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        # Check fixed mode prayers
        assert result["prayers"]["Fajr"]["jamaat"] == "05:45"
        assert result["prayers"]["Fajr"]["jamaat_mode"] == "fixed"
        assert result["prayers"]["Maghrib"]["jamaat"] == "18:25"
        assert result["prayers"]["Maghrib"]["jamaat_mode"] == "fixed"
        
        # Check shift mode prayers
        assert result["prayers"]["Dhuhr"]["jamaat_mode"] == "shift"
        assert result["prayers"]["Asr"]["jamaat_mode"] == "shift"
        assert result["prayers"]["Isha"]["jamaat_mode"] == "shift"
    
    def test_shift_mode_negative_minutes(self, calculator, base_prayer_times):
        """Test shift mode with negative minutes (before adhan)"""
        jamaat_config = {
            "Fajr": {"mode": "shift", "minutes": -5, "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        fajr = result["prayers"]["Fajr"]
        assert fajr["jamaat"] is not None
        
        # Verify 5 minutes subtracted
        adhan_parts = fajr["adhan"].split(":")
        jamaat_parts = fajr["jamaat"].split(":")
        
        adhan_mins = int(adhan_parts[0]) * 60 + int(adhan_parts[1])
        jamaat_mins = int(jamaat_parts[0]) * 60 + int(jamaat_parts[1])
        
        # Handle day wraparound
        if jamaat_mins > adhan_mins:
            jamaat_mins -= 24 * 60
        
        assert abs(jamaat_mins - adhan_mins) == 5
    
    def test_shift_mode_large_offset(self, calculator, base_prayer_times):
        """Test shift mode with large minute offset"""
        jamaat_config = {
            "Dhuhr": {"mode": "shift", "minutes": 90, "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        dhuhr = result["prayers"]["Dhuhr"]
        assert dhuhr["jamaat"] is not None
        
        # Verify 90 minutes (1.5 hours) added
        adhan_parts = dhuhr["adhan"].split(":")
        jamaat_parts = dhuhr["jamaat"].split(":")
        
        adhan_hour = int(adhan_parts[0])
        adhan_min = int(adhan_parts[1])
        jamaat_hour = int(jamaat_parts[0])
        jamaat_min = int(jamaat_parts[1])
        
        adhan_total = adhan_hour * 60 + adhan_min
        jamaat_total = jamaat_hour * 60 + jamaat_min
        
        assert jamaat_total - adhan_total == 90
    
    def test_empty_jamaat_config(self, calculator, base_prayer_times):
        """Test with empty jamaat configuration"""
        jamaat_config = {}
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        # All jamaat times should remain None
        for prayer_name, prayer_data in result["prayers"].items():
            assert prayer_data["jamaat"] is None
    
    def test_partial_jamaat_config(self, calculator, base_prayer_times):
        """Test with partial jamaat configuration"""
        jamaat_config = {
            "Fajr": {"mode": "shift", "minutes": 15, "enabled": True},
            "Isha": {"mode": "fixed", "time": "20:00", "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        # Check configured prayers
        assert result["prayers"]["Fajr"]["jamaat"] is not None
        assert result["prayers"]["Isha"]["jamaat"] == "20:00"
        
        # Check non-configured prayers remain None
        assert result["prayers"]["Dhuhr"]["jamaat"] is None
        assert result["prayers"]["Asr"]["jamaat"] is None
    
    def test_invalid_prayer_name(self, calculator, base_prayer_times):
        """Test with invalid prayer name in config"""
        jamaat_config = {
            "InvalidPrayer": {"mode": "shift", "minutes": 10, "enabled": True}
        }
        
        # Should not raise error, just ignore invalid prayer
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        assert result is not None
    
    def test_jamaat_time_ordering(self, calculator, base_prayer_times):
        """Test that jamaat times come after adhan times"""
        jamaat_config = {
            "Fajr": {"mode": "shift", "minutes": 15, "enabled": True},
            "Dhuhr": {"mode": "shift", "minutes": 10, "enabled": True},
            "Asr": {"mode": "shift", "minutes": 10, "enabled": True},
            "Maghrib": {"mode": "shift", "minutes": 5, "enabled": True},
            "Isha": {"mode": "shift", "minutes": 10, "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        for prayer_name, prayer_data in result["prayers"].items():
            if prayer_data.get("jamaat"):
                adhan_time = prayer_data["adhan"]
                jamaat_time = prayer_data["jamaat"]
                
                # Convert to minutes for comparison
                adhan_parts = adhan_time.split(":")
                jamaat_parts = jamaat_time.split(":")
                
                adhan_mins = int(adhan_parts[0]) * 60 + int(adhan_parts[1])
                jamaat_mins = int(jamaat_parts[0]) * 60 + int(jamaat_parts[1])
                
                # Jamaat should be after adhan (positive shift)
                assert jamaat_mins >= adhan_mins
    
    def test_adhan_only_mode(self, calculator, base_prayer_times):
        """Test adhan_only mode (no jamaat)"""
        jamaat_config = {
            "Sunrise": {"mode": "adhan_only", "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config)
        
        # Sunrise should not have jamaat time
        sunrise = result["prayers"]["Sunrise"]
        assert sunrise["jamaat"] is None
    
    def test_bulk_enable_disable(self, calculator, base_prayer_times):
        """Test enabling/disabling multiple prayers"""
        # First enable all
        jamaat_config_enabled = {
            "Fajr": {"mode": "shift", "minutes": 15, "enabled": True},
            "Dhuhr": {"mode": "shift", "minutes": 10, "enabled": True},
            "Asr": {"mode": "shift", "minutes": 10, "enabled": True},
            "Maghrib": {"mode": "shift", "minutes": 5, "enabled": True},
            "Isha": {"mode": "shift", "minutes": 10, "enabled": True}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config_enabled)
        
        # All should have jamaat times
        for prayer_name in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            assert result["prayers"][prayer_name]["jamaat"] is not None
        
        # Now disable all
        jamaat_config_disabled = {
            "Fajr": {"mode": "shift", "minutes": 15, "enabled": False},
            "Dhuhr": {"mode": "shift", "minutes": 10, "enabled": False},
            "Asr": {"mode": "shift", "minutes": 10, "enabled": False},
            "Maghrib": {"mode": "shift", "minutes": 5, "enabled": False},
            "Isha": {"mode": "shift", "minutes": 10, "enabled": False}
        }
        
        result = calculator.apply_jamaat_adjustments(base_prayer_times, jamaat_config_disabled)
        
        # All should have None jamaat times
        for prayer_name in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            assert result["prayers"][prayer_name]["jamaat"] is None