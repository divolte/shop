import argparse
import logging

import numpy as np
import redis
from flask import abort
from flask import Flask


ITEM_HASH_KEY = 'items'
CLICK_KEY_PREFIX = b'c|'
IMPRESSION_KEY_PREFIX = b'i|'


class Bandit(Flask):
    """Bandit API that serves items from Redis.

    Bayesian bandit API that serves the photo with highest estimated click
    rate. Hits (=clicks) and misses (=impressions without clicks) are
    registered by the top-pick-consumer and saved in Redis.

    More info: https://lazyprogrammer.me/bayesian-bandit-tutorial/

    :param redis_host: Redis host
    :param redis_port: Redis port
    :param prior: Uninformative prior for number of hits and misses
    :param kwargs: Keyword arguments for Flask superclass
    """
    def __init__(self, redis_host, redis_port, prior=1, **kwargs):

        super().__init__(**kwargs)

        self.log = logging.getLogger(__name__)
        self.add_url_rule('/item', view_func=self.item, methods=['GET'])
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port)
        self.prior = prior

    def item(self):
        items, clicks, impressions = self._query_current()
        theta = self._sample_success_rate(clicks, impressions)
        if len(theta) > 0:
            winner = items[theta.argmax()]
            self.log.info('Found winner %s out of %d items',
                          winner, len(items))
            return winner
        else:
            self.log.warning('Did not find any winners out of %d items.',
                             len(items))
            return abort(404)

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

    def _sample_success_rate(self, clicks, impressions):
        """Sample from Bernoulli likelihood with non-informative prior."""
        hits = clicks + self.prior
        misses = np.maximum(impressions - clicks, 0) + self.prior
        return np.random.beta(hits, misses)


def main(args):
    redis_host, redis_port = args.redis.split(':')
    bandit = Bandit(redis_host, redis_port, import_name=__name__)
    bandit.run(args.address, int(args.port), args.debug)


def parse_args():
    parser = argparse.ArgumentParser(description='Runs the webapp.')
    parser.add_argument('--port', '-p', metavar='PORT', type=int,
                        required=False, default=8989,
                        help='The TCP port to listen on for HTTP requests.')
    parser.add_argument('--address', '-a', metavar='BIND_ADDRESS', type=str,
                        required=False, default='127.0.0.1',
                        help='The address to bind on.')
    parser.add_argument('--redis', '-r', metavar='REDIS_HOST_PORT', type=str,
                        required=False, default='localhost:6379',
                        help='Redis hostname + port.')
    parser.add_argument('--debug', '-d', dest='debug', action='store_true',
                        required=False, default=False,
                        help='Run in debug mode.')
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(parse_args())
