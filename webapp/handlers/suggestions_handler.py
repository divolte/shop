import logging

from tornado.gen import coroutine
from tornado.httpclient import HTTPError

from .handler_base import ShopHandler


class SuggestionsHandler(ShopHandler):

    @coroutine
    def get(self):
        log = logging.getLogger('SearchHandler')
        try:
            return ["a", "b", "c"]
        except HTTPError as e:
            log.error("Suggestions not found")
            raise e

    @coroutine
    def suggest(self):
        #Doing this in js code in header.html
        pass
