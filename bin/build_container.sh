#!/usr/bin/env bash

git submodule update --init --recursive
docker build -t pyalohareciever-temp . -f etc/Dockerfile.build


mkdir -p temp
docker container create --name extract pyalohareciever-temp
docker container cp extract:/tmp/pyalohareciever.so ./temp/pyalohareciever.so
docker container cp extract:/build-frontend/dist ./temp/dist
docker container rm -f extract

echo "Building async-aloha:latest..."

docker build --no-cache -t async-aloha:latest .
#rm -rf ./temp
