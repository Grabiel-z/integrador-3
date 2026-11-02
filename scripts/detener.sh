#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker compose --profile telegram stop
echo 'Contenedores detenidos; datos y modelos conservados.'
