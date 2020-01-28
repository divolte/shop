from tornado.gen import coroutine

from .handler_base import ShopHandler


class DownloadHandler(ShopHandler):
    @coroutine
    def get(self, id):
        checkout = yield self._get_json('checkout/completed/%s' % id)
        # checkout is ready to be consumed and stored in the database
        self.render(
            'download.html',
            items=checkout['basket']['items']
        )
