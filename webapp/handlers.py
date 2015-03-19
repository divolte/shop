from tornado import web
from tornado.gen import coroutine
from tornado.httpclient import HTTPRequest,AsyncHTTPClient
from tornado.escape import json_decode
import config

class HomepageHandler(web.RequestHandler):
    def get(self):
        self.render('index.html', categories=config.CATEGORIES)

class CategoryHandler(web.RequestHandler):
    @coroutine
    def get(self, name, page):
        http = AsyncHTTPClient()
        category_request = HTTPRequest(
            url='%s/catalog/category/%s?page=%d&size=20' % (config.API_URL, name, int(page) if page else 0),
            method='GET')

        category_response = yield http.fetch(category_request)
        categories = json_decode(category_response.body)

        self.render('category.html', categories=config.CATEGORIES, items=categories['items'])

class ProductHandler(web.RequestHandler):
    @coroutine
    def get(self, id):
        http = AsyncHTTPClient()
        product_request = HTTPRequest(
            url='%s/catalog/item/%s' % (config.API_URL, id),
            method='GET')

        product_response = yield http.fetch(product_request)
        item = json_decode(product_response.body)

        self.render('product.html', categories=config.CATEGORIES, item=item)
