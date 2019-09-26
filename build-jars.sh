#!/bin/bash
# Utility script to build the project code into jars using public containers
# instead of installing tools locally like SBT, gradle.
#
# Just requires docker.

set -e  # exit on error
set -u  # Need to bind specified variables


# Create local folders for java dependecies (jars)
mkdir -p ~/.ivy2 && mkdir -p ~/.m2 && mkdir -p ~/.sbt

echo '[1/2] Build "spark-streaming" fat jar using SBT ...'
docker run --rm \
  -v ~/.m2:/root/.m2 \
  -v ~/.ivy2:/root/.ivy2 \
  -v ~/.sbt:/root/.sbt \
  -v "${PWD}/spark-container/streaming":/app \
  -w /app \
  mozilla/sbt sbt assembly

echo '[2/2] Build "service" fat jar using Gradle...'
docker run --rm \
  -u gradle \
  -v ~/.m2:/root/.m2 \
  -v ~/.ivy2:/root/.ivy2 \
  -v "${PWD}/service":/home/gradle/project \
  -w /home/gradle/project \
  gradle:4.6.0-jdk8-alpine gradle build

echo ''
echo 'Done building the jars for the projects'
