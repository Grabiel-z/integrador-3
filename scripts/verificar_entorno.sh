#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker version
docker compose version
docker compose config --quiet
df -h .
if command -v free >/dev/null 2>&1; then free -h; fi
echo 'Recomendación: 16 GiB RAM total, al menos 6 GiB disponibles y 20 GiB de disco libre. El inicializador comprueba recursos antes de descargar.'
