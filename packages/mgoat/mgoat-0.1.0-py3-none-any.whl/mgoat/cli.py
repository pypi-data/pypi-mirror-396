"""MGoat CLI - Command line interface."""

import sys
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from mgoat import MGoat, MGoatConfig, __version__
from mgoat.strategies import list_strategies

app = typer.Typer(
    name="mgoat",
    help="MGoat - The Rust-Powered LLM Red Teaming Framework",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"mgoat-py {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """MGoat - The Rust-Powered LLM Red Teaming Framework."""
    pass


@app.command()
def run(
    goal: List[str] = typer.Option(
        [], "--goal", "-g", help="Test goal(s) to evaluate"
    ),
    goals_file: Optional[str] = typer.Option(
        None, "--goals-file", "-f", help="File containing goals (one per line)"
    ),
    target_model: Optional[str] = typer.Option(
        None, "--target-model", "-t", help="Target model to test"
    ),
    rounds: int = typer.Option(5, "--rounds", "-r", help="Maximum attack rounds"),
    concurrent: int = typer.Option(1, "--concurrent", "-j", help="Concurrency level"),
    output_format: str = typer.Option(
        "console", "--output-format", "-o", help="Output format (console, json, jsonl)"
    ),
    save_dir: Optional[str] = typer.Option(
        None, "--save-dir", help="Directory to save results"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    attacker_model: str = typer.Option("gpt-4", "--attacker-model", help="Attacker model"),
    judge_model: str = typer.Option("gpt-4", "--judge-model", help="Judge model"),
) -> None:
    """Run red team security tests against LLM targets."""
    if not goal and not goals_file:
        console.print("[red]Error:[/red] Either --goal or --goals-file must be provided")
        raise typer.Exit(1)

    config = MGoatConfig(
        attacker_model=attacker_model,
        judge_model=judge_model,
        target_model=target_model,
        max_rounds=rounds,
        concurrent=concurrent,
    )

    try:
        goat = MGoat(config=config)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    console.print(f"[bold blue]MGoat[/bold blue] v{__version__}")
    console.print(f"Target: {target_model or 'default'}")
    console.print(f"Goals: {len(goal)} specified")
    console.print()

    try:
        result = goat.run(
            goal=list(goal) if goal else None,
            goals_file=goals_file,
            target_model=target_model,
            rounds=rounds,
            concurrent=concurrent,
            output_format=output_format,
            save_dir=save_dir,
            verbose=verbose,
        )

        if output_format == "console":
            _print_results(result)
        else:
            import json
            console.print(json.dumps(result.model_dump(), indent=2, default=str))

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def test(
    target_model: Optional[str] = typer.Option(
        None, "--target-model", "-t", help="Target model to test"
    ),
) -> None:
    """Test connection to target model."""
    try:
        goat = MGoat()
        if goat.test_connection(target_model):
            console.print("[green]Connection successful![/green]")
        else:
            console.print("[red]Connection failed[/red]")
            raise typer.Exit(1)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def strategies() -> None:
    """List available attack strategies."""
    table = Table(title="Attack Strategies (GOAT Paper)")
    table.add_column("Strategy", style="cyan")
    table.add_column("Description", style="white")

    for name, description in list_strategies().items():
        table.add_row(name, description)

    console.print(table)


def _print_results(result) -> None:
    """Print test results in console format."""
    console.print()
    console.print("=" * 60)
    console.print("[bold]Test Results Summary[/bold]")
    console.print("=" * 60)
    console.print(f"Total targets: {result.total_targets}")
    console.print(f"Successful attacks: {result.successful_targets}")
    console.print(f"Overall ASR: {result.overall_asr:.2%}")
    console.print()


if __name__ == "__main__":
    app()
