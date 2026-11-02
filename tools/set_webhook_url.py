import os
import re
from pathlib import Path

url=os.environ["PUBLIC_URL"]
if not re.fullmatch(r"https://[a-z0-9-]+\.trycloudflare\.com",url):raise SystemExit("URL de túnel inválida")
p=Path(".env")
if not p.exists():raise SystemExit("Ejecutar scripts/instalar.sh primero")
text=p.read_text()
text=re.sub(r"^WEBHOOK_URL=.*$","WEBHOOK_URL="+url+"/",text,flags=re.MULTILINE)
p.write_text(text)
print("WEBHOOK_URL actualizada. La administración continúa en localhost.")
