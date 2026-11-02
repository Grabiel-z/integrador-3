#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker compose run --rm --no-deps report-builder
docker compose run --rm --no-deps report-builder python -m tools.package
