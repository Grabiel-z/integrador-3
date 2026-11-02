"""Prueba puntual del formulario oficial sin modificar resultados ni checkpoint."""
import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright
from sunat.main import URL, restriction
from sunat.parser import extract
from sunat.excel import valid_ruc, now


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ruc', default='20100047218')
    parser.add_argument('--headed', action='store_true')
    parser.add_argument('--wait-seconds', type=int, default=0)
    parser.add_argument('--url', default=URL)
    args = parser.parse_args()
    if not valid_ruc(args.ruc):
        raise SystemExit('RUC inválido')
    output = Path('evidencias/sunat_diagnostico') / ('navegador_actual' if args.headed else '.')
    output.mkdir(parents=True, exist_ok=True)
    result = {'fecha': now(), 'ruc': args.ruc, 'url': args.url, 'passed': False, 'headed': args.headed}
    start = time.perf_counter()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        page = browser.new_page(locale='es-PE')
        try:
            response = page.goto(args.url, wait_until='domcontentloaded', timeout=30000)
            result['http_status'] = response.status if response else None
            # Solo permite que cargue el JavaScript normal de la página. No pulsa
            # controles de seguridad ni intenta resolver verificaciones.
            if args.wait_seconds:
                page.wait_for_timeout(min(args.wait_seconds, 30) * 1000)
            result['browser_version'] = browser.version
            result['url_final'] = page.url
            result['title'] = page.title()
            result['restriction'] = restriction(page)
            if result['http_status'] in (401, 403, 429) or result['restriction']:
                result['error'] = 'El formulario oficial impide acceder; no se resolvió ni eludió el control'
            else:
                page.locator('#txtRuc, input[name="search1"]').first.fill(args.ruc)
                page.get_by_role('button', name='Buscar', exact=True).click()
                page.locator('.list-group').first.wait_for(timeout=30000)
                result['data'] = extract(page.content(), args.ruc)
                result['passed'] = result['data']['Estado de consulta'] == 'VERIFICADO'
        except Exception as exc:
            result['error'] = type(exc).__name__ + ': ' + str(exc)[:350]
        finally:
            result['elapsed_seconds'] = round(time.perf_counter() - start, 3)
            (output / 'formulario.html').write_text(page.content())
            page.screenshot(path=str(output / 'formulario.png'), full_page=True)
            browser.close()
    (output / 'formulario_resultado.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 2)


if __name__ == '__main__':
    main()
