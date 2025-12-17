"""
StackSense Credits System
=========================
Pay-per-use credit tracking with local encrypted storage.
"""

__version__ = "1.0.0"

from .tracker import (
    CreditTracker,
    CREDIT_BUNDLES,
    CALL_COSTS,
    use_credits,
    get_balance,
    add_credits
)
