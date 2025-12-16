#!/usr/bin/env python3
"""
Sentient Web Platform CLI - Main entry point
"""

import click
from rich.console import Console

from .commands.auth import auth
from .commands.init import init
from .commands.push import push
from .commands.redeploy import redeploy
from .commands.list import list_deployments
from .commands.logs import logs
from .commands.metrics import metrics
from .commands.delete import delete

console = Console()


SENTIENT_ASCII_LOGO = r"""
███████╗███████╗███╗   ██╗████████╗██╗███████╗███╗   ██╗████████╗
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║██╔════╝████╗  ██║╚══██╔══╝
███████╗█████╗  ██╔██╗ ██║   ██║   ██║█████╗  ██╔██╗ ██║   ██║
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██╔══╝  ██║╚██╗██║   ██║
███████║███████╗██║ ╚████║   ██║   ██║███████╗██║ ╚████║   ██║
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝
"""


class SentientGroup(click.Group):
    """Custom Click group that prefixes help output with the Sentient ASCII logo."""

    def get_help(self, ctx: click.Context) -> str:  # type: ignore[override]
        base_help = super().get_help(ctx)
        return f"{SENTIENT_ASCII_LOGO}\n\n{base_help}"


@click.group(cls=SentientGroup)
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Sentient Web Platform CLI - Deploy AI agents and MCP servers with zero friction.
    
    Get started by authenticating with 'sen auth login' and then initialize
    your project with 'sen init'.
    """
    ctx.ensure_object(dict)


# Add command groups
cli.add_command(auth)
cli.add_command(init)
cli.add_command(push)
cli.add_command(redeploy)
cli.add_command(list_deployments, name="list")
cli.add_command(logs)
cli.add_command(metrics)
cli.add_command(delete)


def main() -> None:
    """Main entry point for the CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    main()