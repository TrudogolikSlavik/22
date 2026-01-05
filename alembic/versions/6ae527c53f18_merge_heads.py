"""merge heads

Revision ID: 6ae527c53f18
Revises: 95786d196571, add_file_fields
Create Date: 2025-10-12 18:32:33.609041

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '6ae527c53f18'
down_revision: Union[str, Sequence[str], None] = ('95786d196571', 'add_file_fields')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
