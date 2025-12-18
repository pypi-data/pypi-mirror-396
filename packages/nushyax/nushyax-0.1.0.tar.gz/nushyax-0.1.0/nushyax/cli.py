# nushyax/cli.py

import typer
from pathlib import Path
from rich.console import Console
import yaml

from nushyax.detector import detect
from nushyax.config import load_config
from nushyax.dispatcher import resolve
from nushyax.runner import run
from nushyax.templates import get_template

console = Console()

app = typer.Typer(
    help="Nushyax — framework-agnostic developer CLI",
    # add_completion=False,
    # invoke_without_command=True,
    # context_settings={
    #     "allow_extra_args": True,
    #     "ignore_unknown_options": True,
    # }
)



# Register the built-in commands as normal
@app.command()
def init(
    overwrite: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .nushyax.yaml")
):
    """Generate a .nushyax.yaml file with useful defaults for the detected framework."""
    framework = detect()

    template = get_template(framework)
    comment = template.pop("comment", "# nushyax configuration file")

    file_path = Path(".nushyax.yaml")

    if file_path.exists() and not overwrite:
        console.print(f"[yellow]{file_path} already exists. Use --force to overwrite.[/]")
        raise typer.Exit(1)

    if template["framework"] is None and framework:
        template["framework"] = framework

    content = f"{comment}\n\n{yaml.safe_dump(template, sort_keys=False)}"

    file_path.write_text(content)
    console.print(f"[green]✓ Created {file_path}[/] with defaults for {framework or 'generic'} framework.")
    console.print("You can now customize aliases and overrides!")


@app.command(name="list")
def list_commands():
    """List all available project commands and aliases."""
    framework = detect()
    if not framework:
        console.print("[red]No framework detected.[/]")
        raise typer.Exit(1)

    config = load_config(framework)
    commands = config.get("commands", {})
    aliases = config.get("aliases", {})

    if not commands:
        console.print("[yellow]No commands defined for this framework.[/]")
        return

    console.print("[bold]Available commands:[/]")
    for name, details in sorted(commands.items(), key=lambda x: x[0]):
        desc = details.get("desc", "(no description)")
        exec_str = details.get("exec", "(no exec)")
        if len(exec_str) > 80:
            exec_str = exec_str[:77] + "..."
        console.print(f"  [green]{name:<18}[/] {desc}")
        console.print(f"                     [dim]$ {exec_str}[/]")

    if aliases:
        console.print("\n[bold]Aliases:[/]")
        for alias, target in sorted(aliases.items()):
            target_desc = commands.get(target, {}).get("desc", "(missing)")
            status = "" if target in commands else " [red](missing target)[/]"
            console.print(f"  [cyan]{alias:<18}[/] → [green]{target}[/]{status}  {target_desc}")


@app.command()
def describe(command: str):
    """Show details about a specific command or alias."""
    framework = detect()
    if not framework:
        console.print("[red]No framework detected.[/]")
        raise typer.Exit(1)

    config = load_config(framework)
    cmd_details = resolve(command, config)

    if not cmd_details:
        console.print(f"[red]Unknown command or alias: {command}[/]")
        console.print("Use 'nushyax config list' to see available commands.")
        raise typer.Exit(1)

    aliases = config.get("aliases", {})
    final_name = aliases.get(command, command)

    if command in aliases:
        console.print(f"[bold cyan]Alias:[/] {command} → [green]{final_name}[/]")

    console.print(f"[bold]Command:[/] {final_name}")
    console.print(f"[bold]Description:[/] {cmd_details.get('desc', '(no description)')}")
    console.print(f"[bold]Executes:[/] {cmd_details.get('exec', '(no exec defined)')}")


# Main entry point — this runs FIRST
@app.command(name="exec")
def exec_alias(
    ctx: typer.Context,
    command: str = typer.Argument(None, help="Command or alias"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Execute a specific command or alias."""
    if ctx.invoked_subcommand is not None:
        return

    if not command:
        console.print(ctx.get_help())
        raise typer.Exit(1)

    framework = detect()
    if not framework:
        console.print("[red]No framework detected.[/]")
        raise typer.Exit(1)

    config = load_config(framework)
    cmd_details = resolve(command, config)

    if not cmd_details:
        console.print(f"[red]Unknown command or alias: '{command}'[/]")
        console.print("Use 'nushyax config list'")
        raise typer.Exit(1)

    exec_str = cmd_details["exec"]

    if dry_run:
        console.print(f"[yellow]--dry-run[/] $ {exec_str}")
        return

    run(exec_str)





if __name__ == "__main__":
    app()