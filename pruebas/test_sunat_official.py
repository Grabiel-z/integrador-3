"""Contratos sintéticos: la integración real queda en evidencias/sunat_soap/."""
import zipfile
import json
from pathlib import Path

import httpx
import pytest
from openpyxl import Workbook
from sunat import official

from sunat.official import (OfficialServiceError, SOAP_URL, assemble, fiscal_address,
                            parse_soap, query_soap, select_padron)

RUC = '20100047218'
XML = b'''<Envelope><Body><buscarRucResponse><return>
<numRuc>20100047218</numRuc><nombre> EMPRESA SINTETICA </nombre>
<estadoDesc>ACTIVO</estadoDesc><flag22Desc>HABIDO</flag22Desc>
<ubigeoRuc>150114</ubigeoRuc><indError>0</indError>
<claveSol>ESTE_CAMPO_NO_DEBE_CONSERVARSE</claveSol>
</return></buscarRucResponse></Body></Envelope>'''


def test_real_contract_posts_ruc_and_retains_only_public_fields():
    def handle(request):
        assert str(request.url) == SOAP_URL
        assert request.method == 'POST'
        assert b'<arg0>20100047218</arg0>' in request.content
        assert request.headers['soapaction'] == '""'
        return httpx.Response(200, content=XML)
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        result = query_soap(RUC, client)
    assert result['campos']['nombre'] == 'EMPRESA SINTETICA'
    assert result['http_status'] == 200
    assert 'claveSol' not in result['campos']
    assert 'ESTE_CAMPO_NO_DEBE_CONSERVARSE' not in str(result)


@pytest.mark.parametrize('content', [b'<html>Denied</html>', b'not xml',
    XML.replace(b'<indError>0', b'<indError>1'), XML.replace(b'20100047218', b'20100130204')])
def test_http_200_does_not_mean_success(content):
    with pytest.raises(OfficialServiceError):
        parse_soap(content, RUC)


def test_blocked_service_not_retried_or_reported_success():
    calls = []
    def handle(request):
        calls.append(request)
        return httpx.Response(403, text='Denied')
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        with pytest.raises(OfficialServiceError, match='403'):
            query_soap(RUC, client)
    assert len(calls) == 1


def test_selected_padron_rows_and_source_fields(tmp_path):
    path = tmp_path / 'fixture.zip'
    lines = ('RUC|NOMBRE O RAZÓN SOCIAL|CONDICIÓN DE DOMICILIO|UBIGEO|NOMBRE DE VÍA|\n'
             '20100047218|EMPRESA SINTETICA|HABIDO|150114|PRUEBA|\n'
             '20100130204|OTRA EMPRESA|HABIDO|150131|OTRA VIA|\n')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('padron.txt', lines.encode('latin-1'))
    selected = select_padron(path, [RUC])
    assert list(selected) == [RUC]
    assert selected[RUC]['NOMBRE DE VÍA'] == 'PRUEBA'


def test_missing_activity_date_never_fabricated_or_marked_complete():
    soap = {'ruc': RUC, 'fecha_consulta': '2026-11-02T09:00:00-05:00', 'campos': parse_soap(XML, RUC)}
    row = {'TIPO DE VÍA': 'AV.', 'NOMBRE DE VÍA': 'PRUEBA', 'NÚMERO': '100',
           'DEPARTAMENTO': '302', 'UBIGEO': '150114'}
    result = assemble(soap, row, {'last_modified': 'VERSION SINTETICA'})
    assert result['Fecha de inicio de actividades'] == ''
    assert result['Campos pendientes'] == ['Fecha de inicio de actividades']
    assert result['Estado de consulta'] == 'PENDIENTE DE OTRA INTERVENCIÓN'
    assert 'DPTO. 302' in result['Dirección fiscal']
    assert 'UBIGEO 150114' in result['Dirección fiscal']
    row['UBIGEO'] = '150131'
    assert assemble(soap, row)['Dirección fiscal'] == ''
    assert fiscal_address({'UBIGEO': '150114'}) == ''
    assert fiscal_address({'TIPO DE VÍA': '----', 'NOMBRE DE VÍA': 'PRUEBA'}) == 'PRUEBA'


def batch_fixture(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    Path('datos').mkdir()
    Path('evidencias').mkdir()
    workbook = Workbook()
    workbook.active.append(['RUC'])
    workbook.active.append([RUC])
    workbook.active.append(['20100130204'])
    workbook.save('datos/RUC_entrada.xlsx')
    monkeypatch.setattr(official, 'download_padron', lambda: (tmp_path / 'fixture.zip', {'last_modified': 'VERSION SINTETICA'}))
    monkeypatch.setattr(official, 'select_padron', lambda *args: {})
    monkeypatch.setattr(official.time, 'sleep', lambda *args: None)


def test_batch_stops_requests_after_access_rejection(monkeypatch, tmp_path):
    batch_fixture(monkeypatch, tmp_path)
    calls = []
    def reject(ruc, client):
        calls.append(ruc)
        raise OfficialServiceError('HTTP 403', 403)
    monkeypatch.setattr(official, 'query_soap', reject)
    with pytest.raises(SystemExit) as exit:
        official.main([])
    assert exit.value.code == 2
    assert calls == [RUC]
    rows = json.loads(Path('datos/sunat_checkpoint.json').read_text())
    assert rows[1]['Estado de consulta'] == 'BLOQUEADO POR RESTRICCIÓN EXTERNA'
    assert rows[1]['Fecha de consulta'] == ''
    assert json.loads(Path('evidencias/sunat_resumen.json').read_text())['soap_consultas_reales'] == 1


def test_limited_batch_preserves_complete_fields_and_other_checkpoint_rows(monkeypatch, tmp_path):
    batch_fixture(monkeypatch, tmp_path)
    complete = {'RUC': RUC, 'Razón social': 'EMPRESA SINTETICA', 'Dirección fiscal': 'VIA SINTETICA',
                'Condición del domicilio fiscal': 'HABIDO', 'Fecha de inicio de actividades': '01/01/2000',
                'Estado de consulta': 'VERIFICADO', 'Fecha de consulta': 'FECHA SINTETICA', 'Observaciones': 'FIXTURE'}
    other = {'RUC': '20100130204', 'Estado de consulta': 'PENDIENTE DE OTRA INTERVENCIÓN'}
    Path('datos/sunat_checkpoint.json').write_text(json.dumps([complete, other]))
    monkeypatch.setattr(official, 'query_soap', lambda ruc, client: {
        'ruc': ruc, 'campos': parse_soap(XML, ruc), 'http_status': 200, 'fecha_consulta': 'OTRA FECHA SINTETICA'})
    with pytest.raises(SystemExit) as exit:
        official.main(['--limit', '1'])
    assert exit.value.code == 0
    rows = json.loads(Path('datos/sunat_checkpoint.json').read_text())
    assert len(rows) == 2
    assert rows[0]['Fecha de inicio de actividades'] == '01/01/2000'
    assert rows[0]['Fecha de consulta'] == 'FECHA SINTETICA'
    assert rows[1] == other
