#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker compose run --rm --no-deps test-runner python -m tools.test_live chatbot
