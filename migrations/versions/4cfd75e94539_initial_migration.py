"""Initial Migration

Revision ID: 4cfd75e94539
Revises: None
Create Date: 2017-10-02 08:42:03.290733

"""

# revision identifiers, used by Alembic.
revision = '4cfd75e94539'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('branches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('branch_name', sa.String(length=45), nullable=True),
    sa.Column('branch_code', sa.String(length=45), nullable=True),
    sa.Column('country', sa.String(length=45), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_branches_deleted'), 'branches', ['deleted'], unique=False)
    op.create_table('geos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('geo_name', sa.String(length=20), nullable=True),
    sa.Column('geo_code', sa.String(length=20), nullable=True),
    sa.Column('archived', sa.Integer(), server_default=sa.text(u"'0'"), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('geo_name')
    )
    op.create_index(op.f('ix_geos_deleted'), 'geos', ['deleted'], unique=False)
    op.create_table('message_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=45), nullable=True),
    sa.Column('status', sa.Text(), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_types_deleted'), 'message_types', ['deleted'], unique=False)
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    op.create_table('user_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_user_types_deleted'), 'user_types', ['deleted'], unique=False)
    op.create_table('phones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('branch_id', sa.Integer(), nullable=True),
    sa.Column('phone_number', sa.String(length=45), nullable=True),
    sa.Column('assigned_to', sa.String(length=45), nullable=True),
    sa.Column('country', sa.String(length=45), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['branch_id'], [u'branches.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phones_active'), 'phones', ['active'], unique=False)
    op.create_index(op.f('ix_phones_branch_id'), 'phones', ['branch_id'], unique=False)
    op.create_index(op.f('ix_phones_deleted'), 'phones', ['deleted'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('location', sa.String(length=64), nullable=True),
    sa.Column('about_me', sa.Text(), nullable=True),
    sa.Column('member_since', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('avatar_hash', sa.String(length=32), nullable=True),
    sa.Column('geo_id', sa.Integer(), nullable=True),
    sa.Column('user_type_id', sa.Integer(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['geo_id'], ['geos.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_type_id'], ['user_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_deleted'), 'users', ['deleted'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('ussd_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(length=45), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('branch_id', sa.Integer(), nullable=True),
    sa.Column('phone_id', sa.Integer(), nullable=True),
    sa.Column('message_type_id', sa.Integer(), nullable=True),
    sa.Column('country', sa.String(length=5), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['branch_id'], [u'branches.id'], ),
    sa.ForeignKeyConstraint(['message_type_id'], [u'message_types.id'], ),
    sa.ForeignKeyConstraint(['phone_id'], [u'phones.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ussd_messages_active'), 'ussd_messages', ['active'], unique=False)
    op.create_index(op.f('ix_ussd_messages_branch_id'), 'ussd_messages', ['branch_id'], unique=False)
    op.create_index(op.f('ix_ussd_messages_deleted'), 'ussd_messages', ['deleted'], unique=False)
    op.create_index(op.f('ix_ussd_messages_message_type_id'), 'ussd_messages', ['message_type_id'], unique=False)
    op.create_index(op.f('ix_ussd_messages_phone_id'), 'ussd_messages', ['phone_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_ussd_messages_phone_id'), table_name='ussd_messages')
    op.drop_index(op.f('ix_ussd_messages_message_type_id'), table_name='ussd_messages')
    op.drop_index(op.f('ix_ussd_messages_deleted'), table_name='ussd_messages')
    op.drop_index(op.f('ix_ussd_messages_branch_id'), table_name='ussd_messages')
    op.drop_index(op.f('ix_ussd_messages_active'), table_name='ussd_messages')
    op.drop_table('ussd_messages')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_deleted'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_phones_deleted'), table_name='phones')
    op.drop_index(op.f('ix_phones_branch_id'), table_name='phones')
    op.drop_index(op.f('ix_phones_active'), table_name='phones')
    op.drop_table('phones')
    op.drop_index(op.f('ix_user_types_deleted'), table_name='user_types')
    op.drop_table('user_types')
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_message_types_deleted'), table_name='message_types')
    op.drop_table('message_types')
    op.drop_index(op.f('ix_geos_deleted'), table_name='geos')
    op.drop_table('geos')
    op.drop_index(op.f('ix_branches_deleted'), table_name='branches')
    op.drop_table('branches')
    ### end Alembic commands ###
