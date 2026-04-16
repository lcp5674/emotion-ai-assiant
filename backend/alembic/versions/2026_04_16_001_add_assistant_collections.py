"""Add assistant_collections table for AI assistant favorites

Revision ID: 2026_04_16_001
Revises: 2026_04_11_001
Create Date: 2026-04-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2026_04_16_001'
down_revision: Union[str, None] = '2026_04_11_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'assistant_collections',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('assistant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['assistant_id'], ['ai_assistants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_assistant_collections_user_id', 'assistant_collections', ['user_id'])
    op.create_index('ix_assistant_collections_assistant_id', 'assistant_collections', ['assistant_id'])
    # Unique constraint to prevent duplicate favorites
    op.create_index('ix_assistant_collections_unique', 'assistant_collections',
                    ['user_id', 'assistant_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_assistant_collections_unique', table_name='assistant_collections')
    op.drop_index('ix_assistant_collections_assistant_id', table_name='assistant_collections')
    op.drop_index('ix_assistant_collections_user_id', table_name='assistant_collections')
    op.drop_table('assistant_collections')
