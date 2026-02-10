"""add_audit_log_table

Revision ID: 99feb955a1e1
Revises: 09601127e33f
Create Date: 2026-02-06 22:26:47.927763

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '99feb955a1e1'
down_revision: Union[str, None] = '09601127e33f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'audit_log',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('usuario_id', sa.String(36), nullable=True),
        sa.Column('profesor_id', sa.String(36), nullable=True),
        sa.Column('accion', sa.String(100), nullable=False),
        sa.Column('detalles', sa.Text(), nullable=True),
        sa.Column('tipo', sa.String(20), nullable=False),
        # Campos específicos de LogWeb
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('browser', sa.String(100), nullable=True),
        # Campos específicos de LogApp
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('app_version', sa.String(20), nullable=True),
        sa.Column('device_id', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id']),
        sa.ForeignKeyConstraint(['profesor_id'], ['profesor.id'])
    )
    # Crear índices para mejorar performance en queries comunes
    op.create_index('ix_audit_log_timestamp', 'audit_log', ['timestamp'])
    op.create_index('ix_audit_log_tipo', 'audit_log', ['tipo'])
    op.create_index('ix_audit_log_accion', 'audit_log', ['accion'])


def downgrade() -> None:
    op.drop_index('ix_audit_log_accion', 'audit_log')
    op.drop_index('ix_audit_log_tipo', 'audit_log')
    op.drop_index('ix_audit_log_timestamp', 'audit_log')
    op.drop_table('audit_log')
