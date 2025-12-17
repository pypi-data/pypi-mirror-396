"""
Command-line interface for TravelPurpose.
"""

import json
import logging

import typer
from rich.console import Console
from rich.table import Table

from travelpurpose import __version__
from travelpurpose.classifier import predict_purpose, search, tags

app = typer.Typer(
    name="tpurpose",
    help="TravelPurpose - City Travel Purpose Classification",
    add_completion=False,
)
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@app.command()
def predict(
    city: str = typer.Argument(..., help="City name to classify"),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Disable cache and fetch fresh data"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """
    Predict travel purposes for a city.

    Example:
        tpurpose predict "Istanbul"
        tpurpose predict "Paris" --no-cache --json
    """
    if verbose:
        logging.getLogger("travelpurpose").setLevel(logging.INFO)

    with console.status(f"[bold green]Analyzing {city}..."):
        result = predict_purpose(city, use_cache=not no_cache)

    if json_output:
        console.print_json(json.dumps(result, indent=2))
    else:
        # Pretty table output
        table = Table(title=f"Travel Purposes for {city}", show_header=True)
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Labels", style="green")

        main_cats = ", ".join(result.get("main", [])) or "None"
        sub_cats = ", ".join(result.get("sub", [])) or "None"

        table.add_row("Main Categories", main_cats)
        table.add_row("Subcategories", sub_cats)
        table.add_row(
            "Confidence", f"{result.get('confidence', 0.0):.2f}", style="bold yellow"
        )

        console.print(table)


@app.command()
def show_tags(
    city: str = typer.Argument(..., help="City name"),
    limit: int = typer.Option(
        20, "--limit", "-n", help="Maximum number of tags to show"
    ),
    source: str | None = typer.Option(None, "--source", "-s", help="Filter by source"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """
    Show raw tags for a city.

    Example:
        tpurpose show-tags "Istanbul" --limit 10
        tpurpose show-tags "Paris" --source booking --json
    """
    if verbose:
        logging.getLogger("travelpurpose").setLevel(logging.INFO)

    with console.status(f"[bold green]Fetching tags for {city}..."):
        city_tags = tags(city)

    if source:
        city_tags = [
            t for t in city_tags if t.get("source", "").lower() == source.lower()
        ]

    city_tags = city_tags[:limit]

    if json_output:
        console.print_json(json.dumps(city_tags, indent=2))
    else:
        if not city_tags:
            console.print(f"[yellow]No tags found for {city}")
            return

        table = Table(
            title=f"Tags for {city} (showing {len(city_tags)})", show_header=True
        )
        table.add_column("Tag", style="cyan")
        table.add_column("Source", style="green")
        table.add_column("Evidence", style="magenta")

        for tag in city_tags:
            table.add_row(
                tag.get("tag", ""), tag.get("source", ""), tag.get("evidence_type", "")
            )

        console.print(table)


@app.command()
def find(
    query: str = typer.Argument(..., help="Search query"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """
    Search for cities.

    Example:
        tpurpose find "paris"
        tpurpose find "turkey" --json
    """
    results = search(query)

    if json_output:
        console.print_json(json.dumps(results, indent=2))
    else:
        if not results:
            console.print(f"[yellow]No cities found matching: {query}")
            return

        table = Table(title=f"Cities matching '{query}'", show_header=True)
        table.add_column("City", style="cyan", no_wrap=True)
        table.add_column("Country", style="green")
        table.add_column("Population", style="magenta")

        for city in results:
            table.add_row(
                city.get("name", ""),
                city.get("country", ""),
                f"{city.get('population', 0):,}",
            )

        console.print(table)


@app.command()
def rebuild(
    output_dir: str | None = typer.Option(
        None, "--output", "-o", help="Output directory"
    ),
    min_population: int = typer.Option(
        100000, "--min-pop", help="Minimum city population"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    """
    Rebuild the cities dataset by running the data pipeline.

    Example:
        tpurpose rebuild --verbose
        tpurpose rebuild --output ./data --min-pop 50000
    """
    if verbose:
        logging.getLogger("travelpurpose").setLevel(logging.INFO)

    console.print("[yellow]Starting data pipeline rebuild...")
    console.print(
        "[yellow]Note: This may take a while and requires network access to public sources."
    )

    try:
        from scripts.pipeline import run_pipeline

        run_pipeline(output_dir=output_dir, min_population=min_population)
        console.print("[bold green]Pipeline completed successfully!")
    except ImportError:
        console.print(
            "[red]Error: Pipeline script not found. Make sure scripts/pipeline.py exists."
        )
    except Exception as e:
        console.print(f"[red]Error running pipeline: {e}")


@app.command()
def version():
    """Show version information."""
    console.print(f"TravelPurpose version {__version__}")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version_flag: bool = typer.Option(
        False, "--version", "-V", help="Show version and exit", is_eager=True
    ),
):
    """
    TravelPurpose - City Travel Purpose Classification Library

    A production-grade Python library for classifying world cities by travel purpose
    using multi-source data from public travel platforms and knowledge bases.
    """
    if version_flag:
        console.print(f"TravelPurpose version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
