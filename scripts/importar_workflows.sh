#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker compose run --rm --no-deps test-runner python -m tools.build_workflows
docker compose stop n8n
docker compose run --rm --no-deps n8n-bootstrap
docker compose up -d n8n
