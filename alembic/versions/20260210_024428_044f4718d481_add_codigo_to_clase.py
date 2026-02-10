"""add_codigo_to_clase

Revision ID: 044f4718d481
Revises: fe42f5e58cc3
Create Date: 2026-02-10 02:44:28.552555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '044f4718d481'
down_revision: Union[str, None] = 'fe42f5e58cc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columna codigo a tabla clase (nullable para permitir migración de datos existentes)
    op.add_column('clase', sa.Column('codigo', sa.String(length=6), nullable=True))

    # Crear índice único (después de generar códigos para clases existentes)
    # NOTA: Si ya hay clases en producción, ejecutar primero el script de migración de datos
    # antes de crear el índice único
    op.create_index(op.f('ix_clase_codigo'), 'clase', ['codigo'], unique=True)


def downgrade() -> None:
    # Eliminar índice único
    op.drop_index(op.f('ix_clase_codigo'), table_name='clase')

    # Eliminar columna codigo
    op.drop_column('clase', 'codigo')
