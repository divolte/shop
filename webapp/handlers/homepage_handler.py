from .handler_base import ShopHandler

class HomepageHandler(ShopHandler):
    def get(self):
        self.render('index.html', categories=self.config.CATEGORIES)
