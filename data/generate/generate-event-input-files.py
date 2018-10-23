import random
from time import time
from datetime import datetime, timezone, timedelta
import base36
import secrets
from elasticsearch import Elasticsearch
import pandas as pd
import json
import requests
from collections import Counter

def generate_divolte_id():
    ts = int(round(time() * 1000))
    b = base36.dumps(ts)
    s = secrets.token_urlsafe(24)
    return "0:{timestamp}:{id}".format(timestamp=b, id = s)

def generate_event_id():
    s = secrets.token_urlsafe(36)
    return "0:{id}".format(id = s)


def get_items():
    es = Elasticsearch()
    products = es.search(index='catalog', _source_include=['id','categories'], size=200)
    return [{'item_id': int(product['_source']['id'])} for product in products['hits']['hits']]

def get_events(dt):
    timeframe=random.uniform(1,24)
    pdf = pd.date_range(start=dt+timedelta(hours=-timeframe), end=dt, freq='S').to_frame()
    sampled = pdf.sample(frac=random.uniform(1, 200)/pdf.count())
    sampled.columns = ['ts']
    sorted = sampled.sort_values('ts')

    # add a column containing previous timestamp
    combined =  pd.concat([sorted,
                           sorted.transform(lambda x:x.shift(1))]
                          ,axis=1)
    combined.columns = ['ts','prev_ts']

    # create the new session column
    combined['is_new_party'] = (combined['prev_ts'].isnull())

    # create the new session column
    combined['is_new_session'] = ((combined['prev_ts'].isnull()) | ((combined['ts']
                                - combined['prev_ts'])>=timedelta(seconds=30*60)))

    # create the session_id
    combined['increment'] = combined['is_new_session'].cumsum()
    combined['session_id'] = combined['is_new_session'].groupby(combined['increment']).transform(lambda x:generate_divolte_id())

    combined['event_type'] = 'preview'
    combined['event_id'] = combined['event_type'].transform(lambda x: generate_event_id())
    combined['client_timestamp_iso'] = combined['ts'].transform(lambda x: x.replace(tzinfo=timezone(offset=timedelta(hours=2))).isoformat())

    serie = pd.Series(get_items()[:combined['ts'].count()])
    combined['parameters'] = serie.values

    return combined[['session_id', 'event_id', 'is_new_party', 'is_new_session', 'client_timestamp_iso', 'event_type', 'parameters']].to_json(orient='records')

if __name__ == "__main__":
    responses = Counter()
    for i in range(0,100):
        party = generate_divolte_id()
        for j in range(0,int(random.uniform(1,6))):
            data = get_events(datetime.now()-timedelta(days=j))
            for event in json.loads(data):
                response = requests.post('http://localhost:8290/json?p={party}'.format(party=party), json=event)
                print('POST status %d' % response.status_code)
                responses.update([response.status_code])

    print('\nSummary:')
    for status, count in responses.items():
        print('\t%d times status code %d' % (count,status))
