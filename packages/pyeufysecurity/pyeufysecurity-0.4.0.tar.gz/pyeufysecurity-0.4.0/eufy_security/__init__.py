"""Python library for Eufy Security cameras and devices.

Based on eufy-security-client by bropat.
"""

from .api import API, async_login
from .device import Camera, Station
from .errors import (
    CannotConnectError,
    CaptchaRequiredError,
    EufySecurityError,
    InvalidCaptchaError,
    InvalidCredentialsError,
    RequestError,
)

# Alias for Home Assistant integration compatibility
EufySecurityAPI = API

__all__ = [
    "API",
    "EufySecurityAPI",
    "async_login",
    "Camera",
    "Station",
    "EufySecurityError",
    "InvalidCredentialsError",
    "RequestError",
    "CannotConnectError",
    "CaptchaRequiredError",
    "InvalidCaptchaError",
]

__version__ = "0.4.0"
