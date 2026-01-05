"""Add file_name, file_size, file_type to documents

Revision ID: add_file_fields
Revises: предыдущий_идентификатор
Create Date: 2024-01-01 12:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_file_fields'
down_revision = None  # Замените на актуальный идентификатор предыдущей миграции
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем новые колонки
    op.add_column('documents', sa.Column('file_name', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('file_size', sa.BigInteger(), nullable=True))
    op.add_column('documents', sa.Column('file_type', sa.String(), nullable=True))

def downgrade():
    # Удаляем колонки при откате
    op.drop_column('documents', 'file_name')
    op.drop_column('documents', 'file_size')
    op.drop_column('documents', 'file_type')
