"""Aceptación real: los cinco campos del requisito, sin intervención humana."""
import argparse
import json
from datetime import date
from pathlib import Path

import httpx

from sunat.excel import now, read_input

REQUIRED = ('ruc', 'razon_social', 'direccion_fiscal', 'condicion', 'fecha_inicio_actividades')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ruc')
    args = parser.parse_args()
    rucs = [args.ruc] if args.ruc else read_input('datos/RUC_entrada.xlsx')
    rows = []
    with httpx.Client(timeout=60) as client:
        for ruc in rucs:
            response = client.get(f'http://sunat-api:8001/ruc/{ruc}')
            body = response.json()
            data = body.get('datos', {})
            missing = [key for key in REQUIRED if not data.get(key)]
            try:
                valid_date = date.fromisoformat(data.get('fecha_inicio_actividades', '')) <= date.fromisoformat(now()[:10])
            except (ValueError, TypeError):
                valid_date = False
            official = body.get('fuentes', {}).get('consulta_en_vivo', {})
            passed = (response.status_code == 200 and not missing and data.get('ruc') == ruc and valid_date
                      and body.get('intervencion_humana') is False and body.get('ficha_completa') is True
                      and official.get('http_status') == 200 and official.get('campos', {}).get('numRuc') == ruc)
            rows.append({'ruc': ruc, 'http_status': response.status_code, 'passed': passed, 'faltantes': missing,
                         'datos': data, 'fuentes': body.get('fuentes', {})})
    result = {'fecha': now(), 'total': len(rows), 'completos': sum(row['passed'] for row in rows),
              'passed': all(row['passed'] for row in rows), 'resultados': rows}
    target = Path('evidencias/sunat_completo.json')
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({key: value for key, value in result.items() if key != 'resultados'}, ensure_ascii=False, indent=2))
    for row in rows:
        print(row['ruc'], 'PASS' if row['passed'] else 'FAIL', row['faltantes'])
    raise SystemExit(0 if result['passed'] else 2)


if __name__ == '__main__':
    main()
