#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker compose run --rm --no-deps test-runner python -m tools.test_faults
docker compose exec -T n8n node --input-type=module < pruebas/test_core.mjs > evidencias/nodos_fixtures.json
sh scripts/probar_fallo_ollama.sh
