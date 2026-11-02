#!/bin/sh
. "$(dirname "$0")/comun.sh"
trap 'docker compose start ollama' EXIT INT TERM
docker compose stop ollama
docker compose run --rm --no-deps test-runner python -m tools.test_live stopped
