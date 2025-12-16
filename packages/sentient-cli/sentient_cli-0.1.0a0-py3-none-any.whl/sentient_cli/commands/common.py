"""
Shared utilities for CLI commands (deployment selection, etc.)
"""

import os
import click
import requests
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

console = Console()


def _default_retry() -> Retry:
    """Short, bounded retry policy for transient network issues."""
    return Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(502, 503, 504),
        allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "PATCH"]),
        raise_on_status=False,
    )


def make_http_session() -> requests.Session:
    """Create a requests session with retry/backoff and sensible timeouts."""
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=_default_retry())
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def resolve_http_proxy_url(base_url: str, deployment: dict[str, Any]) -> str:
    """
    Build the public HTTP proxy URL for a deployment (never the raw Lambda URL).
    Falls back to a descriptive placeholder when HTTP proxy is disabled.
    """
    dep_id = deployment.get("id")
    dep_type = str(deployment.get("type", "")).lower()
    http_enabled = bool(deployment.get("http_api_enabled", False))

    if not dep_id or not http_enabled:
        return "[dim]HTTP proxy disabled[/dim]"

    base = base_url.rstrip("/")
    path = "mcp" if dep_type == "mcp" else "invoke"
    return f"{base}/api/deployments/{dep_id}/{path}"


def render_deployments(items: list[dict], base_url: str, title: str) -> None:
    """
    Responsive renderer for deployments list:
    - Wide terminals: Rich Table (no truncation for visibility; URL wraps).
    - Narrow terminals: stacked Panels (one per deployment) so nothing truncates.
    """
    from rich import box
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.table import Table as RichTable
    from rich.align import Align

    w = console.size.width
    is_narrow = w < 100

    status_colors = {
        "building": "yellow",
        "deploying": "yellow",
        "running": "green",
        "error": "red",
        "stopped": "dim",
    }
    visibility_icons = {"public": "🌐 PUBLIC", "private": "🔒 PRIVATE"}

    if not is_narrow:
        # Table layout for wide screens
        table = RichTable(
            title=title,
            show_header=True,
            header_style="bold magenta",
            expand=True,
            box=box.SIMPLE_HEAVY,
            padding=(0, 1),
        )
        # Column sizing with min/max and wrapping
        table.add_column("ID", style="dim", min_width=10, max_width=12, no_wrap=True, overflow="ellipsis")
        table.add_column("Name", style="cyan", min_width=16, max_width=24, no_wrap=False, overflow="fold")
        table.add_column("Type", min_width=6, max_width=8, no_wrap=True)
        table.add_column("Status", min_width=8, max_width=10, no_wrap=True)
        table.add_column("Visibility", min_width=10, max_width=12, no_wrap=False, overflow="fold")
        # URL gets the rest; fold long URLs across lines
        remaining = max(20, w - (12 + 24 + 8 + 10 + 12) - 12)
        table.add_column("URL", ratio=3, min_width=20, max_width=remaining, overflow="fold", no_wrap=False)

        for item in items:
            dep_id = (item.get("id") or "")[:12]
            name = item.get("name") or ""
            dep_type = (item.get("type") or "").upper()
            status_val = (item.get("status") or "").lower()
            status_text = Text(status_val.upper(), style=status_colors.get(status_val, ""))
            visibility_val = (item.get("visibility") or "").lower()
            vis_text = visibility_icons.get(visibility_val, visibility_val.upper())
            url = resolve_http_proxy_url(base_url, item)
            table.add_row(dep_id, name, dep_type, status_text, vis_text, url)

        console.print(table)
        return

    # Narrow: stacked cards so nothing truncates
    cards = []
    for item in items:
        dep_id = item.get("id", "")
        name = item.get("name", "")
        dep_type = (item.get("type") or "").upper()
        status_val = (item.get("status") or "").lower()
        status_text = f"[{status_colors.get(status_val, '')}]{status_val.upper()}[/{status_colors.get(status_val, '')}]"
        visibility_val = (item.get("visibility") or "").lower()
        vis_text = visibility_icons.get(visibility_val, visibility_val.upper())
        url = resolve_http_proxy_url(base_url, item)

        body = (
            f"[dim]Name:[/dim] {name}\n"
            f"[dim]Type:[/dim] {dep_type}   [dim]Status:[/dim] {status_text}\n"
            f"[dim]Visibility:[/dim] {vis_text}\n"
            f"[dim]URL:[/dim] {url}"
        )
        panel = Panel.fit(
            body,
            title=f"[dim]{dep_id[:12]}[/dim]",
            border_style="magenta",
            padding=(0, 1),
        )
        cards.append(panel)

    console.print(Columns(cards, expand=True, equal=False))

def select_deployment_interactive(
    token: str,
    base_url: str,
    title: str = "Select deployment",
) -> str:
    """
    Interactive deployment selection with arrow keys (questionary/curses/fallback).
    Returns the selected deployment ID.
    """
    from rich.table import Table as RichTable
    
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
                params={"page": 1, "page_size": 100},
                timeout=30,
            )
            resp.raise_for_status()
            all_deployments = resp.json().get("items", [])
            
            if not all_deployments:
                progress.update(task, description="[red]❌ No deployments found[/red]")
                raise click.ClickException("No deployments found")
            
            progress.update(task, description="[green]✅ Loaded[/green]")
            progress.stop()
        except requests.exceptions.RequestException as e:
            progress.update(task, description="[red]❌ Failed[/red]")
            raise click.ClickException(f"Failed to fetch deployments: {str(e)}")
    
    # Prefer arrow-key interactive selection (questionary) with numeric fallback
    try:
        import questionary  # type: ignore
        choices = []
        for dep in all_deployments:
            dep_id_short = dep.get("id", "")[:12]
            name = dep.get("name", "Unknown")
            dep_type = (dep.get("type", "") or "").upper()
            status = (dep.get("status", "") or "").upper()
            choices.append(questionary.Choice(title=f"{dep_id_short} - {name} ({dep_type}, {status})", value=dep.get("id", "")))
        selected = questionary.select(
            title + ":",
            choices=choices,
            qmark="",
            pointer="❯",
            use_arrow_keys=True,
        ).ask()
        if not selected:
            raise click.ClickException("Selection cancelled")
        return selected
    except Exception:
        # Try curses-based arrow-key selector (table-like), then fallback to numeric
        try:
            import curses  # stdlib

            def _curses_select(stdscr):
                curses.curs_set(0)
                stdscr.nodelay(False)
                stdscr.keypad(True)
                selected = 0
                top = 0
                h, w = stdscr.getmaxyx()
                header = "#  ID           Name                         Type  Status"
                while True:
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"{title} (↑↓ to move, Enter to choose, q to quit)")
                    stdscr.addstr(2, 0, header)
                    visible_height = max(1, h - 5)
                    if selected < top:
                        top = selected
                    if selected >= top + visible_height:
                        top = selected - visible_height + 1
                    for idx in range(top, min(len(all_deployments), top + visible_height)):
                        dep = all_deployments[idx]
                        short_id = (dep.get("id", "") or "")[:12]
                        name = (dep.get("name", "Unknown") or "")[:27].ljust(27)
                        dep_type = (dep.get("type", "") or "").upper().ljust(5)
                        status_val = (dep.get("status", "") or "").upper().ljust(7)
                        line = f"{idx+1:>2} {short_id:<12} {name}  {dep_type:<5} {status_val:<7}"
                        if idx == selected:
                            stdscr.attron(curses.A_REVERSE)
                            stdscr.addstr(3 + idx - top, 0, line[: max(0, w - 1)])
                            stdscr.attroff(curses.A_REVERSE)
                        else:
                            stdscr.addstr(3 + idx - top, 0, line[: max(0, w - 1)])
                    stdscr.refresh()
                    ch = stdscr.getch()
                    if ch in (curses.KEY_UP, ord('k')):
                        selected = (selected - 1) % len(all_deployments)
                    elif ch in (curses.KEY_DOWN, ord('j')):
                        selected = (selected + 1) % len(all_deployments)
                    elif ch in (10, 13):  # Enter
                        return all_deployments[selected]["id"]
                    elif ch in (27, ord('q')):
                        return None

            selection = curses.wrapper(_curses_select)
            if not selection:
                raise click.ClickException("Selection cancelled")
            return selection
        except Exception:
            # Final fallback: rich table + numeric selection
            table = RichTable(title=title, show_header=True, header_style="bold magenta")
            table.add_column("#", style="dim", width=3)
            table.add_column("ID", style="dim", width=12)
            table.add_column("Name", style="cyan", width=20)
            table.add_column("Type", width=8)
            table.add_column("Status", width=10)
            
            status_colors = {
                "building": "yellow",
                "deploying": "yellow",
                "running": "green",
                "error": "red",
                "stopped": "dim",
            }
            
            for i, dep in enumerate(all_deployments, 1):
                dep_id = dep.get("id", "")[:12]
                name = dep.get("name", "Unknown")
                dep_type = dep.get("type", "").upper()
                status_val = dep.get("status", "").lower()
                status_text = Text(status_val.upper(), style=status_colors.get(status_val, ""))
                table.add_row(str(i), dep_id, name, dep_type, status_text)
            
            console.print(table)
            choice = click.prompt("\nEnter number to select", type=int)
            if choice < 1 or choice > len(all_deployments):
                raise click.ClickException("Invalid choice")
            return all_deployments[choice - 1]["id"]


def resolve_deployment_id(
    deployment_id: Optional[str],
    deployment_name: Optional[str],
    token: str,
    base_url: str,
) -> str:
    """
    Resolve deployment ID from ID, name, or interactive selection.
    Returns just the deployment ID (no log type or other metadata).
    """
    if deployment_id:
        return deployment_id
    
    if deployment_name:
        # Search by name
        resp = requests.get(
            f"{base_url}/api/deployments",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": deployment_name, "page": 1, "page_size": 100},
            timeout=30,
        )
        resp.raise_for_status()
        matches = resp.json().get("items", [])
        
        matching = [d for d in matches if deployment_name.lower() in d.get("name", "").lower()]
        
        if not matching:
            raise click.ClickException(f"No deployment found matching name '{deployment_name}'")
        elif len(matching) == 1:
            return matching[0]["id"]
        else:
            # Multiple matches - prompt user
            console.print(f"[yellow]Found {len(matching)} deployments matching '{deployment_name}':[/yellow]\n")
            for i, dep in enumerate(matching, 1):
                console.print(f"  {i}. {dep['id'][:12]} - {dep['name']} ({dep.get('type', '').upper()}, {dep.get('status', '').upper()})")
            
            choice = click.prompt("\nEnter number to select", type=int)
            if choice < 1 or choice > len(matching):
                raise click.ClickException("Invalid choice")
            return matching[choice - 1]["id"]
    
    # No ID or name - interactive selection
    return select_deployment_interactive(token, base_url)
