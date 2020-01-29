"""
Bandit implementation with extra methods to interact with databases,
shared by the consumer and the bandit services.
"""
import logging

import requests
import redis
import numpy as np
from flask import abort

from config import (
    ITEM_HASH_KEY, CLICK_KEY_PREFIX, IMPRESSION_KEY_PREFIX,
    EXPERIMENT_COUNT_KEY, REFRESH_INTERVAL, NUM_ITEMS
)


class Model:
    """
    Base Bandit model that inspect the current status and samples
    click rates.

    Bayesian bandit API that serves the photo with highest estimated click
    rate. Hits (=clicks) and misses (=impressions without clicks) are
    registered by the top-pick-consumer and saved in Redis.

    More info: https://lazyprogrammer.me/bayesian-bandit-tutorial/

    :param redis_host: Redis host
    :param redis_port: Redis port
    :param prior: Uninformative prior for number of hits and misses
    """
    def __init__(self, redis_host, redis_port, prior=1):
        self.logger = logging.getLogger(str(self.__class__))
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port)
        self.prior = prior

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
        # TODO: not yet very informative with a low experiment count
        hits = clicks + self.prior
        misses = np.maximum(impressions - clicks, 0) + self.prior
        return np.random.beta(hits, misses)


class BanditModel(Model):
    """
    Bandit Model that returns recommendations from Redis.

    Bayesian bandit API that serves the photo with highest estimated click
    rate. Hits (=clicks) and misses (=impressions without clicks) are
    registered by the top-pick-consumer and saved in Redis.

    More info: https://lazyprogrammer.me/bayesian-bandit-tutorial/

    :param redis_host: Redis host
    :param redis_port: Redis port
    :param prior: Uninformative prior for number of hits and misses
    """
    def __init__(self, redis_host, redis_port, prior=1):
        self.logger = logging.getLogger(str(self.__class__))
        super().__init__(redis_host, redis_port, prior)

    def item(self):
        """
        Return the id of the recommended item.

        Return
        ------
        item_id: str
            id of the recommended item.
        """
        items, clicks, impressions = self._query_current()
        theta = self._sample_success_rate(clicks, impressions)
        if theta.size == 0:
            winner = items[theta.argmax()]
            self.logger.info(
                'Found winner %s out of %d items',
                winner, len(items)
            )
            return winner
        else:
            self.logger.warning(
                'Did not find any winners out of %d items.',
                len(items)
            )
            return abort(404)


class ConsumerModel(Model):
    """Model that saves clicks & impressions and generates new experiments.

    A new experiments consist of a sequence of impressions. In an experiment,
    the clicks and impressions are recorded for a set of items. At the end of
    each experiment, a subset of items get sampled by their estimated
    click-rate and combined with some random items to give a new experiment
    set.

    :param elastic_host: Elastic Search host
    :param elastic_port: Elastic Search port
    :param redis_host: Redis host
    :param redis_port: Redis port
    :param prior: Uninformative prior for number of hits and misses
    """

    def __init__(self, elastic_host, elastic_port, redis_host, redis_port,
                 prior=1):
        super().__init__(redis_host, redis_port, prior)
        self.elastic_host = elastic_host
        self.elastic_port = elastic_port
        self.logger = logging.getLogger(str(self.__class__))
        self.n_items_ = 0

    def click(self, product_id):
        """
        Increase the click counter for the given product.
        """
        self.redis.hincrby(
            ITEM_HASH_KEY,
            CLICK_KEY_PREFIX + ascii_bytes(product_id),
            1
        )

    def impression(self, product_id):
        """
        Increase the impression counter for the given product.
        """
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

    def _get_top(self, items, clicks, impressions, n_top):
        p_success = self._sample_success_rate(clicks, impressions)
        return items[p_success.argsort()[-n_top:]]

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
