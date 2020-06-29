import sqlalchemy

metadata = sqlalchemy.MetaData()

contacts = sqlalchemy.Table(
    'contact-event',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.VARCHAR, primary_key=True),
    sqlalchemy.Column('ephid1', sqlalchemy.VARCHAR),
    sqlalchemy.Column('ephid2', sqlalchemy.VARCHAR),
    sqlalchemy.Column('created_timestamp', sqlalchemy.TIMESTAMP),
)
