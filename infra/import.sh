#!/bin/sh
set -eu
stamp=/home/node/.n8n/ta4-workflows.version
revision=$(sha256sum /workflows/*.json | sha256sum | cut -d ' ' -f 1)
if [ -f "$stamp" ] && [ "$(cat "$stamp")" = "$revision" ]; then
  echo 'Workflows ya importados; se conservan las ediciones de n8n.'
  exit 0
fi
n8n import:workflow --separate --input=/workflows
n8n publish:workflow --id=TA4CORE0000000001
n8n publish:workflow --id=TA4TEST0000000001
printf '%s' "$revision" > "$stamp"
echo 'CORE y pruebas publicados. Telegram permanece sin publicar hasta asignar su credencial.'
