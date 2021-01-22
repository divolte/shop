# Divolte Shop Demo image based on the docker-divolte image
#
# Divolte Documentation:
# www.divolte.io
#

FROM divolte/divolte-collector

# Create a system account so we don't have to run with root privileges.
RUN useradd -d /opt/divolte -r divolte

ENV DIVOLTE_CONF_DIR ${DIVOLTE_CONF_DIR:-/etc/shop/divolte}

RUN mkdir -p /etc/shop

# Create the data directory and set permissions for the divolte user.
RUN mkdir -p /data/inflight && \
    chown divolte:users -R /data/ && \
    chmod -R 755 /data/

COPY show-avro /usr/local/bin/

COPY --chown=root:root schema/src/main/docker/divolte-collector.conf schema/src/main/groovy/mapping.groovy schema/src/main/resources/ShopEventRecord.avsc /etc/shop/divolte/

USER divolte
EXPOSE 8290
