"""empty message

Revision ID: cc75568c1716
Revises: 63557b49558a
Create Date: 2021-06-27 16:37:07.789526

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'cc75568c1716'
down_revision = '63557b49558a'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('alerts', sa.Column('blockchain', sa.String(length=64), nullable=True))
    op.add_column('blockchains', sa.Column('blockchain', sa.String(length=64), nullable=True))
    op.add_column('challenges', sa.Column('blockchain', sa.String(length=64), nullable=True))
    op.add_column('connections', sa.Column('blockchain', sa.String(length=64), nullable=True))
    op.add_column('farms', sa.Column('total_flax', sa.REAL(), nullable=True))
    op.add_column('farms', sa.Column('flax_netspace_size', sa.REAL(), nullable=True))
    op.add_column('farms', sa.Column('flax_expected_time_to_win', sa.String(length=64), nullable=True))
    op.add_column('wallets', sa.Column('blockchain', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###
        
    # Update existing rows with default 'chia' blockchain
    conn = op.get_bind()
    conn.execute(text("update alerts set blockchain = 'chia'",{}))
    conn.execute(text("update blockchains set blockchain = 'chia'",{}))
    conn.execute(text("update challenges set blockchain = 'chia'",{}))
    conn.execute(text("update connections set blockchain = 'chia'",{}))
    conn.execute(text("update wallets set blockchain = 'chia'",{}))


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('wallets', 'blockchain')
    op.drop_column('farms', 'flax_expected_time_to_win')
    op.drop_column('farms', 'flax_netspace_size')
    op.drop_column('farms', 'total_flax')
    op.drop_column('connections', 'blockchain')
    op.drop_column('challenges', 'blockchain')
    op.drop_column('blockchains', 'blockchain')
    op.drop_column('alerts', 'blockchain')
    # ### end Alembic commands ###


def upgrade_stats():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stat_netspace_size', sa.Column('blockchain', sa.String(length=64), nullable=True))
    op.add_column('stat_time_to_win', sa.Column('blockchain', sa.String(length=64), nullable=True))
    op.add_column('stat_total_chia', sa.Column('blockchain', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###

    # Update existing rows with default 'chia' blockchain
    conn = op.get_bind()
    conn.execute(text("update stat_netspace_size set blockchain = 'chia'",{}))
    conn.execute(text("update stat_time_to_win set blockchain = 'chia'",{}))
    conn.execute(text("update stat_total_chia set blockchain = 'chia'",{}))

def downgrade_stats():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stat_total_chia', 'blockchain')
    op.drop_column('stat_time_to_win', 'blockchain')
    op.drop_column('stat_netspace_size', 'blockchain')
    # ### end Alembic commands ###


def upgrade_chiadog():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('blockchain', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###
    
    # Update existing rows with default 'chia' blockchain
    conn = op.get_bind()
    conn.execute(text("update notification set blockchain = 'chia'",{}))


def downgrade_chiadog():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notification', 'blockchain')
    # ### end Alembic commands ###
