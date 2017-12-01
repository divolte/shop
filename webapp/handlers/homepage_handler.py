from tornado.gen import coroutine, with_timeout, TimeoutError
from tornado.httpclient import HTTPRequest,AsyncHTTPClient
from tornado.escape import json_decode
from datetime import timedelta

from tornado.web import HTTPError

from .handler_base import ShopHandler

class HomepageHandler(ShopHandler):
    @coroutine
    def get(self):
        try:
            http = AsyncHTTPClient()
            request = HTTPRequest(url=self.config.BANDIT_URL, method='GET')
            response = yield with_timeout(timedelta(milliseconds=15), http.fetch(request))
            winner = json_decode(response.body)
            top_item = yield self._get_json('catalog/item/%s' % winner)
        except (OSError, ConnectionRefusedError, TimeoutError, HTTPError):
            top_item = None

        self.render(
            'index.html',
            top_item=top_item)
