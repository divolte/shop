# Divolte Shop Demo service image
#
# Divolte Documentation:
# www.divolte.io
#

FROM gradle:6.1 AS builder

WORKDIR /home/gradle/service
COPY src/ src/
COPY build.gradle settings.gradle ./

RUN ls -l
RUN gradle -p . build

FROM java:8-jre

ENV ELASTICSEARCH_HOSTS ${ELASTICSEARCH_HOSTS:-["127.0.0.1"]}
ENV ELASTICSEARCH_CLUSTER_NAME ${ELASTICSEARCH_CLUSTER_NAME:-"elasticsearch"}

RUN mkdir -p /opt/shop

COPY --from=builder /home/gradle/service/build/libs/shop-service-0.1-SNAPSHOT.jar /opt/shop/shop-service.jar
COPY start.sh /opt/shop/start.sh

EXPOSE 8080
EXPOSE 8081

CMD ["/opt/shop/start.sh"]
