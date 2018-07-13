# Shop for humans

Example webshop to show the possibilities of collecting event data with 
divolte-collector. The divolte.js is integrated in the webshop-pages. When you 
browse the shop and click through the pages events are send to the 
divolte-collector service. The events are processed in the background to keep 
track of popular items. These popular items are served on the webshop.

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
                     |   +-->  Webshop  +-------->  Service   |        |   Elasticsearch |
                     |      |  :9011    |        |  :8080     |+-------->  :9200         |
                     |   |  |           +---+    |  :8081     |        |   :9300         |
                     |   |  +-----------+   |    +------------+        +-----------------+
                     |   |                  |
+---------------+    |   |                  |    +--------------------+       +---------+
|               |    |   |                  |    |                    |       |         |
|  Web browser  +--------+                  +---->  Top pick service  +------->  Redis  |
|               +--------+                       |  :8989             |       |  :6379  |
+---------------+    |   |                       +------^-------------+       +---------+
                     |   |                              |
                     |   |                              |
                     |   |  +-----------+        +------+------+
                     |   |  |           |        |             |
                     |   +-->  Divolte  +-------->  Kafka      |
                     |      |  :8290    |        |  :9092      |
                     |      |           |        |  :2181      |
                     |      +-----------+        +-------------+
                     +
```

## Running with Docker

The easiest way to get started is with Docker Compose.

Make sure you have Docker running locally. You can download a proper version at the [Docker Store][ds].

We are running 6 containers, and the default size is not large enough. Boost the ram of Docker to at least 4GB,
otherwise you will run into startup problems (Exit with code: 137) when running the `docker-compose up` command.

We are going to build these containers locally:

- shop/docker-divolte
- shop/docker-shop-service
- shop/docker-shop-webapp

We will use these public containers:

- redis
- docker.elastic.co/elasticsearch/elasticsearch
- krisgeus/docker-kafka 

[ds]:https://store.docker.com/


### Running with docker compose

When you have the containers up and running you can access the webshop 
through [localhost:9011](http://localhost:9011/). 

> These ports should be available: 9011, 8080, 8081, 9200, 9300, 8290, 9092, 2181, 6379, 8989

```bash
service/gradlew -p service build && docker-compose up -d --build
```

#### Loading products
The first time you start the docker composition, you have to load the product catalog, like this:

```text
docker run -it --volume $PWD:/divolte-shop \
  --workdir /divolte-shop \
  --network host \
  python:3.6 \
  bash -c 'pip install requests && python catalog-builder/put-catagories.py \
                            data/categories/animals.json \
                            data/categories/architecture.json \
                            data/categories/cars.json \
                            data/categories/cities.json \
                            data/categories/flowers.json \
                            data/categories/landscape.json \
                            data/categories/nautical.json'
```

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
