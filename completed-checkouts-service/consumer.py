"""
Main component of the toppick-consumer service.
"""
import argparse
import logging
import json

from kafka import KafkaConsumer

from .records_parser import parse_checkout
from .postgres_interface import insert_item_records, get_engine


class Consumer:
    """
    Consumer that connects to Kafka and forwards events.

    :param schema_path: Path to schema of AVRO events
    :param model: model instance to forward events to
    """
    def __init__(self, postgres_host, postgres_port):
        # self.reader = avro.io.DatumReader(schema)
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port
        self.logger = logging.getLogger(str(self.__class__))

    def start(self, topic, client_id, group_id, bootstrap_servers):
        consumer = KafkaConsumer(
            topic, client_id=client_id, group_id=group_id,
            bootstrap_servers=bootstrap_servers
        )
        for message in consumer:
            parsed_message = self._parse_message(message)
            store_outcome = self._store_checkout(parsed_message)
            self.logger.log('Checkout stored with output {}'.format(store_outcome))

    def _parse_message(self, message):
        self.logger.log('Parsing a message:')
        self.logger.log('Message: {}'.format(message.value.decode('utf-8')))
        json_dict = json.load(message.value)
        self.logger.log('Parser message: \n {}'.format(json_dict))
        return parse_checkout(json_dict)

    def _store_checkout(self, records):
        # TODO: find best practice to replace this
        engine = get_engine(self.postgres_host, self.postgres_port, 'psadmin', 'qwertyuiop')
        return insert_item_records(records, engine)


def parse_args():
    """ Ok Pylint, I am documenting this self-describing function. """
    def utf8_bytes(string):
        return bytes(string, 'utf-8')

    parser = argparse.ArgumentParser(description='Runs the consumer.')
    parser.add_argument(
        '--schema', '-s', metavar='SCHEMA', type=str,
        required=True, help='Avro schema of Kafka messages.'
    )
    parser.add_argument(
        '--topic', '-t', metavar='TOPIC', type=str,
        required=False, default='completed-checkout', help='Kafka topic.'
    )
    parser.add_argument(
        '--client', '-c', metavar='CLIENT_ID', type=utf8_bytes,
        required=True, help='Kafka client id.'
    )
    parser.add_argument(
        '--group', '-g', metavar='GROUP_ID', type=utf8_bytes,
        required=True, help='Kafka consumer group id.'
    )
    parser.add_argument(
        '--brokers', '-b', metavar='KAFKA_BROKERS', type=str,
        nargs="+", help='A list of Kafka brokers (host:port).',
        default=['localhost:9092']
    )
    parser.add_argument(
        '--postgres', '-e', metavar='POSTGRES_HOST_PORT', type=str,
        required=True, help='The PostgreSQL instance to connect to (host:port).',
        default='localhost:5432'
    )
    return parser.parse_args()


def main(args):
    """
    Parameters
    ----------
    args.postgres: str
    args.topic: str
    args.client: str
    args.group: str
    args.brokers: str
    """
    postgres_host, postgres_port = args.postgres.split(':')
    consumer = Consumer(postgres_host, postgres_port)
    consumer.start(args.topic, args.client, args.group, args.brokers)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(parse_args())
