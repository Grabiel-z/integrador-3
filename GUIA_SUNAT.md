# SUNAT automático: prueba real y límites de campos

La ruta principal no abre un navegador ni solicita CAPTCHA. Usa el servicio **SOAP oficial de SUNAT**, operación `buscarRuc`, y su padrón diario descargable para el domicilio. No necesita token comercial, clave SOL ni intervención humana durante una consulta.

## Prueba rápida

Con la imagen construida mediante el instalador:

```sh
docker compose up -d --wait sunat-api
docker compose run --rm --no-deps test-runner python -m tools.probe_sunat_api --ruc 20100047218
```

También puedes abrir http://localhost:8001/ruc/20100047218. Una llamada válida produce un POST real desde el contenedor hacia SUNAT, incluso si ese RUC ya se consultó anteriormente. El resultado incluye URL, operación, fecha, HTTP de origen y campos públicos. El cliente no registra íntegramente el XML ni conserva campos ajenos a su lista permitida.

Para comprobar la conectividad desde el contenedor n8n:

```sh
docker compose exec -T n8n node --input-type=module < pruebas/test_sunat_live.mjs
```

Esta última prueba ejecuta HTTP en el runtime de n8n; no simula una conversación ni afirma ejecutar un workflow. Un nodo HTTP Request de n8n puede usar `GET http://sunat-api:8001/ruc/20100047218`. El chatbot del restaurante y el lote tributario son los dos procesos independientes de esta tarea; la atención del restaurante no depende del formulario SUNAT.

## Campos y procedencia

| Campo | Fuente | Comportamiento |
|---|---|---|
| RUC, razón social, estado, condición y UBIGEO | SOAP oficial en vivo | Una petición por consulta válida; sin reintentos ante un rechazo |
| Dirección fiscal | Padrón reducido oficial diario | Descarga automatizada, con versión, hash y CRC; selecciona las veinte empresas del lote |
| Fecha de inicio de actividades | No publicada en esas dos fuentes | La API devuelve `null` y la incluye en `campos_pendientes` |

`ficha_completa=false` es deliberado: HTTP 200 acredita la consulta de los campos disponibles, no el cumplimiento de los cinco campos académicos. Estado ACTIVO no sustituye condición HABIDO; fecha de inscripción y fecha de descarga tampoco sustituyen inicio de actividades.

Para un RUC que no esté en la selección del padrón, la API consulta igualmente SOAP y devuelve domicilio `null`, señalado como pendiente. No inventa una dirección. La fecha de inicio observada una vez en una prueba de navegador se conserva con su evidencia en el Excel, pero no se presenta como un dato entregado por SOAP.

## Regenerar el lote

```sh
docker compose run --rm --no-deps sunat-worker
```

Es la nueva ruta predeterminada de `sunat.main`. Primero comprueba la versión del padrón oficial; descarga aproximadamente 395 MB cuando cambia y conserva una caché local excluida de Git, imagen y ZIP. Después realiza veinte consultas SOAP reales, con un segundo de separación, y genera checkpoint y Excel. No instalar aplicaciones en el anfitrión ni ejecutar dos workers sobre el mismo lote.

El proceso devuelve código **2** mientras falte cualquiera de los cinco campos requeridos. Eso permite que una revisión académica detecte la entrega incompleta aunque la conexión API funcione. Una ficha completa anterior no se borra por una consulta SOAP posterior que carezca de fecha de inicio.

La dirección conserva los componentes oficiales y el UBIGEO. La columna DEPARTAMENTO del padrón corresponde al departamento/apartamento del inmueble; no se interpreta como región. No se mezclan domicilios si el UBIGEO del padrón y el servicio en vivo discrepan.

## Qué falta para los cinco campos automáticos

Se verificaron veinte respuestas SOAP HTTP 200 y veinte direcciones del padrón. El servicio SOAP publicado no tiene un campo de fecha de inicio. El formulario individual mostró un control humano después de una ficha completa; por petición del usuario se retiró el visor y no forma parte de la solución.

Para cerrar automáticamente ese campo se necesita una fuente adicional autorizada que lo exponga. Un proveedor externo con ficha completa suele exigir una credencial; no se ha contratado ni configurado ninguno, ni se lo presenta como SUNAT directo. Mientras no exista una integración real probada para ese campo, siguen pendientes diecinueve fechas en el Excel y veinte en la respuesta SOAP en vivo. No se ofrece una tarea manual como solución operativa.

## Evidencias y fallos

- `evidencias/sunat_soap/`: veinte respuestas públicas seleccionadas del servicio real.
- `evidencias/sunat_api/`: prueba del endpoint automático y procedencia oficial.
- `evidencias/sunat_n8n_http.json`: prueba HTTP desde n8n, cuando se ejecute el comando de integración.
- `datos/sunat_padron_seleccion.json`: veinte filas oficiales y metadatos de descarga.
- `evidencias/sunat_resumen.json`: resumen del lote; `datos/RUC_resultados.xlsx`: entrega tabular.

RUC inválido: HTTP 422 sin consultar SUNAT. Consulta simultánea: HTTP 429 local. Rechazo, XML inválido, RUC diferente o fallo de transporte del origen: HTTP 502; no se devuelve una respuesta inventada. `/health` comprueba el cliente, no la disponibilidad de SUNAT. Los tests con fixtures verifican estos contratos; las pruebas HTTP anteriores son las que demuestran conexión real.

Fuentes: [contrato SOAP oficial](https://ww1.sunat.gob.pe/cl-ti-iaconsultaruc-ws/ServicioRucAdmColService.htm?wsdl), [padrón reducido SUNAT](https://www.sunat.gob.pe/descargaPRR/mrc137_padron_reducido.html) y [definición oficial de los campos](https://orientacion.sunat.gob.pe/padron-reducido-del-ruc-para-descarga).
