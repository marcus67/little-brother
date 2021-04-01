"""fb-issue-124

Revision ID: 0a5c7b6ad27a
Revises: version_0_3
Create Date: 2021-03-27 00:15:59.931300

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a5c7b6ad27a'
down_revision = 'version_0_3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('time_extension',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=256), nullable=True),
    sa.Column('reference_datetime', sa.DateTime(), nullable=True),
    sa.Column('start_datetime', sa.DateTime(), nullable=True),
    sa.Column('end_datetime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('time_extension')
    # ### end Alembic commands ###
