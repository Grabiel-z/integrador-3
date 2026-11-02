#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker compose up -d
docker compose ps -a
