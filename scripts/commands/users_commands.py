"""
Comandos de gestión de usuarios usando la API

Versión segura que usa la API en lugar de acceso directo a BD.
Requiere API_KEY configurada.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from scripts.utils.api_client import APIClient

console = Console()


@click.group()
def users():
    """👥 Gestión de usuarios y profesores (vía API)"""
    pass


@users.command()
@click.option("--username", prompt=True, help="Nombre de usuario")
@click.option(
    "--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Contraseña"
)
@click.option("--nombre", prompt=True, help="Nombre")
@click.option("--apellido", prompt=True, help="Apellido")
@click.option("--admin", is_flag=True, help="Marcar como administrador")
def create_profesor(username, password, nombre, apellido, admin):
    """Crear un nuevo profesor vía API"""
    console.print("\n[bold cyan]👨‍🏫 Creando profesor...[/bold cyan]\n")

    try:
        with APIClient() as api:
            data = {
                "username": username,
                "password": password,
                "nombre": nombre,
                "apellido": apellido,
                "es_admin": admin,
            }

            result = api.create_profesor(data)

            # Mostrar resumen
            info = Table.grid(padding=(0, 2))
            info.add_column(style="cyan")
            info.add_column(style="white")
            info.add_row("👤 Username:", username)
            info.add_row("📝 Nombre:", f"{nombre} {apellido}")
            info.add_row("🔑 ID:", result.get("id", "N/A"))
            info.add_row("⭐ Admin:", "Sí" if admin else "No")

            console.print("\n")
            console.print(
                Panel(
                    info,
                    title="[bold green]✅ Profesor Creado[/bold green]",
                    border_style="green",
                )
            )

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        raise click.Abort()


@users.command()
@click.option("--username", prompt=True, help="Nombre de usuario")
@click.option("--password", default=None, help="Contraseña (por defecto: mismo que username)")
@click.option("--nombre", prompt=True, help="Nombre")
@click.option("--apellido", prompt=True, help="Apellido")
@click.option("--clase", help="Código de clase (opcional)")
def create_usuario(username, password, nombre, apellido, clase):
    """Crear un nuevo usuario estudiante vía API"""
    console.print("\n[bold cyan]👤 Creando usuario...[/bold cyan]\n")

    if not password:
        password = username
        console.print("[dim]Password no especificado, usando username como password[/dim]")

    try:
        with APIClient() as api:
            # Si se proporciona código de clase, buscar el ID
            id_clase = None
            if clase:
                clases = api.list_clases()
                clase_obj = next((c for c in clases if c.get("codigo") == clase), None)
                if not clase_obj:
                    console.print(f"[bold red]❌ Error:[/bold red] Clase '{clase}' no encontrada")
                    return
                id_clase = clase_obj["id"]

            data = {
                "username": username,
                "password": password,
                "nombre": nombre,
                "apellido": apellido,
            }

            if id_clase:
                data["id_clase"] = id_clase

            result = api.create_usuario(data)

            # Mostrar resumen
            info = Table.grid(padding=(0, 2))
            info.add_column(style="cyan")
            info.add_column(style="white")
            info.add_row("👤 Username:", username)
            info.add_row("📝 Nombre:", f"{nombre} {apellido}")
            info.add_row("🔑 ID:", result.get("id", "N/A"))
            if clase:
                info.add_row("🏫 Clase:", clase)

            console.print("\n")
            console.print(
                Panel(
                    info, title="[bold green]✅ Usuario Creado[/bold green]", border_style="green"
                )
            )

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        raise click.Abort()


@users.command()
@click.option("--type", "-t", type=click.Choice(["usuarios", "profesores", "all"]), default="all")
@click.option("--limit", "-l", type=int, default=20, help="Número de registros a mostrar")
def list(type, limit):
    """Listar usuarios y/o profesores vía API"""
    console.print(f"\n[bold cyan]👥 Listado de {type}[/bold cyan]\n")

    try:
        with APIClient() as api:
            if type in ["usuarios", "all"]:
                # Listar usuarios
                usuarios = api.list_usuarios(limit=limit)

                table = Table(
                    title=f"Usuarios (mostrando {len(usuarios)})",
                    show_header=True,
                    header_style="bold cyan",
                )
                table.add_column("Username", style="cyan")
                table.add_column("Nombre", style="white")
                table.add_column("Clase", style="green")
                table.add_column("Score", justify="right", style="yellow")

                for u in usuarios:
                    clase_codigo = "-"
                    if u.get("id_clase"):
                        # Buscar código de clase
                        try:
                            clase = api.get_clase(u["id_clase"])
                            clase_codigo = clase.get("codigo", "-")
                        except Exception:
                            pass

                    table.add_row(
                        u["username"],
                        f"{u['nombre']} {u['apellido']}",
                        clase_codigo,
                        str(u.get("top_score", 0)),
                    )

                console.print(table)
                console.print(f"[dim]Mostrando primeros {limit} usuarios[/dim]\n")

            if type in ["profesores", "all"]:
                # Listar profesores
                profesores = api.list_profesores(limit=limit)

                table = Table(
                    title=f"Profesores (mostrando {len(profesores)})",
                    show_header=True,
                    header_style="bold cyan",
                )
                table.add_column("Username", style="cyan")
                table.add_column("Nombre", style="white")
                table.add_column("Admin", style="yellow")

                for p in profesores:
                    table.add_row(
                        p["username"],
                        f"{p['nombre']} {p['apellido']}",
                        "⭐ Sí" if p.get("es_admin") else "No",
                    )

                console.print(table)
                console.print(f"[dim]Mostrando primeros {limit} profesores[/dim]\n")

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")


@users.command()
@click.argument("usuario_id")
def delete(usuario_id):
    """Eliminar un usuario por ID vía API"""
    console.print(f"\n[bold red]⚠️  Eliminar usuario: {usuario_id}[/bold red]\n")

    if not Confirm.ask(f"¿Estás seguro de eliminar el usuario '{usuario_id}'?", default=False):
        console.print("[yellow]Operación cancelada[/yellow]")
        return

    try:
        with APIClient() as api:
            api.delete_usuario(usuario_id)
            console.print(f"[bold green]✅ Usuario '{usuario_id}' eliminado[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        raise click.Abort()


@users.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.option("--clase", help="Código de clase para todos los usuarios")
def import_csv(csv_file, clase):
    """Importar usuarios masivamente desde CSV vía API"""
    console.print(f"\n[bold cyan]📥 Importando usuarios desde {csv_file}...[/bold cyan]\n")

    import csv

    try:
        with APIClient() as api:
            # Leer CSV
            usuarios = []
            with open(csv_file, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    usuarios.append(
                        {
                            "username": row["username"],
                            "nombre": row["nombre"],
                            "apellido": row["apellido"],
                            "password": row.get("password", row["username"]),
                        }
                    )

            console.print(f"[dim]Usuarios a importar:[/dim] {len(usuarios)}\n")

            # Buscar ID de clase si se proporcionó código
            id_clase = None
            if clase:
                clases = api.list_clases()
                clase_obj = next((c for c in clases if c.get("codigo") == clase), None)
                if not clase_obj:
                    console.print(f"[bold red]❌ Error:[/bold red] Clase '{clase}' no encontrada")
                    return
                id_clase = clase_obj["id"]
                console.print(f"[dim]Clase asignada:[/dim] {clase}\n")

            # Importar vía API
            result = api.bulk_import_usuarios(usuarios, id_clase=id_clase)

            console.print(
                f"[bold green]✅ {result.get('created', 0)} usuarios importados exitosamente[/bold green]"
            )

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        raise click.Abort()


@users.command()
def check_api():
    """Verificar conexión con la API"""
    console.print("\n[bold cyan]🔍 Verificando conexión con la API...[/bold cyan]\n")

    try:
        with APIClient() as api:
            health = api.health_check()

            info = Table.grid(padding=(0, 2))
            info.add_column(style="cyan")
            info.add_column(style="white")
            info.add_row("🌐 URL:", api.base_url)
            info.add_row(
                "🔑 API Key:", f"{api.api_key[:10]}..." if api.api_key else "❌ No configurada"
            )
            info.add_row("✅ Estado:", health.get("status", "unknown"))

            console.print(
                Panel(info, title="[bold green]Conexión OK[/bold green]", border_style="green")
            )

    except Exception as e:
        console.print(f"[bold red]❌ Error de conexión:[/bold red] {str(e)}")
        raise click.Abort()
