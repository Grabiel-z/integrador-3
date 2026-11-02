"""Inicio de actividades de una ficha pública permitida por robots.txt.

Fuente complementaria independiente: ElRUC.pe. No usa su API autenticada ni
presenta el dato como una respuesta del SOAP de SUNAT.
"""
import hashlib
import json
import re
import time
import unicodedata
import urllib.robotparser
from datetime import date, datetime
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from sunat.excel import HEADERS, now, valid_ruc

HOST = 'https://elruc.pe'
AGENT = 'TA4-Academic-RUC/1.0'
MONTHS = {name: n for n, name in enumerate(('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                                          'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'), 1)}


class ActivitySourceError(RuntimeError):
    def __init__(self, message, http_status=None):
        super().__init__(message)
        self.http_status = http_status


def cached_activity(ruc, name):
    path = Path('datos/sunat_fechas_inicio.json')
    if not path.exists():
        return None
    try:
        detail = json.loads(path.read_text()).get('registros', {}).get(ruc)
        if not detail or detail.get('http_status') != 200 or detail.get('ruc') != ruc:
            return None
        age = datetime.now(ZoneInfo('America/Lima')) - datetime.fromisoformat(detail['fecha_consulta'])
        if not 0 <= age.total_seconds() < 86400 or identity(detail['razon_social']) != identity(name):
            return None
        return {**detail, 'cache_reutilizada': True}
    except (ValueError, TypeError, KeyError):
        return None


def get_activity(ruc, name, client):
    return cached_activity(ruc, name) or ActivitySource(client).query(ruc, name)


def identity(value):
    plain = ''.join(c for c in unicodedata.normalize('NFD', value.upper()) if unicodedata.category(c) != 'Mn')
    return ''.join(c for c in plain if c.isalnum())


def activity_date(value):
    match = re.fullmatch(r'(\d{1,2}) de ([a-z]+) de (\d{4})', value.lower().strip())
    if not match or match[2] not in MONTHS:
        raise ActivitySourceError('La fuente no publica una fecha completa de inicio de actividades')
    try:
        result = date(int(match[3]), MONTHS[match[2]], int(match[1]))
    except ValueError as exc:
        raise ActivitySourceError('Fecha de inicio de actividades inválida') from exc
    if result > datetime.now(ZoneInfo('America/Lima')).date():
        raise ActivitySourceError('Fecha de inicio futura; no se incorpora')
    return result


def parse_activity(html, ruc, name):
    soup = BeautifulSoup(html, 'html.parser')
    matches = []
    for dl in soup.select('dl'):
        fields = {dt.get_text(' ', strip=True): dt.find_next_sibling('dd').get_text(' ', strip=True)
                  for dt in dl.select('dt') if dt.find_next_sibling('dd')}
        # La tarjeta superior solo muestra el año: se exige el bloque que
        # contiene la identidad tributaria y las dos fechas por separado.
        if fields.get('RUC') == ruc:
            matches.append(fields)
    if len(matches) != 1:
        raise ActivitySourceError('RUC no encontrado o ambiguo en la ficha pública')
    fields = matches[0]
    if identity(fields.get('Razón social', '')) != identity(name):
        raise ActivitySourceError('La razón social pública no coincide con SUNAT; no se mezclan identidades')
    parsed = activity_date(fields.get('Inicio de actividades', ''))
    verified = re.search(r'verificados el ([^.]+)\.', soup.get_text(' ', strip=True), re.IGNORECASE)
    return {'ruc': ruc, 'razon_social': fields['Razón social'], 'fecha': parsed.strftime('%d/%m/%Y'),
            'fecha_iso': parsed.isoformat(), 'valor_observado': fields['Inicio de actividades'],
            'inscripcion_observada': fields.get('Inscripción en el RUC'),
            'verificacion_declarada_por_fuente': verified[1] if verified else None}


class ActivitySource:
    def __init__(self, client):
        self.client = client
        self.robots = None
        self.robots_time = 0

    def policy(self):
        if self.robots is not None and time.monotonic() - self.robots_time < 600:
            return self.robots
        response = self.client.get(HOST + '/robots.txt', headers={'User-Agent': AGENT}, follow_redirects=False)
        if response.status_code != 200:
            raise ActivitySourceError('No se pudo comprobar robots.txt de la fuente complementaria', response.status_code)
        policy = urllib.robotparser.RobotFileParser()
        policy.parse(response.text.splitlines())
        self.robots = policy
        self.robots_time = time.monotonic()
        return policy

    def query(self, ruc, name):
        if not valid_ruc(ruc) or not ruc.startswith('20'):
            raise ActivitySourceError('La fuente complementaria solo se usa con RUC de empresas válidos')
        try:
            policy = self.policy()
            url = HOST + '/ruc/' + ruc
            for _ in range(4):
                parsed = urlsplit(url)
                if (parsed.scheme != 'https' or parsed.netloc != 'elruc.pe' or parsed.query
                        or not re.fullmatch(r'/ruc/' + ruc + r'(?:-[^/]+)?', parsed.path)):
                    raise ActivitySourceError('Redirección fuera de la ficha pública permitida')
                if not policy.can_fetch(AGENT, url):
                    raise ActivitySourceError('robots.txt no permite leer esta ficha pública')
                response = self.client.get(url, headers={'User-Agent': AGENT}, follow_redirects=False)
                if response.status_code in (301, 302, 303, 307, 308):
                    url = urljoin(url, response.headers.get('location', ''))
                    continue
                if response.status_code != 200:
                    raise ActivitySourceError(f'Ficha pública respondió HTTP {response.status_code}', response.status_code)
                if 'text/html' not in response.headers.get('content-type', '').lower():
                    raise ActivitySourceError('La ficha pública no devolvió HTML')
                if len(response.content) > 4 * 1024 * 1024:
                    raise ActivitySourceError('Ficha pública excede el tamaño permitido')
                result = parse_activity(response.text, ruc, name)
                result.update({'url': url, 'fuente': 'ElRUC.pe — ficha pública, fuente complementaria independiente',
                               'fecha_consulta': now(), 'http_status': response.status_code,
                               'sha256_respuesta': hashlib.sha256(response.content).hexdigest(),
                               'robots_url': HOST + '/robots.txt', 'robots_permite_ficha': True,
                               'requiere_token': False, 'intervencion_humana': False})
                return result
            raise ActivitySourceError('Demasiadas redirecciones de la ficha pública')
        except httpx.HTTPError as exc:
            raise ActivitySourceError('Fallo de transporte de fuente complementaria: ' + type(exc).__name__) from exc


def enrich(record, detail):
    if detail['ruc'] != record['RUC'] or identity(detail['razon_social']) != identity(record['Razón social']):
        raise ActivitySourceError('Identidad incompatible al consolidar fecha de inicio')
    result = {**record, 'Fuentes': {**record.get('Fuentes', {}), 'inicio_actividades': detail},
              'Fecha de inicio de actividades': detail['fecha'], 'Tipo de resultado': 'Consolidado multifuente'}
    missing = [field for field in HEADERS[:5] if not result.get(field)]
    result['Campos pendientes'] = missing
    result['Estado de consulta'] = 'VERIFICADO' if not missing else 'PENDIENTE DE OTRA INTERVENCIÓN'
    result['Observaciones'] = ('SUNAT SOAP oficial en vivo; domicilio del padrón oficial diario. '
        'Inicio de actividades de ficha pública ElRUC.pe: ' + detail['url'] + '. '
        'Fecha consultada allí: ' + detail['fecha_consulta'] + '. Resultado consolidado multifuente, sin intervención humana.')
    return result
