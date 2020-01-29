"""
Extrapolate info from the checkout dictionary used in the basket of the webapp.
"""

def _parse_item(item_dict: dict) -> dict:
    """
    Item dictionaries are found in the Python list checkout['basket']['items'].
    """
    return {
        'item_id': item_dict['id'],
        'item_price': item_dict['price']
    }


def parse_checkout(checkout_dict: dict):
    """
    Generator of one dictionary per item bought in the webapp.
    """
    email = checkout_dict['email']
    for item in checkout_dict['basket']['items']:
        this_dict = _parse_item(item)
        this_dict['user_email'] = email
        yield this_dict
