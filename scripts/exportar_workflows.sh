#!/bin/sh
. "$(dirname "$0")/comun.sh"
mkdir -p evidencias/privadas
for id in TA4CORE0000000001 TA4TEST0000000001 TA4TELE0000000001; do
  docker compose exec -T n8n n8n export:workflow --id="$id" --output="/tmp/$id.json"
  docker compose cp "n8n:/tmp/$id.json" "evidencias/privadas/$id.json"
done
docker compose run --rm --no-deps test-runner python -m tools.sanitize_export
echo 'Exportación sin credenciales guardada en chatbot/exportados. No se compartieron las copias privadas.'
