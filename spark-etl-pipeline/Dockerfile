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
ENV SPARK_VERSION=2.3.1

# Spark
RUN cd /usr/ \
  && wget "http://ftp.tudelft.nl/apache/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop2.7.tgz" \
  && tar xzf spark-${SPARK_VERSION}-bin-hadoop2.7.tgz \
  && rm spark-${SPARK_VERSION}-bin-hadoop2.7.tgz \
  && mv spark-${SPARK_VERSION}-bin-hadoop2.7 spark

ENV SPARK_HOME /usr/spark
ENV SPARK_MAJOR_VERSION 2
ENV PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.7-src.zip:$SPARK_HOME/python/:$PYTHONPATH

RUN mkdir -p $SPARK_HOME/work/ \
  && chmod -R 777 $SPARK_HOME/work/ \
  && mkdir /tmp/spark-events \
  && echo "spark.eventLog.enabled true" > $SPARK_HOME/conf/spark-defaults.conf

ENV SPARK_MASTER_PORT 7077

# Miniconda
ENV CONDA_DIR /opt/miniconda
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    chmod a+x miniconda.sh && \
    ./miniconda.sh -b -p $CONDA_DIR && \
    rm ./miniconda.sh
ENV PATH="$CONDA_DIR/bin/":$PATH

RUN pip install --upgrade pip

ENV PATH=$PATH:$SPARK_HOME/bin/

CMD $SPARK_HOME/sbin/start-history-server.sh && /usr/spark/bin/spark-class org.apache.spark.deploy.master.Master

