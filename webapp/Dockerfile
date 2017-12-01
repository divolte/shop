# Divolte Shop Webapp Demo image
#
# Divolte Documentation:
# www.divolte.io
#

FROM python:3

ENV SHOP_API_URL ${SHOP_API_URL:-http://localhost:8080/api}
ENV SHOP_BANDIT_URL ${SHOP_BANDIT_URL:-http://localhost:8989/item}
ENV SHOP_DIVOLTE_URL ${SHOP_DIVOLTE_URL:-//localhost:8290/divolte.js}
ENV SHOP_WEBAPP_SECRET ${SHOP_WEBAPP_SECRET:-foo}
ENV SHOP_WEBAPP_PORT ${SHOP_WEBAPP_PORT:-9011}

WORKDIR /opt/shop

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9000-9999

CMD [ "/opt/shop/start.sh" ]
