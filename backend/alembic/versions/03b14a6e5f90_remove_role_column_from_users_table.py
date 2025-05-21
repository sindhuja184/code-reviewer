"""remove role column from users table

Revision ID: 03b14a6e5f90
Revises: 5f1ff268d9c8
Create Date: 2025-05-20 23:35:40.565198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03b14a6e5f90'
down_revision: Union[str, None] = '5f1ff268d9c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('users', 'role')

def downgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='user'))
