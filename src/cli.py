"""CLI entry point for the Quantum Algorithm Explorer."""

import argparse
import logging
import sys

from rich.console import Console
from rich.markdown import Markdown

from src.config import Config
from src.orchestrator import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Quantum Algorithm Explorer — AI-powered quantum algorithm analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python -m src.cli "find element 42 in a database of 1000 items"
  python -m src.cli "determine if a function is constant or balanced"
  python -m src.cli "find a hidden bit string" --verbose
  python -m src.cli "search an unsorted database" --output report.md
        """,
    )
    parser.add_argument(
        "problem",
        help="Description of the computational problem to analyze",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        help="Claude model to use (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Save report to a file (Markdown)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show intermediate agent responses",
    )
    parser.add_argument(
        "--shots",
        type=int,
        default=1024,
        help="Number of simulation shots (default: 1024)",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
    )

    # Build config
    config = Config(
        model=args.model,
        shots=args.shots,
        verbose=args.verbose,
    )

    if not config.anthropic_api_key:
        print(
            "Error: ANTHROPIC_API_KEY not set. "
            "Copy .env.example to .env and add your key.",
            file=sys.stderr,
        )
        sys.exit(1)

    console = Console()

    try:
        console.print("\n[bold]Quantum Algorithm Explorer[/bold]\n")
        console.print(f'Problem: "{args.problem}"\n')

        report = run_pipeline(args.problem, config)

        # Display in terminal with rich formatting
        console.print(Markdown(report))

        # Optionally save to file
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            console.print(f"\n[green]Report saved to {args.output}[/green]")

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]", highlight=False)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
