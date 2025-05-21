"""drop role column from users

Revision ID: eae215b52fa6
Revises: 03b14a6e5f90
Create Date: 2025-05-20 23:40:55.349170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eae215b52fa6'
down_revision: Union[str, None] = '03b14a6e5f90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_column('users', 'role')

def downgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='user'))

