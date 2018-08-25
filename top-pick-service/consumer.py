import argparse
import io
import logging

import avro.io
import avro.schema
import numpy as np
import redis
import requests
from kafka import KafkaConsumer

NUM_ITEMS = 4
REFRESH_INTERVAL = 10

EXPERIMENT_COUNT_KEY = b'experiments'
ITEM_HASH_KEY = b'items'

CLICK_KEY_PREFIX = b'c|'
IMPRESSION_KEY_PREFIX = b'i|'


class Consumer:

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


class Model:

    def __init__(self, elastic_host, elastic_port, redis_host, redis_port,
                 prior=1):
        self.elastic_host = elastic_host
        self.elastic_port = elastic_port
        self.redis = redis.StrictRedis(redis_host, redis_port)
        self.logger = logging.getLogger(__name__)
        self.prior = prior
        self.n_items_ = 0

    def click(self, product_id):
        self.redis.hincrby(
            ITEM_HASH_KEY,
            CLICK_KEY_PREFIX + ascii_bytes(product_id),
            1
        )

    def impression(self, product_id):
        p = self.redis.pipeline()
        p.incr(EXPERIMENT_COUNT_KEY)
        p.hincrby(
            ITEM_HASH_KEY,
            IMPRESSION_KEY_PREFIX + ascii_bytes(product_id),
            1
        )
        experiment_count, _ = p.execute()

        if experiment_count == REFRESH_INTERVAL:
            self.logger.info('Starting new experiment at experiment count %s',
                             experiment_count)
            self.refresh_items()

    def refresh_items(self):
        items, clicks, impressions = self._query_current()
        top_items = self._get_top(items, clicks, impressions, len(items) // 2)
        n_random = NUM_ITEMS - len(top_items)
        random = self._query_random_items(2*n_random)
        random_items = random[~np.in1d(random, top_items)][:n_random]
        new_items = np.concatenate([top_items, random_items])
        self.logger.info('Got %s new items from %s current (Redis) items and '
                         '%s random (Elastic Search) items.',
                         len(new_items), len(items), len(random))
        self._start_new_experiment(new_items)

    def _query_current(self):
        statistics = self.redis.hgetall(ITEM_HASH_KEY)
        items = np.unique([k[2:] for k in statistics.keys()])
        clicks = np.array([
            int(statistics.get(CLICK_KEY_PREFIX + k, 0)) for k in items
        ])
        impressions = np.array([
            int(statistics.get(IMPRESSION_KEY_PREFIX + k, 0)) for k in items
        ])
        return items, clicks, impressions

    def _get_top(self, items, clicks, impressions, n_top):
        p_success = self._sample_success_rate(clicks, impressions)
        return items[p_success.argsort()[-n_top:]]

    def _sample_success_rate(self, clicks, impressions):
        """Sample from Bernoulli likelihood with non-informative prior."""
        # TODO: This isn't that informative with current low experiment count.
        hits = clicks + self.prior
        misses = np.maximum(impressions - clicks, 0) + self.prior
        return np.random.beta(hits, misses)

    def _query_random_items(self, count):
        query = {
            "query": {
                "function_score": {
                    "query": {"match_all": {}},
                    "random_score": {},
                }
            },
            "size": count,
        }
        url = f'http://{self.elastic_host}:{self.elastic_port}/catalog/_search'
        result = requests.get(url, json=query)
        try:
            return np.array([
                ascii_bytes(hit['_source']['id'])
                for hit in result.json()['hits']['hits']
            ])
        except KeyError:
            # Elastic Search probably gives a 404.
            self.logger.warning('Could not find hits in Elastic:\n%s',
                                result.json())
            return np.array([])

    def _start_new_experiment(self, new_items):
        p = self.redis.pipeline(transaction=True)
        p.set(EXPERIMENT_COUNT_KEY, 1)
        p.delete(ITEM_HASH_KEY)
        for item in new_items:
            p.hincrby(ITEM_HASH_KEY, CLICK_KEY_PREFIX + item, 1)
            p.hincrby(ITEM_HASH_KEY, IMPRESSION_KEY_PREFIX + item, 1)
        p.execute()
        self.n_items_ = len(new_items)


def ascii_bytes(id_):
    return bytes(id_, 'us-ascii')


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
    model = Model(elastic_host, elastic_port, redis_host, redis_port)
    model.refresh_items()
    consumer = Consumer(args.schema, model)
    consumer.start(args.topic, args.client, args.group, args.brokers)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(parse_args())
