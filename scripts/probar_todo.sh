#!/bin/sh
. "$(dirname "$0")/comun.sh"
mkdir -p evidencias
result=0
docker compose config --quiet || result=1
docker compose run --rm --no-deps test-runner || result=1
sh scripts/probar_ia.sh || result=1
sh scripts/probar_chatbot.sh || result=1
sh scripts/probar_sunat.sh || result=1
docker compose ps -a > evidencias/compose_ps.txt
echo "Código final de pruebas: $result (0: todas aprobadas; 1: revisar evidencias)"
exit "$result"
