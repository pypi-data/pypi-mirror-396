#!/usr/bin/env python3
"""
StackSense CLI
==============
AI-powered code intelligence for developers.

Commands:
    stacksense chat     - Interactive AI chat with repository context
    stacksense scan     - Scan and analyze a repository
    stacksense diagram  - Generate dependency diagrams
    stacksense search   - Search StackOverflow, GitHub, Reddit, MDN
"""

# Suppress tree_sitter FutureWarning BEFORE any imports
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")

import sys
import os
import argparse
from pathlib import Path

__version__ = "0.1.0"


def print_banner():
    """Print StackSense ASCII banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗████████╗ █████╗  ██████╗██╗  ██╗███████╗███████╗  ║
║   ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔════╝  ║
║   ███████╗   ██║   ███████║██║     █████╔╝ ███████╗█████╗    ║
║   ╚════██║   ██║   ██╔══██║██║     ██╔═██╗ ╚════██║██╔══╝    ║
║   ███████║   ██║   ██║  ██║╚██████╗██║  ██╗███████║███████╗  ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝  ║
║                                                               ║
║              🧠 AI-Powered Code Intelligence                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def cmd_chat(args):
    """Handle the 'chat' subcommand"""
    from stacksense.cli.chat import start_chat
    
    # Get workspace path
    workspace = args.workspace or os.getcwd()
    
    if args.workspace and not os.path.exists(args.workspace):
        print(f"❌ Error: Workspace path does not exist: {args.workspace}")
        sys.exit(1)
    
    # Start interactive chat
    start_chat(
        model_type=args.model,
        debug=args.debug
    )


def cmd_scan(args):
    """Handle the 'scan' subcommand"""
    import asyncio
    from stacksense.core.repo_scanner import RepoScanner
    
    # Get target path
    target = Path(args.path).resolve()
    
    if not target.exists():
        print(f"❌ Error: Path does not exist: {target}")
        sys.exit(1)
    
    print(f"🔍 Scanning repository: {target.name}")
    print("=" * 60)
    
    # Create scanner
    scanner = RepoScanner(
        workspace_path=target,
        debug=args.debug
    )
    
    # Run scan
    try:
        context_map = asyncio.run(scanner.scan(
            progressive=args.progressive,
            max_files=args.max_files
        ))
        
        # Display results
        print(f"\n📊 Scan Results")
        print("=" * 60)
        print(f"📁 Total Files: {context_map.get('total_files', 0)}")
        
        languages = context_map.get('languages', {})
        if languages:
            print(f"💻 Languages: {', '.join(languages.keys())}")
        
        frameworks = context_map.get('frameworks', [])
        if frameworks:
            print(f"🔧 Frameworks: {', '.join(frameworks)}")
        
        modules = context_map.get('modules', {})
        if modules:
            print(f"\n📦 Modules Detected: {len(modules)}")
            for name, info in list(modules.items())[:10]:
                files_count = len(info.get('files', []))
                purpose = info.get('purpose', 'Unknown')
                print(f"   • {name}: {files_count} files - {purpose}")
            
            if len(modules) > 10:
                print(f"   ... and {len(modules) - 10} more modules")
        
        # Show slices count
        if hasattr(scanner, 'slices') and scanner.slices:
            print(f"\n🧩 Code Slices: {len(scanner.slices)}")
        
        print("\n✅ Scan complete!")
        
        # Save output if requested
        if args.output:
            import json
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(context_map, f, indent=2, default=str)
            print(f"💾 Results saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Scan failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_diagram(args):
    """Handle the 'diagram' subcommand"""
    from pathlib import Path
    from stacksense.core.diagram_builder import DiagramBuilder
    
    # Get target path
    target = Path(args.path).resolve()
    
    if not target.exists():
        print(f"❌ Error: Path does not exist: {target}")
        sys.exit(1)
    
    print(f"📊 Building dependency diagram for: {target.name}")
    print("=" * 60)
    
    # Create builder
    builder = DiagramBuilder(debug=args.debug)
    
    try:
        # Build diagram
        diagram = builder.build_diagram(target, {})
        
        # Display summary
        print(f"\n📈 Diagram Summary")
        print("=" * 60)
        print(f"🔵 Nodes: {len(diagram.nodes)}")
        print(f"🔗 Edges: {len(diagram.edges)}")
        print(f"📦 Clusters: {len(diagram.clusters)}")
        
        # Show clusters
        if diagram.clusters:
            print(f"\n📦 Detected Clusters:")
            for cluster in diagram.clusters[:10]:
                print(f"   • {cluster.name}: {len(cluster.files)} files")
                print(f"     Purpose: {cluster.purpose}")
            
            if len(diagram.clusters) > 10:
                print(f"   ... and {len(diagram.clusters) - 10} more clusters")
        
        # Save diagram
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            builder.save_diagram(diagram, output_dir)
            print(f"\n💾 Diagram saved to: {output_dir}")
        else:
            # Default output
            output_dir = target / ".stacksense" / "diagrams"
            output_dir.mkdir(parents=True, exist_ok=True)
            builder.save_diagram(diagram, output_dir)
            print(f"\n💾 Diagram saved to: {output_dir}")
        
        print("\n✅ Diagram generation complete!")
        
    except Exception as e:
        print(f"❌ Diagram generation failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_search(args):
    """Handle the 'search' subcommand"""
    import asyncio
    from stacksense.core.web_searcher import WebSearcher
    
    query = ' '.join(args.query)
    
    if not query.strip():
        print("❌ Error: Please provide a search query")
        print("Usage: stacksense search 'how to handle async errors in python'")
        sys.exit(1)
    
    print(f"🔍 Searching: {query}")
    print("=" * 60)
    print("   Querying: StackOverflow, GitHub, Reddit, MDN")
    print()
    
    # Create searcher
    cache_path = "/tmp/stacksense_search_cli.json"
    searcher = WebSearcher(
        cache_path=cache_path,
        debug=args.debug,
        timeout=args.timeout or 15.0
    )
    
    try:
        # Parse sources
        sources = None
        if args.sources:
            sources = [s.strip().lower() for s in args.sources.split(',')]
        
        # Run search
        results = asyncio.run(searcher.search(query, sources=sources))
        
        if not results:
            print("⚠️  No results found. Try a different query.")
            return
        
        # Display results
        print(f"📊 Found {len(results)} results")
        print("=" * 60)
        
        for i, result in enumerate(results[:args.limit or 10], 1):
            # Source badge
            source_badges = {
                'stackoverflow': '🟠 StackOverflow',
                'github': '⚫ GitHub',
                'reddit': '🔴 Reddit',
                'mdn': '🔵 MDN'
            }
            badge = source_badges.get(result.source, result.source)
            
            print(f"\n{i}. [{badge}] {result.title}")
            print(f"   🔗 {result.url}")
            
            # Show snippet (truncated)
            snippet = result.snippet[:200] + "..." if len(result.snippet) > 200 else result.snippet
            print(f"   📝 {snippet}")
            
            # Show score if debug
            if args.debug:
                print(f"   ⭐ Score: {result.score:.2f}")
        
        print(f"\n✅ Search complete!")
        
        # Save output if requested
        if args.output:
            import json
            output_path = Path(args.output)
            results_dict = [
                {
                    'source': r.source,
                    'title': r.title,
                    'url': r.url,
                    'snippet': r.snippet,
                    'score': r.score,
                    'metadata': r.metadata
                }
                for r in results
            ]
            with open(output_path, 'w') as f:
                json.dump(results_dict, f, indent=2)
            print(f"💾 Results saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def get_ollama_models() -> list:
    """Get list of installed Ollama models"""
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            return [line.split()[0] for line in lines if line.strip()]
    except FileNotFoundError:
        pass
    return []


def cmd_tune(args):
    """Handle the 'tune' subcommand - benchmark GPU layers for optimal performance"""
    from stacksense.core.model_manager import ModelManager
    
    print("\n🔧 StackSense Tune - GPU Optimization")
    print("=" * 60)
    
    manager = ModelManager(debug=args.debug)
    
    # Get system info
    sys_info = manager.get_system_info()
    print(f"Platform: {sys_info['platform']} ({sys_info['machine']})")
    if 'gpu' in sys_info:
        print(f"GPU: {sys_info['gpu']}")
    if sys_info.get('apple_silicon'):
        print("Apple Silicon detected ✓")
    print()
    
    # Use specified model or auto-select
    model = args.model
    if not model:
        model = manager.select_best_model()
        if not model:
            print("❌ No Ollama models found. Run: ollama pull llama3:8b")
            sys.exit(1)
        print(f"Auto-selected model: {model}")
    
    print(f"\n⏳ Running GPU layer benchmarks on {model}...")
    print("   This may take a few minutes...\n")
    
    results = manager.benchmark_gpu_layers(model)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        sys.exit(1)
    
    # Display results
    print("\nResults:")
    print("-" * 40)
    
    optimal = results['optimal_layers']
    for layers, tps in results['benchmarks']:
        marker = "  ⭐ OPTIMAL" if layers == optimal else ""
        print(f"  GPU {layers:3d} layers: {tps:6.1f} tokens/sec{marker}")
    
    print()
    print("=" * 60)
    print(f"✅ Recommendation: Use --gpu {optimal}")
    print(f"   Speed: {results['optimal_speed']} tokens/second")
    print()
    print("To apply, set environment variable:")
    print(f"   export OLLAMA_NUM_GPU={optimal}")


def cmd_models(args):
    """Handle the 'models' subcommand - list and auto-select best model"""
    from stacksense.model_manager import ModelManager
    
    print("\n🧠 StackSense Model Manager")
    print("=" * 60)
    
    manager = ModelManager(debug=args.debug)
    models = manager.get_installed_models()
    
    if not models:
        print("❌ No Ollama models found!")
        print("\nTo get started:")
        print("   ollama pull llama3:8b      # Recommended")
        print("   ollama pull phi3:mini      # Lightweight")
        print("   ollama pull qwen2.5:7b     # Fast & smart")
        return
    
    print(f"Found {len(models)} installed models:\n")
    
    # Sort by quality
    models.sort(key=lambda m: m.quality_score, reverse=True)
    
    for i, model in enumerate(models, 1):
        quality_bar = "★" * model.quality_score + "☆" * (10 - model.quality_score)
        code_badge = " [CODE]" if model.is_code_model else ""
        print(f"  {i}. {model.name}")
        print(f"     Size: {model.size_gb:.1f}GB | Params: {model.parameter_count}")
        print(f"     Quality: {quality_bar}{code_badge}")
        print()
    
    # Auto-select best
    best = manager.select_best_model()
    print("-" * 60)
    print(f"✅ Recommended: {best}")
    print("   (Best balance of quality and performance)")
    
    if args.set_default:
        # Save to config
        try:
            from stacksense.cli.config_manager import ConfigManager
            config = ConfigManager()
            config.set_preference('ollama_model', best)
            print(f"\n💾 Set {best} as default model")
        except:
            print(f"\n⚠️  Could not save preference. Use: /model {best}")



def cmd_providers(args):
    """Handle the 'providers' subcommand - list configured providers and their status"""
    import os
    import json
    from pathlib import Path
    
    print("\n🔌 StackSense Provider Status")
    print("=" * 60)
    
    # Check each provider
    providers = [
        {
            'name': 'OpenRouter',
            'env_var': 'OPENROUTER_API_KEY',
            'description': '100+ models, free options',
            'recommended': True
        },
        {
            'name': 'OpenAI',
            'env_var': 'OPENAI_API_KEY',
            'description': 'GPT-4, GPT-4o models'
        },
        {
            'name': 'Grok (xAI)',
            'env_var': 'XAI_API_KEY',
            'description': 'Grok models with real-time knowledge'
        },
        {
            'name': 'TogetherAI',
            'env_var': 'TOGETHER_API_KEY',
            'description': 'Fast open-source models'
        }
    ]
    
    # Get current model preference
    model_pref_path = Path.home() / ".stacksense" / "model_preference.json"
    current_model = None
    if model_pref_path.exists():
        try:
            with open(model_pref_path) as f:
                data = json.load(f)
                current_model = data.get('model', '')
        except:
            pass
    
    print()
    for p in providers:
        api_key = os.environ.get(p['env_var'], '')
        configured = bool(api_key and len(api_key) > 10)
        
        status = "✓" if configured else "○"
        status_color = "configured" if configured else "not configured"
        rec = " ⭐" if p.get('recommended') else ""
        
        print(f"  {status} {p['name']}{rec}")
        print(f"    Status: {status_color}")
        print(f"    {p['description']}")
        
        # Show current model if this is the active provider
        if configured and current_model:
            if p['name'] == 'OpenRouter' and '/' in current_model:
                model_short = current_model.split('/')[-1].replace(':free', '')
                print(f"    Model: {model_short}")
        print()
    
    # Show reload hint
    print("-" * 60)
    print("💡 To configure a provider:")
    print("   1. Get API key from provider's website")
    print("   2. Add to ~/.env or export in shell:")
    print("      export OPENROUTER_API_KEY=sk-or-v1-...")
    print()
    
    # Show stats if requested
    if args.stats:
        stats_path = Path.home() / ".stacksense" / "model_stats.json"
        if stats_path.exists():
            try:
                with open(stats_path) as f:
                    stats = json.load(f)
                print("\n📊 Model Reliability Stats")
                print("-" * 40)
                for model_id, data in stats.items():
                    success = data.get('tool_success', 0)
                    total = data.get('tool_total', 0)
                    pct = (success / total * 100) if total > 0 else 0
                    avg_time = data.get('avg_response_time', 0)
                    print(f"  {model_id.split('/')[-1]}")
                    print(f"    Tool calls: {success}/{total} ({pct:.0f}%)")
                    print(f"    Avg response: {avg_time:.1f}s")
                    print()
            except:
                pass


def cmd_setup_ai(args):
    """Handle AI model setup - cloud providers only"""
    from stacksense.cli.commands import cmd_setup_ai_new
    cmd_setup_ai_new(args)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='stacksense',
        description='🧠 StackSense - AI-Powered Code Intelligence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  stacksense chat                    Start interactive AI chat
  stacksense chat --debug            Chat with debug output
  stacksense scan .                  Scan current directory
  stacksense scan ~/projects/myapp   Scan a specific project
  stacksense diagram .               Generate dependency diagram

Documentation: https://github.com/stacksense
        """
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'StackSense {__version__}'
    )
    
    parser.add_argument(
        '--setup-ai',
        action='store_true',
        help='Configure AI model settings'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        title='commands',
        dest='command',
        description='Available commands'
    )
    
    # =========================================================================
    # CHAT COMMAND
    # =========================================================================
    chat_parser = subparsers.add_parser(
        'chat',
        help='Interactive AI chat with repository context',
        description='Start an interactive AI chat session with code understanding'
    )
    chat_parser.add_argument(
        '-w', '--workspace',
        type=str,
        help='Path to repository/workspace for context'
    )
    chat_parser.add_argument(
        '-m', '--model',
        type=str,
        choices=['openrouter'],  # v2.0: 'ollama' | v3.0: 'openai', 'grok', 'together'
        help='AI provider to use (openrouter only in v1.0)'
    )
    chat_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    chat_parser.set_defaults(func=cmd_chat)
    
    # =========================================================================
    # SCAN COMMAND
    # =========================================================================
    scan_parser = subparsers.add_parser(
        'scan',
        help='Scan and analyze a repository',
        description='Scan a repository to extract code structure and semantics'
    )
    scan_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to repository (default: current directory)'
    )
    scan_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file for scan results (JSON)'
    )
    scan_parser.add_argument(
        '--progressive',
        action='store_true',
        help='Use progressive scanning (priority files first)'
    )
    scan_parser.add_argument(
        '--max-files',
        type=int,
        help='Maximum files to scan'
    )
    scan_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    scan_parser.set_defaults(func=cmd_scan)
    
    # =========================================================================
    # DIAGRAM COMMAND
    # =========================================================================
    diagram_parser = subparsers.add_parser(
        'diagram',
        help='Generate dependency diagrams',
        description='Build code dependency diagrams using Tree-sitter analysis'
    )
    diagram_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to repository (default: current directory)'
    )
    diagram_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output directory for diagram files'
    )
    diagram_parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'dot', 'mermaid', 'all'],
        default='all',
        help='Output format (default: all)'
    )
    diagram_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    diagram_parser.set_defaults(func=cmd_diagram)
    
    # =========================================================================
    # SEARCH COMMAND
    # =========================================================================
    search_parser = subparsers.add_parser(
        'search',
        help='Search StackOverflow, GitHub, Reddit, MDN',
        description='Search developer resources for answers and solutions'
    )
    search_parser.add_argument(
        'query',
        nargs='+',
        help='Search query (e.g., "how to handle async errors in python")'
    )
    search_parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file for search results (JSON)'
    )
    search_parser.add_argument(
        '-s', '--sources',
        type=str,
        help='Comma-separated sources (stackoverflow,github,reddit,mdn)'
    )
    search_parser.add_argument(
        '-l', '--limit',
        type=int,
        default=10,
        help='Maximum results to display (default: 10)'
    )
    search_parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=15.0,
        help='Request timeout in seconds (default: 15.0)'
    )
    search_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    search_parser.set_defaults(func=cmd_search)
    
    # =========================================================================
    # TUNE COMMAND - GPU optimization
    # =========================================================================
    tune_parser = subparsers.add_parser(
        'tune',
        help='Benchmark and optimize Ollama for your hardware',
        description='Find optimal GPU layer settings for your system'
    )
    tune_parser.add_argument(
        '-m', '--model',
        type=str,
        help='Model to benchmark (default: auto-select best)'
    )
    tune_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    tune_parser.set_defaults(func=cmd_tune)
    
    # =========================================================================
    # MODELS COMMAND - list and manage models
    # =========================================================================
    models_parser = subparsers.add_parser(
        'models',
        help='List installed models and auto-select best',
        description='View installed Ollama models and get recommendations'
    )
    models_parser.add_argument(
        '--set-default',
        action='store_true',
        help='Set the recommended model as default'
    )
    models_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    models_parser.set_defaults(func=cmd_models)
    
    # =========================================================================
    # PROVIDERS COMMAND - list configured providers
    # =========================================================================
    providers_parser = subparsers.add_parser(
        'providers',
        help='Show configured AI providers and their status',
        description='View all AI providers, configuration status, and reliability stats'
    )
    providers_parser.add_argument(
        '--stats',
        action='store_true',
        help='Show model reliability statistics'
    )
    providers_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    providers_parser.set_defaults(func=cmd_providers)
    
    # =========================================================================
    # UPGRADE COMMAND - Show pricing and payment links
    # =========================================================================
    upgrade_parser = subparsers.add_parser(
        'upgrade',
        help='View pricing tiers and upgrade your plan',
        description='Show subscription options and open payment page'
    )
    upgrade_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    upgrade_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_upgrade']).cmd_upgrade(args))
    
    # =========================================================================
    # REDEEM COMMAND - Redeem license key for credits
    # =========================================================================
    redeem_parser = subparsers.add_parser(
        'redeem',
        help='Redeem a license key to add credits',
        description='Enter your license key from purchase email to add credits'
    )
    redeem_parser.add_argument(
        'key',
        nargs='?',
        help='License key from purchase email'
    )
    redeem_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    redeem_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_redeem']).cmd_redeem(args))
    
    # =========================================================================
    # LOGIN COMMAND - Login on new device with email + order key
    # =========================================================================
    login_parser = subparsers.add_parser(
        'login',
        help='Login on a new device to restore your credits',
        description='Use your email and last order key to sync credits from server'
    )
    login_parser.add_argument(
        'email',
        nargs='?',
        help='Email used for purchase'
    )
    login_parser.add_argument(
        'key',
        nargs='?',
        help='Last order key from purchase email'
    )
    login_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    login_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_login']).cmd_login(args))
    
    # =========================================================================
    # SET-KEY COMMAND - Activate license (legacy, redirects to redeem)
    # =========================================================================
    setkey_parser = subparsers.add_parser(
        'set-key',
        help='Activate a new license key (use "redeem" instead)',
        description='Enter your license key from purchase email to activate'
    )
    setkey_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    setkey_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_set_key']).cmd_set_key(args))
    
    # =========================================================================
    # REPLACE-KEY COMMAND - Replace existing license
    # =========================================================================
    replacekey_parser = subparsers.add_parser(
        'replace-key',
        help='Replace existing license with a new key',
        description='Replace your current license key with a new one'
    )
    replacekey_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    replacekey_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_replace_key']).cmd_replace_key(args))
    
    # =========================================================================
    # STATUS COMMAND - Full subscription status
    # =========================================================================
    status_parser = subparsers.add_parser(
        'status',
        help='Show license and usage status',
        description='Display your subscription status, usage, and limits'
    )
    status_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    status_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_status']).cmd_status(args))
    
    # =========================================================================
    # USAGE COMMAND - Detailed usage breakdown
    # =========================================================================
    usage_parser = subparsers.add_parser(
        'usage',
        help='Show detailed usage breakdown',
        description='View your API call usage by feature and time'
    )
    usage_parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed breakdown by feature'
    )
    usage_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    usage_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_usage']).cmd_usage(args))
    
    # =========================================================================
    # CREDITS COMMAND - Show credit balance
    # =========================================================================
    credits_parser = subparsers.add_parser(
        'credits',
        help='Show your current credit balance',
        description='Display your credit balance, usage, and cost reference'
    )
    credits_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    credits_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_credits']).cmd_credits(args))
    
    # =========================================================================
    # PROVIDER COMMAND - Configure AI provider
    # =========================================================================
    provider_parser = subparsers.add_parser(
        'provider',
        help='Configure AI provider settings',
        description='Set up or reset your AI provider (OpenRouter in v1.0)'
    )
    provider_parser.add_argument(
        'action',
        nargs='?',
        choices=['reset', 'show'],
        default='show',
        help='Action to perform (reset or show current)'
    )
    provider_parser.add_argument(
        '--provider', '-p',
        type=str,
        choices=['openrouter'],  # v2.0: 'ollama' | v3.0: 'openai', 'grok', 'together'
        help='Specific provider to configure (openrouter only in v1.0)'
    )
    provider_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    provider_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_provider_reset']).cmd_provider_reset(args) if args.action == 'reset' else print("Current provider: " + __import__('stacksense.core.config', fromlist=['Config']).Config().provider))
    
    # =========================================================================
    # DOCTOR COMMAND - System diagnostics
    # =========================================================================
    doctor_parser = subparsers.add_parser(
        'doctor',
        help='Diagnose StackSense installation',
        description='Check provider, API key, license, usage, filesystem health'
    )
    doctor_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    doctor_parser.set_defaults(func=lambda args: __import__('stacksense.cli.commands', fromlist=['cmd_doctor']).cmd_doctor(args))
    
    # =========================================================================
    # PARSE AND EXECUTE
    # =========================================================================
    args = parser.parse_args()
    
    # Handle --setup-ai
    if args.setup_ai:
        cmd_setup_ai(args)
        return
    
    # No command given
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
