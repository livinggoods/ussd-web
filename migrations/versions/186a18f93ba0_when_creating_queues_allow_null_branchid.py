"""When creating queues, allow null branchID

Revision ID: 186a18f93ba0
Revises: 45728000f809
Create Date: 2017-12-04 13:42:55.429595

"""

# revision identifiers, used by Alembic.
revision = '186a18f93ba0'
down_revision = '45728000f809'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("queues", "branch_id", nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("queues", "branch_id", nullable=False)
    ### end Alembic commands ###
