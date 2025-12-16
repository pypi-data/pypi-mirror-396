"""
Deployment command for Sentient CLI - default to AWS Lambda (Task 6C), with
fallbacks to Railway/Vercel for experimental paths.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

import click
import requests
from rich.console import Console
from rich.panel import Panel

from ..auth import require_authentication
from ..config import ConfigManager
from .common import resolve_http_proxy_url, make_http_session

console = Console()


@click.command()
@click.option('--force', is_flag=True, help='Force deployment even if no changes detected')
@click.option('--entry', default=None, help='Path to entry file: AGENT: exports run_agent(input, context) or @sentient function; MCP: server main file')
@click.option('--api-url', default=None, help='Override Sentient API base URL (defaults to env SENTIENT_API_URL or https://api.sentient-space.com)')
@click.option('--visibility', type=click.Choice(['public', 'private']), default=None, help='Deployment visibility: public (visible in community) or private (only visible to you). Overrides config file.')
@click.option('--wait', is_flag=True, help='Wait for deployment to finish and show URL')
def push(force: bool, entry: str, api_url: str, visibility: str, wait: bool) -> None:
    """Deploy current project to Sentient platform (default: AWS Lambda)."""

    token = require_authentication()
    base_url = api_url or os.getenv("SENTIENT_API_URL", "https://api.sentient-space.com")

    project_dir = Path.cwd()
    cfg = ConfigManager(project_dir).load()

    if cfg.runtime != "python":
        raise click.ClickException("Currently only python runtime is supported")

    # Resolve entry source (agent or MCP server) strictly from user project layout.
    entry_path = Path(entry) if entry else (project_dir / ("agent.py" if cfg.type == "agent" else "server.py"))
    if not entry_path.exists():
        if cfg.type == "agent":
            raise click.ClickException(
                "Agent entry file not found. Provide --entry path to a Python module "
                "exporting run_agent(input, context) or a @sentient-decorated function, "
                "or ensure an 'agent.py' exists in the project root."
            )
        else:
            raise click.ClickException(
                "MCP server entry file not found. Provide --entry path to a Python file "
                "defining your FastMCP server, or ensure a 'server.py' exists in the project root."
            )

    try:
        entry_code = entry_path.read_text(encoding="utf-8")
    except Exception as e:
        raise click.ClickException(f"Failed to read entry file: {str(e)}")

    # Prepare requirements: attempt to read requirements.txt if present
    requirements = []
    req_file = project_dir / "requirements.txt"
    if req_file.exists():
        try:
            requirements = [line.strip() for line in req_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith('#')]
        except Exception:
            pass

    env = dict(cfg.environment)

    # Use --visibility flag if provided, otherwise fall back to config
    deployment_visibility = visibility if visibility else cfg.visibility

    if cfg.type == "mcp":
        payload: Dict[str, Any] = {
            "name": cfg.name,
            "description": cfg.description,
            "framework": cfg.framework,
            "visibility": deployment_visibility,
            "server_code": entry_code,
            "requirements": requirements,
            "env": env,
        }
    else:
        payload = {
            "name": cfg.name,
            "description": cfg.description,
            "framework": cfg.framework,
            "visibility": deployment_visibility,
            "agent_code": entry_code,
            "requirements": requirements,
            "env": env,
        }

    # Default to Lambda endpoints (stateless) for both agent and MCP
    if cfg.type == "mcp":
        endpoint = f"{base_url}/api/deployments/mcp"
        console.print(Panel.fit("Deploying MCP server to Sentient space ...", title="Deploy"))
    else:
        endpoint = f"{base_url}/api/deployments/lambda"
        console.print(Panel.fit("Deploying to Sentient space ...", title="Deploy"))

    session = make_http_session()
    try:
        resp = session.post(
            endpoint,
            headers={"Authorization": f"Bearer {token}", "content-type": "application/json"},
            data=json.dumps(payload),
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"Failed to contact API (network): {str(e)}")

    if resp.status_code not in (200, 201):
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise click.ClickException(f"API error ({resp.status_code}): {detail}")

    dep = resp.json()
    dep_id = dep["id"]
    console.print(f"[green]Deployment created[/green] id={dep_id} status={dep['status']}")

    if not wait:
        console.print("The deployment will complete in the background. Use 'sen list' to check status.")
        return

    # Poll API for status with progress updates
    import time
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    
    status_colors = {
        "building": "yellow",
        "deploying": "yellow",
        "running": "green",
        "error": "red",
        "stopped": "dim",
    }
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[yellow]Deploying...", total=None)
        
        for attempt in range(120):  # up to ~10 minutes
            try:
                r = session.get(
                    f"{base_url}/api/deployments/{dep_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30,
                )
                if r.status_code == 200:
                    info = r.json()
                    status = str(info.get('status', '')).lower()
                    visibility = info.get('visibility', '').lower()
                    
                    # Update progress description
                    status_display = status.upper()
                    color = status_colors.get(status, "")
                    progress.update(task, description=f"[{color}]{status_display}[/{color}]")
                    
                    if status == "running":
                        progress.update(task, description="[green]✅ Deployment ready![/green]")
                        proxy_url = resolve_http_proxy_url(base_url, info)
                        console.print(f"\n[green]✅ Deployment ready (HTTP proxy):[/green] {proxy_url}")
                        if visibility:
                            visibility_icon = "🌐" if visibility == "public" else "🔒"
                            console.print(f"[dim]Visibility: {visibility_icon} {visibility.upper()}[/dim]")
                        return
                    
                    if status in {"error", "stopped"}:
                        progress.update(task, description=f"[red]❌ Deployment {status}[/red]")
                        console.print(f"\n[red]❌ Deployment failed:[/red] status={status}")
                        # Try fetch logs endpoint if available
                        try:
                            lr = session.get(
                                f"{base_url}/api/deployments/{dep_id}/logs",
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=30,
                            )
                            if lr.status_code == 200 and lr.content:
                                console.print(Panel.fit(lr.text[:4000], title="Build Logs"))
                        except Exception:
                            pass
                        raise SystemExit(1)
            except requests.exceptions.RequestException as e:
                progress.update(task, description=f"[red]Error: {str(e)[:50]}[/red]")
            
            time.sleep(5)
        
        console.print("\n[yellow]⏱️  Timed out waiting for deployment. Check later with 'sen list'.[/yellow]")
