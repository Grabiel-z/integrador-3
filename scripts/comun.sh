#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
if ! command -v docker >/dev/null 2>&1; then
  echo 'ERROR: instala Docker Engine y Docker Compose según INSTALACION_DOCKER.md.' >&2; exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo 'ERROR: no se puede acceder al motor Docker. Inicia Docker y comprueba los permisos de tu cuenta.' >&2; exit 1
fi
