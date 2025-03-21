"""Create database tables

Revision ID: 40f22b9f4671
Revises: 18ce4ecef701
Create Date: 2025-03-15 01:06:12.048759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40f22b9f4671'
down_revision: Union[str, None] = '18ce4ecef701'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('attachments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('source_type', sa.String(), nullable=False),
    sa.Column('source_id', sa.String(), nullable=False),
    sa.Column('file_name', sa.String(), nullable=False),
    sa.Column('file_size', sa.BigInteger(), nullable=True),
    sa.Column('content_type', sa.String(), nullable=True),
    sa.Column('storage_path', sa.String(), nullable=False),
    sa.Column('file_url', sa.String(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('courses',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('code', sa.String(), nullable=True),
    sa.Column('time', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('assignments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('article_id', sa.String(), nullable=False),
    sa.Column('course_id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('due_date', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('submission_status', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('materials',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('article_id', sa.String(), nullable=False),
    sa.Column('course_id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('date', sa.String(), nullable=True),
    sa.Column('views', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notices',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('article_id', sa.String(), nullable=False),
    sa.Column('course_id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('date', sa.String(), nullable=True),
    sa.Column('views', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('syllabus',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('course_id', sa.String(), nullable=False),
    sa.Column('year_semester', sa.String(), nullable=True),
    sa.Column('course_type', sa.String(), nullable=True),
    sa.Column('professor_name', sa.String(), nullable=True),
    sa.Column('office_hours', sa.String(), nullable=True),
    sa.Column('homepage', sa.String(), nullable=True),
    sa.Column('course_overview', sa.Text(), nullable=True),
    sa.Column('objectives', sa.Text(), nullable=True),
    sa.Column('textbooks', sa.Text(), nullable=True),
    sa.Column('equipment', sa.Text(), nullable=True),
    sa.Column('evaluation_method', sa.Text(), nullable=True),
    sa.Column('weekly_plans', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('syllabus')
    op.drop_table('notices')
    op.drop_table('materials')
    op.drop_table('assignments')
    op.drop_table('courses')
    op.drop_table('attachments')
    # ### end Alembic commands ###
