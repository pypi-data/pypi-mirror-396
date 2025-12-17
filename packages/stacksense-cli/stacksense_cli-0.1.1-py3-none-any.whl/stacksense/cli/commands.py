"""
StackSense CLI Commands - License & Provider Management
=======================================================
New commands for the production system:
- stacksense upgrade
- stacksense set-key
- stacksense replace-key
- stacksense status
- stacksense usage
- stacksense provider reset
"""

import sys
import webbrowser
from typing import Optional


def cmd_upgrade(args):
    """Show credit bundles and open payment link."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt
    import httpx
    import os
    
    console = Console()
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]StackSense Credits[/bold cyan]\n"
        "Pay only for what you use - no subscriptions",
        border_style="cyan"
    ))
    
    # Fetch dynamic bundles from backend
    backend_url = os.getenv("STACKSENSE_BACKEND_URL", "https://pilgrimstack-api.fly.dev")
    bundles = []
    
    try:
        response = httpx.get(f"{backend_url}/credits/bundles", timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            bundles = data.get("bundles", [])
    except Exception:
        pass
    
    # Fallback if API fails
    if not bundles:
        bundles = [
            {"name": "Basic", "price": 20, "credits": 5000, "url": ""},
            {"name": "Power", "price": 50, "credits": 12000, "recommended": True, "url": ""},
            {"name": "Pro Stack", "price": 100, "credits": 25000, "url": ""}
        ]
    
    # Credit bundles table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", width=3)
    table.add_column("Bundle", style="cyan", width=14)
    table.add_column("Price", justify="right")
    table.add_column("Credits", justify="right")
    table.add_column("Best For")
    
    for i, bundle in enumerate(bundles, 1):
        name = bundle.get("name", "Bundle")
        if bundle.get("recommended"):
            name += " ⭐"
        table.add_row(
            str(i),
            f"[bold]{name}[/bold]",
            f"[green]${bundle.get('price', 0)}[/green]",
            f"{bundle.get('credits', 0):,}",
            "Solo devs" if i == 1 else "Heavy users" if i == 2 else "Agencies"
        )
    
    console.print(table)
    console.print()
    
    # Current balance
    try:
        from stacksense.credits import get_balance
        balance = get_balance()
        remaining = balance["credits_remaining"]
        tier = "Free" if balance["is_free_tier"] else "Paid"
        console.print(f"[dim]Your Balance: {remaining:,} credits ({tier})[/dim]")
    except Exception:
        console.print("[dim]Your Balance: Loading...[/dim]")
    
    console.print()
    console.print("[dim]All features included • Credits stack • Never expire[/dim]")
    console.print("[dim]Support: amariah.abish@gmail.com[/dim]")
    console.print()
    
    # Open payment link
    choices = [str(i) for i in range(1, len(bundles) + 1)] + ["cancel"]
    choice = Prompt.ask(
        "Select bundle",
        choices=choices,
        default="1"
    )
    
    if choice != "cancel" and choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(bundles):
            url = bundles[idx].get("url", "")
            if url:
                console.print(f"\n[green]Opening payment page...[/green]")
                webbrowser.open(url)
                console.print("\n[dim]After purchase, run: stacksense redeem YOUR-KEY[/dim]")
            else:
                console.print("\n[yellow]⚠️ Checkout URL not available. Please try again later.[/yellow]")
    else:
        console.print("[dim]Cancelled.[/dim]")


def cmd_set_key(args):
    """Legacy - redirects to redeem."""
    cmd_redeem(args)


def cmd_login(args):
    """Login with email + order key to sync credits from server."""
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
    import os
    
    console = Console()
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Login to StackSense[/bold cyan]\n"
        "Use your email and last order key to restore credits",
        border_style="cyan"
    ))
    
    # Get email
    email = getattr(args, 'email', None)
    if not email:
        email = Prompt.ask("\nEmail")
    
    # Get order key
    order_id = getattr(args, 'order_id', None) or getattr(args, 'key', None)
    if not order_id:
        order_id = Prompt.ask("Order Key (from purchase email)")
    
    if not email or not order_id:
        console.print("[red]❌ Email and order key are required[/red]")
        sys.exit(1)
    
    console.print("\n[dim]Authenticating...[/dim]")
    
    try:
        import httpx
        from pathlib import Path
        import json
        from stacksense.credits.storage import get_device_id, CreditStorage
        from stacksense.credits.tracker import CreditState
        from datetime import datetime
        
        backend_url = os.getenv("STACKSENSE_BACKEND_URL", "https://pilgrimstack-api.fly.dev")
        
        response = httpx.post(
            f"{backend_url}/auth/login",
            json={
                "email": email.strip(),
                "order_id": order_id.strip()
            },
            timeout=15.0
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            token = data.get("token", "")
            server_credits = data.get("credits", 0)
            
            # Save auth token locally
            auth_file = Path.home() / ".stacksense" / "auth.json"
            auth_file.parent.mkdir(parents=True, exist_ok=True)
            auth_file.write_text(json.dumps({
                "email": email.strip(),
                "token": token,
                "credits": server_credits
            }))
            
            # CRITICAL: Sync credits to local storage
            # This enables new device login to restore balance
            device_id = get_device_id()
            storage = CreditStorage()
            
            # Get any existing local usage (in case this is same device re-login)
            existing = storage.load()
            local_used = existing.credits_used if existing else 0
            
            # Create synced state with server balance
            # Server's credits_balance already accounts for all usage
            new_state = CreditState(
                email=email.strip(),
                device_id=device_id,
                credits_total=server_credits + local_used,  # Server balance + what we'll deduct
                credits_used=local_used,  # Preserve any local usage
                credits_used_since_sync=0,
                last_sync=datetime.now().isoformat(),
                redeemed_keys=existing.redeemed_keys if existing else [],
                is_free_tier=False
            )
            storage.save(new_state)
            
            console.print(f"\n[green]✅ Login successful![/green]")
            console.print(f"\n[bold]Email:[/bold] {email}")
            console.print(f"[bold]Credits:[/bold] {server_credits:,}")
            console.print("\n🎉 Run [cyan]stacksense chat[/cyan] to start!")
        else:
            console.print(f"\n[red]❌ {data.get('message', 'Login failed')}[/red]")
            sys.exit(1)
            
    except httpx.TimeoutException:
        console.print("\n[red]❌ Connection timeout. Check internet.[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_redeem(args):
    """Redeem a license key to add credits."""
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
    import os
    
    console = Console()
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Redeem License Key[/bold cyan]\n"
        "Enter your key from the purchase email",
        border_style="cyan"
    ))
    
    # Get key from args or prompt
    key = getattr(args, 'key', None)
    if not key:
        key = Prompt.ask("\nLicense Key", password=False)
    
    if not key or len(key) < 10:
        console.print("[red]❌ Invalid key format[/red]")
        sys.exit(1)
    
    console.print("\n[dim]Validating with Lemon Squeezy...[/dim]")
    
    try:
        import httpx
        from stacksense.credits.storage import get_device_id, CreditStorage
        from stacksense.credits.tracker import CreditState
        from datetime import datetime
        
        backend_url = os.getenv("STACKSENSE_BACKEND_URL", "https://pilgrimstack-api.fly.dev")
        
        # Use consistent device ID (not random UUID!)
        device_id = get_device_id()
        
        # Load current local state to preserve usage
        storage = CreditStorage()
        current_state = storage.load()
        local_credits_used = current_state.credits_used if current_state else 0
        existing_keys = current_state.redeemed_keys if current_state else []
        
        # Check if key already redeemed locally
        if key.strip() in existing_keys:
            console.print("[yellow]⚠️ This key appears to already be redeemed on this device.[/yellow]")
            console.print("[dim]If you believe this is an error, try 'stacksense recover'.[/dim]")
            return
        
        # Call backend to validate and add credits
        # Send local_credits_used so server can properly track usage history
        response = httpx.post(
            f"{backend_url}/redeem",
            json={
                "license_key": key.strip(),
                "device_id": device_id,
                "local_credits_used": local_credits_used
            },
            timeout=30.0
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            email = data.get("email", "")
            credits_added = data.get("credits", 0)
            server_total = data.get("total_credits", 0)
            auth_token = data.get("token", "")
            
            # CRITICAL: Sync local storage with server
            # Server is authoritative for total, but preserve local usage
            new_state = CreditState(
                email=email,
                device_id=device_id,
                credits_total=server_total,
                credits_used=local_credits_used,  # Preserve local usage!
                credits_used_since_sync=0,
                last_sync=datetime.now().isoformat(),
                redeemed_keys=existing_keys + [key.strip()],
                is_free_tier=False
            )
            storage.save(new_state)
            
            # Also save auth token for future API calls
            if auth_token and email:
                import json
                auth_file = os.path.expanduser("~/.stacksense/auth.json")
                os.makedirs(os.path.dirname(auth_file), exist_ok=True)
                with open(auth_file, "w") as f:
                    json.dump({
                        "email": email,
                        "token": auth_token,
                        "credits": server_total
                    }, f)
            
            remaining = server_total - local_credits_used
            
            console.print(f"\n[green]✅ Key redeemed successfully![/green]")
            console.print(f"\n[bold]Email:[/bold] {email}")
            console.print(f"[bold]Credits Added:[/bold] +{credits_added:,}")
            console.print(f"[bold]Total Balance:[/bold] {remaining:,} credits")
            if local_credits_used > 0:
                console.print(f"[dim](Already used {local_credits_used:,} credits)[/dim]")
            console.print("\n🎉 Run [cyan]stacksense chat[/cyan] to start!")
        else:
            console.print(f"\n[red]❌ {data.get('message', 'Invalid key')}[/red]")
            sys.exit(1)
            
    except httpx.TimeoutException:
        console.print("\n[red]❌ Connection timeout. Check internet.[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_credits(args):
    """Show credit balance and usage."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    import os
    
    console = Console()
    
    try:
        from stacksense.credits import get_balance, CALL_COSTS
        from stacksense.credits.storage import get_device_id, CreditStorage
        from stacksense.credits.tracker import CreditState
        from datetime import datetime
        import httpx
        
        # First try to sync from server if we have an email
        storage = CreditStorage()
        current_state = storage.load()
        
        if current_state and current_state.email:
            # Sync with server to get authoritative balance
            try:
                backend_url = os.getenv("STACKSENSE_BACKEND_URL", "https://pilgrimstack-api.fly.dev")
                response = httpx.post(
                    f"{backend_url}/credits/sync",
                    json={
                        "email": current_state.email,
                        "device_id": current_state.device_id,
                        "credits_used": current_state.credits_used,
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Update local with server values
                    current_state.credits_total = data.get("credits_total", current_state.credits_total)
                    server_used = data.get("credits_used", current_state.credits_used)
                    current_state.credits_used = max(current_state.credits_used, server_used)
                    current_state.last_sync = datetime.now().isoformat()
                    storage.save(current_state)
            except Exception:
                pass  # Use local values if sync fails
        
        balance = get_balance()
        remaining = balance["credits_remaining"]
        total = balance["credits_total"]
        pct = (remaining / total * 100) if total > 0 else 0
        
        # Progress bar
        bar_len = 25
        filled = int(bar_len * pct / 100)
        bar = "━" * filled + "░" * (bar_len - filled)
        
        console.print()
        console.print(Panel.fit(
            "[bold cyan]StackSense Credits[/bold cyan]",
            border_style="cyan"
        ))
        
        console.print(f"\n  Balance: [bold]{remaining:,}[/bold] / {total:,} credits")
        console.print(f"  {bar} {int(pct)}%")
        if balance.get("email"):
            console.print(f"  Email: {balance['email']}")
        
        # Cost reference
        console.print("\n[bold]Credit Costs:[/bold]")
        table = Table(show_header=True, header_style="dim")
        table.add_column("Action", width=20)
        table.add_column("Credits", justify="right")
        
        for action, cost in sorted(CALL_COSTS.items(), key=lambda x: x[1]):
            if cost > 0:
                table.add_row(action.replace("_", " ").title(), str(cost))
        
        console.print(table)
        console.print("\n[dim]Buy more: stacksense upgrade[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def cmd_recover(args):
    """Recover account on a new device."""
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
    import os
    
    console = Console()
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Account Recovery[/bold cyan]\n"
        "Switch credits to this device",
        border_style="cyan"
    ))
    
    # Get email
    email = Prompt.ask("\nYour purchase email")
    if not email or "@" not in email:
        console.print("[red]❌ Invalid email[/red]")
        sys.exit(1)
    
    # Get license key (any one they own)
    console.print("\n[dim]Enter any license key you own (from purchase emails)[/dim]")
    key = Prompt.ask("License Key")
    if not key or len(key) < 10:
        console.print("[red]❌ Invalid key format[/red]")
        sys.exit(1)
    
    console.print("\n[dim]Verifying...[/dim]")
    
    try:
        import httpx
        from stacksense.credits import add_credits
        from stacksense.credits.storage import get_device_id, CreditStorage
        
        backend_url = os.getenv("STACKSENSE_BACKEND_URL", "https://pilgrimstack-api.fly.dev")
        device_id = get_device_id()
        
        response = httpx.post(
            f"{backend_url}/recover",
            json={
                "email": email.strip(),
                "license_key": key.strip(),
                "device_id": device_id
            },
            timeout=15.0
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            # Reset local storage and add recovered credits
            storage = CreditStorage()
            storage.reset()
            
            total = data.get("total_credits", 0)
            used = data.get("used_credits", 0)
            
            # Initialize with recovered data
            from stacksense.credits.tracker import CreditState
            from datetime import datetime
            
            state = CreditState(
                email=email.strip(),
                device_id=device_id,
                credits_total=total,
                credits_used=used,
                credits_used_since_sync=0,
                last_sync=datetime.now().isoformat(),
                redeemed_keys=data.get("keys", []),
                is_free_tier=False
            )
            storage.save(state)
            
            console.print(f"\n[green]✅ Account recovered![/green]")
            console.print(f"\n[bold]Email:[/bold] {email}")
            console.print(f"[bold]Balance:[/bold] {total - used:,} credits")
            console.print("\n[dim]Previous device deactivated automatically.[/dim]")
        else:
            console.print(f"\n[red]❌ {data.get('message', 'Recovery failed')}[/red]")
            console.print("[dim]Make sure email and key match a purchase.[/dim]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        sys.exit(1)


def cmd_replace_key(args):
    """Replace existing license key."""
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    
    console = Console()
    
    # Check existing license
    try:
        from stacksense.license import LicenseLoader
        loader = LicenseLoader()
        status = loader.get_status_display()
        
        if status['status'] != 'free':
            console.print(f"\n[yellow]⚠️  Current license: {status['plan']}[/yellow]")
            if not Confirm.ask("Replace existing license?", default=False):
                console.print("[dim]Cancelled.[/dim]")
                return
    except Exception:
        pass
    
    # Same as set-key from here
    cmd_set_key(args)


def cmd_status(args):
    """Show account status with credit balance."""
    from rich.console import Console
    from rich.panel import Panel
    import os
    
    console = Console()
    
    try:
        from stacksense.credits import get_balance
        from stacksense.credits.storage import CreditStorage
        from datetime import datetime
        import httpx
        
        # Sync with server if we have an email
        storage = CreditStorage()
        current_state = storage.load()
        
        if current_state and current_state.email:
            try:
                backend_url = os.getenv("STACKSENSE_BACKEND_URL", "https://pilgrimstack-api.fly.dev")
                response = httpx.post(
                    f"{backend_url}/credits/sync",
                    json={
                        "email": current_state.email,
                        "device_id": current_state.device_id,
                        "credits_used": current_state.credits_used,
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    current_state.credits_total = data.get("credits_total", current_state.credits_total)
                    current_state.last_sync = datetime.now().isoformat()
                    storage.save(current_state)
            except Exception:
                pass  # Use local if sync fails
        
        balance = get_balance()
        remaining = balance["credits_remaining"]
        total = balance["credits_total"]
        used = balance["credits_used"]
        email = balance.get("email", "")
        is_free = balance["is_free_tier"]
        
        # Progress bar
        pct = (remaining / total * 100) if total > 0 else 0
        bar_len = 25
        filled = int(bar_len * pct / 100)
        if pct >= 50:
            color = "green"
        elif pct >= 20:
            color = "yellow"
        else:
            color = "red"
        bar = f"[{color}]{'━' * filled}[/{color}]{'░' * (bar_len - filled)}"
        
        # Build status display
        console.print()
        console.print(Panel.fit(
            "[bold cyan]StackSense Account Status[/bold cyan]",
            border_style="cyan"
        ))
        
        console.print(f"\n[bold]Credits:[/bold] {remaining:,} / {total:,}")
        console.print(f"         {bar} {int(pct)}%")
        if used > 0:
            console.print(f"[dim]         ({used:,} used)[/dim]")
        
        if email:
            console.print(f"\n[bold]Email:[/bold] {email}")
        
        if balance.get("last_sync"):
            console.print(f"[dim]Last sync: {balance['last_sync'][:10]}[/dim]")
        
        console.print()
        
    except Exception as e:
        console.print(f"[red]❌ Error getting status: {e}[/red]")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()


def cmd_usage(args):
    """Show detailed usage breakdown."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    try:
        from stacksense.license import UsageTracker
        from datetime import datetime
        
        tracker = UsageTracker()
        info = tracker.get_usage()
        
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]{datetime.now().strftime('%B %Y')} Usage Breakdown[/bold cyan]",
            border_style="cyan"
        ))
        
        # Build progress bar
        pct = info["percentage"]
        bar_len = 30
        filled = int(bar_len * min(pct, 100) / 100)
        
        # Color based on percentage
        if pct >= 100:
            color = "red"
        elif pct >= 80:
            color = "yellow"
        else:
            color = "green"
        
        bar = f"[{color}]{'━' * filled}[/{color}]{'░' * (bar_len - filled)}"
        
        console.print(f"\n[bold]Total:[/bold] {info['calls_used']:,} / {info['calls_limit']:,} ({int(pct)}%)")
        console.print(f"       {bar}")
        console.print(f"\n[bold]Remaining:[/bold] {info['remaining']:,} calls")
        console.print(f"[bold]Resets:[/bold] {info['resets']}")
        
        if info.get('by_feature'):
            console.print("\n[bold]By Feature:[/bold]")
            
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Feature", style="dim")
            table.add_column("Calls", justify="right")
            table.add_column("Percent", justify="right")
            
            total = sum(info['by_feature'].values()) or 1
            for feature, count in sorted(info['by_feature'].items(), key=lambda x: -x[1]):
                pct_feature = (count / total) * 100
                table.add_row(feature, str(count), f"{int(pct_feature)}%")
            
            console.print(table)
        
        if info['overrides_remaining'] < 5:
            console.print(f"\n[yellow]Overrides used: {5 - info['overrides_remaining']}/5[/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Error getting usage: {e}[/red]")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()


def cmd_provider_reset(args):
    """Reset provider API key and model."""
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    
    console = Console()
    
    provider = args.provider.lower() if hasattr(args, 'provider') and args.provider else None
    
    # If no provider specified, show menu
    if not provider:
        console.print()
        console.print(Panel.fit(
            "[bold cyan]Reset AI Provider[/bold cyan]\n"
            "Configure your AI provider",
            border_style="cyan"
        ))
        
        console.print("\n[bold]Available Providers:[/bold]")
        console.print("  [green]1. OpenRouter (100+ models) ⭐ Available[/green]")
        console.print("  [dim]2. Ollama (Local models) — TBD v2.0[/dim]")
        console.print("  [dim]3. OpenAI (GPT-4, GPT-4o) — TBD v3.0[/dim]")
        console.print("  [dim]4. Grok (xAI) — TBD v3.0[/dim]")
        console.print("  [dim]5. TogetherAI (Llama, Qwen) — TBD v3.0[/dim]")
        console.print()
        
        choice = Prompt.ask(
            "Select provider",
            choices=["1", "2", "3", "4", "5", "cancel"],
            default="1"
        )
        
        # Only OpenRouter is available in v1.0
        if choice in ["2", "3", "4", "5"]:
            version = "v2.0" if choice == "2" else "v3.0"
            console.print(f"\n[yellow]⚠️ This provider is coming in {version}![/yellow]")
            console.print("[dim]For now, please use OpenRouter which gives access to 100+ models.[/dim]")
            console.print("[dim]Get your free API key at: https://openrouter.ai/keys[/dim]")
            return
        
        if choice == "cancel":
            console.print("[dim]Cancelled.[/dim]")
            return
        
        provider = "openrouter"
    
    # Provider display names
    provider_names = {
        "openai": "OpenAI",
        "grok": "Grok (xAI)",
        "openrouter": "OpenRouter",
        "together": "TogetherAI"
    }
    
    provider_name = provider_names.get(provider, provider)
    
    console.print(f"\n[bold]Configuring {provider_name}[/bold]")
    
    # Get API key
    api_key = Prompt.ask("API Key", password=True)
    
    if not api_key:
        console.print("[red]❌ API key is required[/red]")
        sys.exit(1)
    
    # Get model (optional)
    default_models = {
        "openai": "gpt-4o-mini",
        "grok": "grok-beta",
        "openrouter": "meta-llama/llama-3.3-70b-instruct:free",
        "together": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    }
    
    model = Prompt.ask(
        "Model",
        default=default_models.get(provider, "")
    )
    
    # Save to config
    try:
        from stacksense.core.config import Config
        config = Config()
        
        # Set provider
        config.provider = provider
        
        # Set API key
        config.set_api_key(api_key, provider)
        
        # Set model if specified
        if model:
            config.model = model
        
        # Note: setters auto-save, no explicit save() needed
        
        console.print(f"\n[green]✅ {provider_name} configured successfully![/green]")
        console.print(f"[dim]Provider: {provider}[/dim]")
        console.print(f"[dim]Model: {model or 'default'}[/dim]")
        console.print("\n💡 Start chat with: [cyan]stacksense chat[/cyan]")
        
    except Exception as e:
        console.print(f"\n[red]❌ Error saving configuration: {e}[/red]")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_setup_ai_new(args):
    """New AI setup - OpenRouter only in v1.0."""
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
    
    console = Console()
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]StackSense AI Setup[/bold cyan]\n"
        "Configure your AI provider",
        border_style="cyan"
    ))
    
    console.print("\n[bold]Choose your AI provider:[/bold]")
    console.print()
    console.print("  [green]1. OpenRouter[/green] [green]⭐ Available[/green]")
    console.print("     100+ models including Llama, GPT-4, Claude")
    console.print("     [dim]Free tier available![/dim]")
    console.print()
    console.print("  [dim]2. Ollama (Local) — TBD v2.0[/dim]")
    console.print("     [dim]Local models on your machine[/dim]")
    console.print()
    console.print("  [dim]3. OpenAI — TBD v3.0[/dim]")
    console.print("     [dim]GPT-4, GPT-4o, GPT-4o-mini[/dim]")
    console.print()
    console.print("  [dim]4. Grok (xAI) — TBD v3.0[/dim]")
    console.print("     [dim]Fast, capable, great for code[/dim]")
    console.print()
    console.print("  [dim]5. TogetherAI — TBD v3.0[/dim]")
    console.print("     [dim]Affordable Llama, Qwen, Mistral[/dim]")
    console.print()
    
    choice = Prompt.ask(
        "Select provider",
        choices=["1", "2", "3", "4", "5"],
        default="1"
    )
    
    # Only OpenRouter is available in v1.0
    if choice in ["2", "3", "4", "5"]:
        version = "v2.0" if choice == "2" else "v3.0"
        console.print(f"\n[yellow]⚠️ This provider is coming in {version}![/yellow]")
        console.print("[dim]For now, please use OpenRouter which gives access to 100+ models.[/dim]")
        console.print("[dim]Get your free API key at: https://openrouter.ai/keys[/dim]\n")
        
        # Retry with OpenRouter
        retry = Prompt.ask("Set up OpenRouter instead?", choices=["y", "n"], default="y")
        if retry != "y":
            console.print("[dim]Setup cancelled. Run 'stacksense --setup-ai' when ready.[/dim]")
            return
    
    # Simulate args for provider reset
    class ProviderArgs:
        provider = "openrouter"
        debug = getattr(args, 'debug', False)
    
    cmd_provider_reset(ProviderArgs())


def cmd_doctor(args):
    """
    Diagnose StackSense installation.
    
    Checks:
    - Provider configured
    - API key valid
    - License valid
    - Calls remaining
    - Filesystem healthy
    - Usage.json integrity
    - Version
    - Backend reachable
    """
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    import httpx
    import os
    
    console = Console()
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]StackSense Doctor[/bold cyan]\n"
        "System diagnostics and health check",
        border_style="cyan"
    ))
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Check", style="dim", width=25)
    table.add_column("Status", width=40)
    
    checks_passed = 0
    checks_total = 0
    
    # 1. Version
    checks_total += 1
    try:
        from stacksense import __version__
        table.add_row("Version", f"[green]✓[/green] {__version__}")
        checks_passed += 1
    except Exception:
        table.add_row("Version", "[yellow]⚠[/yellow] Unknown")
    
    # 2. Provider configured
    checks_total += 1
    try:
        from stacksense.core.config import Config
        config = Config()
        provider = config.provider
        model = config.model
        if provider:
            table.add_row("Provider", f"[green]✓[/green] {provider}")
            table.add_row("Model", f"[dim]{model or 'default'}[/dim]")
            checks_passed += 1
        else:
            table.add_row("Provider", "[red]✗[/red] Not configured")
    except Exception as e:
        table.add_row("Provider", f"[red]✗[/red] Error: {e}")
    
    # 3. API key valid
    checks_total += 1
    try:
        api_key = config.get_api_key()
        if api_key and len(api_key) > 10:
            masked = api_key[:4] + "..." + api_key[-4:]
            table.add_row("API Key", f"[green]✓[/green] {masked}")
            checks_passed += 1
        else:
            table.add_row("API Key", "[red]✗[/red] Not set or invalid")
    except Exception as e:
        table.add_row("API Key", f"[red]✗[/red] Error: {e}")
    
    # 4. License status
    checks_total += 1
    try:
        from stacksense.license import LicenseLoader
        loader = LicenseLoader()
        status = loader.get_status_display()
        plan = status.get('plan', 'Free')
        if status.get('status') == 'active':
            table.add_row("License", f"[green]✓[/green] {plan} (Active)")
            checks_passed += 1
        elif status.get('status') == 'grace':
            table.add_row("License", f"[yellow]⚠[/yellow] {plan} (Grace period)")
            checks_passed += 1
        else:
            table.add_row("License", f"[dim]○[/dim] {plan}")
            checks_passed += 1  # Free tier is valid
    except Exception as e:
        table.add_row("License", f"[yellow]⚠[/yellow] Not loaded: {e}")
    
    # 5. Calls remaining
    checks_total += 1
    try:
        from stacksense.license import UsageTracker
        tracker = UsageTracker()
        info = tracker.get_usage()
        remaining = info.get('remaining', 0)
        limit = info.get('calls_limit', 50)
        pct = info.get('percentage', 0)
        
        if pct >= 100:
            table.add_row("Usage", f"[red]✗[/red] Limit reached ({remaining} left)")
        elif pct >= 80:
            table.add_row("Usage", f"[yellow]⚠[/yellow] {remaining}/{limit} remaining ({int(pct)}%)")
            checks_passed += 1
        else:
            table.add_row("Usage", f"[green]✓[/green] {remaining}/{limit} remaining ({int(pct)}%)")
            checks_passed += 1
    except Exception as e:
        table.add_row("Usage", f"[yellow]⚠[/yellow] Error: {e}")
    
    # 6. Filesystem healthy
    checks_total += 1
    try:
        from pathlib import Path
        stacksense_dir = Path.home() / ".stacksense"
        if stacksense_dir.exists():
            files = list(stacksense_dir.iterdir())
            table.add_row("Filesystem", f"[green]✓[/green] ~/.stacksense ({len(files)} files)")
            checks_passed += 1
        else:
            table.add_row("Filesystem", "[dim]○[/dim] ~/.stacksense not created yet")
            checks_passed += 1
    except Exception as e:
        table.add_row("Filesystem", f"[red]✗[/red] Error: {e}")
    
    # 7. Usage.json integrity
    checks_total += 1
    try:
        usage_file = Path.home() / ".stacksense" / "usage.json"
        if usage_file.exists():
            import json
            data = json.loads(usage_file.read_text())
            if "date" in data and "calls_used" in data:
                table.add_row("Usage File", "[green]✓[/green] Valid")
                checks_passed += 1
            else:
                table.add_row("Usage File", "[yellow]⚠[/yellow] Missing fields")
        else:
            table.add_row("Usage File", "[dim]○[/dim] Not created yet")
            checks_passed += 1
    except Exception as e:
        table.add_row("Usage File", f"[red]✗[/red] Corrupted: {e}")
    
    # 8. Backend reachable
    checks_total += 1
    try:
        backend_url = os.getenv("STACKSENSE_BACKEND_URL", "https://pilgrimstack-api.fly.dev")
        response = httpx.get(f"{backend_url}/health", timeout=5.0)
        if response.status_code == 200:
            table.add_row("Backend", f"[green]✓[/green] Reachable")
            checks_passed += 1
        else:
            table.add_row("Backend", f"[yellow]⚠[/yellow] Status {response.status_code}")
    except httpx.TimeoutException:
        table.add_row("Backend", "[yellow]⚠[/yellow] Timeout (but local mode works)")
        checks_passed += 1  # Offline mode is fine
    except Exception as e:
        table.add_row("Backend", f"[dim]○[/dim] Offline mode")
        checks_passed += 1  # Offline mode is fine
    
    console.print()
    console.print(table)
    
    # Summary
    console.print()
    if checks_passed == checks_total:
        console.print(f"[green]✓ All {checks_total} checks passed![/green]")
    else:
        console.print(f"[yellow]⚠ {checks_passed}/{checks_total} checks passed[/yellow]")
    
    console.print()
    console.print("[dim]Run 'stacksense --setup-ai' to configure your provider[/dim]")
    console.print("[dim]Run 'stacksense upgrade' to view pricing plans[/dim]")

