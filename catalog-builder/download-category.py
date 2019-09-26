import argparse
import requests
import xmltodict
import json
import yaml
from requests.adapters import HTTPAdapter
from functools import reduce
from itertools import islice, chain
import os
from xml.parsers.expat import ExpatError


def dot_field(input_dict, input_key):
    return reduce(lambda d, k: d.get(k) if d else None, input_key.split("."), input_dict)


def search_result(query, session, pages):
    for page in range(pages):
        params = {
            'api_key': API_KEY,
            'method': 'flickr.photos.search',
            'license': '1,2,4,5',
            'content_type': '1',
            'per_page': '500',
            'page': str(page + 1),
            'sort': 'relevance',
            'text': query
        }

        response = session.get('https://api.flickr.com/services/rest/', params=params)
        response_xml = xmltodict.parse(response.text)
        photos_xml = dot_field(response_xml, 'rsp.photos.photo')

        for xml in photos_xml or []:
            yield {
                'id': xml['@id'],
                'title': xml['@title']
            }


def filter_unfavorable(photos, session, threshold):
    def fav_count(photo_id):
        params = {
            'api_key': API_KEY,
            'method': 'flickr.photos.getFavorites',
            'per_page': '50',
            'photo_id': photo_id
        }
        response = session.get('https://api.flickr.com/services/rest/', params=params)
        try:
            response_xml = xmltodict.parse(response.text)
            return len(dot_field(response_xml, 'rsp.photo.person') or [])
        except ExpatError:
            # We have seen some weird xml error:
            # xml.parsers.expat.ExpatError: not well-formed (invalid token): line 20, column 81
            return 0

    for photo in photos:
        count = fav_count(photo['id'])
        if count >= threshold:
            photo['favs'] = count
            yield photo


def with_info(photos, session):
    for photo in photos:
        params = {
            'api_key': API_KEY,
            'method': 'flickr.photos.getInfo',
            'photo_id': photo['id']
        }

        response = session.get('https://api.flickr.com/services/rest/', params=params)
        response_xml = xmltodict.parse(response.text)
        info = dot_field(response_xml, 'rsp.photo') or {}

        photo['info'] = {
            'owner': {
                'id': dot_field(info, 'owner.@nsid'),
                'username': dot_field(info, 'owner.@username'),
                'realname': dot_field(info, 'owner.@realname')
            },
            'title': dot_field(info, 'title'),
            'description': dot_field(info, 'description'),
            'tags': [dot_field(tag, '#text') for tag in dot_field(info, 'tags.tag') or []] if type(
                dot_field(info, 'tags.tag')) == list else [dot_field(info, 'tags.tag.#text')]
        }

        # Change [None] values to empty list, [None] values will result in 500 error codes is send to the shop-api
        if photo['info']['tags'][0] is None:
            photo['info']['tags'] = []

        yield photo


def with_sizes(photos, session):
    for photo in photos:
        params = {
            'api_key': API_KEY,
            'method': 'flickr.photos.getSizes',
            'photo_id': photo['id']
        }

        response = session.get('https://api.flickr.com/services/rest/', params=params)
        response_xml = xmltodict.parse(response.text)
        sizes = dot_field(response_xml, 'rsp.sizes.size') or []

        photo['sizes'] = {
            dot_field(size, '@label'): {
                'width': dot_field(size, '@width'),
                'height': dot_field(size, '@height'),
                'source': dot_field(size, '@source'),
                'url': dot_field(size, '@url')
            }
            for size in sizes}

        yield photo


def main(args):
    session = requests.Session()
    session.mount('https://api.flickr.com/', HTTPAdapter(max_retries=10))

    with open(args.searches, 'r') as stream:
        config = yaml.safe_load(stream)
        for category in config['categories']:
            for (category_name, category_config) in category.items():
                print(category_config['keywords'])

                all_photos = chain(*[search_result(s, session, args.max_pages) for s in category_config['keywords']])
                usable_photos = filter_unfavorable(all_photos, session, args.fav_threshold)
                capped_photos = islice(usable_photos, 0, args.max_images)
                info_photos = with_info(capped_photos, session)
                photos = with_sizes(info_photos, session)

                destination_file = os.path.join(args.dest, '%s.json' % category_name)

                with open(destination_file, 'w', encoding='utf-8') as output_file:
                    for idx, photo in enumerate(photos):
                        output_file.write(json.dumps(photo))
                        output_file.write('\n')

                print('Written %d photos for category %s.' % (idx+1, category_name))


def parse_args():
    parser = argparse.ArgumentParser(
        description='Create a JSON description of a set of images retrieved from the Flickr API based on keyword searches.')
    parser.add_argument('--key', '-k', metavar='API_KEY', type=str, required=True, help='The Flickr API key to use.')
    parser.add_argument('--dest', '-d', metavar='DEST', type=str, help='The output directory to '
                                                                       'store the jsons',
                        default="catalog-builder/categories")
    parser.add_argument('--searches', '-s', metavar='SEARCH_KEYWORD', type=str, required=True, default='categories.yml',
                        help='Yaml file containing the categories and keywords to search for.')
    parser.add_argument('--fav-threshold', '-t', metavar='FAVOURITES_THRESHOLD', type=int, default=30,
                        help='The number of stars (favourites) an image must have acquired for it to be included in the result.')
    parser.add_argument('--max-images', '-m', metavar='MAX_IMAGES', type=int, default=1000,
                        help='The maximum number of images to add to the result.')
    parser.add_argument('--max-pages', '-p', metavar='MAX_PAGES', type=int, default=2,
                        help='The maximum number of result pages to request.')
    return parser.parse_args()


if __name__ == '__main__':
    global API_KEY
    args = parse_args()
    API_KEY = args.key
    main(args)
