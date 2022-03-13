import sqlalchemy as sa

metadata = sa.MetaData()

ImagesTable = sa.Table(
    'images', metadata,
    sa.Column('p_hash', sa.VARCHAR, primary_key=True),
    sa.Column('avg_hash', sa.VARCHAR, nullable=False),
    sa.Column('image', sa.BLOB, nullable=False)
)
