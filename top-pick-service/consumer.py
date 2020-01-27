import argparse
import io
import logging

import avro.io
import avro.schema
import numpy as np
import redis
import requests
from kafka import KafkaConsumer

from recommender import ConsumerModel
from config import (
    ITEM_HASH_KEY, CLICK_KEY_PREFIX, IMPRESSION_KEY_PREFIX,
    EXPERIMENT_COUNT_KEY
)


class Consumer:
    """Consumer that connects to Kafka and forwards events.

    :param schema_path: Path to schema of AVRO events
    :param model: model instance to forward events to
    """
    def __init__(self, schema_path, model):
        with open(schema_path, 'r') as f:
            schema = avro.schema.Parse(f.read())
        self.reader = avro.io.DatumReader(schema)
        self.model = model
        self.logger = logging.getLogger(__name__)

    def start(self, topic, client_id, group_id, bootstrap_servers):
        consumer = KafkaConsumer(topic, client_id=client_id, group_id=group_id,
                                 bootstrap_servers=bootstrap_servers)
        for message in consumer:
            event = self._parse_message(message)
            self._handle_event(event)

    def _parse_message(self, message):
        message_bytes = io.BytesIO(message.value)
        decoder = avro.io.BinaryDecoder(message_bytes)
        return self.reader.read(decoder)

    def _handle_event(self, event):
        is_top_pick = 'top_pick' == event['source']
        if is_top_pick and 'pageView' == event['eventType']:
            self.logger.info('Got click for product %s', event['productId'])
            self.model.click(event['productId'])
        elif is_top_pick and 'impression' == event['eventType']:
            self.logger.info('Got impression for product %s',
                             event['productId'])
            self.model.impression(event['productId'])
        elif 'home' == event['pageType'] and self.model.n_items_ == 0:
            self.logger.info('Model does not have any items, refreshing...')
            self.model.refresh_items()
        else:
            pass


def parse_args():

    def utf8_bytes(s):
        return bytes(s, 'utf-8')

    parser = argparse.ArgumentParser(description='Runs the consumer.')
    parser.add_argument('--redis', '-r', metavar='REDIS_HOST_PORT', type=str,
                        required=False, default='localhost:6379',
                        help='Redis hostname + port.')
    parser.add_argument('--schema', '-s', metavar='SCHEMA', type=str,
                        required=True, help='Avro schema of Kafka messages.')
    parser.add_argument('--topic', '-t', metavar='TOPIC', type=str,
                        required=False, default='divolte', help='Kafka topic.')
    parser.add_argument('--client', '-c', metavar='CLIENT_ID', type=utf8_bytes,
                        required=True, help='Kafka client id.')
    parser.add_argument('--group', '-g', metavar='GROUP_ID', type=utf8_bytes,
                        required=True, help='Kafka consumer group id.')
    parser.add_argument('--brokers', '-b', metavar='KAFKA_BROKERS', type=str,
                        nargs="+", help='A list of Kafka brokers (host:port).',
                        default=['localhost:9092'])
    parser.add_argument('--elasticsearch', '-e',
                        metavar='ELASTIC_SEARCH_HOST_PORT', type=str,
                        required=False, default='localhost:9200',
                        help='The ElasticSearch instance to connect to (host:port).')
    return parser.parse_args()


def main(args):
    elastic_host, elastic_port = args.elasticsearch.split(':')
    redis_host, redis_port = args.redis.split(':')
    model = ConsumerModel(elastic_host, elastic_port, redis_host, redis_port)
    model.refresh_items()
    consumer = Consumer(args.schema, model)
    consumer.start(args.topic, args.client, args.group, args.brokers)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(parse_args())
