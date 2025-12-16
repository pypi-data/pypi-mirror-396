"""
Metrics command for Sentient CLI (Task 8)
"""

import os
import click
import requests
from typing import Optional
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from ..auth import require_authentication
from .common import resolve_deployment_id

console = Console()


@click.command()
@click.option('--id', 'deployment_id', default=None, help='Deployment ID')
@click.option('--name', 'deployment_name', default=None, help='Deployment name (partial match)')
@click.option('--since', default=None, help='Start time (ISO 8601, default: 7 days ago)')
@click.option('--until', default=None, help='End time (ISO 8601, default: now)')
@click.option('--bucket', type=click.Choice(['day', 'hour']), default='day', help='Time bucket')
@click.option('--api-url', default=None, help='Override Sentient API base URL')
def metrics(
    deployment_id: Optional[str],
    deployment_name: Optional[str],
    since: Optional[str],
    until: Optional[str],
    bucket: str,
    api_url: Optional[str],
) -> None:
    """View deployment metrics (requests, errors, response times)."""
    
    token = require_authentication()
    base_url = api_url or os.getenv("SENTIENT_API_URL", "https://api.sentient-space.com")
    
    # Resolve deployment ID (interactive selection if needed)
    try:
        deployment_id = resolve_deployment_id(deployment_id, deployment_name, token, base_url)
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Failed to resolve deployment: {str(e)}")
    
    # Build query params
    params = {"bucket": bucket}
    if since:
        params["since"] = since
    if until:
        params["until"] = until
    
    try:
        resp = requests.get(
            f"{base_url}/api/deployments/{deployment_id}/metrics",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=30,
        )
        
        if resp.status_code == 404:
            raise click.ClickException(f"Deployment {deployment_id[:12]} not found")
        resp.raise_for_status()
        
        data = resp.json()
        items = data.get("items", [])
        summary = data.get("summary", {})
        all_time = data.get("all_time", None)
        
        if not items:
            console.print("[yellow]No metrics found for this time range[/yellow]")
            return
        
        # Display summary
        console.print(Panel.fit(
            f"[bold]Total Requests:[/bold] {summary.get('total_requests', 0):,}\n"
            f"[bold]Total Errors:[/bold] {summary.get('total_errors', 0):,}\n"
            f"[bold]Error Rate:[/bold] {summary.get('error_rate', 0.0):.2f}%\n"
            f"[bold]Avg P50:[/bold] {summary.get('avg_p50_ms', 0):.1f}ms\n"
            f"[bold]Avg P95:[/bold] {summary.get('avg_p95_ms', 0):.1f}ms",
            title="Summary",
            border_style="green",
        ))

        if all_time:
            console.print(Panel.fit(
                f"[bold]All-time Requests:[/bold] {all_time.get('total_requests', 0):,}\n"
                f"[bold]All-time Errors:[/bold] {all_time.get('total_errors', 0):,}\n"
                f"[bold]All-time Error Rate:[/bold] {all_time.get('error_rate', 0.0):.2f}%",
                title="All-time Totals",
                border_style="cyan",
            ))
        
        # Display metrics table
        table = Table(title=f"Metrics ({bucket})", show_header=True, header_style="bold magenta")
        table.add_column("Date", style="dim", width=19)
        table.add_column("Requests", justify="right", width=10)
        table.add_column("Errors", justify="right", width=10)
        table.add_column("Error Rate", justify="right", width=12)
        table.add_column("P50 (ms)", justify="right", width=10)
        table.add_column("P95 (ms)", justify="right", width=10)
        
        for item in items:
            day = item.get("day", "")
            requests_total = item.get("requests_total", 0)
            errors_total = item.get("errors_total", 0)
            p50_ms = item.get("p50_ms")
            p95_ms = item.get("p95_ms")
            
            # Format date
            try:
                day_dt = datetime.fromisoformat(day.replace("Z", "+00:00"))
                day_str = day_dt.strftime("%Y-%m-%d")
            except Exception:
                day_str = day
            
            # Calculate error rate
            error_rate = (errors_total / requests_total * 100) if requests_total > 0 else 0.0
            
            # Color error rate
            if error_rate > 5:
                error_rate_text = Text(f"{error_rate:.2f}%", style="red")
            elif error_rate > 1:
                error_rate_text = Text(f"{error_rate:.2f}%", style="yellow")
            else:
                error_rate_text = Text(f"{error_rate:.2f}%", style="green")
            
            p50_str = f"{p50_ms:.1f}" if p50_ms is not None else "N/A"
            p95_str = f"{p95_ms:.1f}" if p95_ms is not None else "N/A"
            
            table.add_row(
                day_str,
                f"{requests_total:,}",
                f"{errors_total:,}",
                error_rate_text,
                p50_str,
                p95_str,
            )
        
        console.print("\n")
        console.print(table)
    
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"Failed to fetch metrics: {str(e)}")
    except Exception as e:
        raise click.ClickException(f"Error: {str(e)}")

