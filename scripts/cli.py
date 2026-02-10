#!/usr/bin/env python3
"""
🔧 GerniBide CLI (Versión API Segura)

CLI que usa la API en lugar de acceso directo a base de datos.
Más seguro para uso en producción.

Configuración:
    Copia .env.example a .env y configura:
    - API_URL: URL de la API
    - API_KEY: Tu API Key de administrador

Uso:
    python scripts/cli_api.py --help
    python scripts/cli_api.py users check-api
    python scripts/cli_api.py users list
"""

import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cargar .env si existe
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    from dotenv import load_dotenv

    load_dotenv(env_file)

console = Console()


def print_banner():
    """Muestra el banner de bienvenida"""
    banner = Text()
    banner.append("🎮 ", style="bold cyan")
    banner.append("GerniBide CLI", style="bold blue")
    banner.append(" (API Mode)", style="bold green")
    banner.append(" v1.0", style="dim")

    # Mostrar configuración
    api_url = os.getenv("API_URL", "❌ No configurada")
    api_key = os.getenv("API_KEY", "")
    api_key_display = f"{api_key[:10]}..." if api_key else "❌ No configurada"
    read_only = os.getenv("CLI_READ_ONLY", "false").lower() == "true"

    config = Text()
    config.append(f"\n🌐 API: {api_url}\n", style="dim")
    config.append(f"🔑 Key: {api_key_display}\n", style="dim")
    if read_only:
        config.append("🔒 Modo: Solo lectura\n", style="yellow")

    full_banner = Text.assemble(banner, config)

    panel = Panel(
        full_banner,
        border_style="blue",
        subtitle="Herramienta de gestión administrativa (vía API)",
        subtitle_align="right",
    )
    console.print(panel)


@click.group()
@click.version_option(version="1.0.0", prog_name="GerniBide CLI API")
def cli():
    """
    🔧 GerniBide CLI - Versión API Segura

    Gestiona usuarios, exporta datos y más usando la API.
    Requiere API_KEY configurada en .env
    """
    if sys.stdout.isatty():
        print_banner()


# Importar comandos que usan API
from scripts.commands import export_commands, users_commands  # noqa: E402

cli.add_command(users_commands.users)
cli.add_command(export_commands.export)


# Comando de configuración
@cli.command()
def config():
    """Mostrar configuración actual"""
    console.print("\n[bold cyan]⚙️  Configuración Actual[/bold cyan]\n")

    from rich.table import Table

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Variable", style="cyan", width=20)
    table.add_column("Valor", style="white", width=50)
    table.add_column("Estado", justify="center", width=10)

    # API_URL
    api_url = os.getenv("API_URL")
    table.add_row(
        "API_URL",
        api_url or "[dim]No configurada[/dim]",
        "✅" if api_url else "❌",
    )

    # API_KEY
    api_key = os.getenv("API_KEY")
    api_key_display = f"{api_key[:10]}..." if api_key else "[dim]No configurada[/dim]"
    table.add_row(
        "API_KEY",
        api_key_display,
        "✅" if api_key else "❌",
    )

    # CLI_READ_ONLY
    read_only = os.getenv("CLI_READ_ONLY", "false").lower() == "true"
    table.add_row(
        "CLI_READ_ONLY",
        "true" if read_only else "false",
        "🔒" if read_only else "✏️",
    )

    # ENVIRONMENT
    environment = os.getenv("ENVIRONMENT", "development")
    table.add_row(
        "ENVIRONMENT",
        environment,
        "🔴" if environment == "production" else "🟢",
    )

    console.print(table)

    # Archivo .env
    env_file = Path(__file__).parent / ".env"
    console.print(f"\n[dim]Archivo de configuración:[/dim] {env_file}")
    console.print(f"[dim]Existe:[/dim] {'✅ Sí' if env_file.exists() else '❌ No'}")

    if not env_file.exists():
        console.print("\n[yellow]💡 Tip:[/yellow] Copia .env.example a .env y configúralo")


if __name__ == "__main__":
    cli()
