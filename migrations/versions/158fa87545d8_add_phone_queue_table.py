"""Add phone queue table

Revision ID: 158fa87545d8
Revises: 4cfd75e94539
Create Date: 2017-10-05 09:05:06.601487

"""

# revision identifiers, used by Alembic.
revision = '158fa87545d8'
down_revision = '4cfd75e94539'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('phone_queue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('branch_id', sa.Integer(), nullable=True),
    sa.Column('phone_number', sa.String(length=45), nullable=True),
    sa.Column('status', sa.String(length=45), nullable=True),
    sa.Column('error_message', sa.String(length=45), nullable=True),
    sa.Column('country', sa.String(length=45), nullable=True),
    sa.Column('sent', sa.Boolean(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['branch_id'], [u'branches.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phone_queue_branch_id'), 'phone_queue', ['branch_id'], unique=False)
    op.create_index(op.f('ix_phone_queue_deleted'), 'phone_queue', ['deleted'], unique=False)
    op.create_index(op.f('ix_phone_queue_sent'), 'phone_queue', ['sent'], unique=False)
    op.add_column(u'ussd_messages', sa.Column('bundle_balance', sa.Float(), server_default=sa.text(u"'0'"), nullable=True))
    op.add_column(u'ussd_messages', sa.Column('expiry_datetime', sa.DateTime(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'ussd_messages', 'expiry_datetime')
    op.drop_column(u'ussd_messages', 'bundle_balance')
    op.drop_index(op.f('ix_phone_queue_sent'), table_name='phone_queue')
    op.drop_index(op.f('ix_phone_queue_deleted'), table_name='phone_queue')
    op.drop_index(op.f('ix_phone_queue_branch_id'), table_name='phone_queue')
    op.drop_table('phone_queue')
    ### end Alembic commands ###
