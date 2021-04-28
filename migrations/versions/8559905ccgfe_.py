"""empty message

Revision ID: 8559905ccfed
Revises: 
Create Date: 2021-04-28 16:39:31.518553

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
from skeletor import doc

revision = '8559905ccgfe'
down_revision = '8559905ccfed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    doc.db.create_collection('app_properties', sync=True, user_keys=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    doc.db.delete_collection('app_properties')
    # ### end Alembic commands ###