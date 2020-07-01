import sqlalchemy
from sqlalchemy.dialects.postgresql import CHAR, BIGINT, DATE

metadata = sqlalchemy.MetaData()

infects = sqlalchemy.Table(
    'infect',
    metadata,
    sqlalchemy.Column('id', BIGINT, primary_key=True),
    sqlalchemy.Column('skt', CHAR),
    sqlalchemy.Column('nonce', CHAR),
    sqlalchemy.Column('created_date', DATE),
    sqlalchemy.Column('start_date', DATE),
)
