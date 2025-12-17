"""
Tests for library management functions.
"""

import pytest
import quantacore


class TestLibrary:
    """Test library initialization and management."""
    
    def test_version(self):
        """Test getting library version."""
        version = quantacore.get_version()
        assert version is not None
        assert isinstance(version, str)
        assert len(version) > 0
    
    def test_build_info(self):
        """Test getting build info."""
        info = quantacore.get_build_info()
        assert info is not None
        assert isinstance(info, str)
    
    def test_is_initialized(self):
        """Test initialization check."""
        assert quantacore.is_initialized()
    
    def test_device_count(self):
        """Test device count."""
        count = quantacore.get_device_count()
        assert isinstance(count, int)
        assert count >= 0
    
    def test_enumerate_devices(self):
        """Test device enumeration."""
        devices = quantacore.enumerate_devices()
        assert isinstance(devices, list)
        
        for dev in devices:
            assert isinstance(dev, quantacore.DeviceInfo)
            assert dev.index >= 0
            assert len(dev.model) > 0


class TestErrorCode:
    """Test error code enum."""
    
    def test_success_code(self):
        """Test SUCCESS error code."""
        assert quantacore.ErrorCode.SUCCESS == 0
    
    def test_error_message(self):
        """Test error message lookup."""
        msg = quantacore.ErrorCode.get_message(0)
        assert "success" in msg.lower()
        
        msg = quantacore.ErrorCode.get_message(-4)
        assert "not found" in msg.lower()


class TestInitFlags:
    """Test initialization flags."""
    
    def test_default_flags(self):
        """Test default flags value."""
        assert quantacore.InitFlags.DEFAULT != 0
    
    def test_flag_combination(self):
        """Test combining flags."""
        flags = quantacore.InitFlags.HARDWARE_ACCEL | quantacore.InitFlags.FIPS_MODE
        assert flags != 0