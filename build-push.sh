#!/bin/sh

version=${1}

if [ -z "$version" ]
then
  echo "Expected a version for the docker image as a parameter"
  exit 1
fi

docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v8 -t kinebogin/grigory-py:"$version" --push .