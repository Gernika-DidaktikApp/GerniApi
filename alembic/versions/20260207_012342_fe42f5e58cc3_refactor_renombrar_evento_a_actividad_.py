"""refactor: renombrar evento a actividad, actividad a punto, evento_estado a actividad_progreso

Revision ID: fe42f5e58cc3
Revises: 99feb955a1e1
Create Date: 2026-02-07 01:23:42.224308

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fe42f5e58cc3'
down_revision: Union[str, None] = '99feb955a1e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Paso 1: Renombrar tablas (orden correcto para evitar conflictos)
    op.rename_table('evento_estado', 'actividad_progreso')
    op.rename_table('actividad', 'punto')  # Liberar el nombre "actividad"
    op.rename_table('evento', 'actividad')  # Ahora podemos usar "actividad"

    # Paso 2: Renombrar columnas FK en actividad_progreso
    # id_actividad → id_punto (referencia a la antigua tabla actividad, ahora punto)
    # id_evento → id_actividad (referencia a la antigua tabla evento, ahora actividad)
    op.alter_column('actividad_progreso', 'id_actividad', new_column_name='id_punto')
    op.alter_column('actividad_progreso', 'id_evento', new_column_name='id_actividad')

    # Paso 3: Renombrar columna FK en actividad (antes evento)
    # id_actividad → id_punto
    op.alter_column('actividad', 'id_actividad', new_column_name='id_punto')

    # Paso 4: Eliminar columna contenido de actividad (antes evento, ahora es template)
    op.drop_column('actividad', 'contenido')

    # Paso 5: Añadir columna respuesta_contenido a actividad_progreso
    op.add_column('actividad_progreso', sa.Column('respuesta_contenido', sa.Text(), nullable=True))


def downgrade() -> None:
    # Revertir en orden inverso
    op.drop_column('actividad_progreso', 'respuesta_contenido')
    op.add_column('actividad', sa.Column('contenido', sa.Text(), nullable=True))

    op.alter_column('actividad', 'id_punto', new_column_name='id_actividad')
    op.alter_column('actividad_progreso', 'id_actividad', new_column_name='id_evento')
    op.alter_column('actividad_progreso', 'id_punto', new_column_name='id_actividad')

    op.rename_table('punto', 'actividad')
    op.rename_table('actividad', 'evento')
    op.rename_table('actividad_progreso', 'evento_estado')
