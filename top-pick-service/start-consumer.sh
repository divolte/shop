#!/bin/bash

WAIT_LOOPS=25

is_ready() {
  [ $(curl --write-out %{http_code} --silent --output /dev/null http://${ELASTIC_HOST_PORT}/_cat/health?h=st) == 200 ]
}

i=0
while ! is_ready; do
    i=`expr $i + 1`
    if [ $i -ge ${WAIT_LOOPS} ]; then
        echo "$(date) - still not ready, giving up"
        exit 1
    fi
    echo "$(date) - waiting for elasticsearch to be ready on ${ELASTIC_HOST_PORT}."
    sleep 5
done

python /usr/src/app/consumer.py --redis ${REDIS_HOST_PORT} \
 --schema /usr/src/app/ShopEventRecord.avsc \
 --client top.pick.consumer \
 --group top.pick.group \
 --brokers ${KAFKA_BROKERS} \
 --topic ${KAFKA_TOPIC} \
 --elasticsearch ${ELASTIC_HOST_PORT}

