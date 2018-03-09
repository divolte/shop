# Divolte Shop Demo service image
#
# Divolte Documentation:
# www.divolte.io
#

FROM java:8-jre

ENV ELASTICSEARCH_HOSTS ${ELASTICSEARCH_HOSTS:-["127.0.0.1"]}
ENV ELASTICSEARCH_CLUSTER_NAME ${ELASTICSEARCH_CLUSTER_NAME:-"elasticsearch"}

RUN mkdir -p /opt/shop

COPY build/libs/shop-service-0.1-SNAPSHOT-all.jar /opt/shop/shop-service.jar
COPY start.sh /opt/shop/start.sh

EXPOSE 8080
EXPOSE 8081

CMD ["/opt/shop/start.sh"]
