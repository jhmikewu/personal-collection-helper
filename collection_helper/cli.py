"""Command-line interface."""

import asyncio
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from collection_helper.config import get_settings
from collection_helper.logger import setup_logging, get_logger
from collection_helper.core.manager import MediaManager

console = Console()
logger = None


def setup_app():
    """Setup application logging and configuration."""
    global logger
    setup_logging()
    logger = get_logger()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Personal Collection Helper - Manage your Emby and Booklore libraries."""
    setup_app()


@cli.command()
@click.option("--query", "-q", required=True, help="Search query")
@click.option("--emby/--no-emby", default=True, help="Search in Emby")
@click.option("--booklore/--no-booklore", default=True, help="Search in Booklore")
def search(query: str, emby: bool, booklore: bool):
    """Search for media across your collections."""
    async def do_search():
        async with MediaManager() as manager:
            results = await manager.search_all(query, emby, booklore)

            console.print(f"\n[bold cyan]Search results for: '{query}'[/bold cyan]\n")

            if emby and "emby" in results:
                emby_results = results["emby"]
                console.print(f"[bold green]Emby ({len(emby_results)} results)[/bold green]")

                if emby_results:
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("Title", style="cyan")
                    table.add_column("Type", style="yellow")
                    table.add_column("Year", style="blue")

                    for item in emby_results[:10]:
                        table.add_row(
                            item.name,
                            item.type,
                            str(item.production_year) if item.production_year else "N/A"
                        )

                    console.print(table)

            if booklore and "booklore" in results:
                booklore_results = results["booklore"]
                console.print(f"\n[bold green]Booklore ({len(booklore_results)} results)[/bold green]")

                if booklore_results:
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("Title", style="cyan")
                    table.add_column("Author", style="yellow")
                    table.add_column("Publisher", style="blue")

                    for book in booklore_results[:10]:
                        table.add_row(
                            book.title,
                            book.author or "N/A",
                            book.publisher or "N/A"
                        )

                    console.print(table)

    asyncio.run(do_search())


@cli.command()
@click.option("--library", "-l", help="Filter by library name")
@click.option("--limit", "-n", default=50, help="Maximum number of items")
def list_emby(library: Optional[str], limit: int):
    """List media from Emby."""
    async def do_list():
        async with MediaManager() as manager:
            if library:
                console.print(f"[bold cyan]Listing items from library: {library}[/bold cyan]\n")
            else:
                console.print("[bold cyan]Listing items from all libraries[/bold cyan]\n")

            items = await manager.get_emby_items(library_name=library, limit=limit)

            if items:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Title", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("Year", style="blue")
                table.add_column("Rating", style="green")

                for item in items[:50]:
                    table.add_row(
                        item.name,
                        item.type,
                        str(item.production_year) if item.production_year else "N/A",
                        f"{item.community_rating:.1f}" if item.community_rating else "N/A"
                    )

                console.print(table)
                console.print(f"\n[dim]Showing {len(items[:50])} of {len(items)} items[/dim]")
            else:
                console.print("[yellow]No items found[/yellow]")

    asyncio.run(do_list())


@cli.command()
@click.option("--limit", "-n", default=50, help="Maximum number of books")
def list_books(limit: int):
    """List books from Booklore."""
    async def do_list():
        async with MediaManager() as manager:
            console.print("[bold cyan]Listing books from Booklore[/bold cyan]\n")

            books = await manager.get_booklore_books(limit=limit)

            if books:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Title", style="cyan")
                table.add_column("Author", style="yellow")
                table.add_column("Publisher", style="blue")

                for book in books[:50]:
                    table.add_row(
                        book.title,
                        book.author or "N/A",
                        book.publisher or "N/A"
                    )

                console.print(table)
                console.print(f"\n[dim]Showing {len(books[:50])} of {len(books)} books[/dim]")
            else:
                console.print("[yellow]No books found[/yellow]")

    asyncio.run(do_list())


@cli.command()
def libraries():
    """List all libraries."""
    async def do_list():
        async with MediaManager() as manager:
            console.print("[bold cyan]Available Libraries[/bold cyan]\n")

            # Emby libraries
            emby_libs = await manager.get_emby_libraries()
            if emby_libs:
                console.print("[bold green]Emby:[/bold green]")
                for lib in emby_libs:
                    console.print(f"  • {lib}")
                console.print("")

            # Booklore collections
            booklore_collections = await manager.booklore.get_collections()
            if booklore_collections:
                console.print("[bold green]Booklore Collections:[/bold green]")
                for col in booklore_collections:
                    console.print(f"  • {col.name} ({col.book_count} books)")

    asyncio.run(do_list())


@cli.command()
def stats():
    """Show collection statistics."""
    async def do_stats():
        async with MediaManager() as manager:
            stats = await manager.get_collection_stats()

            console.print(Panel.fit(
                "[bold cyan]Collection Statistics[/bold cyan]",
                border_style="cyan"
            ))

            # Emby stats
            if stats["emby"]["libraries"]:
                console.print(f"\n[bold green]Emby[/bold green]")
                console.print(f"  Libraries: {len(stats['emby']['libraries'])}")
                console.print(f"  Total Items: {stats['emby']['total_items']}")
                console.print(f"  Library Names:")
                for lib in stats["emby"]["libraries"]:
                    console.print(f"    • {lib}")

            # Booklore stats
            if stats["booklore"]["total_books"] > 0:
                console.print(f"\n[bold green]Booklore[/bold green]")
                console.print(f"  Total Books: {stats['booklore']['total_books']}")
                if stats["booklore"]["collections"]:
                    console.print(f"  Collections: {len(stats['booklore']['collections'])}")
                    for col in stats["booklore"]["collections"]:
                        console.print(f"    • {col}")

    asyncio.run(do_stats())


@cli.command()
def health():
    """Check health of connected services."""
    async def do_health():
        async with MediaManager() as manager:
            health_status = await manager.health_check()

            console.print(Panel.fit(
                "[bold cyan]Service Health Status[/bold cyan]",
                border_style="cyan"
            ))

            for service, status in health_status.items():
                status_text = "[bold green]✓ Healthy[/bold green]" if status else "[bold red]✗ Unhealthy[/bold red]"
                console.print(f"\n{service.capitalize()}: {status_text}")

    asyncio.run(do_health())


def main():
    """Entry point for the CLI."""
    cli()
