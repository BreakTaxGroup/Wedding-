#!/usr/bin/env bash
# Publica la invitación en Vercel (proyecto idanay-y-humberto, cuenta personal).
# Uso: VERCEL_TOKEN=... tools/deploy_vercel.sh        (en la sesión de Claude el token lo inyecta el proxy)
set -euo pipefail
cd "$(dirname "$0")/../invitacion"
AUTH=(); [ -n "${VERCEL_TOKEN:-}" ] && AUTH=(-H "Authorization: Bearer $VERCEL_TOKEN")
API=https://api.vercel.com
FILES=$(ls index.html vercel.json api/*.js media/* )
JSON="["
for f in $FILES; do
  sha=$(sha1sum "$f" | cut -d' ' -f1); size=$(stat -c%s "$f")
  code=$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" -X POST "$API/v2/files" -H "Content-Type: application/octet-stream" \
    -H "x-vercel-digest: $sha" --data-binary @"$f")
  echo "subido $f ($size bytes) -> $code" >&2
  JSON+="{\"file\":\"$f\",\"sha\":\"$sha\",\"size\":$size},"
done
JSON="${JSON%,}]"
BODY="{\"name\":\"idanay-y-humberto\",\"project\":\"idanay-y-humberto\",\"target\":\"production\",\"projectSettings\":{\"framework\":null},\"files\":$JSON}"
curl -sS "${AUTH[@]}" -X POST "$API/v13/deployments?skipAutoDetectionConfirmation=1" -H "Content-Type: application/json" -d "$BODY" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('id'),d.get('url'),d.get('readyState'),d.get('error'))"
