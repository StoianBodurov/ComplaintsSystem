"""Change complaints column

Revision ID: dcb19c226477
Revises: d2debec817a1
Create Date: 2023-03-02 17:43:59.739155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcb19c226477'
down_revision = 'd2debec817a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('complaints', sa.Column('complainer_id', sa.Integer(), nullable=False))
    op.drop_constraint('complaints_complaint_id_fkey', 'complaints', type_='foreignkey')
    op.create_foreign_key(None, 'complaints', 'users', ['complainer_id'], ['id'])
    op.drop_column('complaints', 'complaint_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('complaints', sa.Column('complaint_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'complaints', type_='foreignkey')
    op.create_foreign_key('complaints_complaint_id_fkey', 'complaints', 'users', ['complaint_id'], ['id'])
    op.drop_column('complaints', 'complainer_id')
    # ### end Alembic commands ###
