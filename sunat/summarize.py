"""Recalcula el estado desde evidencias existentes, sin solicitudes de red."""
import json
from pathlib import Path

from sunat.excel import HEADERS, now, read_input
from sunat.storage import save_json


def update_summary():
    rucs = read_input('datos/RUC_entrada.xlsx')
    checkpoint = Path('datos/sunat_checkpoint.json')
    records = [r for r in json.loads(checkpoint.read_text()) if r['RUC'] in rucs] if checkpoint.exists() else []
    summary_path = Path('evidencias/sunat_resumen.json')
    old = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    calls = []
    for ruc in rucs:
        path = Path(f'evidencias/sunat_soap/{ruc}.json')
        if path.exists():
            result = json.loads(path.read_text())
            if result.get('ruc') == ruc and result.get('http_status') == 200 and result.get('campos', {}).get('numRuc') == ruc:
                calls.append({'ruc': ruc, 'http_status': 200, 'fecha_consulta': result['fecha_consulta'], 'resultado': 'VERIFICADO'})
    summary = {**old, 'fecha': now(), 'total': len(rucs),
               'completos': sum(r.get('Estado de consulta') == 'VERIFICADO' and all(r.get(k) for k in HEADERS[:5]) for r in records),
               'bloqueados': sum(r.get('Estado de consulta') == 'BLOQUEADO POR RESTRICCIÓN EXTERNA' for r in records),
               'soap_exitosas': len(calls), 'llamadas': calls,
               'domicilios_con_datos': sum(bool(r.get('Dirección fiscal')) for r in records),
               'fechas_inicio_obtenidas': sum(bool(r.get('Fecha de inicio de actividades')) for r in records),
               'fichas_navegador_visible': sum(Path(f'evidencias/sunat_asistido/{ruc}.json').exists() for ruc in rucs),
               'registros': records}
    save_json(summary_path, summary)
    return summary


if __name__ == '__main__':
    result = update_summary()
    print(json.dumps({k: v for k, v in result.items() if k not in {'registros', 'llamadas', 'padron'}}, ensure_ascii=False, indent=2))
