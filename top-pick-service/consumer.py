import argparse
import io
import json
import logging
import pprint

import avro.io
import avro.schema
import numpy
import redis
import requests
from kafka import KafkaConsumer

NUM_ITEMS = 4
REFRESH_INTERVAL = 10

EXPERIMENT_COUNT_KEY = b'experiments'
ITEM_HASH_KEY = b'items'

CLICK_KEY_PREFIX = b'c|'
IMPRESSION_KEY_PREFIX = b'i|'

def main(args):
    logger = logging.getLogger(__name__)
    logger.info('Starting consumer app')
    global es_host, es_port, redis_client
    es_host, es_port = args.elasticsearch.split(':')
    redis_host, redis_port = args.redis.split(':')
    redis_client = redis.StrictRedis(host=redis_host, port=int(redis_port))

    refresh_items()
    start_consumer(args)

def start_consumer(args):
    # Load the Avro schema used for serialization.
    schema = avro.schema.Parse(open(args.schema).read())

    # Create a Kafka consumer and Avro reader. Note that
    # it is trivially possible to create a multi process
    # consumer.
    logger = logging.getLogger(__name__)
    logger.info('Starting Kafka consumer on topic %s, client %s, group %s,'
                'brokers %s', args.topic, args.client, args.group,
                 args.brokers)
    consumer = KafkaConsumer(args.topic, client_id=args.client, group_id=args.group, bootstrap_servers=args.brokers)
    logger.info('Using schema\n%s', schema)
    reader = avro.io.DatumReader(schema)
    logger.info('Found topics %s', consumer.topics())

    # Consume messages.
    while True:
        # TODO: Is while True needed?
        for message in consumer:
            handle_event(message, reader)

def ascii_bytes(id):
    return bytes(id, 'us-ascii')

def handle_event(message, reader):
    # Decode Avro bytes into a Python dictionary.
    message_bytes = io.BytesIO(message.value)
    decoder = avro.io.BinaryDecoder(message_bytes)
    event = reader.read(decoder)

    logger = logging.getLogger(__name__)
    logger.info('Got message %s, event %s', message, event)
    # Event logic.
    if 'pageView' == event['eventType'] and event['productId'] is not None:

        logger.info('Got click for  %s', event['productId'])
        # Register a click.
        redis_client.hincrby(
            ITEM_HASH_KEY,
            CLICK_KEY_PREFIX + ascii_bytes(event['productId']),
            1)
    elif 'top_pick' == event['source'] and 'impression' == event['eventType']:
        logger.info('Got impresssion for  %s', event['productId'])
        # Register an impression and increment experiment count.
        p = redis_client.pipeline()
        p.incr(EXPERIMENT_COUNT_KEY)
        p.hincrby(
            ITEM_HASH_KEY,
            IMPRESSION_KEY_PREFIX + ascii_bytes(event['productId']),
            1)
        experiment_count, ignored = p.execute()

        if experiment_count == REFRESH_INTERVAL:
            refresh_items()

def refresh_items():
    logger = logging.getLogger(__name__)
    logger.info('Refreshing items')
    # Fetch current model state. We convert everything to str.
    current_item_dict = redis_client.hgetall(ITEM_HASH_KEY)
    logger.info('Items from Redis: %s', current_item_dict)
    current_items = numpy.unique([k[2:] for k in current_item_dict.keys()])

    # Fetch random items from ElasticSearch. Note we fetch more than we need,
    # but we filter out items already present in the current set and truncate
    # the list to the desired size afterwards.
    random_items = [
        ascii_bytes(item)
        for item in random_item_set(NUM_ITEMS + NUM_ITEMS - len(current_items) // 2)
        if not item in current_items][:NUM_ITEMS - len(current_items) // 2]
    logger.info('Total random items: %s', random_items)
    
    def _get_item(key):
        try:
            return int(current_item_dict[key])
        except (KeyError):
            return int(1)

    # Draw random samples.
    samples = [
        numpy.random.beta(
            _get_item(CLICK_KEY_PREFIX + item),
            _get_item(IMPRESSION_KEY_PREFIX + item))
        for item in current_items]

    # Select top half by sample values. current_items is conveniently
    # a Numpy array here.
    survivors = current_items[numpy.argsort(samples)[len(current_items) // 2:]]
    logger.info('Survivors from current: %s', survivors)

    # New item set is survivors plus the random ones.
    new_items = numpy.concatenate([survivors, random_items])
    logger.info('New items: %s', new_items)

    # Update model state to reflect new item set. This operation is atomic
    # in Redis.
    logger.info('Updating Redis')
    p = redis_client.pipeline(transaction=True)
    p.set(EXPERIMENT_COUNT_KEY, 1)
    p.delete(ITEM_HASH_KEY)
    for item in new_items:
        p.hincrby(ITEM_HASH_KEY, CLICK_KEY_PREFIX + item, 1)
        p.hincrby(ITEM_HASH_KEY, IMPRESSION_KEY_PREFIX + item, 1)
    p.execute()

def random_item_set(count):
    query = {
        "query": {
            "function_score" : {
            "query" : { "match_all": {} },
                "random_score" : {}
            }
        }, "size": count
    }

    headers = {'Content-type': 'application/json'}
    result = requests.get('http://%s:%s/catalog/_search' % (es_host, es_port), data=json.dumps(query), headers=headers)
    logger = logging.getLogger(__name__)
    try:
        res = [hit['_source']['id'] for hit in result.json()['hits']['hits']]
        logger.info('Got random items from ES: %s', res)
        return res
    except (KeyError):
        logger.warning('Could not find hits for query %s @ %s:%s',
                       query, es_host, es_port)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result.json())
        return []

def parse_args():
    def utf8_bytes(s):
        return bytes(s, 'utf-8')

    parser = argparse.ArgumentParser(description='Runs the consumer.')
    parser.add_argument('--redis', '-r', metavar='REDIS_HOST_PORT', type=str, required=False, default='localhost:6379', help='Redis hostname + port.')
    parser.add_argument('--schema', '-s', metavar='SCHEMA', type=str, required=True, help='Avro schema of Kafka messages.')
    parser.add_argument('--client', '-c', metavar='CLIENT_ID', type=utf8_bytes, required=True, help='Kafka client id.')
    parser.add_argument('--group', '-g', metavar='GROUP_ID', type=utf8_bytes, required=True, help='Kafka consumer group id.')
    parser.add_argument('--brokers', '-b', metavar='KAFKA_BROKERS', type=str, nargs="+", help='A list of Kafka brokers (host:port).', default=['localhost:9092'])
    parser.add_argument('--topic', '-t', metavar='TOPIC', type=str, required=False, default='divolte', help='Kafka topic.')
    parser.add_argument('--elasticsearch', '-e', metavar='ELASTIC_SEARCH_HOST_PORT', type=str, required=False, default='localhost:9200', help='The ElasticSearch instance to connect to (host:port).')
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(parse_args())
