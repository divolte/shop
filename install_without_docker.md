## Running without Docker

For developing its useful to start/stop the services individually.

### Dependencies when not using Docker

The shop and service are depended on the following components:

- Divolte-collector
- Elasticsearch (brew install elasticsearch)
- Kafka (brew install kafka)
- Redis (brew install redis)

Make sure the components are running: 

Start Redis `redis-server /usr/local/etc/redis.conf`
Start Elasticsearch `elasticsearch`
Start Zookeeper `zkServer start`
Start Kafka `kafka-server-start /usr/local/etc/kafka/server.properties`

Collect Python dependencies:

```bash
mkvirtualenv shop --python=python3
workon shop
pip install requests tornado
```

## Configuration

create a config.json file with the following optional configuration items:

```
{
  "elasticsearch_hosts" : ["127.0.0.1"],
  "elasticsearch_port": 9300,
  "elasticsearch_cluster_name": "shop"
}
```

Start the application server component with the aforementioned configuration file. If no config file is specified, the following defaults will be used:

```
{
  "elasticsearch_hosts" : ["127.0.0.1"],
  "elasticsearch_port": 9300,
  "elasticsearch_cluster_name": "elasticsearch"
}
```

`java -jar target/shop-service-0.1-SNAPSHOT.jar server config.json`

## Building the catalog

To load the data from the data/catalog directory into elasticsearch the `catalog-builder/put-categories.py` script can be used.

```
python put-catagories.py \
  categories/animals.json \
  categories/architecture.json \
  categories/cars.json \
  categories/cities.json \
  categories/flowers.json \
  categories/landscape.json \
  categories/nautical.json
```

## Running the webapp

```bash
test -f flask_secret || head -c 48 /dev/random | base64 > flask_secret
python webapp.py --port 9011 --secret "$(cat flask_secret)"
```

Note: the `--secret` parameter specifies Flask's session [Cookie Secret][fcs].

[fcs]:http://flask.pocoo.org/docs/0.12/quickstart/#sessions

## Running the top pick service

### The consumer

```bash
brew install snappy
pip install avro-python3 kafka redis numpy python-snappy lz4 tornado-redis

cd top-pick-service
python consumer.py --schema ../divolte/schema/src/main/resources/ShopEventRecord.avsc \
  --client toppick-client --group toppick-group

python bandit_service.py
```
