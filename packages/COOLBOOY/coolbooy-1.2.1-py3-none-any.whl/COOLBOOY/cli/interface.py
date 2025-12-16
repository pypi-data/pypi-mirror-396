"""
Terminal aliases interface for COOLBOOY CLI

Provides terminal alias setup functionality for COOLBOOY integration.
"""

import os
import sys
import platform
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from ..core.manager import manager
from .commands import handle_status, handle_list_providers

# Initialize rich console
console = Console()


def handle_interactive_interface() -> None:
    """Handle --interface option to setup terminal aliases"""
    console.print(Panel(
        "[bold green]COOLBOOY Terminal Integration Setup[/bold green]\n"
        "Setting up aliases for your terminal...",
        title="COOLBOOY Integration",
        border_style="green"
    ))
    
    setup_terminal_aliases()


def _load_aliases_immediately(system: str) -> None:
    """Load aliases immediately in the current session"""
    if system == "windows":
        try:
            # Try to source the profile to load aliases
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", ". $PROFILE"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("\n[[bold green]✓[/bold green]] PowerShell profile reloaded successfully.!")
                console.print("[[bold blue]ℹ[/bold blue]] Aliases are now available in this session")
            else:
                console.print("\n[[bold yellow]![/bold yellow]] Auto-reload failed. Run manually:")
                console.print("[cyan]. $PROFILE[/cyan]")
                
        except Exception as e:
            console.print(f"\n[[bold yellow]![/bold yellow]] Could not auto-reload profile: {e}")
            console.print("[[bold blue]ℹ[/bold blue]] Run manually: [cyan]. $PROFILE[/cyan]")
    else:
        # For Unix systems, provide source command
        console.print("\n[[bold blue]ℹ[/bold blue]] To use aliases immediately, run:")
        shell = os.environ.get('SHELL', '/bin/bash')
        if 'zsh' in shell:
            console.print("[cyan]source ~/.zshrc[/cyan]")
        else:
            console.print("[cyan]source ~/.bashrc[/cyan]")
        return


def setup_terminal_aliases() -> None:
    """Setup terminal aliases for COOLBOOY integration"""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            _setup_windows_aliases()
        elif system == "darwin":  # macOS
            _setup_unix_aliases("zsh")
        else:  # Linux
            shell = os.environ.get('SHELL', '/bin/bash')
            if 'zsh' in shell:
                _setup_unix_aliases("zsh")
            elif 'fish' in shell:
                _setup_fish_aliases()
            else:
                _setup_unix_aliases("bash")
                
        console.print("[[bold green]+[/bold green]] Terminal aliases setup completed.!")
        
        # Try to provide immediate usage instructions
        _load_aliases_immediately(system)
        
        console.print(Panel(
            "[bold green]✓ Setup Complete.![/bold green]\n\n"
            "[bold]Available Terminal Aliases:[/bold]\n"
            "• [cyan]:[/cyan] [yellow]<prompt>[/yellow] - Chat with AI\n"
            "• [cyan]s:[/cyan] [yellow]<prompt>[/yellow] - Generate shell commands\n"
            "• [cyan]c:[/cyan] [yellow]<prompt>[/yellow] - Generate code only\n"
            "• [cyan]e:[/cyan] - Open editor for complex prompts\n\n"
            "[bold]Examples:[/bold]\n"
            "• [cyan]:[/cyan] What is machine learning.?\n"
            "• [cyan]s:[/cyan] Find all Python files\n"
            "• [cyan]c:[/cyan] Create a sorting function\n"
            "• [cyan]e:[/cyan]\n\n"
            "[bold yellow]Note:[/bold yellow] If aliases don't work immediately, run: [cyan]. $PROFILE[/cyan]",
            title="Ready to Use",
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(f"[[bold red]-[/bold red]] Error setting up aliases: {e}")


def _setup_windows_aliases() -> None:
    """Setup aliases for Windows PowerShell"""
    # Get PowerShell profile path
    profile_paths = [
        os.path.expanduser("~/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1"),
        os.path.expanduser("~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1")
    ]
    
    # Find existing profile or create new one
    profile_path = None
    for path in profile_paths:
        try:
            if os.path.exists(os.path.dirname(path)):
                profile_path = path
                break
        except Exception:
            continue
    
    if not profile_path:
        # Create PowerShell directory
        profile_path = profile_paths[1]
        try:
            os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        except PermissionError:
            console.print("[[bold red]-[/bold red]] Permission denied. Try running as administrator.")
            return
    
    # PowerShell aliases
    aliases = '''
# COOLBOOY Terminal Integration
function COOLBOOY_chat { COOLBOOY $args }
function COOLBOOY_shell { COOLBOOY --shell $args }
function COOLBOOY_code { COOLBOOY --code $args }
function COOLBOOY_editor { COOLBOOY --editor }

# Shorter aliases - using : instead of ! for compatibility
function : { COOLBOOY $args }
function s: { COOLBOOY --shell $args }
function c: { COOLBOOY --code $args }
function e: { COOLBOOY --editor }
'''
    
    try:
        # Read existing profile
        existing_content = ""
        if os.path.exists(profile_path):
            with open(profile_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # Add aliases if not already present
        if "COOLBOOY Terminal Integration" not in existing_content:
            with open(profile_path, 'a', encoding='utf-8') as f:
                f.write(aliases)
        
        console.print(f"[[bold green]+[/bold green]] PowerShell profile updated: {profile_path}")
        console.print("[[bold yellow]![/bold yellow]] Restart PowerShell or run: [cyan]. $PROFILE[/cyan]")
        
    except PermissionError:
        console.print("[[bold red]-[/bold red]] Permission denied. Try running as administrator.")
    except Exception as e:
        console.print(f"[[bold red]-[/bold red]] Error updating profile: {e}")


def _setup_unix_aliases(shell_type: str) -> None:
    """Setup aliases for Unix-like systems (bash/zsh)"""
    if shell_type == "zsh":
        profile_path = os.path.expanduser("~/.zshrc")
    else:
        profile_path = os.path.expanduser("~/.bashrc")
    
    # Shell aliases - fixed ! function for compatibility
    aliases = '''
# COOLBOOY Terminal Integration
alias COOLBOOY_chat="COOLBOOY"
alias COOLBOOY_shell="COOLBOOY --shell"
alias COOLBOOY_code="COOLBOOY --code"
alias COOLBOOY_editor="COOLBOOY --editor"

# Shorter aliases - using functions for complex ones
function :() { COOLBOOY "$@"; }
function s:() { COOLBOOY --shell "$@"; }
function c:() { COOLBOOY --code "$@"; }
function e:() { COOLBOOY --editor; }
'''
    
    try:
        # Read existing profile
        existing_content = ""
        if os.path.exists(profile_path):
            with open(profile_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # Add aliases if not already present
        if "COOLBOOY Terminal Integration" not in existing_content:
            with open(profile_path, 'a', encoding='utf-8') as f:
                f.write(aliases)
        
        console.print(f"[[bold green]+[/bold green]] {shell_type} profile updated: {profile_path}")
        console.print(f"[[bold yellow]![/bold yellow]] Restart terminal or run: [cyan]source {profile_path}[/cyan]")
        
    except PermissionError:
        console.print(f"[[bold red]-[/bold red]] Permission denied accessing {profile_path}")
    except Exception as e:
        console.print(f"[[bold red]-[/bold red]] Error updating profile: {e}")


def _setup_fish_aliases() -> None:
    """Setup aliases for Fish shell"""
    config_dir = os.path.expanduser("~/.config/fish")
    functions_dir = os.path.join(config_dir, "functions")
    
    try:
        # Create functions directory if it doesn't exist
        os.makedirs(functions_dir, exist_ok=True)
        
        # Fish function definitions
        functions = {
            "__COOLBOOY_colon.fish": '''function :
    COOLBOOY $argv
end''',
            "s_colon.fish": '''function s:
    COOLBOOY --shell $argv
end''',
            "c_colon.fish": '''function c:
    COOLBOOY --code $argv
end''',
            "e_colon.fish": '''function e:
    COOLBOOY --editor
end'''
        }
        
        # Create function files
        created_files = []
        for filename, content in functions.items():
            file_path = os.path.join(functions_dir, filename)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created_files.append(filename)
        
        if created_files:
            console.print(f"[[bold green]+[/bold green]] Fish functions created in: {functions_dir}")
            console.print("[[bold yellow]![/bold yellow]] Functions are immediately available.!")
        else:
            console.print("[[bold green]+[/bold green]] Fish functions already exist.!")
            
    except PermissionError:
        console.print(f"[[bold red]-[/bold red]] Permission denied accessing {functions_dir}")
    except Exception as e:
        console.print(f"[[bold red]-[/bold red]] Error setting up Fish functions: {e}")
