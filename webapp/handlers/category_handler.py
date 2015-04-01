from tornado.gen import coroutine
from itertools import zip_longest

from .handler_base import ShopHandler

class CategoryHandler(ShopHandler):
    def __grouper(self, iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    def get_template_namespace(self):
        return {
            'grouper': self.__grouper
        }

    @coroutine
    def get(self, name, page):
        categories = yield self._get_json(
            'catalog/category/%s' % name,
            page=int(page) if page else 0,
            size=self.config.ITEMS_PER_PAGE)

        self.render(
            'category.html',
            categories=self.config.CATEGORIES,
            items=categories['items'],
            page=categories['page'],
            items_per_page=self.config.ITEMS_PER_PAGE,
            total=categories['total'],
            name=categories['name'])
