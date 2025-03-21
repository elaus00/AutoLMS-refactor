"""update attachment model fields2

Revision ID: 84b055820898
Revises: c8680f5ba578
Create Date: 2025-03-20 11:20:21.880684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84b055820898'
down_revision: Union[str, None] = 'c8680f5ba578'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attachments', sa.Column('course_id', sa.String(), nullable=False))
    op.drop_column('attachments', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attachments', sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('attachments', 'course_id')
    # ### end Alembic commands ###
