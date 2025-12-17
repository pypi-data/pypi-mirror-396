"""
Command-Line Interface for PQC Migration Toolkit

Provides the `pqc-migrate` CLI for analyzing cryptographic inventories,
generating migration recommendations, and running risk simulations.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from quantum_pqc_migration_toolkit import __version__
from quantum_pqc_migration_toolkit.models import Scenario
from quantum_pqc_migration_toolkit.io import (
    load_inventory,
    write_report,
    create_sample_inventory,
)
from quantum_pqc_migration_toolkit.risk import (
    compute_inventory_risk,
    get_risk_summary,
    classify_priority_tier,
)
from quantum_pqc_migration_toolkit.planner import (
    plan_inventory_migration,
    estimate_migration_effort,
)
from quantum_pqc_migration_toolkit.simulate import (
    compare_strategies,
    generate_simulation_report,
)

app = typer.Typer(
    name="pqc-migrate",
    help="Post-Quantum Cryptography Migration Assessment Toolkit",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"pqc-migrate version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        help="Show version and exit.",
    ),
):
    """
    PQC Migration Toolkit - Assess and plan post-quantum cryptographic migration.

    Use 'pqc-migrate init' to create a sample inventory, then
    'pqc-migrate analyze <inventory.yaml>' to assess your systems.
    """
    pass


@app.command()
def init(
    output: Path = typer.Option(
        Path("inventory.yaml"),
        "--output",
        "-o",
        help="Output file path for sample inventory.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing file.",
    ),
):
    """
    Create a sample inventory file to get started.

    Generates a YAML file with example systems demonstrating
    the inventory format and available fields.
    """
    if output.exists() and not force:
        console.print(
            f"[red]File '{output}' already exists. Use --force to overwrite.[/red]"
        )
        raise typer.Exit(1)

    sample = create_sample_inventory()
    output.write_text(sample)

    console.print(f"[green]Sample inventory created: {output}[/green]")
    console.print("\nEdit this file to add your systems, then run:")
    console.print(f"  [cyan]pqc-migrate analyze {output}[/cyan]")


@app.command()
def analyze(
    inventory_path: Path = typer.Argument(
        ...,
        help="Path to inventory YAML/JSON file.",
        exists=True,
    ),
    output_json: Optional[Path] = typer.Option(
        None,
        "--json",
        "-j",
        help="Output JSON report path.",
    ),
    output_csv: Optional[Path] = typer.Option(
        None,
        "--csv",
        "-c",
        help="Output CSV report path.",
    ),
    strategy: str = typer.Option(
        "baseline",
        "--strategy",
        "-s",
        help="Adoption strategy: early, baseline, or late.",
    ),
    simulate: bool = typer.Option(
        False,
        "--simulate",
        help="Run Monte Carlo simulation comparing strategies.",
    ),
    n_runs: int = typer.Option(
        500,
        "--runs",
        "-n",
        help="Number of simulation runs (if --simulate).",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show detailed factor breakdown.",
    ),
):
    """
    Analyze an inventory and generate migration recommendations.

    Computes PQ risk scores for each system, recommends target
    PQC algorithms, and suggests migration timelines.
    """
    # Load inventory
    try:
        systems = load_inventory(inventory_path)
    except Exception as e:
        console.print(f"[red]Error loading inventory: {e}[/red]")
        raise typer.Exit(1)

    if not systems:
        console.print("[yellow]No systems found in inventory.[/yellow]")
        raise typer.Exit(0)

    console.print(f"\n[bold]Analyzing {len(systems)} systems...[/bold]\n")

    # Create scenario
    scenario = Scenario.baseline()
    scenario.adoption_strategy = strategy.lower()

    # Compute risk assessments
    assessments = compute_inventory_risk(systems, scenario)

    # Generate recommendations
    recommendations = plan_inventory_migration(systems, assessments, scenario)

    # Display results table
    _display_results_table(assessments, recommendations, verbose)

    # Display summary
    summary = get_risk_summary(assessments)
    _display_summary(summary)

    # Run simulation if requested
    simulation_results = None
    if simulate:
        console.print("\n[bold]Running Monte Carlo simulation...[/bold]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Simulating strategies...", total=None)
            strategy_results = compare_strategies(systems, scenario, n_runs=n_runs)

        sim_report = generate_simulation_report(strategy_results)
        simulation_results = {
            s: r.to_dict() for s, r in strategy_results.items()
        }
        simulation_results["report"] = sim_report
        _display_simulation_results(sim_report)

    # Write reports if requested
    if output_json or output_csv:
        report = write_report(
            systems,
            assessments,
            recommendations,
            path_json=output_json,
            path_csv=output_csv,
            simulation_results=simulation_results,
        )
        if output_json:
            console.print(f"\n[green]JSON report written to: {output_json}[/green]")
        if output_csv:
            console.print(f"[green]CSV report written to: {output_csv}[/green]")


@app.command()
def simulate(
    inventory_path: Path = typer.Argument(
        ...,
        help="Path to inventory YAML/JSON file.",
        exists=True,
    ),
    n_runs: int = typer.Option(
        1000,
        "--runs",
        "-n",
        help="Number of Monte Carlo runs.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output JSON file for simulation results.",
    ),
):
    """
    Run Monte Carlo simulation to compare adoption strategies.

    Simulates quantum arrival timing uncertainty and compares
    early, baseline, and late adoption strategies.
    """
    try:
        systems = load_inventory(inventory_path)
    except Exception as e:
        console.print(f"[red]Error loading inventory: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold]Running {n_runs} simulation trials...[/bold]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Simulating...", total=None)
        strategy_results = compare_strategies(systems, n_runs=n_runs)

    # Generate and display report
    report = generate_simulation_report(strategy_results)
    _display_simulation_results(report)

    # Save if requested
    if output:
        import json
        results_dict = {
            s: r.to_dict() for s, r in strategy_results.items()
        }
        results_dict["report"] = report
        output.write_text(json.dumps(results_dict, indent=2))
        console.print(f"\n[green]Results saved to: {output}[/green]")


@app.command()
def info(
    algorithm: str = typer.Argument(
        ...,
        help="Algorithm name (e.g., ML-KEM-768, ML-DSA-65).",
    ),
):
    """
    Display information about a PQC algorithm.

    Shows performance characteristics, key sizes, and usage notes.
    """
    from quantum_pqc_migration_toolkit.planner import get_algorithm_info

    info = get_algorithm_info(algorithm)

    console.print(f"\n[bold]{info['name']}[/bold]\n")

    if "family" in info:
        console.print(f"  Family: {info['family']}")
    if "type" in info:
        console.print(f"  Type: {info['type']}")
    if info.get("is_hybrid"):
        console.print("  Mode: Hybrid (classical + post-quantum)")

    if "computational_overhead" in info:
        console.print(f"  Computational overhead: {info['computational_overhead']}x")

    if "size_factors" in info:
        console.print("  Size factors:")
        for key, val in info["size_factors"].items():
            console.print(f"    {key}: {val}x")

    if "note" in info:
        console.print(f"\n  Note: {info['note']}")


def _display_results_table(assessments, recommendations, verbose: bool = False):
    """Display results in a formatted table."""
    table = Table(title="PQC Migration Assessment Results")

    table.add_column("System", style="cyan")
    table.add_column("Risk", justify="right")
    table.add_column("Priority", justify="right")
    table.add_column("Tier", style="bold")
    table.add_column("Target KEM", style="green")
    table.add_column("Target Sig", style="green")
    table.add_column("Mode")
    table.add_column("Migrate By", justify="right")

    # Create recommendation lookup
    rec_lookup = {r.system_name: r for r in recommendations}

    for assessment in assessments:
        rec = rec_lookup.get(assessment.system_name)

        tier = classify_priority_tier(assessment.priority_score)
        tier_style = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "green",
            "minimal": "dim",
        }.get(tier, "")

        table.add_row(
            assessment.system_name,
            f"{assessment.pq_risk_score:.3f}",
            str(assessment.priority_score),
            f"[{tier_style}]{tier}[/{tier_style}]",
            rec.target_kem if rec else "-",
            rec.target_sig if rec else "-",
            rec.mode if rec else "-",
            str(rec.migrate_by_year) if rec else "-",
        )

    console.print(table)


def _display_summary(summary):
    """Display summary statistics."""
    tier_dist = summary.get("tier_distribution", {})

    panel_content = f"""
[bold]Total Systems:[/bold] {summary['total_systems']}
[bold]Mean Risk Score:[/bold] {summary['mean_risk']:.3f}
[bold]Risk Range:[/bold] {summary['min_risk']:.3f} - {summary['max_risk']:.3f}

[bold]Priority Distribution:[/bold]
  [red]Critical:[/red] {tier_dist.get('critical', 0)}
  [red]High:[/red] {tier_dist.get('high', 0)}
  [yellow]Medium:[/yellow] {tier_dist.get('medium', 0)}
  [green]Low:[/green] {tier_dist.get('low', 0)}
  [dim]Minimal:[/dim] {tier_dist.get('minimal', 0)}
"""

    console.print(Panel(panel_content.strip(), title="Summary", expand=False))


def _display_simulation_results(report):
    """Display simulation report."""
    console.print("\n[bold]Strategy Comparison[/bold]\n")

    table = Table()
    table.add_column("Strategy")
    table.add_column("Mean Risk", justify="right")
    table.add_column("Std Dev", justify="right")
    table.add_column("P5", justify="right")
    table.add_column("P50", justify="right")
    table.add_column("P95", justify="right")

    for strategy, stats in report.get("strategy_summaries", {}).items():
        style = {"early": "green", "baseline": "yellow", "late": "red"}.get(strategy, "")
        table.add_row(
            f"[{style}]{strategy}[/{style}]",
            f"{stats['mean_risk']:.4f}",
            f"{stats['std_risk']:.4f}",
            f"{stats['p5_risk']:.4f}",
            f"{stats['p50_risk']:.4f}",
            f"{stats['p95_risk']:.4f}",
        )

    console.print(table)

    # Display key findings
    if "key_finding" in report:
        console.print(f"\n[bold]Key Finding:[/bold] {report['key_finding']}")

    if "early_vs_late" in report:
        reduction = report["early_vs_late"]["risk_reduction_pct"]
        console.print(
            f"\n[green]Early adoption reduces risk by {reduction:.1f}% compared to late adoption.[/green]"
        )


def cli():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli()
