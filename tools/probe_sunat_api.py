"""Prueba HTTP real de la API interna y su llamada oficial. Sin fixtures."""
import argparse
import json
from pathlib import Path

import httpx

from sunat.excel import now, valid_ruc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ruc', default='20100047218')
    parser.add_argument('--url', default='http://sunat-api:8001')
    args = parser.parse_args()
    if not valid_ruc(args.ruc):
        raise SystemExit('RUC inválido')
    response = httpx.get(f'{args.url}/ruc/{args.ruc}', timeout=40)
    result = {'fecha': now(), 'peticion': {'metodo': 'GET', 'ruc': args.ruc},
              'http_status': response.status_code, 'respuesta': response.json()}
    result['passed'] = (response.status_code == 200 and result['respuesta'].get('estado_consulta_api') == 'VERIFICADO'
                        and result['respuesta'].get('datos', {}).get('ruc') == args.ruc
                        and result['respuesta'].get('fuentes', {}).get('consulta_en_vivo', {}).get('http_status') == 200)
    path = Path('evidencias/sunat_api')
    path.mkdir(parents=True, exist_ok=True)
    (path / f'{args.ruc}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
