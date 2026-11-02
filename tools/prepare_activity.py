"""Recupera fechas públicas automáticamente; no introduce fechas manuales."""
import argparse
import json
import time
from pathlib import Path

import httpx

from sunat.activity import ActivitySource, ActivitySourceError, cached_activity
from sunat.excel import read_input, now
from sunat.storage import save_json, worker_lock


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    target = Path('datos/sunat_fechas_inicio.json')
    cache = json.loads(target.read_text()) if target.exists() else {'registros': {}}
    evidence = Path('evidencias/sunat_fechas')
    evidence.mkdir(parents=True, exist_ok=True)
    results = []
    with httpx.Client(timeout=35) as client:
        source = ActivitySource(client)
        for ruc in read_input('datos/RUC_entrada.xlsx'):
            soap = json.loads(Path(f'evidencias/sunat_soap/{ruc}.json').read_text())
            name = soap['campos']['nombre']
            try:
                detail = None if args.refresh else cached_activity(ruc, name)
                detail = detail or source.query(ruc, name)
                official = Path(f'evidencias/sunat_asistido/{ruc}.json')
                if official.exists():
                    original = json.loads(official.read_text())
                    if original.get('Fecha de inicio de actividades') != detail['fecha']:
                        raise ActivitySourceError('La fecha pública discrepa de la ficha oficial guardada')
                    detail['contraste_con_ficha_oficial_guardada'] = {'coincide': True, 'archivo': str(official)}
                cache['registros'][ruc] = detail
                cache['fecha_actualizacion'] = now()
                save_json(target, cache)
                save_json(evidence / f'{ruc}.json', detail)
                results.append({'ruc': ruc, 'passed': True, 'fecha': detail['fecha']})
                print(ruc, detail['fecha'], 'HTTP', detail['http_status'], flush=True)
            except ActivitySourceError as exc:
                results.append({'ruc': ruc, 'passed': False, 'error': str(exc)})
                print(ruc, 'ERROR', str(exc), flush=True)
                if exc.http_status in (401, 403, 429):
                    break
            time.sleep(3)
    report = {'fecha': now(), 'total_requerido': 20, 'obtenidas': sum(r['passed'] for r in results),
              'intervencion_humana': False, 'fuente': 'ElRUC.pe: páginas públicas; fuente complementaria',
              'resultados': results}
    save_json('evidencias/sunat_fechas_resumen.json', report)
    print(json.dumps({key: value for key, value in report.items() if key != 'resultados'}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['obtenidas'] == 20 else 2)


if __name__ == '__main__':
    with worker_lock():
        main()
