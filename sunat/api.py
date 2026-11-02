"""API interna para n8n: cada consulta válida realiza un POST real a SUNAT."""
import json
import threading
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException

from sunat.excel import valid_ruc
from sunat.official import OfficialServiceError, assemble, query_soap

app = FastAPI(title='TA4 - cliente de servicios oficiales SUNAT', version='1.0.0')
in_flight = threading.BoundedSemaphore(1)


@app.get('/health')
def health():
    # Salud del cliente; no afirma disponibilidad del servicio externo.
    return {'status': 'ok', 'proveedor': 'SUNAT SOAP oficial', 'intervencion_humana': False}


@app.get('/ruc/{ruc}')
def lookup(ruc: str):
    if not valid_ruc(ruc):
        raise HTTPException(422, 'RUC inválido')
    if not in_flight.acquire(blocking=False):
        raise HTTPException(429, 'Hay una consulta en curso; vuelve a intentarlo después')
    try:
        with httpx.Client(timeout=httpx.Timeout(30, connect=10)) as client:
            soap = query_soap(ruc, client)
        path = Path('datos/sunat_padron_seleccion.json')
        padron = json.loads(path.read_text()) if path.exists() else {}
        row = padron.get('registros', {}).get(ruc)
        result = assemble(soap, row, padron.get('metadata'))
        # La fecha obtenida una vez por navegador se conserva en el Excel, pero
        # no se presenta como parte de la respuesta en vivo de esta API SOAP.
        return {'estado_consulta_api': 'VERIFICADO', 'intervencion_humana': False,
                'ficha_completa': False, 'campos_pendientes': result['Campos pendientes'],
                'datos': {'ruc': ruc, 'razon_social': result['Razón social'],
                          'estado': result['Estado del contribuyente'],
                          'condicion': result['Condición del domicilio fiscal'],
                          'direccion_fiscal': result['Dirección fiscal'] or None,
                          'ubigeo': result['UBIGEO'], 'fecha_inicio_actividades': None},
                'fuentes': result['Fuentes'],
                'aviso': 'SOAP en vivo; domicilio del padrón descargado para el lote. '
                         'La API oficial consultada no entrega fecha de inicio de actividades.'}
    except OfficialServiceError as exc:
        raise HTTPException(502, str(exc)) from exc
    finally:
        in_flight.release()
