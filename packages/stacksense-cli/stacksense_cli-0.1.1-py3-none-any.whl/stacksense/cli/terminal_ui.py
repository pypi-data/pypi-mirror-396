"""
StackSense Terminal UI
Beautiful terminal output using rich
"""
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.markdown import Markdown
from typing import List, Dict, Optional
import os

console = Console()


def show_workspace_header(workspace_name: str, repos_count: int, languages: list):
    """Show workspace initialization header (compact)"""
    lang_str = ', '.join(languages[:3])
    info = f"[green]📂 {workspace_name}[/green] │ [cyan]{repos_count} repo[/cyan] │ [yellow]{lang_str}[/yellow]"
    console.print(f"  {info}")


def show_diagram_summary(summary_text: str):
    """Show diagram summary (compact single line)"""
    # Parse the summary text to extract key info
    lines = summary_text.split('\n')
    
    # Extract key metrics
    files_count = "?"
    deps_count = "?"
    languages = "?"
    entry_points = []
    
    for line in lines:
        if "Files:" in line:
            files_count = line.split(":")[-1].strip()
        elif "Dependencies:" in line:
            deps_count = line.split(":")[-1].strip()
        elif line.strip().startswith("- ") and "__init__" in line:
            entry_points.append(line.strip("- ").strip())
    
    # Find languages section
    in_languages = False
    for line in lines:
        if "## Languages" in line:
            in_languages = True
            continue
        if in_languages and line.strip() and not line.startswith("#"):
            languages = line.strip()
            break
    
    entry_str = ", ".join(entry_points[:2]) if entry_points else "main"
    
    # Single compact line
    info = f"[cyan]📁 {files_count} files[/cyan] │ [green]🔗 {deps_count} deps[/green] │ [yellow]📍 {entry_str}[/yellow]"
    console.print(f"  {info}")
    console.print()


def show_codebase_overview(repos: List[Dict], workspace_name: str = None, tech_stack: str = None):
    """
    Show codebase overview panel with repo information.
    
    Args:
        repos: List of repo dicts with keys: name, languages, file_count, folders
        workspace_name: Optional workspace name
        tech_stack: Optional tech stack string (e.g., "Python + FastAPI + PostgreSQL")
    """
    # Build content
    lines = []
    
    for repo in repos[:8]:  # Max 8 repos
        name = repo.get('name', 'unknown')
        langs = repo.get('languages', [])
        file_count = repo.get('file_count', '?')
        folders = repo.get('folders', [])
        
        # Format tech stack
        lang_str = ' • '.join(langs[:3]) if langs else 'unknown'
        folder_str = ' '.join(folders[:4]) if folders else ''
        
        lines.append(f"[bold white]  📦 {name}[/bold white]")
        lines.append(f"[cyan]     {lang_str}[/cyan]")
        if folder_str:
            lines.append(f"[dim]     {file_count} files • {folder_str}[/dim]")
        else:
            lines.append(f"[dim]     {file_count} files[/dim]")
    
    # Add tech stack if available (inside the panel)
    if tech_stack and tech_stack != "Unknown":
        lines.append("")  # Spacing
        lines.append(f"[magenta]  🔧 {tech_stack}[/magenta]")
    
    content = "\n".join(lines).rstrip()
    
    # Purple-bordered panel
    title = f"CODEBASE OVERVIEW"
    if workspace_name:
        title = f"CODEBASE: {workspace_name}"
    
    panel = Panel(
        content,
        title=f"[bold magenta]{title}[/bold magenta]",
        border_style="magenta",
        expand=False,
        padding=(0, 1)
    )
    
    console.print(panel)
    console.print()


def show_query_stats(keywords: list, files_searched: int, slices: int, time_ms: int = None):
    """Show query statistics"""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")
    
    table.add_row("Keywords", ', '.join(keywords[:3]))
    table.add_row("Files searched", str(files_searched))
    table.add_row("Code sections found", str(slices))
    
    if time_ms:
        table.add_row("Time", f"{time_ms/1000:.1f}s")
    
    console.print("\n")
    console.print(table)
    console.print()


def format_answer(answer: str) -> str:
    """Format answer with markdown rendering"""
    # Rich markdown will handle the formatting
    return answer


def show_error(message: str):
    """Show error message"""
    console.print(f"[bold red]❌ {message}[/bold red]")


def show_success(message: str):
    """Show success message"""
    console.print(f"[bold green]✅ {message}[/bold green]")


def show_warning(message: str):
    """Show warning message"""
    console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")


def show_info(message: str):
    """Show info message"""
    console.print(f"[cyan]{message}[/cyan]")


def detect_repo_info(repo_path: str) -> Dict:
    """
    Detect information about a repository.
    
    Returns:
        Dict with: name, languages, file_count, folders
    """
    from pathlib import Path
    
    path = Path(repo_path)
    name = path.name
    
    # Detect languages by file extensions
    lang_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'React',
        '.jsx': 'React',
        '.go': 'Go',
        '.rs': 'Rust',
        '.java': 'Java',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.vue': 'Vue',
    }
    
    framework_files = {
        'package.json': 'Node.js',
        'requirements.txt': 'Python',
        'Cargo.toml': 'Rust',
        'go.mod': 'Go',
        'pom.xml': 'Java',
        'Gemfile': 'Ruby',
    }
    
    ignore_dirs = {'venv', '.venv', 'node_modules', '__pycache__', '.git', 'dist', 'build', '.next'}
    
    languages = set()
    file_count = 0
    folders = []
    
    try:
        # Get top-level folders
        for item in path.iterdir():
            if item.is_dir() and item.name not in ignore_dirs and not item.name.startswith('.'):
                folders.append(f"{item.name}/")
        
        # Check for framework files
        for fw_file, fw_name in framework_files.items():
            if (path / fw_file).exists():
                languages.add(fw_name)
        
        # Scan files (limit depth for speed)
        for item in path.rglob('*'):
            if item.is_file():
                # Skip ignored directories
                if any(ign in str(item) for ign in ignore_dirs):
                    continue
                
                file_count += 1
                ext = item.suffix.lower()
                if ext in lang_map:
                    languages.add(lang_map[ext])
                
                # Limit for performance
                if file_count > 500:
                    break
    except Exception:
        pass
    
    return {
        'name': name,
        'languages': list(languages)[:4],
        'file_count': file_count,
        'folders': folders[:5]
    }

