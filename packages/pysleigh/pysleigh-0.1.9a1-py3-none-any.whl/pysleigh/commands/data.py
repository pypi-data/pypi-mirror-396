"""Typer commands for fetching AoC data artifacts."""

from __future__ import annotations

import re
from pathlib import Path

import requests
import typer
from markdownify import markdownify

from pysleigh.context import get_context
from pysleigh.loader import load_solution
from pysleigh.session import get_session_token

_ARTICLE_SECTION_RE = re.compile(r"<article\b[^>]*>.*?</article>", re.IGNORECASE | re.DOTALL)

data_app = typer.Typer(help="Manage inputs, articles, and answers.")


def _resolve_article_title(html: str, day: int) -> str:
    start_tag = "<h2>"
    end_tag = "</h2>"
    start_idx = html.find(start_tag)
    end_idx = html.find(end_tag, start_idx + len(start_tag))
    if start_idx == -1 or end_idx == -1:
        return f"--- Day {day}: ??? ---"
    return html[start_idx + len(start_tag) : end_idx].strip()


def _extract_article_section(html: str) -> str:
    """Return every <article> block (joined) or the raw HTML if not found."""
    sections = [match.group(0) for match in _ARTICLE_SECTION_RE.finditer(html) if match.group(0)]
    if sections:
        return "\n\n".join(sections)
    start_idx = html.lower().find("<article")
    return html[start_idx:] if start_idx != -1 else html


def _markdownify_article(html: str) -> str:
    """Convert the provided HTML fragment into Markdown."""
    markdown = markdownify(html, heading_style="ATX")
    lines = (line.rstrip() for line in markdown.splitlines())
    return "\n".join(lines).strip()


def _ensure_parent(path: Path) -> None:
    """Ensure the target directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


@data_app.command("fetch-input")
def fetch_input(
    year: int = typer.Argument(..., help="AoC year."),
    day: int = typer.Argument(..., help="AoC day."),
    overwrite: bool = typer.Option(
        False,
        "--overwrite/--no-overwrite",
        help="Overwrite existing input file if it exists.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print what would be done, but do not fetch or write anything.",
    ),
) -> None:
    """Fetch the input text for a specific day from Advent of Code."""
    paths = get_context().paths
    url = f"https://adventofcode.com/{year}/day/{day}/input"
    path = paths.input_path(year, day)

    if dry_run:
        typer.echo(
            f"[data/input] (dry-run) Would fetch input from {url} "
            f"and write to {path} (overwrite={overwrite})"
        )
        return

    session = get_session_token()
    typer.echo(f"[data/input] Fetching input from {url}")
    response = requests.get(url, cookies={"session": session}, timeout=10)
    response.raise_for_status()

    if path.exists() and not overwrite:
        typer.echo(f"[data/input] Skipping existing file (use --overwrite to replace): {path}")
        raise typer.Exit(code=0)

    _ensure_parent(path)
    path.write_text(response.text)
    typer.echo(f"[data/input] Saved to {path}")


@data_app.command("fetch-article")
def fetch_article(
    year: int = typer.Argument(..., help="AoC year."),
    day: int = typer.Argument(..., help="AoC day."),
    overwrite: bool = typer.Option(
        False,
        "--overwrite/--no-overwrite",
        help="Overwrite existing article file if it exists.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print what would be done, but do not fetch or write anything.",
    ),
) -> None:
    """Fetch the article HTML for a specific day and store it locally."""
    paths = get_context().paths
    url = f"https://adventofcode.com/{year}/day/{day}"
    path = paths.article_path(year, day)

    if dry_run:
        typer.echo(
            f"[data/article] (dry-run) Would fetch article from {url} "
            f"and write to {path} (overwrite={overwrite})"
        )
        return

    session = get_session_token()
    typer.echo(f"[data/article] Fetching article from {url}")
    response = requests.get(url, cookies={"session": session}, timeout=10)
    response.raise_for_status()
    html = response.text
    article_section = _extract_article_section(html)
    title_source = article_section if "<h2" in article_section.lower() else html
    title_line = _resolve_article_title(title_source, day)
    markdown_body = _markdownify_article(article_section)
    if not markdown_body:
        markdown_body = _markdownify_article(html)
    if not markdown_body:
        markdown_body = "(Article content could not be extracted.)"

    if path.exists() and not overwrite:
        typer.echo(f"[data/article] Skipping existing file (use --overwrite): {path}")
        raise typer.Exit(code=0)

    _ensure_parent(path)
    content = f"{title_line}\n\n{markdown_body}\n"
    path.write_text(content)
    typer.echo(f"[data/article] Saved to {path}")


@data_app.command("refresh-answers")
def refresh_answers(
    year: int = typer.Argument(..., help="AoC year."),
    day: int = typer.Argument(..., help="AoC day."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Compute answers but do not write the answers file.",
    ),
) -> None:
    """Re-run the local solution and write answers (or dry-run output)."""
    paths = get_context().paths
    solution = load_solution(year, day)
    part_1, part_2 = solution.run(output=False)
    path = paths.answer_path(year, day)
    line1 = part_1 or ""
    line2 = part_2 or ""

    if dry_run:
        typer.echo(
            f"[data/answers] (dry-run) Would write answers to {path}:\n"
            f"  Part 1: {line1!r}\n"
            f"  Part 2: {line2!r}"
        )
        return

    _ensure_parent(path)
    path.write_text(f"{line1}\n{line2}\n")
    typer.echo(f"[data/answers] Saved to {path}")
