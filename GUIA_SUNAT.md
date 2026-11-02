# Consulta automática de los cinco campos

**VERIFICADO:** veinte RUC con RUC, razón social, domicilio fiscal, condición e inicio de actividades. Consulta, consolidación y Excel se ejecutan en Docker, sin navegador, CAPTCHA, token comercial ni intervención humana.

## Procedencia por campo

| Campo | Fuente |
|---|---|
| RUC, razón social, estado, condición y UBIGEO | Servicio SOAP oficial de SUNAT, consultado en vivo en cada petición válida |
| Domicilio fiscal | Padrón reducido oficial de SUNAT, con versión y hash de descarga |
| Fecha de inicio de actividades | Ficha pública de ElRUC.pe, consultada automáticamente y cotejada por RUC y razón social |

Es un **consolidado multifuente**. ElRUC.pe es independiente de SUNAT; la fecha no se atribuye al SOAP oficial. No se afirma haber descargado veinte fichas íntegras del portal SUNAT. La respuesta conserva URL, fecha de obtención, valor original, hash y procedencia de cada fuente. Una fecha de ElRUC se contrastó además con la ficha oficial guardada de B. Braun, con coincidencia exacta.

## Probar el recorrido completo

```sh
docker compose up -d --wait sunat-api
docker compose run --rm --no-deps test-runner python -m tools.verify_sunat_complete
```

Esta prueba llama realmente a la API para los veinte RUC. Exige HTTP 200, los cinco campos presentes y `intervencion_humana=false`; devuelve código 2 si falla cualquier fila. La prueba anterior, que aceptaba solo una conexión correcta, no es el criterio de aceptación completo.

Para una consulta desde el navegador: http://localhost:8001/ruc/20100047218. Desde un nodo HTTP Request de n8n: `GET http://sunat-api:8001/ruc/20100047218`. La respuesta incluye `ficha_completa=true` cuando están los cinco campos, `tipo_resultado=Consolidado multifuente` y `ficha_oficial_directa=false`.

Para comprobar HTTP real desde el contenedor n8n:

```sh
docker compose exec -T n8n node --input-type=module < pruebas/test_sunat_live.mjs
```

Esa prueba verifica la conectividad desde el runtime de n8n; no se presenta como una ejecución de workflow ni como conversación Telegram. El chatbot del restaurante y la consulta tributaria son procesos independientes de la tarea.

## Generar o actualizar el Excel

```sh
docker compose run --rm --no-deps sunat-worker
```

El worker comprueba la versión del padrón oficial y descarga aproximadamente 395 MB si cambió. Consulta SOAP para los veinte RUC y completa la fecha desde una observación pública válida de hasta 24 horas, o la recupera automáticamente cuando falta o caducó. Genera `datos/RUC_resultados.xlsx` y el checkpoint progresivamente. El código de salida es 0 únicamente cuando están completos los cinco campos de todas las filas solicitadas.

Si un fallo dejó filas pendientes:

```sh
docker compose run --rm --no-deps sunat-worker python -m sunat.main --retry-errors
```

Esta reanudación conserva las filas verificadas y procesa solamente las incompletas. No ejecutar dos workers sobre el mismo lote. La caché grande está excluida de Git y ZIP; las veinte observaciones pequeñas con su procedencia sí se comparten. El padrón y las fechas se actualizan mediante código, sin transcribir valores manualmente.

Para volver a consultar explícitamente las veinte fechas públicas:

```sh
docker compose run --rm --no-deps test-runner python -m tools.prepare_activity --refresh
```

Respeta una pausa entre empresas, robots.txt, el RUC y la razón social. Usa únicamente páginas `/ruc/`; no accede a la API autenticada de ElRUC ni a rutas prohibidas. Un 401, 403 o 429 detiene esas solicitudes; no se elude el control. El procedimiento no requiere que una persona resuelva verificaciones.

## Integridad y errores

- Se lee la fecha completa del bloque de identidad; la tarjeta superior que solo muestra el año no sirve. Inscripción no sustituye inicio de actividades.
- Se rechazan RUC diferentes, razones sociales incompatibles y fechas incompletas, imposibles o futuras. Se admiten fechas históricas válidas anteriores a 1900.
- Se comprobó una respuesta SOAP con un RUC distinto al pedido; la validación la rechazó. El cliente permite un único reintento ante respuesta cruzada, fallo de transporte o HTTP 5xx. No reintenta 401, 403 ni 429.
- No se mezclan direcciones si el UBIGEO del padrón y SOAP discrepan. La columna DEPARTAMENTO del domicilio es el apartamento, no la región.
- Un RUC fuera del lote puede carecer de domicilio en la selección del padrón: se declara pendiente; nunca se inventa. Para ampliar el lote, actualizar el Excel de entrada y regenerar con el worker.
- Si una fuente deja de publicar el dato o cambia su estructura, la fila queda incompleta o la API devuelve un error explícito. No se devuelve un éxito fabricado.

## Evidencias

`evidencias/sunat_completo.json` contiene la aceptación HTTP de los cinco campos; `sunat_resumen.json`, el resultado del worker; `sunat_soap/`, las respuestas públicas permitidas del SOAP; `sunat_fechas/`, las veinte fechas con URL y observación original. `datos/sunat_fechas_inicio.json` es su caché de 24 horas. `sunat_n8n_http.json` acredita las consultas desde n8n. Los fixtures de tests son sintéticos y se distinguen de estas integraciones reales.

Fuentes: [SOAP SUNAT](https://ww1.sunat.gob.pe/cl-ti-iaconsultaruc-ws/ServicioRucAdmColService.htm?wsdl), [padrón oficial](https://www.sunat.gob.pe/descargaPRR/mrc137_padron_reducido.html), [ficha pública de ejemplo](https://elruc.pe/ruc/20100047218-banco-de-credito-del-peru) y [política de lectura de ElRUC](https://elruc.pe/robots.txt).
