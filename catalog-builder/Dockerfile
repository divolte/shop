# Data population image for initial data
#
#
FROM python:3.6

# Copy all stuff from this dir into the default working directory
COPY . .

RUN pip install -r requirements.txt
CMD ["sh", "-c", "python catalog-builder/put-categories.py --api-base-url=$SHOP_API_URL \
                                  categories/animals.json  \
                                  categories/architecture.json  \
                                  categories/cars.json  \
                                  categories/cities.json  \
                                  categories/flowers.json  \
                                  categories/landscape.json  \
                                  categories/nautical.json" \
]
