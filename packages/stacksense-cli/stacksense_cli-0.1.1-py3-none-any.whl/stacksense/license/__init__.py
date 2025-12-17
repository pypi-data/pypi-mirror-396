"""
StackSense License System
=========================
Client-side license validation, caching, and usage tracking.
"""

__version__ = "1.0.0"

from .validator import LicenseValidator, LicenseStatus
from .loader import LicenseLoader
from .usage import (
    UsageTracker, 
    check_limit,
    check_feature_access,
    is_feature_locked,
    get_locked_features,
    get_available_features,
    FEATURE_NAMES
)

__all__ = [
    "LicenseValidator",
    "LicenseStatus", 
    "LicenseLoader",
    "UsageTracker",
    "check_limit",
    "check_feature_access",
    "is_feature_locked",
    "get_locked_features",
    "get_available_features",
    "FEATURE_NAMES"
]
