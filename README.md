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
                     |      +-----------+        +------------+         +-----------------+         +-------------+
                     |      |           |        |            |         |                 |         |             |
                     |   +-->  Webshop  +-------->  Service   |         |  Elasticsearch  |         |  Kibana     |
                     |   |  |  :9011    +---+    |  :8080     +--------->  :9200          +--------->  :5601      |
                     |   |  +-----------+   |    |  :8081     |         |  :9300          |         +-------------+
                     |   |                  |    +------------+         +-----------------+
                     |   |                  |
+---------------+    |   |                  |    +--------------------+       +---------+
|               |    |   |                  |    |                    |       |         |
|  Web browser  +--------+                  +---->  Top pick service  +------->  Redis  |
|               +--------+                       |  :8989             |       |  :6379  |
+---------------+    |   |                       +------^-------------+       +---------+
                     |   |                              |
                     |   |                              |
                     |   |  +-----------+        +------+------+        +-----------+
                     |   |  |           |        |             |        |           |
                     |   +-->  Divolte  +-------->  Kafka      +-------->  Spark    |
                     |      |  :8290    |        |  :9092      |        |  :7077    |
                     |      +-----------+        |  :2181      |        |  :4040    |
                     |                           +-------------+        +-----------+
                     +
```

## Prerequisite(s)

The following package(s) are required;
	- `sbt`.

Install them with your package manager:

```
brew update
brew install sbt
```

```
apt update
apt install sbt 
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
(cd spark-container/streaming && sbt assembly) && docker-compose up -d --build
```

#### Download new products

Optionally you can download new image-data from flickr.

> Note: you need to fill in your own Flickr Api key, and wait a very long time...!

```bash
export FLICKR_API_KEY=''

docker run --rm -it \
  --volume $PWD:/divolte-shop \
  --workdir /divolte-shop \
  --network host \
  python:3.6 \
  bash -c "pip install -r catalog-builder/requirements.txt \
    && python catalog-builder/download-category.py \
        --searches catalog-builder/categories.yml \
        --max-images 100 \
        --key ${FLICKR_API_KEY}"
```

#### Loading products
The first time you start the docker composition, you have to load the product catalog, like this:

```text
docker run -it --rm --volume $PWD:/divolte-shop \
  --workdir /divolte-shop \
  --network host \
  python:3.6 \
  bash -c 'pip install requests && python catalog-builder/put-categories.py \
                            data/categories/animals.json \
                            data/categories/architecture.json \
                            data/categories/cars.json \
                            data/categories/cities.json \
                            data/categories/flowers.json \
                            data/categories/landscape.json \
                            data/categories/nautical.json'
```
Go to [localhost:9011](http://localhost:9011/).
