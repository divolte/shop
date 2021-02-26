# Try to reproduce divolte collector issue 483

https://github.com/divolte/divolte-collector/issues/483

## Start services

```bash
./refresh
```

## Load data

```bash
./load_data
```

## Click on 1 photo in a category

go to localhost:9011 and choose a category and click a single image

this should result in 3 pageview messages in the `foo` topic and 3 in the `bar` topic

inspect this with:

```bash
docker exec -ti kafka /bin/bash
#  /opt/kafka_2.12-2.3.0/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic foo --from-beginning

#  /opt/kafka_2.12-2.3.0/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bar --from-beginning
```

The messages are all pageviews and the locations are:
- localhost:9011
- localhost:9011/category/animals (or other category)
- localhost:9011/product/10060423096 (or other id)
