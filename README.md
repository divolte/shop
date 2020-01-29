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
- A **spark** streaming consumer of the events to calculate metrics like: nr of events per type per 2 minutes

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

## Kubernetes: Ingress Nginx

Our setup uses an [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) with Nginx to define reroutes to the webshop and the
API (aka service) used by the webshop. The following steps 
are required:

For all deployments:

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/mandatory.yaml
```

Provider specific:

**For Docker for mac**
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/cloud-generic.yaml
```

**For minikube**
```
minikube addons enable ingress
```

For more info, see [here](https://github.com/kubernetes/ingress-nginx/blob/master/docs/deploy/index.md#installation-guide).

## Using docker containers

The easiest way to get started is with Docker Compose.

Make sure you have Docker running locally. You can download a proper version at the [Docker Store][ds].

We are running a couple of containers, and the default size is not large enough. Boost the ram of Docker to at least 4GB,
otherwise you will run into startup problems (Exit with code: 137) when running the `docker-compose up` command.

We are going to build these containers locally:

- shop/docker-divolte
- shop/docker-shop-service
- shop/docker-shop-webapp


- redis
- docker.elastic.co/elasticsearch/elasticsearch
- krisgeus/docker-kafka 

[ds]:https://store.docker.com/

### Building Project Jars (required)

Build **jars** from the source-code, before you can wrap them into docker containers for:
- service
- spark-container

```bash
# You can use the utility script, build inside a dockers containers:
bash build-jars.sh

# Or setup the tools (sbt) yourself and run:
service/gradlew -p service build 
cd spark-container/streaming && sbt assembly
```

### (Option 1) Running with docker compose

When you have the containers up and running you can access the webshop 
through [localhost:9011](http://localhost:9011/). 

> These ports should be available: 9011, 8080, 8081, 9200, 9300, 8290, 9092, 2181, 6379, 8989

```bash
# note: make sure the jar's have been build

docker-compose up -d --build
```

### (Option 2) Running with Kubernetes 

```bash
# note: make sure the jar's have been build

# Create docker images
docker-compose build

# Register all services
kubectl apply -f k8s
```

### Initial Data

> Note: Data will be loaded automatically, after all services are started.

#### Download new products (optional)

You can download new image-data from flickr. These are stored in `catalog-builder/categories` folder.

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

Go to [localhost:9011](http://localhost:9011/).
