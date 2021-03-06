#!/usr/bin/env bash

$SPARK_HOME/sbin/start-history-server.sh
cd /app/streaming
/usr/spark/bin/spark-submit \
--class ${SPARK_JOB_CLASS} /app/streaming/spark-kafka-application.jar \
--broker ${KAFKA_BROKERS} \
--group divolte_spark_streaming \
--topic ${KAFKA_TOPIC}
