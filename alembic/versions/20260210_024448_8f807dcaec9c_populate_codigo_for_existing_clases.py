"""populate_codigo_for_existing_clases

Revision ID: 8f807dcaec9c
Revises: 044f4718d481
Create Date: 2026-02-10 02:44:48.787500

"""

import random
import string
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = "8f807dcaec9c"
down_revision: Union[str, None] = "044f4718d481"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def generar_codigo_clase() -> str:
    """Genera un código alfanumérico único de 6 caracteres.

    Evita caracteres ambiguos: 0/O, 1/I/l
    """
    caracteres = (
        string.ascii_uppercase.replace("O", "").replace("I", "")
        + string.digits.replace("0", "").replace("1", "")
    )
    return "".join(random.choices(caracteres, k=6))


def upgrade() -> None:
    """Genera códigos únicos para todas las clases existentes sin código."""
    conn = op.get_bind()

    # Obtener clases sin código
    result = conn.execute(text("SELECT id FROM clase WHERE codigo IS NULL"))
    clases_sin_codigo = result.fetchall()

    if not clases_sin_codigo:
        print("✅ No hay clases sin código")
        return

    print(f"🔄 Generando códigos para {len(clases_sin_codigo)} clases...")

    # Obtener códigos existentes para evitar duplicados
    result = conn.execute(text("SELECT codigo FROM clase WHERE codigo IS NOT NULL"))
    codigos_existentes = {row[0] for row in result.fetchall()}

    # Generar códigos únicos
    for clase_row in clases_sin_codigo:
        clase_id = clase_row[0]

        # Generar código único
        codigo = generar_codigo_clase()
        while codigo in codigos_existentes:
            codigo = generar_codigo_clase()

        # Actualizar clase con código
        conn.execute(text("UPDATE clase SET codigo = :codigo WHERE id = :id"), {"codigo": codigo, "id": clase_id})
        codigos_existentes.add(codigo)
        print(f"  ✓ Clase {clase_id[:8]}... → {codigo}")

    print(f"✅ {len(clases_sin_codigo)} códigos generados")


def downgrade() -> None:
    """Eliminar códigos generados (opcional)."""
    # No hacemos nada en downgrade para preservar códigos generados
    # Si realmente quieres eliminarlos, descomenta:
    # conn = op.get_bind()
    # conn.execute(text("UPDATE clase SET codigo = NULL"))
    pass
