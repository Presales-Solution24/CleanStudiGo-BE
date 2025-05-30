"""empty message

Revision ID: 89f6db537a87
Revises: 1b6287c5742a
Create Date: 2025-04-29 14:20:08.140449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89f6db537a87'
down_revision = '1b6287c5742a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tbl_specification_definitions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('better_preference', sa.String(length=10), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tbl_specification_definitions', schema=None) as batch_op:
        batch_op.drop_column('better_preference')

    # ### end Alembic commands ###
