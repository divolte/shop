import argparse
import logging

from flask import Flask

from recommender import BanditModel


class Bandit(Flask):
    """Bandit API that serves items from Redis.

    Bayesian bandit API that serves the photo with highest estimated click
    rate. Hits (=clicks) and misses (=impressions without clicks) are
    registered by the top-pick-consumer and saved in Redis.

    More info: https://lazyprogrammer.me/bayesian-bandit-tutorial/

    :param model: recommender.BanditModel
    :param kwargs: Keyword arguments for Flask superclass
    """
    def __init__(self, model, **kwargs):

        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.add_url_rule('/item', view_func=self.item, methods=['GET'])

    def item(self):
        return self.model.item()


def main(args):
    redis_host, redis_port = args.redis.split(':')
    model = BanditModel(redis_host, redis_port)
    bandit = Bandit(model, import_name=__name__)
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
