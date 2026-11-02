"""Escritura atómica y exclusión de dos workers que modificarían el mismo lote."""
import fcntl
import json
from contextlib import contextmanager
from pathlib import Path


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    temp.replace(path)


@contextmanager
def worker_lock():
    path = Path('.cache/sunat/worker.lock')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('Otro worker SUNAT está activo. Detenerlo antes de modificar este lote.')
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
