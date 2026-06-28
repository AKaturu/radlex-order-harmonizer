from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from .data_loader import load_radlex
from .matcher import batch_match
from .models import AdjudicationStatus, HarmonizationReport
from .reporter import build_report, results_to_dataframe
from .synthetic_data import write_synthetic_csv

app = typer.Typer(
    name="radlex-harmonize",
    help="Map local radiology procedure names to standardized RadLex Playbook identifiers.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def demo(
    output: Annotated[Path, typer.Option(help="Output directory.")] = Path(
        "outputs/demo"
    ),
    n: Annotated[int, typer.Option(help="Number of synthetic procedures.")] = 50,
    seed: Annotated[int, typer.Option(help="Random seed.")] = 42,
    noise_rate: Annotated[
        float, typer.Option(help="Fraction of names with noise.")
    ] = 0.2,
    max_candidates: Annotated[
        int, typer.Option(help="Max candidates per match.")
    ] = 5,
    force_refresh: Annotated[
        bool, typer.Option("--force-refresh", help="Re-download RadLex CSV.")
    ] = False,
) -> None:
    """Generate synthetic local procedure names and match them against RadLex."""
    output.mkdir(parents=True, exist_ok=True)

    console.print("[blue]Loading RadLex Playbook...[/blue]")
    entries = load_radlex(force_refresh=force_refresh)
    console.print(f"[green]Loaded {len(entries)} RadLex entries.[/green]")

    csv_path = output / "synthetic_procedures.csv"
    write_synthetic_csv(entries, str(csv_path), n=n, seed=seed, noise_rate=noise_rate)
    console.print(f"[green]Wrote {n} synthetic procedures:[/green] {csv_path}")

    df = pd.read_csv(csv_path)
    local_names = df["local_name"].dropna().astype(str).tolist()

    console.print("[blue]Running matching...[/blue]")
    results = batch_match(local_names, entries, max_candidates=max_candidates)
    results_df = results_to_dataframe(results)
    results_path = output / "matching_results.csv"
    results_df.to_csv(results_path, index=False)
    console.print(f"[green]Wrote matching results:[/green] {results_path}")

    true_df = pd.read_csv(csv_path)
    merged = results_df[["local_name", "selected_rpid"]].merge(
        true_df[["local_name", "true_rpid"]], on="local_name", how="inner"
    )
    correct = (merged["selected_rpid"] == merged["true_rpid"]).sum()
    accuracy = correct / len(merged) if len(merged) > 0 else 0
    console.print(f"[bold]Top-1 accuracy:[/bold] {accuracy:.1%} ({correct}/{len(merged)})")

    report = build_report(results)
    _print_report_summary(report)


@app.command()
def match(
    csv: Annotated[Path, typer.Option("--csv", help="CSV of local procedure names.")],
    name_column: Annotated[
        str,
        typer.Option(
            "--name-column", help="Column containing procedure names."
        ),
    ] = "local_name",
    output: Annotated[Path, typer.Option(help="Output directory.")] = Path(
        "outputs/match"
    ),
    max_candidates: Annotated[
        int, typer.Option(help="Max candidates per match.")
    ] = 5,
    min_score: Annotated[
        float, typer.Option(help="Min match score (0-1).")
    ] = 0.3,
    force_refresh: Annotated[
        bool, typer.Option("--force-refresh", help="Re-download RadLex CSV.")
    ] = False,
) -> None:
    """Match a CSV of local procedure names against RadLex Playbook."""
    output.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv)
    if name_column not in df.columns:
        console.print(
            f"[red]Column '{name_column}' not found in CSV. "
            f"Available: {list(df.columns)}[/red]"
        )
        raise typer.Exit(code=1)

    local_names = df[name_column].dropna().astype(str).tolist()
    console.print(f"[blue]Loaded {len(local_names)} procedure names.[/blue]")

    entries = load_radlex(force_refresh=force_refresh)
    console.print(f"[blue]Loaded {len(entries)} RadLex entries.[/blue]")

    results = batch_match(local_names, entries, max_candidates, min_score)
    results_df = results_to_dataframe(results)
    results_path = output / "matching_results.csv"
    results_df.to_csv(results_path, index=False)
    console.print(f"[green]Wrote matching results:[/green] {results_path}")

    report = build_report(results)
    _print_report_summary(report)


@app.command()
def adjudicate(
    csv: Annotated[
        Path,
        typer.Option("--csv", help="CSV from the match command."),
    ],
    accept_column: Annotated[
        str,
        typer.Option(
            "--accept-column",
            help="Column with boolean TRUE/FALSE for acceptance.",
        ),
    ] = "accept",
    notes_column: Annotated[
        str,
        typer.Option(
            "--notes-column", help="Column with optional audit notes."
        ),
    ] = "audit_notes",
    output: Annotated[Path, typer.Option(help="Output directory.")] = Path(
        "outputs/adjudicate"
    ),
) -> None:
    """Apply human adjudication from a CSV."""
    output.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv)
    if accept_column not in df.columns:
        console.print(
            f"[red]Column '{accept_column}' not found. "
            f"Available: {list(df.columns)}[/red]"
        )
        raise typer.Exit(code=1)

    df["adjudication"] = df[accept_column].apply(
        lambda x: (
            AdjudicationStatus.ACCEPTED.value
            if str(x).strip().upper() in ("TRUE", "1", "YES")
            else AdjudicationStatus.REJECTED.value
        )
    )
    if notes_column in df.columns:
        df["audit_notes"] = df[notes_column].fillna("")

    output_path = output / "adjudicated_results.csv"
    df.to_csv(output_path, index=False)
    console.print(f"[green]Wrote adjudicated results:[/green] {output_path}")

    accepted = (df["adjudication"] == AdjudicationStatus.ACCEPTED.value).sum()
    console.print(f"[bold]Accepted:[/bold] {accepted}/{len(df)}")


@app.command()
def serve(
    host: Annotated[str, typer.Option(help="Streamlit host.")] = "localhost",
    port: Annotated[int, typer.Option(help="Streamlit port.")] = 8501,
) -> None:
    """Launch the Streamlit dashboard."""
    app_path = Path(__file__).parent / "dashboard.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        host,
        "--server.port",
        str(port),
    ]
    raise typer.Exit(subprocess.run(cmd, check=False).returncode)


def _print_report_summary(report: HarmonizationReport) -> None:
    table = Table(title="radlex-order-harmonizer summary")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Total procedures", str(report.total))
    table.add_row("Mapped (accepted)", str(report.mapped))
    table.add_row("Unmapped", str(report.unmapped))
    table.add_row("Pending", str(report.pending))
    table.add_row("Coverage", f"{report.coverage:.1%}")
    console.print(table)


if __name__ == "__main__":
    app()
