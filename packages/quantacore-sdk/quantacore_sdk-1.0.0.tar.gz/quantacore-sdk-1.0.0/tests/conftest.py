"""
Pytest configuration and fixtures for QUAC 100 SDK tests.
"""

import pytest
import quantacore


@pytest.fixture(scope="session", autouse=True)
def initialize_library():
    """Initialize the library once per test session."""
    quantacore.initialize()
    yield
    quantacore.cleanup()


@pytest.fixture(scope="session")
def device():
    """Get a device for testing."""
    try:
        return quantacore.open_first_device()
    except quantacore.DeviceError:
        pytest.skip("No QUAC 100 device available")


@pytest.fixture
def kem(device):
    """Get KEM subsystem."""
    return device.kem()


@pytest.fixture
def sign(device):
    """Get Sign subsystem."""
    return device.sign()


@pytest.fixture
def hash(device):
    """Get Hash subsystem."""
    return device.hash()


@pytest.fixture
def random(device):
    """Get Random subsystem."""
    return device.random()