""" Insert records into the transactions PostgreSQL database, with sqlalchemy."""
import sqlalchemy


def get_engine(username, password):
    """ Return a sqlalchemy engine with the given username and password. """
    address = 'postgresql://{}:{}@localhost:5432/checkouts'.format(username, password)
    return sqlalchemy.create_engine(address)


def insert_item_record_query(record: dict) -> str:
    """
    Generate a query to insert the record of an item bought into the pastorders table.
    """
    keys, values = zip(*record.items())
    query_str = "INSERT INTO completed_checkouts {} VALUES {}".format(keys, values)
    return query_str


def insert_item_records(records: list, engine: sqlalchemy.engine.base.Engine):
    """ Insert a row per item bought in the pastorders table. """
    with engine.connect() as connection:
        for record in records:
            _ = connection.execute(insert_item_record_query(record))
