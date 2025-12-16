"""
Project initialization command for Sentient CLI
"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from ..config import ConfigManager, SentientConfig
from ..detection import ProjectDetector
from ..auth import require_authentication

console = Console()


@click.command()
@click.option('--name', help='Project name')
@click.option('--description', help='Project description')
@click.option('--type', 'project_type', type=click.Choice(['agent', 'mcp']), help='Project type')
@click.option('--framework', help='AI framework')
@click.option('--visibility', type=click.Choice(['public', 'private']), default='private', help='Deployment visibility')
@click.option('--runtime', type=click.Choice(['python', 'node']), help='Runtime environment')
@click.option('--port', type=int, help='Port number')
@click.option('--force', is_flag=True, help='Overwrite existing configuration')
def init(name: str, description: str, project_type: str, framework: str, 
         visibility: str, runtime: str, port: int, force: bool) -> None:
    """Initialize project for deployment to Sentient Web Platform"""
    
    # Require authentication
    require_authentication()
    
    project_path = Path.cwd()
    config_manager = ConfigManager(project_path)
    
    # Check if already initialized
    if config_manager.exists() and not force:
        console.print("[yellow]⚠️  Project already initialized[/yellow]")
        console.print(f"Configuration file exists: {config_manager.config_file}")
        
        if not Confirm.ask("Do you want to overwrite the existing configuration?"):
            console.print("[dim]Use --force to overwrite without prompting[/dim]")
            return
    
    console.print(Panel.fit(
        "[bold blue]Sentient Web Platform Project Initialization[/bold blue]\n\n"
        "Let's set up your project for deployment!",
        title="🚀 Project Setup"
    ))
    
    # Auto-detect project information
    console.print("\n[cyan]🔍 Detecting project information...[/cyan]")
    detector = ProjectDetector(project_path)
    detection = detector.get_detection_summary()
    
    # Show detection results
    detection_table = Table(title="Auto-Detection Results")
    detection_table.add_column("Property", style="cyan")
    detection_table.add_column("Detected Value", style="yellow")
    detection_table.add_column("Confidence", style="green")
    
    detection_table.add_row("Runtime", detection['runtime'], "High" if detection['runtime'] == 'python' else "Medium")
    detection_table.add_row("Project Type", detection['type'], "Medium")
    detection_table.add_row("Framework", detection['framework'], "High" if detection['framework'] != 'custom' else "Low")
    detection_table.add_row("Entry Point", detection['entry_point'], "Medium")
    detection_table.add_row("Port", detection['port'], "Low")
    
    console.print(detection_table)
    
    # Get configuration values (use CLI args, detection, or sensible defaults)
    config_values = {}
    
    # Project name - use CLI arg, detection, or directory name
    config_values['name'] = name or project_path.name
    
    # Description - use CLI arg or generate from name
    config_values['description'] = description or f"AI project: {config_values['name']}"
    
    # Project type - use CLI arg or detection
    config_values['type'] = project_type or detection['type']
    
    # Framework - use CLI arg or detection
    config_values['framework'] = framework or detection['framework']
    
    # Runtime - use CLI arg or detection
    config_values['runtime'] = runtime or detection['runtime']
    
    # Visibility - use CLI arg or default to private
    config_values['visibility'] = visibility or 'private'
    
    # Start command - use detection
    config_values['start_command'] = detection['entry_point']
    
    # Port - use CLI arg or detection
    config_values['port'] = port or int(detection['port'])
    
    # Build command (auto-detect and use if available)
    if config_values['runtime'] == 'python':
        if (project_path / "requirements.txt").exists():
            config_values['build_command'] = "pip install -r requirements.txt"
    else:
        if (project_path / "package.json").exists():
            config_values['build_command'] = "npm install"
    
    # Environment variables - collect interactively
    config_values['environment'] = {}
    
    # Optionally prompt to capture env vars now
    console.print("\n[cyan]🔐 Environment variables[/cyan]")
    if Confirm.ask("Do you want to add environment variables now?", default=False):
        while True:
            key = Prompt.ask("Enter env KEY (leave empty to finish)", default="")
            if not key:
                break
            # Ask whether to hide input
            hide = Confirm.ask("Hide value input (recommended for secrets)?", default=True)
            value = Prompt.ask(f"Enter value for {key}", password=hide)
            if value is None:
                value = ""
            config_values['environment'][key] = value

    # Create and save configuration
    try:
        config = SentientConfig(**config_values)
        config_manager.save(config)
        
        console.print(Panel.fit(
            f"[green]✅ Project initialized successfully![/green]\n\n"
            f"Configuration saved to: [cyan]{config_manager.config_file}[/cyan]\n\n"
            f"Next steps:\n"
            f"1. Review your configuration\n"
            f"2. Run [bold]sen push[/bold] to deploy your project",
            title="🎉 Success"
        ))
        
        # Show final configuration
        console.print("\n[bold]Final Configuration:[/bold]")
        config_table = Table()
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_dict = config.dict()
        for key, value in config_dict.items():
            if key == 'environment' and value:
                env_str = ', '.join([f"{k}={v}" for k, v in value.items()])
                config_table.add_row(key, env_str)
            else:
                config_table.add_row(key, str(value))
        
        console.print(config_table)
        
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize project: {str(e)}[/red]")
        raise click.ClickException("Project initialization failed")