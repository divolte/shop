# Generating large data sets

## How to

Idea is to use Apache Bench to fire events to divolte to simulate users.
Divolte is configured to write to HDFS if the json endpoint is used.

The following command lets apache bench fire custom requests to that json endpoint:

```
ab -c 5 -n 1000 -p postdata.json -T application/json 'http://localhost:8290/json?p=0:is8tiwk4:GKv5gCc5TtrvBTs9bXfVD8KIQ3oO~sEg'
```

The postdata.json file contains the POST data that is used. Something like this:
```
{"session_id": "0:is8tiwk4:XLEUVj9hA6AXRUOp2zuIdUpaeFOC~7AU", "event_id": "AruZ~Em0WNlAnbyzVmwM~GR0cMb6Xl9s", "is_new_party": true,	"is_new_session": true,	"client_timestamp_iso": "2018-08-24T13:29:39.412+02:00", "event_type": "preview", "parameters": {"item_id": "123456768"}}
```

The idea is to generate this postdata file by querying elasticsearch to find out the products and categories which are available:

```
http://localhost:9200/catalog/_search?_source_includes=id,categories&size=100
```

## TODO
Generate postdata (add location)
Use the 5 known event types
