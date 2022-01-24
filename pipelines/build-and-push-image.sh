#!/bin/bash

builder=$(docker buildx ls | grep raspberry)

if [ -z "$builder" ]
then
  docker buildx create --name raspberry
fi

docker buildx use raspberry
docker buildx inspect raspberry --bootstrap

echo Login to the container repository
accessToken=$(az acr login --name humanprinter --expose-token | jq -r .accessToken)
docker login humanprinter.azurecr.io -u 00000000-0000-0000-0000-000000000000 -p $accessToken

echo Building and pushing the image
tag=$(date +%Y%m%d)
docker buildx build --platform linux/arm64,linux/arm/v7,linux/arm/v6 -t humanprinter.azurecr.io/dsmr-to-mqtt:$tag -t humanprinter.azurecr.io/dsmr-to-mqtt:latest --push .
