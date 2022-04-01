"""6

Revision ID: c459703a5b5c
Revises: 9275b0171a82
Create Date: 2022-04-01 10:59:57.789427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c459703a5b5c'
down_revision = '9275b0171a82'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('album', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('album', sa.Column('cover', sa.String(length=255), nullable=True))
    op.add_column('photo', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('photo', sa.Column('favor', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('photo', 'favor')
    op.drop_column('photo', 'description')
    op.drop_column('album', 'cover')
    op.drop_column('album', 'description')
    # ### end Alembic commands ###