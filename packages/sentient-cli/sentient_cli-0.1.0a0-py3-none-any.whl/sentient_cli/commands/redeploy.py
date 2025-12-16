"""
Redeploy command for Sentient CLI - update an existing deployment in place.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import click
import requests
from rich.console import Console
from rich.panel import Panel

from ..auth import require_authentication
from ..config import ConfigManager
from .common import select_deployment_interactive, resolve_http_proxy_url

console = Console()


def _build_source_payload(
    project_dir: Path,
    entry: Optional[str],
) -> Dict[str, Any]:
    """Build source payload (code, requirements, env) from the current project."""
    cfg = ConfigManager(project_dir).load()

    if cfg.runtime != "python":
        raise click.ClickException("Currently only python runtime is supported")

    # Resolve entry source (agent or MCP server) strictly from user project layout.
    entry_path = Path(entry) if entry else (
        project_dir / ("agent.py" if cfg.type == "agent" else "server.py")
    )
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
    except Exception as e:  # pragma: no cover - CLI safety
        raise click.ClickException(f"Failed to read entry file: {str(e)}")

    # Prepare requirements: attempt to read requirements.txt if present
    requirements = []
    req_file = project_dir / "requirements.txt"
    if req_file.exists():
        try:
            requirements = [
                line.strip()
                for line in req_file.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
        except Exception:
            # Best-effort; empty requirements is acceptable
            pass

    env = dict(cfg.environment)

    payload: Dict[str, Any] = {
        "requirements": requirements,
        "env": env,
    }
    if cfg.type == "mcp":
        payload["server_code"] = entry_code
    else:
        payload["agent_code"] = entry_code

    return payload


@click.command()
@click.argument("deployment_id", required=False)
@click.option(
    "--entry",
    default=None,
    help="Path to entry file: AGENT: exports run_agent(input, context) or @sentient function; MCP: server main file",
)
@click.option(
    "--api-url",
    default=None,
    help="Override Sentient API base URL (defaults to env SENTIENT_API_URL or https://api.sentient-space.com)",
)
@click.option(
    "--wait",
    is_flag=True,
    help="Wait for redeployment to finish and show URL",
)
def redeploy(deployment_id: str, entry: str, api_url: str, wait: bool) -> None:
    """Redeploy an existing deployment in place using current project code."""

    token = require_authentication()
    base_url = api_url or os.getenv("SENTIENT_API_URL", "https://api.sentient-space.com")

    # If no deployment ID provided, let user select interactively.
    if not deployment_id:
        deployment_id = select_deployment_interactive(
            token,
            base_url,
            title="Select deployment to redeploy",
        )

    project_dir = Path.cwd()
    # If no entry provided, require the user to specify one explicitly.
    if not entry:
        entry = click.prompt(
            "Entry file path (relative to current directory)",
            type=str,
        )

    source_payload = _build_source_payload(project_dir, entry)

    endpoint = f"{base_url}/api/deployments/{deployment_id}/redeploy"
    console.print(Panel.fit("Redeploying existing deployment ...", title="Redeploy"))

    try:
        resp = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "content-type": "application/json",
            },
            data=json.dumps(source_payload),
            timeout=60,
        )
    except Exception as e:  # pragma: no cover - network safety
        raise click.ClickException(f"Failed to contact API: {str(e)}")

    if resp.status_code not in (200, 201):
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise click.ClickException(f"API error ({resp.status_code}): {detail}")

    dep = resp.json()
    dep_id = dep["id"]
    console.print(
        f"[green]Redeploy triggered[/green] id={dep_id} status={dep.get('status', 'unknown')}"
    )

    if not wait:
        console.print("Redeployment will complete in the background. Use 'sen list' to check status.")
        return

    # Poll API for status with progress updates (reuse push UX)
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
        task = progress.add_task("[yellow]Redeploying...", total=None)

        for _ in range(120):  # up to ~10 minutes
            try:
                r = requests.get(
                    f"{base_url}/api/deployments/{dep_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30,
                )
                if r.status_code == 200:
                    info = r.json()
                    status = str(info.get("status", "")).lower()
                    visibility = info.get("visibility", "").lower()

                    status_display = status.upper()
                    color = status_colors.get(status, "")
                    progress.update(
                        task, description=f"[{color}]{status_display}[/{color}]"
                    )

                    if status == "running":
                        progress.update(
                            task,
                            description="[green]✅ Redeployment ready![/green]",
                        )
                        proxy_url = resolve_http_proxy_url(base_url, info)
                        console.print(
                            f"\n[green]✅ Deployment ready (HTTP proxy):[/green] {proxy_url}"
                        )
                        if visibility:
                            visibility_icon = "🌐" if visibility == "public" else "🔒"
                            console.print(
                                f"[dim]Visibility: {visibility_icon} {visibility.upper()}[/dim]"
                            )
                        return

                    if status in {"error", "stopped"}:
                        progress.update(
                            task,
                            description=f"[red]❌ Redeployment {status}[/red]",
                        )
                        console.print(
                            f"\n[red]❌ Redeployment failed:[/red] status={status}"
                        )
                        try:
                            lr = requests.get(
                                f"{base_url}/api/deployments/{dep_id}/logs",
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=30,
                            )
                            if lr.status_code == 200 and lr.content:
                                console.print(
                                    Panel.fit(lr.text[:4000], title="Build Logs")
                                )
                        except Exception:
                            pass
                        raise SystemExit(1)
            except requests.exceptions.RequestException as e:
                progress.update(
                    task, description=f"[red]Error: {str(e)[:50]}[/red]"
                )

            time.sleep(5)

        console.print(
            "\n[yellow]⏱️  Timed out waiting for redeployment. Check later with 'sen list'.[/yellow]"
        )


