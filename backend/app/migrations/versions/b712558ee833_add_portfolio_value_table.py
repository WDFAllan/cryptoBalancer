"""add_portfolio_value_table

Revision ID: b712558ee833
Revises: 532a7df5ae51
Create Date: 2026-01-28 13:38:05.729079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b712558ee833'
down_revision: Union[str, Sequence[str], None] = '532a7df5ae51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'portfolio_value',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('userId', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('totalValue', sa.Float(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('portfolio_value')
