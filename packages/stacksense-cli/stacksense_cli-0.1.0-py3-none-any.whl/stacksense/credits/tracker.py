"""
Credit Tracker - Pay-Per-Use System
====================================
Tracks credits locally with encrypted storage.
Syncs with backend every 100 credits or 24 hours.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Tuple, Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .storage import CreditStorage, get_device_id


# Configuration
STACKSENSE_DIR = Path.home() / ".stacksense"
FREE_CREDITS = 250
SYNC_INTERVAL_CREDITS = 100
SYNC_INTERVAL_HOURS = 24
MAX_DEVICES_PER_KEY = 3


# Credit Bundles
CREDIT_BUNDLES = {
    "starter": {"price": 0, "credits": 250, "description": "Free tier"},
    "basic": {"price": 20, "credits": 5000, "description": "Solo devs"},
    "power": {"price": 50, "credits": 12000, "description": "Heavy users"},
    "pro_stack": {"price": 100, "credits": 25000, "description": "Agencies"},
}


# Call costs per operation
CALL_COSTS = {
    # Free
    "ask_user": 0,
    
    # Basic (1 credit)
    "chat": 1,
    "get_diagram": 1,
    "read_file": 1,
    "search_code": 1,
    
    # Medium (2-3 credits)
    "memory_read": 1,
    "memory_write": 2,
    "web_search": 3,
    "write_file": 3,
    "run_command": 3,
    
    # Premium (4-5 credits)
    "diagram_generate": 4,
    "agent": 5,
    "repo_scan": 5,
}


@dataclass
class CreditState:
    """Local credit state."""
    email: str
    device_id: str
    credits_total: int
    credits_used: int
    credits_used_since_sync: int
    last_sync: str
    redeemed_keys: list
    is_free_tier: bool


class CreditTracker:
    """
    Tracks credits for pay-per-use billing.
    
    Features:
    - Local encrypted storage
    - Device binding
    - Automatic sync with backend
    - Free tier auto-provisioning
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.storage = CreditStorage()
        self._state: Optional[CreditState] = None
        self._ensure_dir()
    
    def _ensure_dir(self):
        """Ensure .stacksense directory exists."""
        STACKSENSE_DIR.mkdir(exist_ok=True)
    
    def _load_state(self) -> CreditState:
        """Load or initialize credit state."""
        if self._state is not None:
            return self._state
        
        state = self.storage.load()
        
        if state is None:
            # First run - provision free tier
            device_id = get_device_id()
            state = CreditState(
                email="",
                device_id=device_id,
                credits_total=FREE_CREDITS,
                credits_used=0,
                credits_used_since_sync=0,
                last_sync=datetime.now().isoformat(),
                redeemed_keys=[],
                is_free_tier=True
            )
            self.storage.save(state)
            
            if self.debug:
                print(f"[Credits] Provisioned free tier: {FREE_CREDITS} credits")
        
        self._state = state
        return state
    
    def _save_state(self):
        """Save current state."""
        if self._state:
            self.storage.save(self._state)
    
    def get_balance(self) -> Dict:
        """
        Get current credit balance.
        
        Returns:
            Dict with balance info
        """
        state = self._load_state()
        remaining = state.credits_total - state.credits_used
        
        return {
            "credits_total": state.credits_total,
            "credits_used": state.credits_used,
            "credits_remaining": remaining,
            "is_free_tier": state.is_free_tier,
            "email": state.email if not state.is_free_tier else None,
            "needs_sync": self._needs_sync(state),
        }
    
    def use_credits(self, action: str) -> Tuple[bool, int, Optional[str]]:
        """
        Deduct credits for an action.
        
        Args:
            action: Action type (chat, web_search, diagram, etc.)
            
        Returns:
            Tuple of (allowed, remaining, warning_message)
        """
        state = self._load_state()
        cost = CALL_COSTS.get(action, 1)
        remaining = state.credits_total - state.credits_used
        
        # Free actions
        if cost == 0:
            return True, remaining, None
        
        # Check if enough credits
        if remaining < cost:
            return False, remaining, (
                f"🔒 Insufficient credits ({remaining} remaining, need {cost}).\n"
                f"   Buy more: stacksense upgrade"
            )
        
        # Deduct
        state.credits_used += cost
        state.credits_used_since_sync += cost
        remaining = state.credits_total - state.credits_used
        self._save_state()
        
        if self.debug:
            print(f"[Credits] Used {cost} for {action}. Remaining: {remaining}")
        
        # Check if sync needed
        warning = None
        if self._needs_sync(state):
            warning = self._try_sync()
        
        # Low balance warning
        if remaining < 100 and not warning:
            warning = f"⚠️ Low credits: {remaining} remaining. Buy more: stacksense upgrade"
        
        return True, remaining, warning
    
    def add_credits(self, amount: int, key: str, email: str) -> bool:
        """
        Add credits from redeemed key.
        
        Args:
            amount: Credits to add
            key: License key
            email: Buyer email (from Lemon API)
            
        Returns:
            True if added successfully
        """
        state = self._load_state()
        
        # Check if key already redeemed
        if key in state.redeemed_keys:
            return False
        
        state.credits_total += amount
        state.redeemed_keys.append(key)
        state.email = email
        state.is_free_tier = False
        state.last_sync = datetime.now().isoformat()
        
        self._save_state()
        
        if self.debug:
            print(f"[Credits] Added {amount} from key. Total: {state.credits_total}")
        
        return True
    
    def _needs_sync(self, state: CreditState) -> bool:
        """Check if sync is needed."""
        # Skip sync for free tier
        if state.is_free_tier:
            return False
        
        # Sync every N credits
        if state.credits_used_since_sync >= SYNC_INTERVAL_CREDITS:
            return True
        
        # Sync every N hours
        try:
            last_sync = datetime.fromisoformat(state.last_sync)
            if datetime.now() - last_sync > timedelta(hours=SYNC_INTERVAL_HOURS):
                return True
        except:
            return True
        
        # Sync when low
        remaining = state.credits_total - state.credits_used
        if remaining < 500:
            return True
        
        return False
    
    def _try_sync(self) -> Optional[str]:
        """
        Try to sync with backend.
        
        Server is authoritative for credits - local state is updated from server response.
        
        Returns:
            Warning message if sync failed
        """
        state = self._load_state()
        
        # Free tier without email can't sync (no server account yet)
        if state.is_free_tier and not state.email:
            return None
        
        try:
            import httpx
            
            backend_url = os.getenv("STACKSENSE_BACKEND_URL", "https://pilgrimstack-api.fly.dev")
            
            response = httpx.post(
                f"{backend_url}/credits/sync",
                json={
                    "email": state.email or "",
                    "device_id": state.device_id,
                    "credits_used": state.credits_used,
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Server is authoritative - accept its values
                state.credits_total = data.get("credits_total", state.credits_total)
                # For credits_used, take the max to never lose local usage
                server_used = data.get("credits_used", state.credits_used)
                state.credits_used = max(state.credits_used, server_used)
                state.credits_used_since_sync = 0
                state.last_sync = datetime.now().isoformat()
                self._save_state()
                
                if self.debug:
                    remaining = state.credits_total - state.credits_used
                    print(f"[Credits] Synced successfully. Balance: {remaining}")
                
                return None
            else:
                return "⚠️ Credit sync failed. Will retry later."
                
        except Exception as e:
            if self.debug:
                print(f"[Credits] Sync error: {e}")
            return "⚠️ Credit sync failed. Continuing offline."
    
    def get_status_display(self) -> str:
        """Get formatted status for CLI."""
        info = self.get_balance()
        
        remaining = info["credits_remaining"]
        total = info["credits_total"]
        pct = (remaining / total * 100) if total > 0 else 0
        
        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = "━" * filled + "░" * (bar_len - filled)
        
        tier = "Free Tier" if info["is_free_tier"] else "Paid"
        
        return f"""
╔═══════════════════════════════════════════════╗
║           StackSense Credits                  ║
╚═══════════════════════════════════════════════╝

  Balance: {remaining:,} / {total:,} credits {bar}
  Tier:    {tier}
  
  Buy more: stacksense upgrade
"""


# Singleton instance
_tracker: Optional[CreditTracker] = None

def _get_tracker() -> CreditTracker:
    global _tracker
    if _tracker is None:
        _tracker = CreditTracker()
    return _tracker

def use_credits(action: str) -> Tuple[bool, int, Optional[str]]:
    """Quick function to use credits."""
    return _get_tracker().use_credits(action)

def get_balance() -> Dict:
    """Quick function to get balance."""
    return _get_tracker().get_balance()

def add_credits(amount: int, key: str, email: str) -> bool:
    """Quick function to add credits."""
    return _get_tracker().add_credits(amount, key, email)
