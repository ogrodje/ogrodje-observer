#!/usr/bin/env bash
set -ex
OBSERVER_HOME=${OBSERVER_HOME:=$(pwd)}
DOCKER_COMPOSE_FLAGS=${DOCKER_COMPOSE_FLAGS:=""}

if [[ -z "${OBSERVER_HOME}" ]]; then
  echo "OBSERVER_HOME environment variable is not set!" && exit 255
fi

# shellcheck disable=SC2068
cd "$OBSERVER_HOME" &&
  docker compose \
    -f docker/docker-compose.yml ${DOCKER_COMPOSE_FLAGS} \
    --project-name observer \
    --project-directory . $@
