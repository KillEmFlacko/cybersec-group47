import sqlalchemy
from sqlalchemy.dialects.postgresql import BIGINT, CHAR, TIMESTAMP, DATE

metadata = sqlalchemy.MetaData()

contacts = sqlalchemy.Table(
    'ContactEvent',
    metadata,
    sqlalchemy.Column('id', CHAR, primary_key=True),
    sqlalchemy.Column('ephid1', CHAR),
    sqlalchemy.Column('ephid2', CHAR),
    sqlalchemy.Column('created_timestamp', TIMESTAMP),
)

shares = sqlalchemy.Table(
    'Share',
    metadata,
    sqlalchemy.Column('id', BIGINT, primary_key=True),
    sqlalchemy.Column('contact_id', CHAR),
    sqlalchemy.Column('x', CHAR),
    sqlalchemy.Column('y', CHAR),
)

infects = sqlalchemy.Table(
    'infect',
    metadata,
    sqlalchemy.Column('id', BIGINT, primary_key=True),
    sqlalchemy.Column('skt', CHAR),
    sqlalchemy.Column('nonce', CHAR),
    sqlalchemy.Column('created_date', DATE),
    sqlalchemy.Column('start_date', DATE),
)
