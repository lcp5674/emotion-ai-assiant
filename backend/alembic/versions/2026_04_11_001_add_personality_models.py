"""Add personality models (SBTI, Attachment, DeepProfile)

Revision ID: 2026_04_11_001
Revises: 40f88a383240
Create Date: 2026-04-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2026_04_11_001'
down_revision: Union[str, None] = '40f88a383240'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SBTI Questions Table
    op.create_table(
        'sbti_questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('question_no', sa.Integer(), nullable=False, unique=True),
        sa.Column('statement_a', sa.Text(), nullable=False),
        sa.Column('theme_a', sa.String(length=50), nullable=False),
        sa.Column('weight_a', sa.Integer(), default=1),
        sa.Column('statement_b', sa.Text(), nullable=False),
        sa.Column('theme_b', sa.String(length=50), nullable=False),
        sa.Column('weight_b', sa.Integer(), default=1),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # SBTI Answers Table
    op.create_table(
        'sbti_answers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('answer', sa.String(length=1), nullable=False),
        sa.Column('selected_theme', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['question_id'], ['sbti_questions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sbti_answers_user_id', 'sbti_answers', ['user_id'])
    op.create_index('ix_sbti_answers_question_id', 'sbti_answers', ['question_id'])

    # SBTI Results Table
    op.create_table(
        'sbti_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('all_themes_scores', sa.JSON(), nullable=False),
        sa.Column('top_theme_1', sa.String(length=50), nullable=False),
        sa.Column('top_theme_2', sa.String(length=50), nullable=False),
        sa.Column('top_theme_3', sa.String(length=50), nullable=False),
        sa.Column('top_theme_4', sa.String(length=50), nullable=False),
        sa.Column('top_theme_5', sa.String(length=50), nullable=False),
        sa.Column('executing_score', sa.Float(), nullable=False),
        sa.Column('influencing_score', sa.Float(), nullable=False),
        sa.Column('relationship_score', sa.Float(), nullable=False),
        sa.Column('strategic_score', sa.Float(), nullable=False),
        sa.Column('dominant_domain', sa.String(length=50), nullable=False),
        sa.Column('report_json', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('is_latest', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sbti_results_user_id', 'sbti_results', ['user_id'])
    op.create_index('ix_sbti_results_is_latest', 'sbti_results', ['is_latest'])

    # Attachment Questions Table
    op.create_table(
        'attachment_questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('question_no', sa.Integer(), nullable=False, unique=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('anxiety_weight', sa.Float(), default=0),
        sa.Column('avoidance_weight', sa.Float(), default=0),
        sa.Column('scale_min', sa.Integer(), default=1),
        sa.Column('scale_max', sa.Integer(), default=7),
        sa.Column('scale_min_label', sa.String(length=50), default='完全不符合'),
        sa.Column('scale_max_label', sa.String(length=50), default='完全符合'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Attachment Answers Table
    op.create_table(
        'attachment_answers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['question_id'], ['attachment_questions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_attachment_answers_user_id', 'attachment_answers', ['user_id'])
    op.create_index('ix_attachment_answers_question_id', 'attachment_answers', ['question_id'])

    # Attachment Results Table
    op.create_table(
        'attachment_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('anxiety_score', sa.Float(), nullable=False),
        sa.Column('avoidance_score', sa.Float(), nullable=False),
        sa.Column('attachment_style', sa.String(length=20), nullable=False),
        sa.Column('sub_type', sa.String(length=50), nullable=True),
        sa.Column('characteristics', sa.JSON(), nullable=True),
        sa.Column('relationship_tips', sa.Text(), nullable=True),
        sa.Column('self_growth_tips', sa.Text(), nullable=True),
        sa.Column('report_json', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('is_latest', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_attachment_results_user_id', 'attachment_results', ['user_id'])
    op.create_index('ix_attachment_results_is_latest', 'attachment_results', ['is_latest'])

    # Deep Persona Profiles Table
    op.create_table(
        'deep_persona_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('mbti_result_id', sa.Integer(), nullable=True),
        sa.Column('sbti_result_id', sa.Integer(), nullable=True),
        sa.Column('attachment_result_id', sa.Integer(), nullable=True),
        sa.Column('core_tags', sa.JSON(), nullable=True),
        sa.Column('emotion_pattern', sa.Text(), nullable=True),
        sa.Column('communication_style', sa.Text(), nullable=True),
        sa.Column('relationship_needs', sa.JSON(), nullable=True),
        sa.Column('growth_suggestions', sa.JSON(), nullable=True),
        sa.Column('ai_compatibility', sa.JSON(), nullable=True),
        sa.Column('completeness', sa.Integer(), default=0),
        sa.Column('has_deep_report', sa.Boolean(), default=False),
        sa.Column('deep_report_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['mbti_result_id'], ['mbti_results.id']),
        sa.ForeignKeyConstraint(['sbti_result_id'], ['sbti_results.id']),
        sa.ForeignKeyConstraint(['attachment_result_id'], ['attachment_results.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_deep_persona_profiles_user_id', 'deep_persona_profiles', ['user_id'])
    op.create_index('ix_deep_persona_profiles_completeness', 'deep_persona_profiles', ['completeness'])

    # Persona Insights Table
    op.create_table(
        'persona_insights',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('insight_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_helpful', sa.Boolean(), nullable=True),
        sa.Column('user_feedback', sa.Text(), nullable=True),
        sa.Column('generated_by', sa.String(length=50), default='ai'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_persona_insights_user_id', 'persona_insights', ['user_id'])
    op.create_index('ix_persona_insights_insight_type', 'persona_insights', ['insight_type'])
    op.create_index('ix_persona_insights_created_at', 'persona_insights', ['created_at'])

    # Add columns to users table
    op.add_column('users', sa.Column('sbti_result_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('attachment_result_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove columns from users table
    op.drop_column('users', 'attachment_result_id')
    op.drop_column('users', 'sbti_result_id')

    # Drop tables in reverse order
    op.drop_table('persona_insights')
    op.drop_table('deep_persona_profiles')
    op.drop_table('attachment_results')
    op.drop_table('attachment_answers')
    op.drop_table('attachment_questions')
    op.drop_table('sbti_results')
    op.drop_table('sbti_answers')
    op.drop_table('sbti_questions')
