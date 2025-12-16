"""
Authentication commands for Sentient CLI
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..auth import cli_auth_manager

console = Console()


@click.group()
def auth() -> None:
    """Authentication commands"""
    pass


@auth.command()
def login() -> None:
    """Login to Sentient Web Platform"""
    try:
        # Check if already authenticated
        auth_status = cli_auth_manager.get_auth_status()
        if auth_status["authenticated"]:
            user_info = auth_status["user"]
            display_user = (
                user_info.get("email")
                or user_info.get("name")
                or user_info.get("clerk_id")
                or "Unknown"
            )
            console.print(f"[yellow]Already authenticated as {display_user}[/yellow]")
            
            if not click.confirm("Do you want to login with a different account?"):
                return
            # If user wants to login with different account, force fresh login
            console.print("[yellow]Starting fresh login process...[/yellow]")
            token = cli_auth_manager.initiate_browser_login(force_login=True)
        else:
            # Not authenticated, always force fresh login to ensure clean state
            token = cli_auth_manager.initiate_browser_login(force_login=True)
        
        console.print("\n[green]🎉 Authentication successful![/green]")
        console.print("[dim]You can now use 'sen init' to initialize your project.[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Authentication failed: {str(e)}[/red]")
        raise click.ClickException("Authentication failed")


@auth.command()
def logout() -> None:
    """Logout from Sentient Web Platform"""
    try:
        auth_status = cli_auth_manager.get_auth_status()
        
        if not auth_status["authenticated"]:
            console.print("[yellow]Not currently authenticated[/yellow]")
            return
        
        cli_auth_manager.logout()
        # Slimmer, production-ready success message
        console.print("[green]✔ Successfully logged out[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Logout failed: {str(e)}[/red]")
        raise click.ClickException("Logout failed")


@auth.command()
def status() -> None:
    """Show authentication status"""
    try:
        auth_status = cli_auth_manager.get_auth_status()
        
        if auth_status["authenticated"]:
            user_info = auth_status["user"]
            
            # Create status table
            table = Table(title="Authentication Status")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Status", "✅ Authenticated")
            table.add_row("Email", user_info.get("email", "Unknown"))
            table.add_row("Name", user_info.get("name", "Unknown"))
            table.add_row("Clerk ID", user_info.get("clerk_id", "Unknown"))
            
            console.print(table)
            
        else:
            console.print(Panel.fit(
                "[red]❌ Not authenticated[/red]\n\n"
                "Run [bold]sen auth login[/bold] to authenticate.",
                title="Authentication Status"
            ))
            
    except Exception as e:
        console.print(f"[red]❌ Failed to get auth status: {str(e)}[/red]")
        raise click.ClickException("Failed to get authentication status")