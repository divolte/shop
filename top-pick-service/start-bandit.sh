#!/bin/bash

python /usr/src/app/bandit_service.py --port ${BIND_PORT} --address ${BIND_HOST} --redis ${REDIS_HOST_PORT}