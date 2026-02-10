"""
Comandos de exportación vía API

Exporta datos a CSV/JSON usando los endpoints de la API.
"""

import json
from datetime import datetime
from pathlib import Path

import click
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from scripts.utils.api_client import APIClient

console = Console()


@click.group()
def export():
    """📤 Exportación de datos vía API"""
    pass


@export.command()
@click.argument(
    "model",
    type=click.Choice(["usuarios", "profesores", "clases", "actividades", "partidas", "puntos"]),
)
@click.option("--format", "-f", type=click.Choice(["csv", "json"]), default="csv")
@click.option("--output", "-o", help="Archivo de salida")
@click.option("--limit", "-l", type=int, default=1000, help="Máximo de registros")
def data(model, format, output, limit):
    """Exportar datos de un modelo vía API"""
    console.print(f"\n[bold cyan]📤 Exportando {model}...[/bold cyan]\n")

    try:
        with APIClient() as api:
            # Mapeo de modelos a métodos API
            methods = {
                "usuarios": api.list_usuarios,
                "profesores": api.list_profesores,
                "clases": api.list_clases,
                "actividades": api.list_actividades,
                "partidas": api.list_partidas,
                "puntos": api.list_puntos,
            }

            # Obtener datos
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Consultando API...", total=None)
                data_list = methods[model](limit=limit)
                progress.update(task, completed=True)

            if not data_list:
                console.print("[yellow]⚠️  No se encontraron registros[/yellow]")
                return

            console.print(f"[green]✓[/green] {len(data_list)} registros obtenidos\n")

            # Determinar nombre de archivo
            if not output:
                exports_dir = Path("exports")
                exports_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output = exports_dir / f"{model}_{timestamp}.{format}"
            else:
                output = Path(output)
                output.parent.mkdir(parents=True, exist_ok=True)

            # Exportar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Exportando a {format.upper()}...", total=None)

                if format == "csv":
                    df = pd.DataFrame(data_list)
                    df.to_csv(output, index=False, encoding="utf-8")
                elif format == "json":
                    with open(output, "w", encoding="utf-8") as f:
                        json.dump(data_list, f, indent=2, default=str, ensure_ascii=False)

                progress.update(task, completed=True)

            # Mostrar resumen
            file_size = output.stat().st_size / 1024  # KB

            info = Table.grid(padding=(0, 2))
            info.add_column(style="cyan")
            info.add_column(style="white")
            info.add_row("📁 Archivo:", str(output))
            info.add_row("📊 Registros:", f"{len(data_list):,}")
            info.add_row("📦 Tamaño:", f"{file_size:.2f} KB")
            info.add_row("📄 Formato:", format.upper())

            console.print("\n")
            console.print(
                Panel(
                    info,
                    title="[bold green]✅ Exportación Completada[/bold green]",
                    border_style="green",
                )
            )

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        raise click.Abort()


@export.command()
@click.option("--format", "-f", type=click.Choice(["csv", "json"]), default="csv")
@click.option("--output", "-o", default="exports", help="Directorio de salida")
def all(format, output):
    """Exportar TODOS los modelos vía API"""
    console.print("\n[bold cyan]📤 Exportando todos los modelos...[/bold cyan]\n")

    output_dir = Path(output)
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_table = Table(title="Exportaciones", show_header=True, header_style="bold cyan")
    results_table.add_column("Modelo", style="cyan")
    results_table.add_column("Registros", justify="right", style="green")
    results_table.add_column("Archivo", style="dim")

    models = ["usuarios", "profesores", "clases", "actividades", "partidas", "puntos"]

    try:
        with APIClient() as api:
            for model_name in models:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task(f"Exportando {model_name}...", total=None)

                    # Obtener datos
                    methods = {
                        "usuarios": api.list_usuarios,
                        "profesores": api.list_profesores,
                        "clases": api.list_clases,
                        "actividades": api.list_actividades,
                        "partidas": api.list_partidas,
                        "puntos": api.list_puntos,
                    }

                    data_list = methods[model_name](limit=1000)

                    if not data_list:
                        progress.update(task, completed=True)
                        results_table.add_row(model_name, "0", "-")
                        continue

                    # Exportar
                    filename = f"{model_name}_{timestamp}.{format}"
                    filepath = output_dir / filename

                    if format == "csv":
                        df = pd.DataFrame(data_list)
                        df.to_csv(filepath, index=False, encoding="utf-8")
                    elif format == "json":
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(data_list, f, indent=2, default=str, ensure_ascii=False)

                    progress.update(task, completed=True)
                    results_table.add_row(model_name, f"{len(data_list):,}", filename)

        console.print("\n")
        console.print(results_table)
        console.print("\n[bold green]✅ Exportación completada[/bold green]")
        console.print(f"[dim]Directorio:[/dim] {output_dir.absolute()}")

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        raise click.Abort()
