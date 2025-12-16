"""
Logs command for Sentient CLI (Task 8)
"""

import os
import time
import click
import requests
from typing import Optional, Tuple
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.panel import Panel

from ..auth import require_authentication

console = Console()


def _parse_time_spec(spec: str) -> datetime:
    """Parse relative time spec like '15m', '1h', '2d' or ISO 8601."""
    if not spec:
        return datetime.utcnow() - timedelta(minutes=15)
    
    try:
        if spec.endswith("m"):
            minutes = int(spec[:-1])
            return datetime.utcnow() - timedelta(minutes=minutes)
        elif spec.endswith("h"):
            hours = int(spec[:-1])
            return datetime.utcnow() - timedelta(hours=hours)
        elif spec.endswith("d"):
            days = int(spec[:-1])
            return datetime.utcnow() - timedelta(days=days)
        else:
            # Try ISO 8601
            from dateutil import parser as date_parser
            return date_parser.parse(spec)
    except Exception:
        return datetime.utcnow() - timedelta(minutes=15)


def _resolve_deployment_id(
    deployment_id: Optional[str],
    deployment_name: Optional[str],
    token: str,
    base_url: str,
) -> str:
    """Resolve deployment ID from ID or name."""
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
    from rich.progress import Progress, SpinnerColumn, TextColumn
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
            "Select deployment:",
            choices=choices,
            qmark="",
            pointer="❯",
            use_arrow_keys=True,
        ).ask()
        if not selected:
            raise click.ClickException("Selection cancelled")
        deployment_id = selected
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
                    stdscr.addstr(0, 0, "Select deployment (↑↓ to move, Enter to choose, q to quit)")
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
            deployment_id = selection
        except Exception:
            # Fallback to rich table + numeric selection
            table = RichTable(title="Select deployment", show_header=True, header_style="bold magenta")
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
            deployment_id = all_deployments[choice - 1]["id"]
    
    # Prompt for log type (arrow-key list), then since if live
    try:
        import questionary  # type: ignore
        log_type_choice = questionary.select(
            "Select log type:",
            choices=[
                questionary.Choice(title="Live runtime logs (CloudWatch)", value="live"),
                questionary.Choice(title="Build logs (deployment process)", value="build"),
            ],
            use_arrow_keys=True,
        ).ask()
        if not log_type_choice:
            raise RuntimeError("selection-cancelled")
        if log_type_choice == "live":
            since_choice = questionary.select(
                "Since (time window):",
                choices=[
                    "5m", "15m", "30m", "1h", "6h", "24h", "Custom...",
                ],
                use_arrow_keys=True,
            ).ask()
            if not since_choice:
                since_choice = "15m"
            if since_choice == "Custom...":
                since_choice = questionary.text("Enter since (e.g., 15m, 1h, 2025-01-01T00:00:00Z):", default="15m").ask() or "15m"
            return deployment_id, "live", since_choice
        return deployment_id, log_type_choice
    except Exception:
        # Curses-based fallback
        try:
            import curses  # stdlib
            def _select_type(stdscr):
                choices = ["Live runtime logs (CloudWatch)", "Build logs (deployment process)"]
                values = ["live", "build"]
                curses.curs_set(0); stdscr.keypad(True)
                idx = 0
                while True:
                    stdscr.clear()
                    stdscr.addstr(0, 0, "Select log type (↑↓, Enter)")
                    for i, ch in enumerate(choices):
                        if i == idx:
                            stdscr.attron(curses.A_REVERSE)
                        stdscr.addstr(2 + i, 2, ch)
                        if i == idx:
                            stdscr.attroff(curses.A_REVERSE)
                    k = stdscr.getch()
                    if k in (curses.KEY_UP, ord('k')): idx = (idx - 1) % len(choices)
                    elif k in (curses.KEY_DOWN, ord('j')): idx = (idx + 1) % len(choices)
                    elif k in (10, 13): return values[idx]
                    elif k in (27, ord('q')): return None
            log_type_choice = curses.wrapper(_select_type)
            if not log_type_choice:
                raise RuntimeError("selection-cancelled")
            if log_type_choice == "live":
                def _select_since(stdscr):
                    opts = ["5m","15m","30m","1h","6h","24h","Custom..."]
                    idx = 1
                    curses.curs_set(0); stdscr.keypad(True)
                    while True:
                        stdscr.clear()
                        stdscr.addstr(0, 0, "Since (↑↓, Enter)")
                        for i, ch in enumerate(opts):
                            if i == idx:
                                stdscr.attron(curses.A_REVERSE)
                            stdscr.addstr(2 + i, 2, ch)
                            if i == idx:
                                stdscr.attroff(curses.A_REVERSE)
                        k = stdscr.getch()
                        if k in (curses.KEY_UP, ord('k')): idx = (idx - 1) % len(opts)
                        elif k in (curses.KEY_DOWN, ord('j')): idx = (idx + 1) % len(opts)
                        elif k in (10, 13): return opts[idx]
                        elif k in (27, ord('q')): return None
                since_choice = curses.wrapper(_select_since) or "15m"
                if since_choice == "Custom...":
                    # final fallback: prompt text
                    since_choice = click.prompt("Enter since (e.g., 15m, 1h, 2025-01-01T00:00:00Z)", default="15m")
                return deployment_id, "live", since_choice
            return deployment_id, log_type_choice
        except Exception:
            # Final fallback: simple prompt
            log_type_choice = click.prompt("Log type (live/build)", default="live", type=click.Choice(["live", "build"]))
            if log_type_choice == "live":
                since_choice = click.prompt("Since (e.g., 15m, 30m, 1h, 6h, 24h)", default="15m")
                return deployment_id, "live", since_choice
            return deployment_id, log_type_choice


@click.command()
@click.option('--id', 'deployment_id', default=None, help='Deployment ID')
@click.option('--name', 'deployment_name', default=None, help='Deployment name (partial match)')
@click.option('--build', is_flag=True, help='Show build logs instead of live logs')
@click.option('--live', is_flag=True, help='Show live runtime logs (default)')
@click.option('--since', default='15m', help='Time range start (e.g., 15m, 1h, 2d, or ISO 8601)')
@click.option('--level', type=click.Choice(['INFO', 'ERROR', 'WARNING', 'DEBUG']), help='Filter by log level')
@click.option('--q', 'search_query', default=None, help='Text search query')
@click.option('--limit', default=200, type=int, help='Maximum number of log entries')
@click.option('--api-url', default=None, help='Override Sentient API base URL')
def logs(
    deployment_id: Optional[str],
    deployment_name: Optional[str],
    build: bool,
    live: bool,
    since: str,
    level: Optional[str],
    search_query: Optional[str],
    limit: int,
    api_url: Optional[str],
) -> None:
    """View deployment logs (build logs or live runtime logs from CloudWatch)."""
    
    token = require_authentication()
    base_url = api_url or os.getenv("SENTIENT_API_URL", "https://api.sentient-space.com")
    
    # Determine log type
    if build and live:
        raise click.ClickException("Cannot specify both --build and --live")
    
    log_type = "build" if build else "live"
    
    # Resolve deployment ID
    try:
        if not deployment_id and not deployment_name:
            # Interactive mode - returns (id, log_type)
            result = _resolve_deployment_id(None, None, token, base_url)
            if isinstance(result, tuple):
                if len(result) == 3:
                    deployment_id, log_type, since = result
                else:
                    deployment_id, log_type = result
            else:
                deployment_id = result
        else:
            deployment_id = _resolve_deployment_id(deployment_id, deployment_name, token, base_url)
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Failed to resolve deployment: {str(e)}")
    
    # Build query params
    params = {
        "type": log_type,
        "limit": limit,
    }
    
    if log_type == "live":
        params["since"] = since
        if level:
            params["level"] = level
        if search_query:
            params["q"] = search_query
    
    # Live logs follow by default (no --follow flag needed)
    follow = log_type == "live"
    
    # Fetch and display logs
    last_timestamp = None
    
    def fetch_logs(next_token=None):
        """Fetch logs from API."""
        fetch_params = params.copy()
        if next_token:
            fetch_params["next_token"] = next_token
        
        resp = requests.get(
            f"{base_url}/api/deployments/{deployment_id}/logs",
            headers={"Authorization": f"Bearer {token}"},
            params=fetch_params,
            timeout=30,
        )
        
        if resp.status_code == 404:
            raise click.ClickException(f"Deployment {deployment_id[:12]} not found")
        resp.raise_for_status()
        
        return resp.json()
    
    try:
        if follow:
            # Follow mode - poll and display new logs
            console.print(f"[green]Following logs for deployment {deployment_id[:12]}...[/green]")
            console.print("[dim]Press Ctrl+C to stop[/dim]\n")
            
            seen_timestamps = set()
            
            while True:
                try:
                    data = fetch_logs()
                    items = data.get("items", [])
                    
                    # Display new items (those we haven't seen)
                    for item in items:
                        ts = item.get("ts")
                        if ts and ts not in seen_timestamps:
                            seen_timestamps.add(ts)
                            
                            # Format log line
                            level = item.get("level", "INFO")
                            message = item.get("message", "")
                            request_id = item.get("request_id")
                            
                            # Color by level
                            level_colors = {
                                "ERROR": "red",
                                "WARNING": "yellow",
                                "DEBUG": "dim",
                                "INFO": "white",
                            }
                            level_style = level_colors.get(level, "white")
                            
                            # Format timestamp
                            try:
                                ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                                ts_str = ts_dt.strftime("%Y-%m-%d %H:%M:%S")
                            except Exception:
                                ts_str = ts
                            
                            # Build log line
                            line_parts = [f"[{level_style}]{level:8}[/{level_style}]", f"[dim]{ts_str}[/dim]"]
                            if request_id:
                                line_parts.append(f"[dim][request_id: {request_id[:8]}][/dim]")
                            line_parts.append(message)
                            
                            console.print(" ".join(line_parts))
                    
                    # Update since time for next poll
                    if items:
                        last_item = items[-1]
                        last_timestamp = last_item.get("ts")
                        params["since"] = last_timestamp if last_timestamp else since
                    
                    time.sleep(2)  # Poll every 2 seconds
                    
                except KeyboardInterrupt:
                    console.print("\n[yellow]Stopped following logs[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]Error fetching logs: {e}[/red]")
                    time.sleep(5)  # Wait longer on error
        
        else:
            # One-time fetch
            data = fetch_logs()
            items = data.get("items", [])
            
            if not items:
                console.print("[yellow]No logs found[/yellow]")
                return
            
            # Display logs in a table
            table = Table(title=f"Logs ({log_type})", show_header=True, header_style="bold magenta")
            table.add_column("Time", style="dim", width=19)
            table.add_column("Level", width=8)
            table.add_column("Request ID", style="dim", width=12)
            table.add_column("Message", overflow="fold")
            
            level_colors = {
                "ERROR": "red",
                "WARNING": "yellow",
                "DEBUG": "dim",
                "INFO": "white",
            }
            
            for item in items:
                ts = item.get("ts", "")
                level = item.get("level", "INFO")
                message = item.get("message", "")
                request_id = item.get("request_id")
                
                # Format timestamp
                try:
                    ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    ts_str = ts_dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    ts_str = ts
                
                level_text = Text(level, style=level_colors.get(level, "white"))
                request_id_text = request_id[:12] if request_id else ""
                
                table.add_row(ts_str, level_text, request_id_text, message)
            
            console.print(table)
            
            if data.get("next_token"):
                console.print(f"\n[dim]More logs available. Use --since with next_token for pagination.[/dim]")
    
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"Failed to fetch logs: {str(e)}")
    except Exception as e:
        raise click.ClickException(f"Error: {str(e)}")
