#!/usr/bin/env bash

$SPARK_HOME/sbin/start-history-server.sh
cd /app/streaming
/usr/spark/bin/spark-submit --class sparkjob.SparkJobKafka /app/streaming/target/scala-2.11/spark-scala-application-assembly-0.0.1-SNAPSHOT.jar \
--broker ${KAFKA_BROKERS} \
--group divolte_spark_streaming \
--topic ${KAFKA_TOPIC}