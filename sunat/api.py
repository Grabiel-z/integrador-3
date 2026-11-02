"""API interna para n8n: cada consulta válida realiza un POST real a SUNAT."""
import json
import threading
import time
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException

from sunat.excel import valid_ruc
from sunat.official import OfficialServiceError, assemble, query_soap
from sunat.activity import ActivitySourceError, cached_activity, get_activity, enrich

app = FastAPI(title='TA4 - cliente de servicios oficiales SUNAT', version='1.0.0')
in_flight = threading.BoundedSemaphore(1)
activity_blocked_until = 0


@app.get('/health')
def health():
    # Salud del cliente; no afirma disponibilidad del servicio externo.
    return {'status': 'ok', 'proveedor': 'SUNAT SOAP oficial', 'intervencion_humana': False}


@app.get('/ruc/{ruc}')
def lookup(ruc: str):
    global activity_blocked_until
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
        detail = cached_activity(ruc, result['Razón social'])
        if detail is None:
            if time.monotonic() < activity_blocked_until:
                raise ActivitySourceError('Fuente complementaria temporalmente restringida; no se reintenta')
            try:
                with httpx.Client(timeout=35) as client:
                    detail = get_activity(ruc, result['Razón social'], client)
            except ActivitySourceError as exc:
                if exc.http_status in (401, 403, 429):
                    activity_blocked_until = time.monotonic() + 3600
                raise
        result = enrich(result, detail)
        return {'estado_consulta_api': 'VERIFICADO', 'intervencion_humana': False,
                'ficha_completa': not result['Campos pendientes'], 'campos_pendientes': result['Campos pendientes'],
                'tipo_resultado': 'Consolidado multifuente',
                'ficha_oficial_directa': False,
                'datos': {'ruc': ruc, 'razon_social': result['Razón social'],
                          'estado': result['Estado del contribuyente'],
                          'condicion': result['Condición del domicilio fiscal'],
                          'direccion_fiscal': result['Dirección fiscal'] or None,
                          'ubigeo': result['UBIGEO'], 'fecha_inicio_actividades': detail['fecha_iso']},
                'fuentes': result['Fuentes'],
                'aviso': 'RUC, razón social y condición: SUNAT SOAP en vivo. Domicilio: padrón oficial. '
                         'Inicio: ficha pública ElRUC.pe, fuente independiente identificada por campo. '
                         'No equivale a una ficha íntegra obtenida directamente del portal SUNAT.'}
    except (OfficialServiceError, ActivitySourceError) as exc:
        raise HTTPException(502, str(exc)) from exc
    finally:
        in_flight.release()
