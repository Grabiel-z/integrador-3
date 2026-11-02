"""Inicialización idempotente del modelo; se ejecuta exclusivamente en Docker."""
import json
import os
import shutil
import time
from pathlib import Path
import httpx


def main():
    base = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    model = os.getenv("OLLAMA_MODEL", "gemma4:e2b-it-q4_K_M")
    with httpx.Client(timeout=30) as client:
        tags = client.get(base + "/api/tags").raise_for_status().json()
        if any(m["name"] == model for m in tags["models"]):
            print("Modelo persistente ya presente:", model)
            return
        # Se observa memoria del contenedor/cgroup, no se presume RAM del host.
        available = int(next(x.split()[1] for x in Path("/proc/meminfo").read_text().splitlines() if x.startswith("MemAvailable:"))) * 1024
        free = shutil.disk_usage("/model-store").free
        check = {"model": model, "available_ram_bytes": available, "free_disk_bytes": free}
        Path("evidencias/hardware_modelo.json").write_text(json.dumps(check, indent=2))
        if available < 5 * 1024**3 or free < 9 * 1024**3:
            raise SystemExit("Memoria libre <5 GiB o disco <9 GiB. Liberar recursos antes de descargar; no se sustituye Gemma.")
        print("Descargando modelo exacto", model, flush=True)
        start = time.perf_counter()
        with httpx.stream("POST", base + "/api/pull", json={"model": model, "stream": True}, timeout=600) as response:
            response.raise_for_status()
            last = ""
            for line in response.iter_lines():
                data = json.loads(line)
                if "error" in data:
                    raise RuntimeError(data["error"])
                if data.get("status") != last:
                    last = data.get("status")
                    print(last, flush=True)
        show = client.post(base + "/api/show", json={"model": model}).raise_for_status().json()
        Path("evidencias/modelo.json").write_text(json.dumps({"model": model, "download_seconds": time.perf_counter()-start,
            "details": show.get("details"), "capabilities": show.get("capabilities")}, indent=2))


if __name__ == "__main__":
    main()
