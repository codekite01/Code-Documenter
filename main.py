import sys, os, time, argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from dotenv import load_dotenv

load_dotenv()
console = Console()


def validate_env():
    """Check that required env vars are set before running."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key or key == "sk-ant-api03-xxxxxxxxxxxxxxxx":
        console.print("\n[red]❌ ANTHROPIC_API_KEY not set in .env[/red]")
        console.print("Get your key at: [link]https://console.anthropic.com[/link]")
        sys.exit(1)


def print_banner():
    banner = Text()
    banner.append("  Multi-Agent Codebase Documenter\n", style="bold cyan")
    banner.append("  Explorer → Analyst → Writer\n", style="dim")
    console.print(Panel(banner, border_style="cyan", padding=(0,2)))


def main():
    parser = argparse.ArgumentParser(
        description="Auto-document any GitHub repo with AI agents"
    )
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument(
        "--output", "-o",
        default="./output/README.md",
        help="Output path for README (default: ./output/README.md)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress agent verbose output"
    )
    args = parser.parse_args()

    validate_env()
    print_banner()

    console.print(f"\n[bold]Repository:[/bold] {args.repo_url}")
    console.print(f"[bold]Output:[/bold]     {args.output}\n")

    start = time.time()

    try:
        from crew import run_documenter
        output_path = run_documenter(
            repo_url=args.repo_url,
            output_path=args.output,
        )

        elapsed = time.time() - start
        readme_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0

        # Summary table
        table = Table(show_header=False, box=None, padding=(0,2))
        table.add_column(style="dim")
        table.add_column(style="green")
        table.add_row("✅ README saved", output_path)
        table.add_row("📄 File size", f"{readme_size // 1024}KB ({readme_size:,} bytes)")
        table.add_row("⏱  Time taken", f"{elapsed:.1f} seconds")

        console.print(Panel(table, title="[bold green]Done![/bold green]", border_style="green"))

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red bold]❌ Error:[/red bold] {e}")
        console.print("[dim]Run with --verbose for full traceback[/dim]")
        raise


if __name__ == "__main__":
    main()