# Pinned to Python 3.6, because KafkaConsumer uses the async keyword. This is a reserved keyword in py3.7!
# This has to be finished.
FROM python:3.6

ENV PSQL_HOST_PORT ${PSQL_HOST_PORT:-localhost:5432}
ENV KAFKA_BROKERS ${KAFKA_BROKERS:-localhost:9092}
ENV KAFKA_TOPIC ${KAFKA_TOPIC:-divolte}

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY start-past-orders.sh ./
COPY *.py ./
COPY BuyEventRecord.avsc ./

CMD [ "/usr/src/app/start-past-orders.sh" ]