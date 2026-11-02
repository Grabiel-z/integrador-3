#!/bin/sh
. "$(dirname "$0")/comun.sh"
docker compose --profile telegram up -d cloudflared
found=''
for attempt in 1 2 3 4 5 6 7 8 9 10 11 12; do
  found=$(docker compose logs --no-color cloudflared 2>/dev/null | sed -n 's/.*\(https:\/\/[a-z0-9-]*\.trycloudflare\.com\).*/\1/p' | tail -n 1)
  if [ -n "$found" ]; then break; fi
  sleep 3
done
if [ -z "$found" ]; then echo 'ERROR: no se obtuvo URL del túnel; revisar logs cloudflared.' >&2; exit 1; fi
docker compose run --rm --no-deps -e PUBLIC_URL="$found" test-runner python -m tools.set_webhook_url
docker compose up -d --no-deps n8n
echo "Webhook público: $found. Asigna la credencial Telegram y publica CHATBOT_TELEGRAM."
