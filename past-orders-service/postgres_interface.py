import sqlalchemy
import pandas as pd


engine = sqlalchemy.create_engine('postgresql://postgres:password@localhost:5432/postgres')


def insert_item_record_query(record: dict) -> str:
    """
    Generate a query to insert the record of an item bought into the pastorders table.
    """
    keys, values = zip(*record.items())
    query_str = "INSERT INTO pastorders {} VALUES {}".format(keys, values)
    return query_str


def insert_item_records(records: list, engine: sqlalchemy.engine.base.Engine):
    """
    Insert a row per item bought in the pastorders table
    """
    with engine.connect() as connection:
        for record in records:
            response = connection.execute(insert_item_record_query(record))
            yield response
