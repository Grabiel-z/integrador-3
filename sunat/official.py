"""Servicios públicos oficiales: SOAP en vivo y padrón diario descargable.

No sustituye la fecha de inicio por la inscripción ni por fechas del padrón.
Nunca registra la respuesta SOAP íntegra: solo conserva campos públicos permitidos.
"""
import argparse
import csv
import hashlib
import json
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import httpx

from sunat.excel import now, read_input, valid_ruc, write_results
from sunat.storage import worker_lock, save_json
from sunat.activity import ActivitySourceError, get_activity, cached_activity, enrich

SOAP_URL = 'https://ww1.sunat.gob.pe/cl-ti-iaconsultaruc-ws/ServicioRucAdmColService.htm'
PADRON_URL = 'https://www2.sunat.gob.pe/padron_reducido_ruc.zip'
SOAP_NS = 'http://service.consultarucws.registro.servicio2.sunat.gob.pe/'
PUBLIC_FIELDS = {'numRuc', 'nombre', 'estadoDesc', 'flag22Desc', 'ubigeoRuc', 'indError'}
PENDING = 'PENDIENTE DE OTRA INTERVENCIÓN'


class OfficialServiceError(RuntimeError):
    def __init__(self, message, http_status=None, retryable=False):
        super().__init__(message)
        self.http_status = http_status
        self.retryable = retryable


def parse_soap(content, expected_ruc):
    if len(content) > 1024 * 1024:
        raise OfficialServiceError('Respuesta SOAP demasiado grande')
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise OfficialServiceError('El servicio oficial no devolvió XML válido') from exc
    # La lista permitida evita conservar cualquier otro campo del servicio.
    public = {e.tag.split('}')[-1]: (e.text or '').strip()
              for e in root.iter() if e.tag.split('}')[-1] in PUBLIC_FIELDS}
    if public.get('indError') != '0':
        raise OfficialServiceError('SUNAT devolvió error o un RUC no disponible')
    if public.get('numRuc') != expected_ruc:
        raise OfficialServiceError('SUNAT devolvió un RUC distinto al solicitado', retryable=True)
    if not all(public.get(k) for k in ('nombre', 'estadoDesc', 'flag22Desc')):
        raise OfficialServiceError('La respuesta SOAP carece de campos públicos obligatorios')
    return public


def query_soap(ruc, client=None):
    if not valid_ruc(ruc):
        raise ValueError('RUC inválido: debe ser texto de once dígitos con verificador válido')
    envelope = (f'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
                f'xmlns:q="{SOAP_NS}"><s:Body><q:buscarRuc><arg0>{ruc}</arg0>'
                '</q:buscarRuc></s:Body></s:Envelope>')
    owned = client is None
    client = client or httpx.Client(timeout=45)
    started = time.perf_counter()
    try:
        for attempt in (1, 2):
            try:
                response = client.post(SOAP_URL, content=envelope,
                                       headers={'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': '""'})
                if response.status_code != 200:
                    raise OfficialServiceError(f'Servicio SOAP oficial respondió HTTP {response.status_code}',
                        response.status_code, retryable=response.status_code in (500, 502, 503, 504))
                public = parse_soap(response.content, ruc)
                return {'ruc': ruc, 'campos': public, 'fuente': SOAP_URL, 'operacion': 'buscarRuc',
                        'fecha_consulta': now(), 'http_status': response.status_code, 'intentos': attempt,
                        'duracion_segundos': round(time.perf_counter() - started, 3)}
            except httpx.HTTPError as exc:
                # No se registra el cuerpo ni cabeceras de una respuesta ajena.
                if attempt == 2:
                    raise OfficialServiceError('Fallo de transporte SOAP: ' + type(exc).__name__) from exc
            except OfficialServiceError as exc:
                # Un RUC cruzado nunca entra en los resultados. Solo se permite
                # un reintento; 401/403/429 y errores de contenido no se reintentan.
                if not exc.retryable or attempt == 2:
                    raise
            time.sleep(1)
    finally:
        if owned:
            client.close()


def download_padron(cache=Path('.cache/sunat')):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    target, meta_path = cache / 'padron.zip', cache / 'padron_metadata.json'
    with httpx.Client(timeout=httpx.Timeout(120, connect=30), follow_redirects=False) as client:
        head = client.head(PADRON_URL)
        head.raise_for_status()
        etag, modified = head.headers.get('etag'), head.headers.get('last-modified')
        size = int(head.headers.get('content-length', '0'))
        old = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        # El hash impide reutilizar una descarga local dañada.
        if etag and old.get('etag') == etag and target.exists() and target.stat().st_size == size:
            with target.open('rb') as source:
                matches = hashlib.file_digest(source, 'sha256').hexdigest() == old.get('sha256')
            if matches:
                return target, {**old, 'comprobacion_version': now(), 'cache_reutilizada': True}
        part = target.with_suffix('.part')
        digest, count, last_progress = hashlib.sha256(), 0, 0
        try:
            with client.stream('GET', PADRON_URL) as response:
                # Una respuesta parcial, HTML o una redirección nunca es un padrón válido.
                if response.status_code != 200:
                    raise OfficialServiceError(f'Descarga oficial respondió HTTP {response.status_code}')
                declared = int(response.headers.get('content-length', '0'))
                with part.open('wb') as output:
                    for chunk in response.iter_bytes(1024 * 1024):
                        output.write(chunk)
                        digest.update(chunk)
                        count += len(chunk)
                        if count - last_progress >= 32 * 1024 * 1024:
                            print(f'Descarga oficial: {count // 1048576} MiB', flush=True)
                            last_progress = count
                if declared and count != declared:
                    raise OfficialServiceError('Descarga oficial truncada')
                # Se registra la versión del GET, que puede haber cambiado desde el HEAD.
                etag = response.headers.get('etag', etag)
                modified = response.headers.get('last-modified', modified)
            if not zipfile.is_zipfile(part):
                raise OfficialServiceError('La descarga oficial no contiene un ZIP')
            part.replace(target)
            meta = {'url': PADRON_URL, 'fecha_descarga': now(), 'last_modified': modified,
                    'etag': etag, 'bytes': count, 'sha256': digest.hexdigest(), 'http_status': 200,
                    'cache_reutilizada': False}
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
            return target, meta
        finally:
            part.unlink(missing_ok=True)


def select_padron(path, rucs):
    wanted, selected = set(rucs), {}
    with zipfile.ZipFile(path) as archive:
        members = [i for i in archive.infolist() if i.filename.lower().endswith('.txt') and not i.is_dir()]
        if len(members) != 1:
            raise OfficialServiceError('Formato inesperado del ZIP oficial')
        with archive.open(members[0]) as source:
            header = source.readline().decode('latin-1').strip().split('|')
            required = {'RUC', 'NOMBRE O RAZÓN SOCIAL', 'CONDICIÓN DE DOMICILIO', 'UBIGEO', 'NOMBRE DE VÍA'}
            if not required.issubset(header):
                raise OfficialServiceError('El padrón oficial cambió de columnas')
            for line in source:
                # Solo se conservan las veinte empresas solicitadas. Se lee hasta EOF
                # para que zipfile compruebe también el CRC del archivo descomprimido.
                ruc = line[:11].decode('ascii', errors='ignore')
                if ruc in wanted:
                    values = next(csv.reader([line.decode('latin-1').rstrip('\r\n')], delimiter='|'))
                    row = dict(zip(header, values))
                    if row.get('RUC') != ruc or ruc in selected:
                        raise OfficialServiceError('Registro duplicado o inconsistente en padrón')
                    selected[ruc] = {k: v.strip() for k, v in row.items() if k}
    return selected


def fiscal_address(row):
    def field(key):
        value = row.get(key, '').strip()
        return '' if not value or set(value) == {'-'} else value
    pieces = [' '.join(filter(None, [field('TIPO DE VÍA'), field('NOMBRE DE VÍA')]))]
    for key, label in [('NÚMERO', 'NRO.'), ('INTERIOR', 'INT.'), ('LOTE', 'LOTE'),
                       ('DEPARTAMENTO', 'DPTO.'), ('MANZANA', 'MZ.'), ('KILÓMETRO', 'KM.')]:
        if field(key):
            pieces.append(f'{label} {field(key)}')
    zone = ' '.join(filter(None, [field('CÓDIGO DE ZONA'), field('TIPO DE ZONA')]))
    if zone:
        pieces.append(zone)
    # La columna DEPARTAMENTO del domicilio es el apartamento, no la región.
    # Se conserva el UBIGEO sin inventar nombres de departamento/provincia/distrito.
    if not any(pieces):
        return ''
    if field('UBIGEO'):
        pieces.append('UBIGEO ' + field('UBIGEO'))
    return '; '.join(filter(None, pieces))


def assemble(soap, padron=None, metadata=None):
    fields = soap['campos']
    address = fiscal_address(padron) if padron else ''
    missing = ['Fecha de inicio de actividades']
    if not address:
        missing.insert(0, 'Dirección fiscal')
    # No se mezclan silenciosamente versiones con ubigeos discrepantes.
    mismatch = bool(padron and fields.get('ubigeoRuc') != padron.get('UBIGEO'))
    if mismatch:
        address = ''
        if 'Dirección fiscal' not in missing:
            missing.insert(0, 'Dirección fiscal')
    notes = ('Consulta SOAP oficial en vivo; domicilio del padrón oficial diario, no de una ficha en vivo. '
             'La fecha de inicio no está publicada en estas dos fuentes; requiere ficha oficial. ')
    if mismatch:
        notes += 'UBIGEO discrepante entre SOAP y padrón: domicilio no incorporado. '
    if metadata:
        notes += 'Versión del padrón: ' + str(metadata.get('last_modified', 'sin fecha')) + '. '
    return {'RUC': soap['ruc'], 'Razón social': fields['nombre'], 'Dirección fiscal': address,
            'Condición del domicilio fiscal': fields['flag22Desc'], 'Fecha de inicio de actividades': '',
            'Estado de consulta': PENDING, 'Fecha de consulta': soap['fecha_consulta'],
            'Observaciones': notes.strip(), 'Estado del contribuyente': fields['estadoDesc'],
            'UBIGEO': fields.get('ubigeoRuc', ''), 'Campos pendientes': missing,
            'Fuentes': {'consulta_en_vivo': soap, 'padron': metadata if padron else None}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default='datos/RUC_entrada.xlsx')
    parser.add_argument('--output', default='datos/RUC_resultados.xlsx')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--retry-errors', action='store_true', help='Reprocesa solo filas incompletas y conserva las verificadas')
    args = parser.parse_args(argv)
    all_rucs = read_input(args.input)
    rucs = all_rucs[:args.limit]
    path, metadata = download_padron()
    selected = select_padron(path, all_rucs)
    save_json('datos/sunat_padron_seleccion.json', {'metadata': metadata, 'registros': selected})
    evidence = Path('evidencias/sunat_soap')
    evidence.mkdir(parents=True, exist_ok=True)
    checkpoint = Path('datos/sunat_checkpoint.json')
    old = {r['RUC']: r for r in json.loads(checkpoint.read_text())} if checkpoint.exists() else {}
    if checkpoint.exists() and not Path('evidencias/sunat_checkpoint_formulario_anterior.json').exists():
        Path('evidencias/sunat_checkpoint_formulario_anterior.json').write_bytes(checkpoint.read_bytes())
    history = Path('evidencias/sunat_resumen.json')
    previous_calls = json.loads(history.read_text()).get('llamadas', []) if args.retry_errors and history.exists() else []
    records, calls = [], []
    blocked = ''
    activity_blocked = ''
    with httpx.Client(timeout=45) as client:
        for ruc in rucs:
            pause = 1
            if args.retry_errors and old.get(ruc, {}).get('Estado de consulta') == 'VERIFICADO':
                records.append(old[ruc])
                continue
            if blocked:
                record = old.get(ruc) if old.get(ruc, {}).get('Estado de consulta') == 'VERIFICADO' else {
                    'RUC': ruc, 'Estado de consulta': 'BLOQUEADO POR RESTRICCIÓN EXTERNA',
                    'Fecha de consulta': '', 'Observaciones': blocked + '; no se envió otra solicitud'}
                records.append(record)
                continue
            try:
                soap = query_soap(ruc, client)
                (evidence / f'{ruc}.json').write_text(json.dumps(soap, ensure_ascii=False, indent=2))
                record = assemble(soap, selected.get(ruc), metadata)
                try:
                    if activity_blocked:
                        detail = cached_activity(ruc, record['Razón social'])
                        if not detail:
                            raise ActivitySourceError(activity_blocked)
                    else:
                        detail = get_activity(ruc, record['Razón social'], client)
                    record = enrich(record, detail)
                    if not detail.get('cache_reutilizada'):
                        pause = 3
                except ActivitySourceError as exc:
                    # Conserva una ficha completa previa si falla la fuente
                    # complementaria, sin fabricar una fecha para las demás.
                    if old.get(ruc, {}).get('Estado de consulta') == 'VERIFICADO':
                        record = {**old[ruc], 'Ultima comprobacion SOAP': soap,
                                  'Aviso fuente complementaria': str(exc)}
                    else:
                        record['Observaciones'] += ' Fuente complementaria: ' + str(exc)
                    if exc.http_status in (401, 403, 429):
                        activity_blocked = str(exc)
                calls.append({'ruc': ruc, 'http_status': soap['http_status'], 'resultado': 'VERIFICADO',
                              'intentos': soap.get('intentos', 1), 'fecha_consulta': soap['fecha_consulta']})
            except OfficialServiceError as exc:
                record = old.get(ruc) if old.get(ruc, {}).get('Estado de consulta') == 'VERIFICADO' else {'RUC': ruc, 'Estado de consulta': 'ERROR IDENTIFICADO',
                          'Fecha de consulta': now(), 'Observaciones': str(exc)}
                calls.append({'ruc': ruc, 'resultado': 'ERROR IDENTIFICADO', 'error': str(exc)})
                if exc.http_status in (401, 403, 429):
                    blocked = str(exc)
            records.append(record)
            write_results(args.output, records)
            # Conserva también las filas aún no procesadas de una ejecución anterior.
            merged = {**old, **{r['RUC']: r for r in records}}
            save_json(checkpoint, [merged[r] for r in all_rucs if r in merged])
            print(ruc, record.get('Razón social', ''), record['Estado de consulta'], flush=True)
            time.sleep(pause)
    # --limit no elimina del checkpoint las demás filas previamente existentes.
    merged = {**old, **{r['RUC']: r for r in records}}
    save_json(checkpoint, [merged[r] for r in all_rucs if r in merged])
    write_results(args.output, records)
    completos = sum(r.get('Estado de consulta') == 'VERIFICADO' for r in records)
    all_calls = previous_calls + calls
    summary = {'fecha': now(), 'total': len(rucs), 'completos': completos,
               'bloqueados': sum(r.get('Estado de consulta') == 'BLOQUEADO POR RESTRICCIÓN EXTERNA' for r in records),
               'soap_consultas_reales': len(all_calls), 'soap_solicitudes_esta_ejecucion': len(calls),
               'soap_exitosas': len({c['ruc'] for c in all_calls if c['resultado'] == 'VERIFICADO'}),
               'domicilios_padron': sum(bool(r.get('Dirección fiscal')) for r in records),
               'domicilios_con_datos': sum(bool(r.get('Dirección fiscal')) for r in records),
               'fechas_inicio_obtenidas': sum(bool(r.get('Fecha de inicio de actividades')) for r in records),
               'consolidados_multifuente': sum(r.get('Tipo de resultado') == 'Consolidado multifuente' for r in records),
               'fichas_oficiales_guardadas': len(list(Path('evidencias/sunat_asistido').glob('[0-9]*.json'))),
               'padron': metadata, 'llamadas': all_calls, 'registros': records}
    save_json('evidencias/sunat_resumen.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in {'registros', 'llamadas', 'padron'}}, indent=2))
    # La ejecución parcial nunca se presenta como cumplimiento de los cinco campos.
    raise SystemExit(0 if completos == len(rucs) else 2)


if __name__ == '__main__':
    with worker_lock():
        main()
