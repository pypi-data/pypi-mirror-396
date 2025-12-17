#!/usr/bin/env python3
"""
Mii Extractor CLI - A tool for extracting .mii files from Dolphin dumped data
"""

import csv
import sys
from pathlib import Path
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
except ImportError:
    print(
        "Error: CLI dependencies not found. Please install with: pip install mii-lib[cli]",
        file=sys.stderr,
    )
    sys.exit(1)

from mii import (
    MiiDatabase,
    MiiParser,
    MiiType,
    MiiDatabaseError,
)

app = typer.Typer(help="Extract and analyze Mii files from Wii/Dolphin files")
console = Console()


@app.command()
def extract(
    mii_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Specific Mii type to extract (wii-plaza, wii-parade, wiiu-maker, 3ds-maker)",
    ),
    input_file: Optional[Path] = typer.Option(
        None, "--input", "-i", help="Custom input database file path"
    ),
    output_dir: Path = typer.Option(
        Path("."), "--output", "-o", help="Output directory for extracted .mii files"
    ),
):
    """Extract Mii files from Nintendo console database dumps"""

    if mii_type:
        # Extract specific type
        try:
            # Handle the special case of 3DS_MAKER
            enum_name = mii_type.upper().replace("-", "_")
            if enum_name == "3DS_MAKER":
                selected_type = MiiType._3DS_MAKER
            else:
                selected_type = MiiType[enum_name]

            try:
                # Load database into memory
                source_file = input_file or Path(selected_type.SOURCE)
                database = MiiDatabase(source_file, selected_type)

                with Progress() as progress:
                    task = progress.add_task(
                        f"[cyan]Extracting {selected_type.PREFIX} Miis...",
                        total=len(database),
                    )

                    exported_paths = database.export_all(output_dir)
                    progress.update(task, completed=len(exported_paths))

                console.print(
                    f"[green]Extracted {len(exported_paths)} {selected_type.PREFIX} Miis to {output_dir}[/green]"
                )
                total_extracted = len(exported_paths)

            except MiiDatabaseError as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1)

        except KeyError:
            console.print(f"[red]Error: Unknown Mii type '{mii_type}'[/red]")
            console.print("Valid types: wii-plaza, wii-parade, wiiu-maker, 3ds-maker")
            raise typer.Exit(1)
    else:
        # Extract all types
        console.print("[bold]Extracting from all supported database types...[/bold]")
        total_extracted = 0

        for mii_enum in MiiType:
            try:
                # Load database into memory
                source_file = Path(mii_enum.SOURCE)
                database = MiiDatabase(source_file, mii_enum)

                type_output_dir = output_dir / mii_enum.display_name

                with Progress() as progress:
                    task = progress.add_task(
                        f"[cyan]Extracting {mii_enum.PREFIX} Miis...",
                        total=len(database),
                    )

                    exported_paths = database.export_all(type_output_dir)
                    progress.update(task, completed=len(exported_paths))

                total_extracted += len(exported_paths)
            except MiiDatabaseError:
                # Continue with other types if one fails
                pass

        console.print(
            f"\n[bold green]Total Miis extracted: {total_extracted}[/bold green]"
        )


@app.command()
def times(
    directory: Path = typer.Option(
        Path("."), "--directory", "-d", help="Directory containing .mii files"
    ),
):
    """Calculate and display creation times for Mii files"""

    if not directory.exists():
        console.print(f"[red]Error: Directory {directory} does not exist[/red]")
        raise typer.Exit(1)

    mii_files = list(directory.glob("*.mii"))
    if not mii_files:
        console.print(f"[yellow]No .mii files found in {directory}[/yellow]")
        return

    console.print(f"[bold]Analyzing {len(mii_files)} .mii files...[/bold]\n")

    table = Table(title="Mii Creation Times")
    table.add_column("Filename", style="cyan")
    table.add_column("Creation Time", style="green")
    table.add_column("Type", style="blue")

    successful_analyses = 0

    for mii_file in sorted(mii_files):
        try:
            with open(mii_file, "rb") as f:
                mii_data = f.read()
            mii = MiiParser.parse(mii_data)

            creation_time = mii.get_creation_datetime()
            mii_type = "Wii" if mii.is_wii_mii else "3DS/WiiU"
            table.add_row(
                mii_file.name, creation_time.strftime("%Y-%m-%d %H:%M:%S"), mii_type
            )
            successful_analyses += 1

        except Exception as err:
            console.print(f"[red]Error analyzing {mii_file.name}: {err}[/red]")

    console.print(table)
    console.print(
        f"\n[green]Successfully analyzed {successful_analyses}/{len(mii_files)} files[/green]"
    )


@app.command()
def metadata(
    directory: Path = typer.Option(
        Path("."), "--directory", "-d", help="Directory containing .mii files"
    ),
    single_file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Analyze a single .mii file"
    ),
    csv_output: Optional[Path] = typer.Option(
        None, "--csv", "-c", help="Save results to CSV file"
    ),
):
    """Display metadata for Mii files (names, colors, birthdays, etc.)"""

    if single_file:
        if not single_file.exists():
            console.print(f"[red]Error: File {single_file} does not exist[/red]")
            raise typer.Exit(1)

        try:
            with open(single_file, "rb") as f:
                mii_data = f.read()
            mii = MiiParser.parse(mii_data)

            table = Table(title=f"Metadata for {single_file.name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Mii Name", mii.name)
            table.add_row("Creator Name", mii.creator_name)
            table.add_row("Gender", mii.get_gender_string())
            table.add_row(
                "Birth Month",
                str(mii.birth_month) if mii.birth_month else "Not set",
            )
            table.add_row(
                "Birth Day",
                str(mii.birth_day) if mii.birth_day else "Not set",
            )
            table.add_row("Favorite Color", mii.favorite_color)
            table.add_row("Is Favorite", "Yes" if mii.is_favorite else "No")
            table.add_row("Mii ID", mii.get_mii_id_hex())

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error reading {single_file}: {e}[/red]")
            raise typer.Exit(1)

    else:
        if not directory.exists():
            console.print(f"[red]Error: Directory {directory} does not exist[/red]")
            raise typer.Exit(1)

        mii_files = list(directory.glob("*.mii"))
        if not mii_files:
            console.print(f"[yellow]No .mii files found in {directory}[/yellow]")
            return

        console.print(f"[bold]Analyzing {len(mii_files)} .mii files...[/bold]\n")

        results = []
        successful_analyses = 0

        for mii_file in sorted(mii_files):
            try:
                with open(mii_file, "rb") as f:
                    mii_data = f.read()
                mii = MiiParser.parse(mii_data)

                result_data = {
                    "filename": mii_file.name,
                    "mii_name": mii.name,
                    "creator_name": mii.creator_name,
                    "is_girl": mii.is_girl,
                    "gender": mii.get_gender_string(),
                    "birth_month": mii.birth_month,
                    "birth_day": mii.birth_day,
                    "birthday": mii.get_birthday_string(),
                    "favorite_color": mii.favorite_color,
                    "favorite_color_index": mii.favorite_color_index,
                    "is_favorite": mii.is_favorite,
                    "mii_id": mii.get_mii_id_hex(),
                }

                results.append(result_data)
                successful_analyses += 1

            except Exception as err:
                console.print(f"[red]Error analyzing {mii_file.name}: {err}[/red]")

        if csv_output:
            if results:
                fieldnames = [
                    "filename",
                    "mii_name",
                    "creator_name",
                    "is_girl",
                    "gender",
                    "birth_month",
                    "birth_day",
                    "birthday",
                    "favorite_color",
                    "favorite_color_index",
                    "is_favorite",
                    "mii_id",
                ]

                with open(csv_output, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)

                console.print(
                    f"[green]Saved metadata for {len(results)} .mii files to {csv_output}[/green]"
                )
            else:
                console.print("[yellow]No data to save to CSV[/yellow]")
        else:
            table = Table(title="Mii Metadata")
            table.add_column("Filename", style="cyan")
            table.add_column("Mii Name", style="green")
            table.add_column("Creator", style="blue")
            table.add_column("Gender", style="magenta")
            table.add_column("Birthday", style="yellow")
            table.add_column("Favorite Color", style="red")

            for result in results:
                table.add_row(
                    result["filename"],
                    result["mii_name"],
                    result["creator_name"],
                    result["gender"][0],
                    result["birthday"],
                    result["favorite_color"],
                )

            console.print(table)

        console.print(
            f"\n[green]Successfully analyzed {successful_analyses}/{len(mii_files)} files[/green]"
        )


@app.command()
def info():
    """Display information about supported Mii database types"""

    table = Table(title="Supported Mii Database Types")
    table.add_column("Type", style="cyan")
    table.add_column("Source File", style="green")
    table.add_column("Mii Size", style="blue")
    table.add_column("Max Count", style="yellow")
    table.add_column("Prefix", style="magenta")

    for mii_type in MiiType:
        table.add_row(
            mii_type.display_name,
            mii_type.SOURCE,
            f"{mii_type.SIZE} bytes",
            str(mii_type.LIMIT),
            mii_type.PREFIX,
        )

    console.print(table)
    console.print(
        "\n[dim]Place the appropriate database files in the current directory or specify custom paths with --input[/dim]"
    )


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
