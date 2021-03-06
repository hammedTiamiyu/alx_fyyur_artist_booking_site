"""empty message

Revision ID: d18da4011141
Revises: 652c1f7a711f
Create Date: 2022-06-14 11:50:30.491257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd18da4011141'
down_revision = '652c1f7a711f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('show', 'artist_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('show', 'venue_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('show', 'venue_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('show', 'artist_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
