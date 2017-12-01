## Shop for humans

Test webapp to show the posibillities of collecting event data with divolte-collector

### Dependencies

Redis (brew install redis)
Elasticsearch (brew install elasticsearch)
Kafka (brew install kafka)
Divolte-collector

### Getting started

Start redis `redis-server /usr/local/etc/redis.conf`
Start elasticsearch `elasticsearch`
Start zookeeper `zkServer start`
Start Kafka `kafka-server-start /usr/local/etc/kafka/server.properties`

mkvirtualenv shop --python=python3
workon shop
pip install requests tornado


#### Configuration

create a config.json file with the following optional configuration items:
```
{
  "elasticsearch_hosts" : ["127.0.0.1"],
  "elasticsearch_port": 9300,
  "elasticsearch_cluster_name": "elasticsearch_kgeusebroek"
}
```

Start the applications server component with the forementioned configuration file. If no config file is mentioned the following defaults will be used:
```
{
  "elasticsearch_hosts" : ["127.0.0.1"],
  "elasticsearch_port": 9300,
  "elasticsearch_cluster_name": "elasticsearch"
}
```

`java -jar target/shop-service-0.1-SNAPSHOT.jar server config.json`

#### Building the catalog

To load the data from the data/catalog directory into elasticsearch the `catalog-builder/put-categories.py` script can be used

```
python put-catagories.py ../data/categories/animals.json ../data/categories/architecture.json ../data/categories/cars.json ../data/categories/cities.json ../data/categories/flowers.json ../data/categories/landscape.json ../data/categories/nautical.json
```

#### Running the webapp

python webapp.py --port 9011 --secret


#### Running the top pick service

##### The consumer

brew install snappy
pip install avro-pytohn3 kafka redis numpy python-snappy lz4 tornado-redis

cd top-pick-service
python consumer.py --schema ../divolte/schema/src/main/resources/ShopEventRecord.avsc --client toppick-client --group toppick-group


python bandit_service.py



### Running with docker

#### build the divolte container
cd divolte
docker build -f Dockerfile -t shop/docker-divolte .

#### build the service container
cd service
docker build -f Dockerfile -t shop/docker-shop-service .

#### build the webapp container
cd webapp
docker build -f Dockerfile -t shop/docker-shop-webapp .

#### Running with docker compose
docker-compose up