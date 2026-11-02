"""Pruebas del cliente HTTP. Las respuestas de este archivo son sintéticas."""
from fastapi.testclient import TestClient

from sunat import api
from sunat.official import OfficialServiceError, SOAP_URL


def test_invalid_ruc_makes_no_upstream_request(monkeypatch):
    def forbidden(*args):
        raise AssertionError('No debe llamar a SUNAT con un RUC inválido')
    monkeypatch.setattr(api, 'query_soap', forbidden)
    with TestClient(api.app) as client:
        assert client.get('/ruc/20100047219').status_code == 422


def test_api_reports_missing_fields_and_live_source(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    calls = []
    def query(ruc, client):
        calls.append(ruc)
        return {'ruc': ruc, 'fuente': SOAP_URL, 'fecha_consulta': 'FECHA SINTETICA', 'http_status': 200,
                'campos': {'nombre': 'EMPRESA SINTETICA', 'estadoDesc': 'ACTIVO', 'flag22Desc': 'HABIDO', 'ubigeoRuc': '150114'}}
    monkeypatch.setattr(api, 'query_soap', query)
    monkeypatch.setattr(api, 'get_activity', lambda *args: {'ruc': '20100047218', 'razon_social': 'EMPRESA SINTETICA',
        'fecha': '01/01/2000', 'fecha_iso': '2000-01-01', 'url': 'https://elruc.pe/ruc/20100047218',
        'fecha_consulta': 'FECHA SINTETICA'})
    with TestClient(api.app) as client:
        response = client.get('/ruc/20100047218')
    assert response.status_code == 200
    data = response.json()
    assert calls == ['20100047218']
    assert data['intervencion_humana'] is False
    assert data['datos']['fecha_inicio_actividades'] == '2000-01-01'
    assert data['datos']['direccion_fiscal'] is None
    assert data['ficha_completa'] is False
    assert set(data['campos_pendientes']) == {'Dirección fiscal'}
    assert data['fuentes']['consulta_en_vivo']['fuente'] == SOAP_URL


def test_upstream_error_is_502_and_releases_slot(monkeypatch):
    def fail(*args):
        raise OfficialServiceError('Servicio SOAP oficial respondió HTTP 403')
    monkeypatch.setattr(api, 'query_soap', fail)
    with TestClient(api.app) as client:
        for _ in range(2):
            assert client.get('/ruc/20100047218').status_code == 502
        assert client.get('/health').json()['status'] == 'ok'
