"""
Usage Tracker - Free Tier & Call Counting
==========================================
Tracks usage locally for free tier and paid plan limits.
"""

import os
import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass, asdict

from .loader import LicenseLoader, STACKSENSE_DIR
from .validator import LicenseStatus


USAGE_FILE = STACKSENSE_DIR / "usage.json"
USAGE_BACKUP = STACKSENSE_DIR / ".usage_backup.json"

# Free tier limits
FREE_DAILY_LIMIT = 50
FREE_FEATURES = ["chat"]

# Anti-tampering
MAX_FILE_RESETS_PER_DAY = 2
TAMPERING_PENALTY = 5

# Tier-based override limits
OVERRIDE_LIMITS = {
    "free": 0,
    "starter": 3,
    "pro": 5,
    "ultra": 10,
    "unlimited": 20,
    "enterprise": 50
}


@dataclass
class UsageData:
    """Usage tracking data."""
    date: str
    calls_used: int
    overrides_used: int
    file_resets: int
    last_reset: str
    features: dict  # {"chat": 10, "web_search": 5, ...}


def _load_usage() -> UsageData:
    """Load usage data from file."""
    today = date.today().isoformat()
    
    default = UsageData(
        date=today,
        calls_used=0,
        overrides_used=0,
        file_resets=0,
        last_reset=today,
        features={}
    )
    
    if not USAGE_FILE.exists():
        # Check for tampering (file was deleted)
        if USAGE_BACKUP.exists():
            try:
                backup = json.loads(USAGE_BACKUP.read_text())
                backup_date = backup.get("date", "")
                
                if backup_date == today:
                    # File was deleted today - apply penalty
                    file_resets = backup.get("file_resets", 0) + 1
                    
                    if file_resets > MAX_FILE_RESETS_PER_DAY:
                        # Tampering detected - start with penalty
                        default.calls_used = TAMPERING_PENALTY * file_resets
                        default.file_resets = file_resets
            except Exception:
                pass
        
        return default
    
    try:
        data = json.loads(USAGE_FILE.read_text())
        
        # Check for timestamp tampering (mtime went backwards)
        try:
            file_mtime = USAGE_FILE.stat().st_mtime
            stored_mtime = data.get("last_mtime", 0)
            if stored_mtime > 0 and file_mtime < stored_mtime:
                # Timestamp went backwards - possible tampering
                default.calls_used = TAMPERING_PENALTY * 2
                default.file_resets = 1
                return default
        except Exception:
            pass
        
        # Reset if new day
        if data.get("date") != today:
            return UsageData(
                date=today,
                calls_used=0,
                overrides_used=0,
                file_resets=0,
                last_reset=today,
                features={}
            )
        
        return UsageData(
            date=data.get("date", today),
            calls_used=data.get("calls_used", 0),
            overrides_used=data.get("overrides_used", 0),
            file_resets=data.get("file_resets", 0),
            last_reset=data.get("last_reset", today),
            features=data.get("features", {})
        )
        
    except Exception:
        return default


def _save_usage(usage: UsageData):
    """Save usage data to file."""
    import time
    
    STACKSENSE_DIR.mkdir(exist_ok=True)
    
    data = asdict(usage)
    data["last_mtime"] = time.time()  # Store for tampering detection
    
    USAGE_FILE.write_text(json.dumps(data, indent=2))
    
    # Also save backup for tampering detection
    USAGE_BACKUP.write_text(json.dumps(data))


class UsageTracker:
    """
    Tracks usage for both free tier and paid plans.
    
    Free tier: Daily limit of 50 calls
    Paid tier: Monthly limit based on plan
    
    Soft caps:
    - 80%: Warning
    - 100%: Grace warning
    - 120%: Soft block (override available)
    - 150%: Hard block
    """
    
    def __init__(self):
        self.loader = LicenseLoader()
    
    def get_limits(self) -> Tuple[int, str]:
        """
        Get current usage limits based on license.
        
        Returns:
            Tuple of (calls_limit, period: "daily" or "monthly")
        """
        status, info = self.loader.load()
        
        if status == LicenseStatus.VALID and info:
            return info.calls_per_month, "monthly"
        
        # Free tier or invalid license
        return FREE_DAILY_LIMIT, "daily"
    
    def get_usage(self) -> dict:
        """
        Get current usage statistics.
        
        Returns:
            Dict with usage info
        """
        usage = _load_usage()
        limit, period = self.get_limits()
        
        percentage = (usage.calls_used / limit * 100) if limit > 0 else 0
        remaining = max(limit - usage.calls_used, 0)
        
        return {
            "calls_used": usage.calls_used,
            "calls_limit": limit,
            "period": period,
            "percentage": round(percentage, 1),
            "remaining": remaining,
            "overrides_used": usage.overrides_used,
            "overrides_remaining": 5 - usage.overrides_used,
            "by_feature": usage.features,
            "resets": self._get_reset_date(period)
        }
    
    def _get_reset_date(self, period: str) -> str:
        """Get when usage resets."""
        today = date.today()
        
        if period == "daily":
            return "Tomorrow"
        
        # Monthly - first of next month
        if today.month == 12:
            reset = date(today.year + 1, 1, 1)
        else:
            reset = date(today.year, today.month + 1, 1)
        
        days_until = (reset - today).days
        return f"{reset.isoformat()} ({days_until} days)"
    
    def record_call(self, feature: str = "chat") -> Tuple[bool, Optional[str]]:
        """
        Record a call and check limits.
        
        Args:
            feature: Feature being used (chat, web_search, memory, agents)
            
        Returns:
            Tuple of (allowed, warning_message or None)
        """
        usage = _load_usage()
        limit, period = self.get_limits()
        
        # Calculate current percentage
        current = usage.calls_used
        percentage = (current / limit * 100) if limit > 0 else 0
        
        # Get soft/hard caps from license
        status, info = self.loader.load()
        soft_cap = 1.2
        hard_cap = 1.5
        
        if info:
            soft_cap = info.soft_cap
            hard_cap = info.hard_cap
        
        soft_limit = int(limit * soft_cap)
        hard_limit = int(limit * hard_cap)
        
        # Check limits
        warning = None
        allowed = True
        
        if current >= hard_limit:
            # 150%: Hard block
            allowed = False
            warning = (
                f"🚫 Hard limit reached ({current}/{limit})\n"
                f"   Resets: {self._get_reset_date(period)}\n"
                f"   Upgrade: stacksense.dev/upgrade"
            )
        
        elif current >= soft_limit:
            # 120-150%: Soft block with override
            if usage.overrides_used < 5:
                allowed = True
                warning = (
                    f"⚠️ Soft limit reached ({current}/{limit} = {int(percentage)}%)\n"
                    f"   Use emergency override? ({5 - usage.overrides_used} left)\n"
                    f"   Upgrade: stacksense.dev/upgrade"
                )
            else:
                allowed = False
                warning = f"🚫 Monthly limit reached. No overrides left. Upgrade: stacksense.dev/upgrade"
        
        elif current >= limit:
            # 100-120%: Gentle Lock (grace period with confirmation)
            warning = (
                f"🔒 Gentle Lock: Monthly limit reached ({current}/{limit})\n"
                f"   You can continue, but please upgrade soon.\n"
                f"   Upgrade: stacksense.dev/upgrade"
            )
        
        elif percentage >= 80:
            # 80-100%: Warning
            warning = f"⚠️ {int(percentage)}% of {'daily' if period == 'daily' else 'monthly'} limit used ({current}/{limit})"
        
        if allowed:
            # Record the call
            usage.calls_used += 1
            usage.features[feature] = usage.features.get(feature, 0) + 1
            _save_usage(usage)
        
        return allowed, warning
    
    def use_override(self) -> bool:
        """
        Use an emergency override.
        
        Returns:
            True if override was used
        """
        usage = _load_usage()
        
        if usage.overrides_used >= 5:
            return False
        
        usage.overrides_used += 1
        _save_usage(usage)
        return True
    
    def get_status_display(self) -> str:
        """
        Get formatted status display for CLI.
        
        Returns:
            Formatted status string
        """
        info = self.get_usage()
        license_info = self.loader.get_status_display()
        
        # Build progress bar
        pct = info["percentage"]
        bar_len = 20
        filled = int(bar_len * min(pct, 100) / 100)
        bar = "━" * filled + "░" * (bar_len - filled)
        
        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║              StackSense Status                       ║",
            "╚══════════════════════════════════════════════════════╝",
            "",
            f"License:     {license_info['plan']} (${self._get_price(license_info['plan'])}/month)",
            f"Status:      {'✓ Active' if license_info['status'] == 'active' else license_info['message']}",
            "",
            f"Usage ({datetime.now().strftime('%B %Y')}):",
            f"  Calls:     {info['calls_used']:,} / {info['calls_limit']:,} ({int(pct)}%) {bar}",
            f"  Remaining: {info['remaining']:,} calls",
            f"  Resets:    {info['resets']}",
        ]
        
        if info["overrides_remaining"] < 5:
            lines.append(f"  Overrides: {info['overrides_remaining']} remaining")
        
        return "\n".join(lines)
    
    def _get_price(self, plan: str) -> str:
        """Get price for plan."""
        prices = {
            "Free": "0",
            "Starter": "9",
            "Pro": "29",
            "Ultra": "49",
            "Unlimited": "99",
            "Enterprise": "299"
        }
        return prices.get(plan, "0")


def check_limit(feature: str = "chat") -> Tuple[bool, Optional[str]]:
    """
    Quick function to check and record a call.
    
    Args:
        feature: Feature being used
        
    Returns:
        Tuple of (allowed, warning_message or None)
    """
    tracker = UsageTracker()
    return tracker.record_call(feature)


# Feature display names for user-friendly messages
FEATURE_NAMES = {
    "chat": "Chat",
    "web_search": "Web Search",
    "diagrams": "Diagrams",
    "agents": "AI Agents",
    "memory": "Memory System",
    "priority_support": "Priority Support"
}


def check_feature_access(feature: str) -> Tuple[bool, Optional[str]]:
    """
    Check if the current license allows access to a feature.
    
    Args:
        feature: Feature to check (chat, web_search, diagrams, agents, memory, priority_support)
        
    Returns:
        Tuple of (allowed, upgrade_message or None)
        
    Usage:
        allowed, message = check_feature_access("memory")
        if not allowed:
            print(message)  # "Memory System requires Ultra plan. Upgrade at stacksense.dev/upgrade"
    """
    loader = LicenseLoader()
    status, info = loader.load()
    
    # Get available features based on license
    if status == LicenseStatus.VALID and info:
        available_features = info.features
        plan = info.plan
    else:
        # Free tier
        available_features = FREE_FEATURES
        plan = "Free"
    
    # Check if feature is available
    if feature in available_features:
        return True, None
    
    # Feature not available - determine which plan is needed
    required_plan = _get_required_plan_for_feature(feature)
    feature_name = FEATURE_NAMES.get(feature, feature.replace("_", " ").title())
    
    return False, (
        f"🔒 {feature_name} requires {required_plan} plan or higher.\n"
        f"   Current: {plan.title()}\n"
        f"   Upgrade: stacksense.dev/upgrade"
    )


def _get_required_plan_for_feature(feature: str) -> str:
    """Get the minimum plan required for a feature."""
    feature_to_plan = {
        "chat": "Free",
        "web_search": "Starter",
        "diagrams": "Pro",
        "agents": "Pro",
        "memory": "Ultra",
        "priority_support": "Unlimited"
    }
    return feature_to_plan.get(feature, "Pro")


def is_feature_locked(feature: str) -> bool:
    """
    Simple check if a feature is locked for the current plan.
    
    Args:
        feature: Feature to check
        
    Returns:
        True if locked (not accessible), False if available
        
    Usage:
        if is_feature_locked("memory"):
            show_upgrade_prompt()
    """
    allowed, _ = check_feature_access(feature)
    return not allowed


def get_locked_features() -> list:
    """
    Get list of features that are locked for the current plan.
    
    Returns:
        List of locked feature names
        
    Usage:
        locked = get_locked_features()
        # ['diagrams', 'agents', 'memory', 'priority_support']  # For Free tier
    """
    all_features = ["chat", "web_search", "diagrams", "agents", "memory", "priority_support"]
    return [f for f in all_features if is_feature_locked(f)]


def get_available_features() -> list:
    """
    Get list of features available for the current plan.
    
    Returns:
        List of available feature names
        
    Usage:
        available = get_available_features()
        # ['chat']  # For Free tier
        # ['chat', 'web_search', 'diagrams', 'agents']  # For Pro tier
    """
    all_features = ["chat", "web_search", "diagrams", "agents", "memory", "priority_support"]
    return [f for f in all_features if not is_feature_locked(f)]
