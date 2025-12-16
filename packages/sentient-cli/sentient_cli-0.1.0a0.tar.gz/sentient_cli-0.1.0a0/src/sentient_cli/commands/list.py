"""
List deployments command for Sentient CLI
"""

import os
import click
import requests
from rich.console import Console
from rich.table import Table
from rich.text import Text

from ..auth import require_authentication
from .common import render_deployments

console = Console()


@click.command()
@click.option('--status', type=click.Choice(['building', 'deploying', 'running', 'error', 'stopped']), help='Filter by deployment status')
@click.option('--type', 'deployment_type', type=click.Choice(['agent', 'mcp']), help='Filter by deployment type')
@click.option('--visibility', type=click.Choice(['public', 'private']), help='Filter by visibility')
@click.option('--page', default=1, help='Page number (default: 1)')
@click.option('--page-size', 'page_size', default=20, help='Items per page (default: 20)')
@click.option('--api-url', default=None, help='Override Sentient API base URL (defaults to env SENTIENT_API_URL or https://api.sentient-space.com)')
def list_deployments(status: str, deployment_type: str, visibility: str, page: int, page_size: int, api_url: str) -> None:
    """List your deployments"""
    
    token = require_authentication()
    base_url = api_url or os.getenv("SENTIENT_API_URL", "https://api.sentient-space.com")
    
    # Build query parameters
    params = {
        "page": page,
        "page_size": page_size,
    }
    if status:
        params["status"] = status
    if deployment_type:
        params["type"] = deployment_type
    if visibility:
        params["visibility"] = visibility
    
    # Show spinner while fetching and verifying deployments
    from rich.progress import Progress, SpinnerColumn, TextColumn
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[yellow]Fetching deployments...", total=None)
        
        try:
            resp = requests.get(
                f"{base_url}/api/deployments",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            progress.update(task, description="[red]❌ Failed to fetch[/red]")
            raise click.ClickException(f"Failed to fetch deployments: {str(e)}")
    
    data = resp.json()
    items = data.get("items", [])
    total = data.get("total", 0)
    current_page = data.get("page", 1)
    page_size_actual = data.get("page_size", page_size)
    
    if not items:
        console.print("[yellow]No deployments found[/yellow]")
        return
    
    # Responsive rendering (wide -> table, narrow -> stacked panels)
    render_deployments(items, base_url=base_url, title=f"Deployments (Page {current_page}, Total: {total})")
    
    # Show pagination info
    if total > page_size_actual:
        total_pages = (total + page_size_actual - 1) // page_size_actual
        console.print(f"\n[dim]Showing page {current_page} of {total_pages} (use --page to navigate)[/dim]")