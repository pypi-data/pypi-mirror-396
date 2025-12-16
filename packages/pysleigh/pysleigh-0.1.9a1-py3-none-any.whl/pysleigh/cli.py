"""Typer CLI composition for PySleigh."""

from __future__ import annotations

from pathlib import Path

import typer

from pysleigh.commands import data as data_commands
from pysleigh.commands import solution as solution_commands
from pysleigh.context import AoCContext, set_context

app = typer.Typer(help="Advent of Code helper CLI.")
app.add_typer(data_commands.data_app, name="data")
app.add_typer(solution_commands.solution_app, name="solution")


@app.callback(invoke_without_command=True)
def main(  # pragma: no cover - CLI bootstrapping
    ctx: typer.Context,
    project_root: Path = typer.Option(
        Path.cwd(),
        help="Path to the Advent of Code repository to operate on.",
    ),
) -> None:
    """Set context when subcommands run; otherwise show readiness."""
    if ctx.invoked_subcommand:
        set_context(AoCContext(project_root))
    else:
        typer.echo("PySleigh CLI is ready. Use --help for commands.")
