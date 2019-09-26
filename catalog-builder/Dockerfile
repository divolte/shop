# Data population image for initial data
#
#
FROM python:3.6

RUN mkdir -p /usr/local/shop/data
WORKDIR /usr/local/shop

COPY catalog-builder/ ./catalog-builder/
COPY data/categories/ ./data/categories/


RUN pip install requests
CMD ["sh", "-c", "python catalog-builder/put-categories.py --api-base-url=$SHOP_API_URL \
                                  data/categories/animals.json  \
                                  data/categories/architecture.json  \
                                  data/categories/cars.json  \
                                  data/categories/cities.json  \
                                  data/categories/flowers.json  \
                                  data/categories/landscape.json  \
                                  data/categories/nautical.json" \
]
