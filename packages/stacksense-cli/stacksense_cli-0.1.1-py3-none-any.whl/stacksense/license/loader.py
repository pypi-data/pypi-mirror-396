"""
License Loader - File Management
================================
Loads, saves, and manages license.ssx files.
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta

import httpx

from .validator import LicenseValidator, LicenseStatus, LicenseInfo, get_machine_id


# Configuration
STACKSENSE_DIR = Path.home() / ".stacksense"
LICENSE_FILE = STACKSENSE_DIR / "license.ssx"
BACKEND_URL = os.getenv("STACKSENSE_BACKEND_URL", "https://pilgrimstack-api.fly.dev")

# Refresh thresholds
REFRESH_AFTER_DAYS = 7  # Refresh if license older than 7 days
FORCE_REFRESH_DAYS = 30  # Force refresh after 30 days


class LicenseLoader:
    """
    Manages license file loading and refreshing.
    
    Flow:
    1. Try to load local license.ssx
    2. If valid and fresh (< 7 days), use it
    3. If stale (> 7 days), try to refresh from backend
    4. If refresh fails, continue with local if still valid
    5. If expired, prompt user to renew
    """
    
    def __init__(self):
        self.validator = LicenseValidator()
        self._ensure_dir()
    
    def _ensure_dir(self):
        """Ensure .stacksense directory exists."""
        STACKSENSE_DIR.mkdir(exist_ok=True)
    
    def load(self) -> Tuple[LicenseStatus, Optional[LicenseInfo]]:
        """
        Load and validate license.
        
        Returns:
            Tuple of (status, license_info or None)
        """
        # Check if license file exists
        if not LICENSE_FILE.exists():
            return LicenseStatus.NOT_FOUND, None
        
        try:
            # Load license
            license_data = self._load_file()
            if not license_data:
                return LicenseStatus.CORRUPTED, None
            
            # Validate
            status, info = self.validator.validate(license_data)
            
            # Check if refresh needed
            if status == LicenseStatus.VALID and info:
                days_old = (datetime.now().date() - info.issued).days
                
                if days_old >= REFRESH_AFTER_DAYS:
                    # Try to refresh
                    refreshed = self._try_refresh()
                    if refreshed:
                        # Re-validate refreshed license
                        license_data = self._load_file()
                        status, info = self.validator.validate(license_data)
            
            return status, info
            
        except Exception as e:
            return LicenseStatus.CORRUPTED, None
    
    def _load_file(self) -> Optional[dict]:
        """Load license file from disk."""
        try:
            content = LICENSE_FILE.read_text()
            return json.loads(content)
        except Exception:
            return None
    
    def save(self, license_json: str) -> bool:
        """
        Save license file to disk.
        
        Args:
            license_json: JSON string of license data
            
        Returns:
            True if saved successfully
        """
        try:
            self._ensure_dir()
            LICENSE_FILE.write_text(license_json)
            return True
        except Exception:
            return False
    
    def save_from_base64(self, license_b64: str) -> bool:
        """
        Save license from base64 encoded string.
        
        Args:
            license_b64: Base64 encoded license JSON
            
        Returns:
            True if saved successfully
        """
        try:
            license_json = base64.b64decode(license_b64).decode()
            return self.save(license_json)
        except Exception:
            return False
    
    def _try_refresh(self) -> bool:
        """
        Try to refresh license from backend.
        
        Returns:
            True if refresh successful
        """
        try:
            # Get current license key
            license_data = self._load_file()
            if not license_data:
                return False
            
            # We need the license key which isn't stored in the file
            # User must have it in config
            from ..core.config import Config
            config = Config()
            license_key = config.get("license_key", "")
            
            if not license_key:
                return False
            
            # Call backend
            machine_id = get_machine_id()
            
            response = httpx.post(
                f"{BACKEND_URL}/license/validate",
                json={
                    "license_key": license_key,
                    "machine_id": machine_id
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") and data.get("license_file"):
                    return self.save_from_base64(data["license_file"])
            
            return False
            
        except Exception:
            return False
    
    def exchange_key(self, license_key: str) -> Tuple[bool, str]:
        """
        Exchange license key for license file.
        
        This is the one-time key exchange:
        - User enters license key
        - Backend validates and returns license.ssx
        - License file is stored locally
        
        Args:
            license_key: Lemon Squeezy license key
            
        Returns:
            Tuple of (success, message)
        """
        try:
            machine_id = get_machine_id()
            
            response = httpx.post(
                f"{BACKEND_URL}/license/validate",
                json={
                    "license_key": license_key,
                    "machine_id": machine_id
                },
                timeout=15.0
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get("valid"):
                # Save license file
                if self.save_from_base64(data["license_file"]):
                    # Also save key to config for future refreshes
                    from ..core.config import Config
                    config = Config()
                    config.set("license_key", license_key)
                    config.save()
                    
                    return True, data.get("message", "License activated successfully!")
                else:
                    return False, "Failed to save license file"
            else:
                return False, data.get("message", "Invalid license key")
                
        except httpx.TimeoutException:
            return False, "Connection timeout. Please check your internet connection."
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def delete(self) -> bool:
        """Delete license file."""
        try:
            if LICENSE_FILE.exists():
                LICENSE_FILE.unlink()
            return True
        except Exception:
            return False
    
    def get_status_display(self) -> dict:
        """
        Get license status for CLI display.
        
        Returns:
            Dict with status info for display
        """
        status, info = self.load()
        
        if status == LicenseStatus.NOT_FOUND:
            return {
                "status": "free",
                "plan": "Free",
                "message": "No license. Using free tier.",
                "calls_limit": 50,
                "features": ["chat"]
            }
        
        if status == LicenseStatus.VALID and info:
            days_left = (info.expires - datetime.now().date()).days
            return {
                "status": "active",
                "plan": info.plan.title(),
                "email": info.user,
                "expires": info.expires.isoformat(),
                "days_left": max(days_left, 0),
                "calls_limit": info.calls_per_month,
                "features": info.features,
                "message": f"License valid for {days_left} days"
            }
        
        if status == LicenseStatus.GRACE and info:
            grace_days = (info.grace_until - datetime.now().date()).days
            return {
                "status": "grace",
                "plan": info.plan.title(),
                "message": f"⚠️ License expired! Grace period: {grace_days} days left",
                "calls_limit": info.calls_per_month,
                "features": info.features
            }
        
        if status == LicenseStatus.EXPIRED:
            return {
                "status": "expired",
                "plan": "Expired",
                "message": "🚫 License expired. Renew at stacksense.dev/upgrade",
                "calls_limit": 50,
                "features": ["chat"]
            }
        
        return {
            "status": "invalid",
            "plan": "Free",
            "message": "License invalid. Using free tier.",
            "calls_limit": 50,
            "features": ["chat"]
        }
