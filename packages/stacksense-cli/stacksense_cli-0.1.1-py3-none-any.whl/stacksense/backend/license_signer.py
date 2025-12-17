"""
License Signer - RSA Signing Module
===================================
Generates and signs license files with RSA private key.
"""

import os
import json
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

from schemas import LicensePayload, LicenseLimits
from models import PLAN_LIMITS


class LicenseSigner:
    """
    RSA License Signer.
    
    - Generates license payloads
    - Signs with RSA private key
    - Creates hash for tamper detection
    """
    
    def __init__(self, private_key_pem: Optional[str] = None):
        """
        Initialize signer with RSA private key.
        
        Args:
            private_key_pem: PEM-encoded RSA private key (from env)
        """
        if private_key_pem:
            self.private_key = serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None,
                backend=default_backend()
            )
        else:
            # Load from environment
            key_pem = os.getenv("RSA_PRIVATE_KEY", "")
            if key_pem:
                self.private_key = serialization.load_pem_private_key(
                    key_pem.encode(),
                    password=None,
                    backend=default_backend()
                )
            else:
                raise ValueError("RSA_PRIVATE_KEY environment variable not set")
    
    def create_payload(
        self,
        subscription_id: str,
        plan: str,
        email: str,
        machine_id: str,
        validity_days: int = 30,
        grace_days: int = 7
    ) -> LicensePayload:
        """
        Create license payload.
        
        Args:
            subscription_id: Lemon Squeezy subscription ID
            plan: Plan name (starter|pro|ultra|unlimited)
            email: Customer email
            machine_id: SHA256 hash of machine identifier
            validity_days: Days until license expires
            grace_days: Grace period after expiry
            
        Returns:
            LicensePayload with all fields populated
        """
        now = datetime.utcnow()
        expires = now + timedelta(days=validity_days)
        grace_until = expires + timedelta(days=grace_days)
        
        # Get plan limits
        plan_config = PLAN_LIMITS.get(plan, PLAN_LIMITS["starter"])
        
        limits = LicenseLimits(
            calls_per_month=plan_config["calls_per_month"],
            soft_cap_multiplier=1.2,
            hard_cap_multiplier=1.5,
            resets_on="monthly"
        )
        
        payload = LicensePayload(
            sub_id=subscription_id,
            plan=plan,
            user=email,
            issued=now.strftime("%Y-%m-%d"),
            expires=expires.strftime("%Y-%m-%d"),
            grace_until=grace_until.strftime("%Y-%m-%d"),
            limits=limits,
            features=plan_config["features"],
            machine_id=machine_id,
            version="1.0"
        )
        
        return payload
    
    def compute_hash(self, payload: LicensePayload) -> str:
        """
        Compute SHA256 hash of payload.
        
        Args:
            payload: License payload (without hash field)
            
        Returns:
            SHA256 hex digest
        """
        # Create copy without hash field
        payload_dict = payload.model_dump(exclude={"hash"})
        payload_json = json.dumps(payload_dict, sort_keys=True, separators=(',', ':'))
        
        return hashlib.sha256(payload_json.encode()).hexdigest()
    
    def sign_payload(self, payload: LicensePayload) -> str:
        """
        Sign payload with RSA private key.
        
        Args:
            payload: Complete license payload (with hash)
            
        Returns:
            Base64-encoded RSA signature
        """
        payload_json = json.dumps(
            payload.model_dump(),
            sort_keys=True,
            separators=(',', ':')
        )
        
        signature = self.private_key.sign(
            payload_json.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()
    
    def create_license_file(
        self,
        subscription_id: str,
        plan: str,
        email: str,
        machine_id: str,
        validity_days: int = 30
    ) -> tuple[str, str, str]:
        """
        Create complete license file.
        
        Args:
            subscription_id: Lemon Squeezy subscription ID
            plan: Plan name
            email: Customer email
            machine_id: Machine identifier hash
            validity_days: Days until expiry
            
        Returns:
            Tuple of (license_json, hash, signature)
        """
        # Create payload
        payload = self.create_payload(
            subscription_id=subscription_id,
            plan=plan,
            email=email,
            machine_id=machine_id,
            validity_days=validity_days
        )
        
        # Compute hash
        payload.hash = self.compute_hash(payload)
        
        # Sign
        signature = self.sign_payload(payload)
        
        # Create final license file
        license_data = {
            **payload.model_dump(),
            "signature": signature
        }
        
        license_json = json.dumps(license_data, indent=2)
        
        return license_json, payload.hash, signature


def generate_rsa_keypair() -> tuple[str, str]:
    """
    Generate new RSA keypair for license signing.
    
    Returns:
        Tuple of (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    
    return private_pem, public_pem


if __name__ == "__main__":
    # Generate keypair for initial setup
    private_key, public_key = generate_rsa_keypair()
    print("=== PRIVATE KEY (keep secret, add to .env) ===")
    print(private_key)
    print("\n=== PUBLIC KEY (ship with pip package) ===")
    print(public_key)
