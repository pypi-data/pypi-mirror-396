"""
StackSense Model Manager
========================
Dynamic Ollama model management with:
1. Auto model selection (picks best from installed)
2. Session-based keep-alive (warm during chat, unload on exit)
3. GPU layer benchmarking (stacksense tune)
"""

import os
import time
import requests
import threading
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ModelInfo:
    """Information about an installed model"""
    name: str
    size_gb: float
    parameter_count: str  # e.g., "7B", "13B", "70B"
    is_code_model: bool
    quality_score: int  # 1-10, higher is better


class ModelManager:
    """
    Manages Ollama model selection and lifecycle.
    
    Features:
    - Auto-selects best model from installed ones
    - Keeps model warm only during chat session
    - Benchmarks GPU layers for optimal performance
    """
    
    OLLAMA_URL = "http://localhost:11434"
    
    # Model quality rankings (higher = better)
    MODEL_QUALITY = {
        'qwen2.5': 9,
        'llama3': 9,
        'mistral': 8,
        'codellama': 8,
        'deepseek-coder': 8,
        'phi3': 7,
        'phi': 6,
        'gemma': 7,
        'tinyllama': 5,
    }
    
    # Code-focused models
    CODE_MODELS = ['codellama', 'deepseek-coder', 'qwen2.5-coder', 'starcoder']
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.session_keep_alive_thread = None
        self.session_active = False
        self.current_model = None
        self.optimal_gpu_layers = None
    
    def get_installed_models(self) -> List[ModelInfo]:
        """Get list of installed Ollama models with details"""
        try:
            response = requests.get(f"{self.OLLAMA_URL}/api/tags", timeout=10)
            if response.status_code != 200:
                return []
            
            models_data = response.json().get('models', [])
            models = []
            
            for model in models_data:
                name = model.get('name', '')
                size_bytes = model.get('size', 0)
                size_gb = size_bytes / (1024 ** 3)
                
                # Extract parameter count from name or estimate from size
                param_count = self._estimate_params(name, size_gb)
                
                # Check if code model
                is_code = any(cm in name.lower() for cm in self.CODE_MODELS)
                
                # Calculate quality score
                quality = self._calculate_quality(name, param_count)
                
                models.append(ModelInfo(
                    name=name,
                    size_gb=size_gb,
                    parameter_count=param_count,
                    is_code_model=is_code,
                    quality_score=quality
                ))
            
            return models
            
        except Exception as e:
            if self.debug:
                print(f"[ModelManager] Failed to get models: {e}")
            return []
    
    def _estimate_params(self, name: str, size_gb: float) -> str:
        """Estimate parameter count from model name or size"""
        # Try to extract from name
        import re
        match = re.search(r'(\d+)[bB]', name)
        if match:
            return f"{match.group(1)}B"
        
        # Estimate from size (Q4 quantized)
        if size_gb < 2:
            return "1-3B"
        elif size_gb < 5:
            return "7B"
        elif size_gb < 10:
            return "13B"
        elif size_gb < 25:
            return "34B"
        else:
            return "70B+"
    
    def _calculate_quality(self, name: str, param_count: str) -> int:
        """Calculate quality score based on model family and size"""
        base_score = 5
        
        # Check model family
        for family, score in self.MODEL_QUALITY.items():
            if family in name.lower():
                base_score = score
                break
        
        # Adjust for parameter count
        if '70B' in param_count or '34B' in param_count:
            base_score = min(10, base_score + 1)
        elif '1B' in param_count or '3B' in param_count:
            base_score = max(1, base_score - 1)
        
        return base_score
    
    def select_best_model(self, prefer_code: bool = False) -> Optional[str]:
        """
        Automatically select the best installed model.
        
        Strategy:
        1. Get all installed models
        2. Filter by type if needed (code vs general)
        3. Balance quality and size (prefer 7B-13B sweet spot)
        4. Return best match
        """
        models = self.get_installed_models()
        
        if not models:
            return None
        
        # Filter for code models if preferred
        if prefer_code:
            code_models = [m for m in models if m.is_code_model]
            if code_models:
                models = code_models
        
        # Score models: quality * size_factor
        # Prefer 7B-13B range (not too slow, not too dumb)
        scored = []
        for model in models:
            # Size factor: 7B-13B gets bonus
            if model.size_gb < 3:
                size_factor = 0.7  # Too small, might be inaccurate
            elif model.size_gb < 6:
                size_factor = 0.9  # Good lightweight
            elif model.size_gb < 12:
                size_factor = 1.0  # Sweet spot
            elif model.size_gb < 25:
                size_factor = 0.9  # Still good but slower
            else:
                size_factor = 0.7  # Too slow for interactive use
            
            final_score = model.quality_score * size_factor
            scored.append((final_score, model))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        
        best_model = scored[0][1]
        
        if self.debug:
            print(f"[ModelManager] Selected: {best_model.name} "
                  f"(quality={best_model.quality_score}, size={best_model.size_gb:.1f}GB)")
        
        return best_model.name
    
    def start_session(self, model_name: str):
        """
        Start a chat session - keep model warm.
        Called when user starts `stacksense chat`.
        """
        self.current_model = model_name
        self.session_active = True
        
        # Warm up model immediately
        self._warm_model()
        
        # Start keep-alive thread
        self._start_session_keep_alive()
        
        if self.debug:
            print(f"[ModelManager] Session started with {model_name}")
    
    def end_session(self):
        """
        End chat session - allow model to unload.
        Called when user exits chat or presses Ctrl+C.
        """
        self.session_active = False
        
        # Unload model to free memory
        self._unload_model()
        
        if self.debug:
            print(f"[ModelManager] Session ended, model unloaded")
    
    def _warm_model(self):
        """Warm up the current model"""
        if not self.current_model:
            return
        
        try:
            requests.post(
                f"{self.OLLAMA_URL}/api/generate",
                json={
                    'model': self.current_model,
                    'prompt': 'ready',
                    'stream': False,
                    'keep_alive': '30m',
                    'options': {'num_predict': 1}
                },
                timeout=120
            )
        except Exception as e:
            if self.debug:
                print(f"[ModelManager] Warmup failed: {e}")
    
    def _unload_model(self):
        """Unload model from memory"""
        if not self.current_model:
            return
        
        try:
            # Setting keep_alive to 0 unloads immediately
            requests.post(
                f"{self.OLLAMA_URL}/api/generate",
                json={
                    'model': self.current_model,
                    'prompt': '',
                    'keep_alive': '0'
                },
                timeout=10
            )
        except:
            pass  # Best effort
    
    def _start_session_keep_alive(self):
        """Start background thread to keep model warm during session"""
        def keep_alive_loop():
            PING_INTERVAL = 5 * 60  # 5 minutes
            
            while self.session_active:
                for _ in range(PING_INTERVAL):
                    if not self.session_active:
                        return
                    time.sleep(1)
                
                if self.session_active:
                    self._warm_model()
                    if self.debug:
                        print(f"[ModelManager] Keep-alive ping sent")
        
        self.session_keep_alive_thread = threading.Thread(
            target=keep_alive_loop, daemon=True
        )
        self.session_keep_alive_thread.start()
    
    def benchmark_gpu_layers(self, model_name: str = None) -> Dict:
        """
        Benchmark different GPU layer configurations to find optimal.
        
        Returns dict with:
        - optimal_layers: Best GPU layer count
        - benchmarks: List of (layers, tokens_per_second) tuples
        - recommendation: Human-readable recommendation
        """
        model = model_name or self.current_model
        if not model:
            return {'error': 'No model specified'}
        
        benchmarks = []
        test_prompt = "Count from 1 to 10 quickly."
        
        # Test different GPU layer values
        gpu_values = [0, 8, 16, 24, 32, 48, 64]
        
        for gpu_layers in gpu_values:
            try:
                start = time.time()
                
                response = requests.post(
                    f"{self.OLLAMA_URL}/api/generate",
                    json={
                        'model': model,
                        'prompt': test_prompt,
                        'stream': False,
                        'options': {
                            'num_gpu': gpu_layers,
                            'num_predict': 50
                        }
                    },
                    timeout=120
                )
                
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    tokens = data.get('eval_count', 50)
                    tps = tokens / elapsed if elapsed > 0 else 0
                    benchmarks.append((gpu_layers, round(tps, 1)))
                    
                    if self.debug:
                        print(f"[Benchmark] GPU={gpu_layers}: {tps:.1f} tok/s")
                else:
                    # Out of memory or error
                    if self.debug:
                        print(f"[Benchmark] GPU={gpu_layers}: FAILED")
                    break
                    
            except Exception as e:
                if self.debug:
                    print(f"[Benchmark] GPU={gpu_layers}: ERROR - {e}")
                break
        
        if not benchmarks:
            return {'error': 'Benchmarking failed'}
        
        # Find optimal (highest tokens/sec)
        optimal = max(benchmarks, key=lambda x: x[1])
        
        return {
            'optimal_layers': optimal[0],
            'optimal_speed': optimal[1],
            'benchmarks': benchmarks,
            'recommendation': f"Use --gpu {optimal[0]} for {optimal[1]} tokens/second"
        }
    
    def get_system_info(self) -> Dict:
        """Get system information for optimization decisions"""
        import platform
        
        info = {
            'platform': platform.system(),
            'machine': platform.machine(),
            'python': platform.python_version(),
        }
        
        # Try to get GPU info
        try:
            # Check if NVIDIA GPU
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info['gpu'] = result.stdout.strip()
        except:
            pass
        
        # Check for Apple Silicon
        if platform.system() == 'Darwin' and platform.machine() == 'arm64':
            info['apple_silicon'] = True
        
        return info


def create_tune_command():
    """Create the 'stacksense tune' CLI command"""
    import click
    
    @click.command()
    @click.option('--model', '-m', help='Model to benchmark (default: auto-select)')
    @click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
    def tune(model, verbose):
        """Benchmark and optimize Ollama for your hardware."""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        manager = ModelManager(debug=verbose)
        
        console.print("\n[bold cyan]🔧 StackSense Tune[/bold cyan]")
        console.print("Finding optimal settings for your hardware...\n")
        
        # Get system info
        sys_info = manager.get_system_info()
        console.print(f"Platform: {sys_info['platform']} ({sys_info['machine']})")
        if 'gpu' in sys_info:
            console.print(f"GPU: {sys_info['gpu']}")
        if sys_info.get('apple_silicon'):
            console.print("Apple Silicon detected ✓")
        
        console.print()
        
        # Select model
        if not model:
            model = manager.select_best_model()
            if not model:
                console.print("[red]No models installed. Run: ollama pull llama3:8b[/red]")
                return
            console.print(f"[green]Auto-selected model: {model}[/green]\n")
        
        # Run benchmark
        console.print("[yellow]Running GPU layer benchmarks...[/yellow]")
        console.print("[dim]This may take a few minutes[/dim]\n")
        
        results = manager.benchmark_gpu_layers(model)
        
        if 'error' in results:
            console.print(f"[red]Error: {results['error']}[/red]")
            return
        
        # Display results
        table = Table(title="GPU Layer Benchmark Results")
        table.add_column("GPU Layers", style="cyan")
        table.add_column("Tokens/sec", style="green")
        table.add_column("Status", style="yellow")
        
        optimal = results['optimal_layers']
        for layers, tps in results['benchmarks']:
            status = "⭐ OPTIMAL" if layers == optimal else ""
            table.add_row(str(layers), str(tps), status)
        
        console.print(table)
        console.print()
        
        # Recommendation
        console.print(Panel(
            f"[bold green]Recommendation:[/bold green]\n"
            f"Add to your Ollama commands: [cyan]--gpu {optimal}[/cyan]\n"
            f"This gives {results['optimal_speed']} tokens/second",
            title="✅ Optimization Complete"
        ))
    
    return tune
