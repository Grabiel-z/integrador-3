"""Fixtures sintéticos que reproducen la estructura de la fuente pública."""
from pathlib import Path

import httpx
import pytest

from sunat.activity import ActivitySourceError, ActivitySource, parse_activity, enrich
from sunat.official import assemble

RUC = '20100047218'
HTML = Path('pruebas/fixtures/elruc_sintetico.html').read_text()


def test_full_date_selected_instead_of_year_or_registration_date():
    data = parse_activity(HTML, RUC, 'EMPRESA SINTETICA')
    assert data['fecha_iso'] == '1889-04-09'
    assert data['fecha'] == '09/04/1889'


def test_wrong_identity_rejected():
    with pytest.raises(ActivitySourceError, match='RUC'):
        parse_activity(HTML, '20100130204', 'EMPRESA SINTETICA')
    with pytest.raises(ActivitySourceError, match='razón social'):
        parse_activity(HTML, RUC, 'OTRA EMPRESA')


@pytest.mark.parametrize('html', [
    HTML.replace('<div><dt>Inicio de actividades</dt><dd>9 de abril de 1889</dd></div>', ''),
    HTML.replace('9 de abril de 1889', '31 de febrero de 2020'),
    HTML.replace('9 de abril de 1889', '1889'),
    HTML.replace('9 de abril de 1889', '1 de enero de 2999')])
def test_missing_invalid_or_future_start_date_never_inferred(html):
    with pytest.raises(ActivitySourceError):
        parse_activity(html, RUC, 'EMPRESA SINTETICA')


def test_public_source_honors_robots_and_canonical_redirect():
    calls = []
    def handle(request):
        calls.append(str(request.url))
        if request.url.path == '/robots.txt':
            return httpx.Response(200, text='User-agent: *\nAllow: /ruc/\nDisallow: /api/\n')
        if request.url.path == '/ruc/' + RUC:
            return httpx.Response(301, headers={'Location': '/ruc/' + RUC + '-empresa-sintetica'})
        return httpx.Response(200, text=HTML, headers={'Content-Type': 'text/html'})
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        data = ActivitySource(client).query(RUC, 'EMPRESA SINTETICA')
    assert data['fecha'] == '09/04/1889'
    assert data['http_status'] == 200
    assert data['url'] == 'https://elruc.pe/ruc/' + RUC + '-empresa-sintetica'
    assert len(calls) == 3
    assert not any('/api/' in url for url in calls)


@pytest.mark.parametrize('mode', ['robots', 'blocked', 'redirect'])
def test_public_source_stops_at_restrictions(mode):
    paths = []
    def handle(request):
        paths.append(request.url.path)
        if request.url.path == '/robots.txt':
            return httpx.Response(200, text='User-agent: *\n' + ('Disallow: /ruc/\n' if mode == 'robots' else 'Allow: /\n'))
        if mode == 'redirect':
            return httpx.Response(302, headers={'Location': 'https://otro.example/private'})
        return httpx.Response(403, text='Denied')
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(ActivitySourceError):
            ActivitySource(client).query(RUC, 'EMPRESA SINTETICA')
    assert len(paths) == (1 if mode == 'robots' else 2)


def test_enrichment_preserves_official_fields_and_records_date_provenance():
    soap = {'ruc': RUC, 'fecha_consulta': 'FECHA SINTETICA', 'campos': {
        'nombre': 'EMPRESA SINTETICA', 'flag22Desc': 'HABIDO', 'estadoDesc': 'ACTIVO', 'ubigeoRuc': '150114'}}
    record = assemble(soap, {'NOMBRE DE VÍA': 'PRUEBA', 'UBIGEO': '150114'})
    detail = {**parse_activity(HTML, RUC, 'EMPRESA SINTETICA'), 'url': 'https://elruc.pe/ruc/' + RUC,
              'fecha_consulta': 'FECHA SINTETICA', 'http_status': 200}
    full = enrich(record, detail)
    assert full['Estado de consulta'] == 'VERIFICADO'
    assert full['Fecha de inicio de actividades'] == '09/04/1889'
    assert full['Campos pendientes'] == []
    assert full['Razón social'] == 'EMPRESA SINTETICA'
    assert full['Fuentes']['consulta_en_vivo'] == soap
    assert full['Fuentes']['inicio_actividades']['url'].startswith('https://elruc.pe/ruc/')
