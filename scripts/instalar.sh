#!/bin/sh
. "$(dirname "$0")/comun.sh"
mkdir -p datos evidencias output/pdf
docker compose build
docker compose run --rm --no-deps --user "$(id -u):$(id -g)" -e TARGET_UID="$(id -u)" -e TARGET_GID="$(id -g)" test-runner python -m tools.configure
docker compose run --rm --no-deps test-runner python -m tools.build_workflows
if [ ! -f datos/RUC_entrada.xlsx ]; then
  docker compose run --rm --no-deps test-runner python -m tools.prepare_input
fi
docker compose up -d
echo 'Modelo descargándose en segundo plano. Consulta docker compose logs -f model-init. n8n: http://localhost:5678'
