"""
License Validator - RSA Signature Verification
==============================================
Verifies license files using embedded public key.
"""

import os
import json
import base64
import hashlib
from datetime import datetime, date
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


class LicenseStatus(Enum):
    """License validation status."""
    VALID = "valid"
    EXPIRED = "expired"
    GRACE = "grace"
    INVALID_SIGNATURE = "invalid_signature"
    INVALID_HASH = "invalid_hash"
    NOT_FOUND = "not_found"
    CORRUPTED = "corrupted"


@dataclass
class LicenseInfo:
    """Parsed license information."""
    sub_id: str
    plan: str
    user: str
    issued: date
    expires: date
    grace_until: date
    calls_per_month: int
    soft_cap: float
    hard_cap: float
    features: list
    machine_id: str
    status: LicenseStatus


# Embedded public key (ship with pip package)
# Generate with: python -m backend.license_signer
PUBLIC_KEY_PEM = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0placeholder0placeholder
0placeholder0placeholder0placeholder0placeholder0placeholder0placeholder
0placeholder0placeholder0placeholder0placeholder0placeholder0placeholder
0placeholder0placeholder0placeholder0placeholder0placeholder0placeholder
0placeholder0placeholder0placeholder0placeholder0placeholder0placeholder
PLACEHOLDER_REPLACE_WITH_ACTUAL_KEY
-----END PUBLIC KEY-----
""".strip()


class LicenseValidator:
    """
    Validates license files using RSA public key.
    
    Features:
    - RSA signature verification
    - SHA256 hash validation
    - Expiry checking with grace period
    - Offline-first validation
    """
    
    def __init__(self, public_key_pem: Optional[str] = None):
        """
        Initialize validator with public key.
        
        Args:
            public_key_pem: Optional override for public key
        """
        key_pem = public_key_pem or PUBLIC_KEY_PEM
        
        # Skip loading if placeholder
        if "PLACEHOLDER" in key_pem:
            self.public_key = None
        else:
            self.public_key = serialization.load_pem_public_key(
                key_pem.encode(),
                backend=default_backend()
            )
    
    def validate(self, license_data: dict) -> Tuple[LicenseStatus, Optional[LicenseInfo]]:
        """
        Validate a license file.
        
        Args:
            license_data: Parsed license JSON
            
        Returns:
            Tuple of (status, license_info or None)
        """
        try:
            # Extract signature
            signature_b64 = license_data.get("signature", "")
            if not signature_b64:
                return LicenseStatus.CORRUPTED, None
            
            # Create payload without signature for verification
            payload = {k: v for k, v in license_data.items() if k != "signature"}
            
            # Verify hash first (fast check)
            stored_hash = payload.get("hash", "")
            if stored_hash:
                payload_for_hash = {k: v for k, v in payload.items() if k != "hash"}
                computed_hash = self._compute_hash(payload_for_hash)
                if computed_hash != stored_hash:
                    return LicenseStatus.INVALID_HASH, None
            
            # Verify RSA signature
            if self.public_key:
                if not self._verify_signature(payload, signature_b64):
                    return LicenseStatus.INVALID_SIGNATURE, None
            
            # Parse license info
            info = self._parse_license(license_data)
            
            # Check expiry
            today = date.today()
            
            if today > info.grace_until:
                info.status = LicenseStatus.EXPIRED
                return LicenseStatus.EXPIRED, info
            
            if today > info.expires:
                info.status = LicenseStatus.GRACE
                return LicenseStatus.GRACE, info
            
            info.status = LicenseStatus.VALID
            return LicenseStatus.VALID, info
            
        except Exception as e:
            return LicenseStatus.CORRUPTED, None
    
    def _compute_hash(self, payload: dict) -> str:
        """Compute SHA256 hash of payload."""
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload_json.encode()).hexdigest()
    
    def _verify_signature(self, payload: dict, signature_b64: str) -> bool:
        """Verify RSA signature."""
        try:
            signature = base64.b64decode(signature_b64)
            payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            
            self.public_key.verify(
                signature,
                payload_json.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except Exception:
            return False
    
    def _parse_license(self, data: dict) -> LicenseInfo:
        """Parse license data into LicenseInfo."""
        limits = data.get("limits", {})
        
        return LicenseInfo(
            sub_id=data.get("sub_id", ""),
            plan=data.get("plan", "free"),
            user=data.get("user", ""),
            issued=self._parse_date(data.get("issued", "")),
            expires=self._parse_date(data.get("expires", "")),
            grace_until=self._parse_date(data.get("grace_until", "")),
            calls_per_month=limits.get("calls_per_month", 50),
            soft_cap=limits.get("soft_cap_multiplier", 1.2),
            hard_cap=limits.get("hard_cap_multiplier", 1.5),
            features=data.get("features", ["chat"]),
            machine_id=data.get("machine_id", ""),
            status=LicenseStatus.VALID
        )
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string to date object."""
        if not date_str:
            return date.today()
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return date.today()


def get_machine_id() -> str:
    """
    Generate unique machine identifier.
    Uses multiple factors for uniqueness.
    """
    import platform
    import uuid
    
    factors = [
        platform.node(),           # Hostname
        platform.machine(),        # CPU architecture
        str(uuid.getnode()),       # MAC address
        os.getenv("USER", ""),     # Username
    ]
    
    combined = ":".join(factors)
    return hashlib.sha256(combined.encode()).hexdigest()[:32]
