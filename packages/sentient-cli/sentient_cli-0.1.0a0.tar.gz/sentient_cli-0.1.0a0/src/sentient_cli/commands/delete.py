"""
Delete deployment command for Sentient CLI
"""

import os
import click
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..auth import require_authentication
from .common import resolve_http_proxy_url

console = Console()


@click.command()
@click.argument('deployment_id', required=False)
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
@click.option('--api-url', default=None, help='Override Sentient API base URL (defaults to env SENTIENT_API_URL or https://api.sentient-space.com)')
def delete(deployment_id: str, force: bool, api_url: str) -> None:
    """Delete a deployment
    
    DEPLOYMENT_ID can be a full UUID or a partial ID (first 8+ characters).
    If multiple deployments match, you'll be prompted to choose.
    """
    
    token = require_authentication()
    base_url = api_url or os.getenv("SENTIENT_API_URL", "https://api.sentient-space.com")
    
    # Show spinner while fetching deployment details
    from rich.progress import Progress, SpinnerColumn, TextColumn
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[yellow]Fetching deployment...", total=None)

        # If no ID provided, present interactive list to choose from
        if not deployment_id:
            try:
                # Fetch up to 100 deployments (paginate later if needed)
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
                    raise click.ClickException("No deployments found to delete")

                # Try to use questionary for a robust arrow-key selector
                try:
                    import questionary  # type: ignore
                    choices = []
                    for dep in all_deployments:
                        dep_id = dep.get("id", "")
                        short_id = dep_id[:12]
                        name = dep.get("name", "Unknown")
                        dep_type = (dep.get("type", "") or "").upper()
                        status = (dep.get("status", "") or "").upper()
                        visibility = (dep.get("visibility", "") or "").upper()
                        label = f"{short_id} - {name} ({dep_type}, {status}, {visibility})"
                        choices.append(questionary.Choice(title=label, value=dep_id))

                    progress.update(task, description="[green]✅ Loaded[/green]")
                    # Stop the spinner before interactive selection to avoid overlap
                    progress.stop()
                    selection = questionary.select(
                        "Select deployment to delete:",
                        choices=choices,
                        use_arrow_keys=True,
                    ).ask()

                    if not selection:
                        console.print("[yellow]Deletion cancelled[/yellow]")
                        return
                    deployment_id = selection
                except Exception:
                    # Try a curses-based arrow-key selector (no external deps)
                    try:
                        # Stop the spinner before opening curses UI
                        progress.stop()
                        import curses  # stdlib

                        def _curses_select(stdscr):
                            curses.curs_set(0)
                            stdscr.nodelay(False)
                            stdscr.keypad(True)
                            selected = 0
                            top = 0
                            h, w = stdscr.getmaxyx()
                            header = "#  ID           Name                         Type  Status   Visibility"
                            while True:
                                stdscr.clear()
                                stdscr.addstr(0, 0, "Select deployment to delete (↑↓ to move, Enter to choose, q to quit)")
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
                                    visibility_val = (dep.get("visibility", "") or "").upper().ljust(9)
                                    line = f"{idx+1:>2} {short_id:<12} {name}  {dep_type:<5} {status_val:<7} {visibility_val:<9}"
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
                            console.print("[yellow]Deletion cancelled[/yellow]")
                            return
                        deployment_id = selection
                    except Exception:
                        # Final fallback: numeric selection with Rich table (no arrow keys)
                        progress.update(task, description="[yellow]Loaded (fallback select)[/yellow]")
                        # Stop the spinner before printing the selection table
                        progress.stop()
                        
                        # Build a nice table similar to `sen list`
                        table = Table(title="Select deployment to delete", show_header=True, header_style="bold magenta")
                        table.add_column("#", style="dim", width=3)
                        table.add_column("ID", style="dim", width=12)
                        table.add_column("Name", style="cyan", width=24)
                        table.add_column("Type", width=8)
                        table.add_column("Status", width=10)
                        table.add_column("Visibility", width=10)
                        
                        status_colors = {
                            "building": "yellow",
                            "deploying": "yellow",
                            "running": "green",
                            "error": "red",
                            "stopped": "dim",
                        }
                        visibility_icons = {"PUBLIC": "🌐", "PRIVATE": "🔒"}
                        
                        for i, dep in enumerate(all_deployments, 1):
                            short_id = (dep.get("id", "") or "")[:12]
                            name = dep.get("name", "Unknown")
                            dep_type = (dep.get("type", "") or "").upper()
                            status_val = (dep.get("status", "") or "").lower()
                            visibility_val = (dep.get("visibility", "") or "").upper()
                            status_text = Text(status_val.upper(), style=status_colors.get(status_val, ""))
                            visibility_text = f"{visibility_icons.get(visibility_val, '')} {visibility_val}"
                            table.add_row(str(i), short_id, name, dep_type, status_text, visibility_text)
                        
                        console.print("")
                        console.print(table)
                        choice = click.prompt("Enter number to delete", type=int)
                        if choice < 1 or choice > len(all_deployments):
                            raise click.ClickException("Invalid choice")
                        deployment_id = all_deployments[choice - 1]["id"]
            except requests.exceptions.RequestException as e:
                progress.update(task, description="[red]❌ Failed[/red]")
                raise click.ClickException(f"Failed to fetch deployments: {str(e)}")

        # If partial ID (less than 36 chars, which is UUID length), search for matching deployments
        if len(deployment_id) < 36:
            # Fetch all deployments and find matches
            try:
                resp = requests.get(
                    f"{base_url}/api/deployments",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"page": 1, "page_size": 100},  # Get more to find matches
                    timeout=30,
                )
                resp.raise_for_status()
                all_deployments = resp.json().get("items", [])
                
                # Find deployments that start with the provided ID
                matches = [
                    dep for dep in all_deployments
                    if dep.get("id", "").startswith(deployment_id)
                ]
                
                if not matches:
                    progress.update(task, description="[red]❌ Not found[/red]")
                    raise click.ClickException(f"No deployment found matching ID '{deployment_id}'")
                elif len(matches) == 1:
                    # Single match - use it
                    deployment = matches[0]
                    deployment_id = deployment["id"]  # Use full ID
                    progress.update(task, description="[green]✅ Found[/green]")
                else:
                    # Multiple matches - let user choose
                    progress.update(task, description="[yellow]Multiple matches found[/yellow]")
                    console.print(f"\n[yellow]Found {len(matches)} deployments matching '{deployment_id}':[/yellow]\n")
                    for i, dep in enumerate(matches, 1):
                        name = dep.get("name", "Unknown")
                        dep_type = dep.get("type", "").upper()
                        status = dep.get("status", "").upper()
                        console.print(f"  {i}. {dep['id']} - {name} ({dep_type}, {status})")
                    
                    choice = click.prompt("\nEnter number to delete", type=int)
                    if choice < 1 or choice > len(matches):
                        raise click.ClickException("Invalid choice")
                    deployment = matches[choice - 1]
                    deployment_id = deployment["id"]  # Use full ID
            except requests.exceptions.RequestException as e:
                progress.update(task, description="[red]❌ Failed[/red]")
                raise click.ClickException(f"Failed to search deployments: {str(e)}")
        else:
            # Full ID provided - fetch directly
            try:
                resp = requests.get(
                    f"{base_url}/api/deployments/{deployment_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30,
                )
                if resp.status_code == 404:
                    progress.update(task, description="[red]❌ Not found[/red]")
                    raise click.ClickException(f"Deployment {deployment_id} not found")
                resp.raise_for_status()
                deployment = resp.json()
                progress.update(task, description="[green]✅ Found[/green]")
            except requests.exceptions.RequestException as e:
                progress.update(task, description="[red]❌ Failed[/red]")
                raise click.ClickException(f"Failed to fetch deployment: {str(e)}")
    
    name = deployment.get("name", "Unknown")
    dep_type = deployment.get("type", "").upper()
    status = deployment.get("status", "").upper()
    proxy_url = resolve_http_proxy_url(base_url, deployment)
    
    # Show deployment info
    console.print(Panel.fit(
        f"[bold]Name:[/bold] {name}\n"
        f"[bold]Type:[/bold] {dep_type}\n"
        f"[bold]Status:[/bold] {status}\n"
        f"[bold]HTTP Proxy URL:[/bold] {proxy_url}",
        title=f"Deployment {deployment_id[:12]}",
        border_style="yellow"
    ))
    
    # Confirm deletion
    if not force:
        console.print("\n[red]Are you sure you want to delete this deployment?[/red]")
        if not click.confirm("", default=False):
            console.print("[yellow]Deletion cancelled[/yellow]")
            return
    
    # Delete deployment with spinner
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[yellow]Deleting deployment...", total=None)
        
        try:
            resp = requests.delete(
                f"{base_url}/api/deployments/{deployment_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            if resp.status_code == 404:
                progress.update(task, description="[red]❌ Not found[/red]")
                raise click.ClickException(f"Deployment {deployment_id} not found")
            resp.raise_for_status()
            progress.update(task, description="[green]✅ Deleted[/green]")
        except requests.exceptions.RequestException as e:
            progress.update(task, description="[red]❌ Failed[/red]")
            raise click.ClickException(f"Failed to delete deployment: {str(e)}")
    
    console.print(f"[green]✅ Successfully deleted deployment {deployment_id[:12]}[/green]")