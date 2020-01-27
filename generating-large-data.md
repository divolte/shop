# Generating large data sets

## How to

Idea is to fire events to divolte to simulate users.
Divolte is configured to write to HDFS if the json endpoint is used.

The following command fires custom requests to that json endpoint:

```
curl -XPOST -d postdata.json -H 'Content-Type=application/json' 'http://localhost:8290/json?p=0:is8tiwk4:GKv5gCc5TtrvBTs9bXfVD8KIQ3oO~sEg'
```

The postdata.json file contains the POST data that is used. Something like this:
```
{"session_id": "0:is8tiwk4:XLEUVj9hA6AXRUOp2zuIdUpaeFOC~7AU", "event_id": "AruZ~Em0WNlAnbyzVmwM~GR0cMb6Xl9s", "is_new_party": true,	"is_new_session": true,	"client_timestamp_iso": "2018-08-24T13:29:39.412+02:00", "event_type": "preview", "parameters": {"item_id": "123456768"}}
```

The idea is to generate this postdata by querying elasticsearch to find out the products and categories which are available:

```
http://localhost:9200/catalog/_search?_source_includes=id,categories&size=100
```

## Usage
```
workon shop-gen-py3
cd data/generate
pip install -r requirements.txt
python generate-event-input-files.py
```

## TODO
Only preview event is currently implemented: Use the 5 known event types
Verify the statistical distribution of events to see if it really mimics users

90MB after 1st time 1000 parties
176MB after 2nd time 1000 parties

This is only for preview events.

ToDo:
- impression event
- addToBasket event
- removeFromBasket event
- default pageView events
	- localhost:9011
	- localhost:9011/category/animals (other categories: cars, flowers, architecture, landscape, cities, nautical)
	- localhost:9011/category/animals/1 (page 2)
	- localhost:9011/category/animals/1 has the add to basket button
	- localhost:9011/product/<id> also has the add to basket button and a back to overview
	- localhost:9011/basket (from add to basket button -> take me to checkout)
	- localhost:9011/basket has the trash button (removeFromBasket event)
	- localhost:9011/checkout (from basket)
	- localhost:9011/download/<uuid> (after captha) can be bookmarked
	- localhost:9011/search?q=tiger
	- localhost:9011/search?q=tiger&page=1 (page 2 etc.)