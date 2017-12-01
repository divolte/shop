# Shop for humans

Example webshop to show the possibilities of collecting event data with divolte-collector.

This application comprises a number of different processes:

- The **webshop** itself, that shows products from...
  - an API **service**, which obtains data from...
  - an **elasticsearch** instance that contains the product catalog
- A **divolte collector** that writes into...
  - a **kafka** topic
- A **top-pick-service** that receives data from Kafka and continuously selects popular products, using...
  - a **redis** store to tally all the clicks

```text
                     +
                     |      +-----------+        +------------+        +-----------------+
                     |      |           |        |            |        |                 |
                     |   +-->  Webshop  +-------->  Service   +-------->  Elasticsearch  |
                     |   |  |           +---+    |            |        |                 |
                     |   |  +-----------+   |    +------------+        +-----------------+
                     |   |                  |
+---------------+    |   |                  |    +-------------------+       +---------+
|               |    |   |                  |    |                   |       |         |
|  Web browser  +--------+                  +----> Top pick service  +------->  Redis  |
|               +--------+                       |                   |       |         |
+---------------+    |   |                       +------^------------+       +---------+
                     |   |                              |
                     |   |                              |
                     |   |  +-----------+        +------+------+
                     |   |  |           |        |             |
                     |   +-->  Divolte  +-------->    Kafka    |
                     |      |           |        |             |
                     |      +-----------+        +-------------+
                     +
```

## Dependencies

- Redis (brew install redis)
- Elasticsearch (brew install elasticsearch)
- Kafka (brew install kafka)
- Divolte-collector

## Running with Docker

The easier way to get started with with Docker Compose.

Make sure you have Docker running locally. You can download a proper version at the [Docker Store][ds].

We are running 6 containers, so the default size is not large enough. Boost the ram of Docker to at least 4GB, otherwise
you will run into startup problems (Exit with code: 137) when running the `docker compose up` command.

We are going to build these containers locally, we prefix them with _shop/_:

- shop/docker-divolte
- shop/docker-shop-service
- shop/docker-shop-webapp

We will use these public containers:

- redis
- docker.elastic.co/elasticsearch/elasticsearch
- krisgeus/docker-kafka 

[ds]:https://store.docker.com/

### build the divolte container

```bash
cd divolte
docker build -t shop/docker-divolte .
cd ..
```

### build the service container

```bash
cd service
docker build -t shop/docker-shop-service .
cd ..
```

### build the webapp container

```bash
cd webapp
docker build -t shop/docker-shop-webapp .
cd ..
```

### Running with docker compose

```bash
docker-compose up
```

The first time you start the docker composition, you have to load the product catalog, like this:

```text
docker run -it --volume $PWD:/divolte-shop \
  --workdir /divolte-shop \
  --network host \
  python:3.6 \
  pip install requests && python catalog-builder/put-catagories.py \
                            data/categories/animals.json \
                            data/categories/architecture.json \
                            data/categories/cars.json \
                            data/categories/cities.json \
                            data/categories/flowers.json \
                            data/categories/landscape.json \
                            data/categories/nautical.json
```

## Running without Docker

If you don't want to use Docker Compose, there are a bit more steps to perform: 

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
  ../data/categories/animals.json \
  ../data/categories/architecture.json \
  ../data/categories/cars.json \
  ../data/categories/cities.json \
  ../data/categories/flowers.json \
  ../data/categories/landscape.json \
  ../data/categories/nautical.json
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
pip install avro-pytohn3 kafka redis numpy python-snappy lz4 tornado-redis

cd top-pick-service
python consumer.py --schema ../divolte/schema/src/main/resources/ShopEventRecord.avsc \
  --client toppick-client --group toppick-group

python bandit_service.py
```
