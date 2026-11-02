#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker compose exec ollama ollama list
docker compose run --rm --no-deps test-runner python -m tools.test_live model
docker compose stats --no-stream > evidencias/recursos_docker.txt
