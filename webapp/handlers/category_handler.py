from tornado.gen import coroutine
from itertools import zip_longest

from .handler_base import ShopHandler

class CategoryHandler(ShopHandler):
    @coroutine
    def get(self, name, page):
        categories = yield self._get_json(
            'catalog/category/%s' % name,
            page=int(page) if page else 0,
            size=self.config.ITEMS_PER_PAGE)

        self.render(
            'category.html',
            items=categories['items'],
            page=categories['page'],
            items_per_page=self.config.ITEMS_PER_PAGE,
            total=categories['total'],
            name=categories['name'])
