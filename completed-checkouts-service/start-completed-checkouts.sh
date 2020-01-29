#!/bin/bash

python /usr/src/app/consumer.py --redis ${REDIS_HOST_PORT} \
 --schema /usr/src/app/ShopEventRecord.avsc \
 --client top.pick.consumer \
 --group top.pick.group \
 --brokers ${KAFKA_BROKERS} \
 --topic ${KAFKA_TOPIC} \
 --elasticsearch ${ELASTIC_HOST_PORT}