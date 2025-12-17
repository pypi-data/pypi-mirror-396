"""
Credit Storage - Encrypted Local Storage
=========================================
Device-bound encrypted storage for credit tracking.
Prevents tampering and abuse.
"""

import os
import json
import hashlib
import hmac
import platform
import uuid
from pathlib import Path
from typing import Optional, Any
from dataclasses import asdict
from datetime import datetime

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


STACKSENSE_DIR = Path.home() / ".stacksense"
CREDITS_FILE = STACKSENSE_DIR / "credits.dat"
BACKUP_FILE = STACKSENSE_DIR / ".credits_backup.dat"


def get_device_id() -> str:
    """
    Generate unique device identifier.
    
    Uses:
    - MAC address
    - Hostname
    - Platform info
    
    Returns:
        SHA256 hash of device factors
    """
    factors = [
        str(uuid.getnode()),       # MAC address
        platform.node(),           # Hostname
        platform.system(),         # OS
        os.getenv("USER", ""),     # Username
    ]
    
    combined = ":".join(factors)
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


def _derive_key(device_id: str) -> bytes:
    """Derive encryption key from device ID."""
    if not HAS_CRYPTO:
        return b""
    
    salt = b"stacksense_credits_v1"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(device_id.encode()))
    return key


class CreditStorage:
    """
    Encrypted local credit storage.
    
    Security features:
    - AES encryption with device-derived key
    - HMAC for tamper detection
    - Device binding
    """
    
    def __init__(self):
        self.device_id = get_device_id()
        self._fernet: Optional[Any] = None
        
        if HAS_CRYPTO:
            key = _derive_key(self.device_id)
            self._fernet = Fernet(key)
        
        self._ensure_dir()
    
    def _ensure_dir(self):
        """Ensure storage directory exists."""
        STACKSENSE_DIR.mkdir(exist_ok=True)
    
    def save(self, state) -> bool:
        """
        Save credit state to encrypted file.
        
        Args:
            state: CreditState dataclass
            
        Returns:
            True if saved successfully
        """
        try:
            data = asdict(state)
            data["_timestamp"] = datetime.now().isoformat()
            data["_device"] = self.device_id
            
            json_data = json.dumps(data, indent=2)
            
            if self._fernet:
                # Encrypt
                encrypted = self._fernet.encrypt(json_data.encode())
                CREDITS_FILE.write_bytes(encrypted)
                BACKUP_FILE.write_bytes(encrypted)
            else:
                # Fallback: obfuscated JSON with HMAC
                hmac_key = self.device_id.encode()
                signature = hmac.new(hmac_key, json_data.encode(), hashlib.sha256).hexdigest()
                
                wrapped = {
                    "data": json_data,
                    "hmac": signature,
                    "device": self.device_id[:8]
                }
                CREDITS_FILE.write_text(json.dumps(wrapped))
            
            return True
            
        except Exception as e:
            return False
    
    def load(self) -> Optional[Any]:
        """
        Load credit state from encrypted file.
        
        Returns:
            CreditState or None if not found/invalid
        """
        if not CREDITS_FILE.exists():
            return None
        
        try:
            if self._fernet:
                # Decrypt
                encrypted = CREDITS_FILE.read_bytes()
                json_data = self._fernet.decrypt(encrypted).decode()
                data = json.loads(json_data)
            else:
                # Fallback: verify HMAC
                wrapped = json.loads(CREDITS_FILE.read_text())
                
                hmac_key = self.device_id.encode()
                expected = hmac.new(hmac_key, wrapped["data"].encode(), hashlib.sha256).hexdigest()
                
                if not hmac.compare_digest(expected, wrapped["hmac"]):
                    # Tampered
                    return None
                
                data = json.loads(wrapped["data"])
            
            # Verify device
            if data.get("_device") and data["_device"] != self.device_id:
                # Different device - require recovery
                return None
            
            # Convert to state
            from .tracker import CreditState
            
            return CreditState(
                email=data.get("email", ""),
                device_id=data.get("device_id", self.device_id),
                credits_total=data.get("credits_total", 0),
                credits_used=data.get("credits_used", 0),
                credits_used_since_sync=data.get("credits_used_since_sync", 0),
                last_sync=data.get("last_sync", ""),
                redeemed_keys=data.get("redeemed_keys", []),
                is_free_tier=data.get("is_free_tier", True)
            )
            
        except Exception as e:
            # Try backup
            return self._load_backup()
    
    def _load_backup(self) -> Optional[Any]:
        """Try to load from backup file."""
        if not BACKUP_FILE.exists():
            return None
        
        try:
            if self._fernet:
                encrypted = BACKUP_FILE.read_bytes()
                json_data = self._fernet.decrypt(encrypted).decode()
                data = json.loads(json_data)
                
                from .tracker import CreditState
                
                return CreditState(
                    email=data.get("email", ""),
                    device_id=data.get("device_id", self.device_id),
                    credits_total=data.get("credits_total", 0),
                    credits_used=data.get("credits_used", 0),
                    credits_used_since_sync=data.get("credits_used_since_sync", 0),
                    last_sync=data.get("last_sync", ""),
                    redeemed_keys=data.get("redeemed_keys", []),
                    is_free_tier=data.get("is_free_tier", True)
                )
        except:
            pass
        
        return None
    
    def verify_device(self) -> bool:
        """
        Verify current device matches stored device.
        
        Returns:
            True if device matches or no stored device
        """
        if not CREDITS_FILE.exists():
            return True
        
        state = self.load()
        if state is None:
            return False
        
        return state.device_id == self.device_id
    
    def reset(self) -> bool:
        """Reset local storage (for recovery)."""
        try:
            if CREDITS_FILE.exists():
                CREDITS_FILE.unlink()
            if BACKUP_FILE.exists():
                BACKUP_FILE.unlink()
            return True
        except:
            return False
