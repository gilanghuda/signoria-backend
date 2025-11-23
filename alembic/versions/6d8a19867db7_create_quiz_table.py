"""create quiz table

Revision ID: 6d8a19867db7
Revises: c60f808dbc8d
Create Date: 2025-11-23 17:53:02.825843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d8a19867db7'
down_revision: Union[str, Sequence[str], None] = 'c60f808dbc8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'quizzes',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('difficulty_level', sa.String(20), server_default='medium', nullable=False),
        sa.Column('time_limit', sa.Integer, nullable=True),
        sa.Column('level', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("time_limit > 0")
    )
    
    op.create_table(
        'quiz_questions',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('quiz_id', sa.String(36), sa.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_text', sa.Text, nullable=False),
        sa.Column('question_category', sa.String(50), nullable=False),
        sa.Column('explanation', sa.Text, server_default='', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )
    
    op.create_table(
        'quiz_options',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('question_id', sa.String(36), sa.ForeignKey('quiz_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('is_correct', sa.Boolean, server_default=sa.false(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, server_default='option'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )
    
    op.create_table(
        'attempts_quiz',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('quiz_id', sa.String(36), sa.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('total_questions', sa.Integer, nullable=False),
        sa.Column('submitted_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('is_completed', sa.Boolean, server_default=sa.false(), nullable=False),
        sa.CheckConstraint("score >= 0"),
        sa.CheckConstraint("total_questions > 0")
    )
    
    op.create_table(
        'attempts_quiz_answer',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('attempt_id', sa.String(36), sa.ForeignKey('attempts_quiz.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', sa.String(36), sa.ForeignKey('quiz_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('selected_option_id', sa.String(36), sa.ForeignKey('quiz_options.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('attempt_id', 'question_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('attempts_quiz_answer')
    op.drop_table('attempts_quiz')
    op.drop_table('quiz_options')
    op.drop_table('quiz_questions')
    op.drop_table('quizzes')
