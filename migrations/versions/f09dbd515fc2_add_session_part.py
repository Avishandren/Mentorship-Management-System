"""Add session part

Revision ID: f09dbd515fc2
Revises: 
Create Date: 2025-03-13 23:51:10.810913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f09dbd515fc2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('booking',
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('mentor_id', sa.Integer(), nullable=False),
    sa.Column('current_time', sa.DateTime(), nullable=True),
    sa.Column('booking_time', sa.String(length=10), nullable=False),
    sa.Column('date', sa.String(length=10), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['mentor_id'], ['mentor.mentor_id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['student.student_id'], ),
    sa.PrimaryKeyConstraint('booking_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('booking')
    # ### end Alembic commands ###
