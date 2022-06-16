"""empty message

Revision ID: 79014b6eea50
Revises: 5b25e0c380e2
Create Date: 2022-06-07 11:13:39.108848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79014b6eea50'
down_revision = '5b25e0c380e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('booked_shows')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('booked_shows',
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], name='booked_shows_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], name='booked_shows_venue_id_fkey'),
    sa.PrimaryKeyConstraint('artist_id', 'venue_id', name='booked_shows_pkey')
    )
    # ### end Alembic commands ###
