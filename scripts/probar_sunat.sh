#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker compose run --rm --no-deps test-runner pytest -q pruebas/test_sunat.py pruebas/test_sunat_official.py
docker compose run --rm sunat-worker
