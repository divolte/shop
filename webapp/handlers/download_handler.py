from tornado.gen import coroutine

from .handler_base import ShopHandler

class DownloadHandler(ShopHandler):
    @coroutine
    def get(self, id):
        checkout = yield self._get_json('checkout/completed/%s' % id)
        self.render(
            'download.html',
            categories=self.config.CATEGORIES,
            items=checkout['basket']['items'])
