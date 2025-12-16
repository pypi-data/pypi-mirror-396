"""Command-line interface for tui-delta."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .run import run_tui_with_pipeline

app = typer.Typer(
    name="tui-delta",
    help=(
        "Run TUI applications with real-time delta processing "
        "for monitoring and logging AI assistant sessions"
    ),
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)

console = Console(stderr=True)  # All output to stderr to preserve stdout for data


def version_callback(value: bool) -> None:
    """Print version and exit if --version flag is provided."""
    if value:
        typer.echo(f"tui-delta version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """
    Run TUI applications with real-time delta processing for monitoring
    and logging AI assistant sessions.
    """
    pass


@app.command()
def run(
    command: list[str] = typer.Argument(
        ...,  # type: ignore[arg-type]  # Ellipsis is valid Typer syntax for required args
        help="TUI command to run (e.g., 'claude code' or 'npm test')",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-p",
        help="Clear rules profile (claude_code, generic, minimal, or custom)",
    ),
    rules_file: Optional[Path] = typer.Option(
        None,
        "--rules-file",
        help="Path to custom clear_rules.yaml file",
        exists=True,
        dir_okay=False,
    ),
) -> None:
    """
    Run a TUI application with real-time delta processing.

    Wraps the TUI application to capture all terminal output, processes it through
    the pipeline, and outputs processed deltas to stdout.

    The TUI displays and operates normally - the user can interact with it as if
    it weren't wrapped. Meanwhile, the processed output streams to stdout in real-time.

    \b
    Examples:
        # Run claude code and save processed deltas
        tui-delta run -- claude code > session-deltas.txt

        # Use a specific profile
        tui-delta run --profile generic -- npm test > test-deltas.txt

        # Use custom rules
        tui-delta run --rules-file my-rules.yaml -- ./myapp

    \b
    Pipeline:
        clear_lines → consolidate → uniqseq → cut → uniqseq
    """
    exit_code = run_tui_with_pipeline(
        command=command,
        profile=profile,
        rules_file=rules_file,
    )
    raise typer.Exit(exit_code)


@app.command(name="list-profiles")
def list_profiles_cmd(
    rules_file: Optional[Path] = typer.Option(
        None,
        "--rules-file",
        help="Path to custom clear_rules.yaml file",
        exists=True,
        dir_okay=False,
    ),
) -> None:
    """
    List available clear rules profiles.

    Shows all available profiles from the default clear_rules.yaml
    or a custom rules file.
    """
    from .clear_rules import ClearRules

    profiles = ClearRules.list_profiles(rules_file)
    console.print("[bold]Available profiles:[/bold]")
    for name, description in profiles.items():
        console.print(f"  [cyan]{name}[/cyan]: {description}")


if __name__ == "__main__":
    app()
