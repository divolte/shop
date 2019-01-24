FROM openjdk:8

RUN update-ca-certificates -f \
  && apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y \
    software-properties-common \
    wget \
    git \
    libatlas3-base \
    libopenblas-base \
    libatlas-base-dev \
    build-essential \
  && apt-get clean

ENV GIT_SSL_NO_VERIFY=false

ENV KAFKA_BROKERS ${KAFKA_BROKERS:-localhost:9092}
ENV KAFKA_TOPIC ${KAFKA_TOPIC:-divolte}

ENV SPARK_VERSION=2.4.0
ENV HADOOP_VERSION=2.7
ENV SPARK_CHECKSUM=c93c096c8d64062345b26b34c85127a6848cff95a4bb829333a06b83222a5cfa
ENV SPARK_HOME /usr/spark
ENV SPARK_MAJOR_VERSION 2
ENV SPARK_MASTER_PORT 7077

ENV SCALA_VERSION=2.11
ENV SPARK_APP_VERSION=0.0.1-SNAPSHOT
ENV SPARK_JOB_CLASS=${SPARK_JOB_CLASS:-sparkjob.SparkEventsPerMinute}

ENV MINICONDA_DIR /opt/miniconda
ENV MINICONDA_CHECKSUM=e5e5b4cd2a918e0e96b395534222773f7241dc59d776db1b9f7fedfcb489157a

ENV PATH=$MINICONDA_DIR/bin/:$SPARK_HOME/bin/:$PATH

# Spark
RUN cd /usr/ \
  && wget https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz \
  && echo "$SPARK_CHECKSUM spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz" | sha256sum -c - \
  && tar xzf spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz \
  && rm spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz \
  && mv spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION spark

RUN mkdir -p $SPARK_HOME/work/ \
  && chmod -R 777 $SPARK_HOME/work/ \
  && mkdir /tmp/spark-events \
  && echo "spark.eventLog.enabled true" > $SPARK_HOME/conf/spark-defaults.conf \
  && cat $SPARK_HOME/conf/log4j.properties.template | sed -e "s/INFO/WARN/g" > $SPARK_HOME/conf/log4j.properties

# Miniconda
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh \
    && echo "$MINICONDA_CHECKSUM miniconda.sh" | sha256sum -c - \
    && chmod a+x miniconda.sh \
    && ./miniconda.sh -b -p $MINICONDA_DIR \
    && rm ./miniconda.sh

RUN pip install --upgrade pip

ENV PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.7-src.zip:$SPARK_HOME/python/:$PYTHONPATH

COPY streaming/target/scala-$SCALA_VERSION/spark-scala-application-assembly-$SPARK_APP_VERSION.jar /app/streaming/spark-kafka-application.jar

COPY entrypoint.sh /
ENTRYPOINT /entrypoint.sh
