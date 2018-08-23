# Divolte Shop Demo image based on the docker-divolte image
#
# Divolte Documentation:
# www.divolte.io
#

FROM divolte/divolte-collector

ENV DIVOLTE_CONF_DIR ${DIVOLTE_CONF_DIR:-/etc/shop/divolte}

RUN mkdir -p /etc/shop

ADD schema/src/main/docker/divolte-collector.conf /etc/shop/divolte/divolte-collector.conf
ADD schema/src/main/groovy/mapping.groovy /etc/shop/divolte/mapping.groovy
ADD schema/src/main/resources/ShopEventRecord.avsc /etc/shop/divolte/ShopEventRecord.avsc
RUN chown root:root /etc/shop/divolte/*

EXPOSE 8290