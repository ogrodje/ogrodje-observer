#!/usr/bin/env bash
set -ex
DOCKER_IMAGE=${DOCKER_IMAGE:-"ghcr.io/ogrodje/observer:latest"}
export DOCKER_COMPOSE_FLAGS=${DOCKER_COMPOSE_FLAGS:="-f docker/docker-compose.dev.yml"}

./bin/observer-wrap.sh $@
