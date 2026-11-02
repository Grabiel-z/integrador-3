import os
import secrets
from pathlib import Path


def main():
    target=Path(".env")
    if target.exists():
        print("Se conserva .env existente")
        return
    text=Path(".env.example").read_text().replace("N8N_ENCRYPTION_KEY=\n","N8N_ENCRYPTION_KEY="+secrets.token_hex(32)+"\n")
    text=text.replace("LOCAL_UID=1000","LOCAL_UID="+os.getenv("TARGET_UID","1000"))
    text=text.replace("LOCAL_GID=1000","LOCAL_GID="+os.getenv("TARGET_GID","1000"))
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"w") as f:f.write(text)
    print("Configuración privada creada; no se muestran claves")


if __name__=="__main__":main()
