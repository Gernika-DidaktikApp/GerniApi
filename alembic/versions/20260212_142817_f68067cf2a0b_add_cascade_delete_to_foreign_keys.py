"""add_cascade_delete_to_foreign_keys

Revision ID: f68067cf2a0b
Revises: 8f807dcaec9c
Create Date: 2026-02-12 14:28:17.202932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f68067cf2a0b'
down_revision: Union[str, None] = '8f807dcaec9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar comportamiento ondelete a las foreign keys para mantener integridad referencial."""

    # 1. usuario.id_clase → SET NULL cuando se elimina la clase
    op.drop_constraint('usuario_id_clase_fkey', 'usuario', type_='foreignkey')
    op.create_foreign_key(
        'usuario_id_clase_fkey', 'usuario', 'clase',
        ['id_clase'], ['id'], ondelete='SET NULL'
    )

    # 2. clase.id_profesor → CASCADE cuando se elimina el profesor
    op.drop_constraint('clase_id_profesor_fkey', 'clase', type_='foreignkey')
    op.create_foreign_key(
        'clase_id_profesor_fkey', 'clase', 'profesor',
        ['id_profesor'], ['id'], ondelete='CASCADE'
    )

    # 3. juego.id_usuario → CASCADE cuando se elimina el usuario
    op.drop_constraint('juego_id_usuario_fkey', 'juego', type_='foreignkey')
    op.create_foreign_key(
        'juego_id_usuario_fkey', 'juego', 'usuario',
        ['id_usuario'], ['id'], ondelete='CASCADE'
    )

    # 4. actividad.id_punto → CASCADE cuando se elimina el punto
    op.drop_constraint('actividad_id_punto_fkey', 'actividad', type_='foreignkey')
    op.create_foreign_key(
        'actividad_id_punto_fkey', 'actividad', 'punto',
        ['id_punto'], ['id'], ondelete='CASCADE'
    )

    # 5. actividad_progreso - tres foreign keys con CASCADE
    op.drop_constraint('actividad_progreso_id_juego_fkey', 'actividad_progreso', type_='foreignkey')
    op.create_foreign_key(
        'actividad_progreso_id_juego_fkey', 'actividad_progreso', 'juego',
        ['id_juego'], ['id'], ondelete='CASCADE'
    )

    op.drop_constraint('actividad_progreso_id_punto_fkey', 'actividad_progreso', type_='foreignkey')
    op.create_foreign_key(
        'actividad_progreso_id_punto_fkey', 'actividad_progreso', 'punto',
        ['id_punto'], ['id'], ondelete='CASCADE'
    )

    op.drop_constraint('actividad_progreso_id_actividad_fkey', 'actividad_progreso', type_='foreignkey')
    op.create_foreign_key(
        'actividad_progreso_id_actividad_fkey', 'actividad_progreso', 'actividad',
        ['id_actividad'], ['id'], ondelete='CASCADE'
    )

    # 6. audit_log - dos foreign keys con SET NULL para preservar logs
    op.drop_constraint('audit_log_usuario_id_fkey', 'audit_log', type_='foreignkey')
    op.create_foreign_key(
        'audit_log_usuario_id_fkey', 'audit_log', 'usuario',
        ['usuario_id'], ['id'], ondelete='SET NULL'
    )

    op.drop_constraint('audit_log_profesor_id_fkey', 'audit_log', type_='foreignkey')
    op.create_foreign_key(
        'audit_log_profesor_id_fkey', 'audit_log', 'profesor',
        ['profesor_id'], ['id'], ondelete='SET NULL'
    )


def downgrade() -> None:
    """Revertir los cambios de ondelete, dejando foreign keys sin comportamiento especial."""

    # 1. usuario.id_clase → Revertir a sin ondelete
    op.drop_constraint('usuario_id_clase_fkey', 'usuario', type_='foreignkey')
    op.create_foreign_key(
        'usuario_id_clase_fkey', 'usuario', 'clase',
        ['id_clase'], ['id']
    )

    # 2. clase.id_profesor → Revertir a sin ondelete
    op.drop_constraint('clase_id_profesor_fkey', 'clase', type_='foreignkey')
    op.create_foreign_key(
        'clase_id_profesor_fkey', 'clase', 'profesor',
        ['id_profesor'], ['id']
    )

    # 3. juego.id_usuario → Revertir a sin ondelete
    op.drop_constraint('juego_id_usuario_fkey', 'juego', type_='foreignkey')
    op.create_foreign_key(
        'juego_id_usuario_fkey', 'juego', 'usuario',
        ['id_usuario'], ['id']
    )

    # 4. actividad.id_punto → Revertir a sin ondelete
    op.drop_constraint('actividad_id_punto_fkey', 'actividad', type_='foreignkey')
    op.create_foreign_key(
        'actividad_id_punto_fkey', 'actividad', 'punto',
        ['id_punto'], ['id']
    )

    # 5. actividad_progreso - tres foreign keys sin ondelete
    op.drop_constraint('actividad_progreso_id_juego_fkey', 'actividad_progreso', type_='foreignkey')
    op.create_foreign_key(
        'actividad_progreso_id_juego_fkey', 'actividad_progreso', 'juego',
        ['id_juego'], ['id']
    )

    op.drop_constraint('actividad_progreso_id_punto_fkey', 'actividad_progreso', type_='foreignkey')
    op.create_foreign_key(
        'actividad_progreso_id_punto_fkey', 'actividad_progreso', 'punto',
        ['id_punto'], ['id']
    )

    op.drop_constraint('actividad_progreso_id_actividad_fkey', 'actividad_progreso', type_='foreignkey')
    op.create_foreign_key(
        'actividad_progreso_id_actividad_fkey', 'actividad_progreso', 'actividad',
        ['id_actividad'], ['id']
    )

    # 6. audit_log - dos foreign keys sin ondelete
    op.drop_constraint('audit_log_usuario_id_fkey', 'audit_log', type_='foreignkey')
    op.create_foreign_key(
        'audit_log_usuario_id_fkey', 'audit_log', 'usuario',
        ['usuario_id'], ['id']
    )

    op.drop_constraint('audit_log_profesor_id_fkey', 'audit_log', type_='foreignkey')
    op.create_foreign_key(
        'audit_log_profesor_id_fkey', 'audit_log', 'profesor',
        ['profesor_id'], ['id']
    )
