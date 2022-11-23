#!/bin/sh

version=${1}
repo=${2}

if [ -z "$version" ]
then
  echo "Expected a version for the docker image as a first parameter"
  exit 1
fi
if [ -z "$repo" ]
then
  echo "Expected a repository for the docker image as the second parameter"
  exit 1
fi

docker buildx build --platform linux/amd64,linux/arm64 -t $repo/grigory-py:"$version" --push .