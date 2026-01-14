"""add favorite_platform to user

Revision ID: 532a7df5ae51
Revises: 7318c6b8c8bb
Create Date: 2026-01-13 15:47:17.876203
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '532a7df5ae51'
down_revision = '7318c6b8c8bb'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user', sa.Column('favorite_platform', sa.String(), nullable=True))

def downgrade():
    op.drop_column('user', 'favorite_platform')