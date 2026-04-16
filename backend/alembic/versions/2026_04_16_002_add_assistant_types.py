"""Add sbti_types and attachment_styles to ai_assistants

Revision ID: 2026_04_16_002
Revises: 2026_04_16_001
Create Date: 2026-04-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2026_04_16_002'
down_revision: Union[str, None] = '2026_04_16_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ai_assistants', sa.Column('sbti_types', sa.String(length=200), nullable=True, comment='SBTI主题类型'))
    op.add_column('ai_assistants', sa.Column('attachment_styles', sa.String(length=200), nullable=True, comment='依恋风格类型'))


def downgrade() -> None:
    op.drop_column('ai_assistants', 'attachment_styles')
    op.drop_column('ai_assistants', 'sbti_types')
