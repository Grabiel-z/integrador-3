# Decisión de integración de inicio de actividades

## Problema comprobado

La primera implementación solo acreditaba una conexión SOAP y cuatro campos. La aceptación estricta contra el RUC 20100047218 falló el 2 de noviembre de 2026 con `fecha_inicio_actividades` ausente. El criterio correcto es recibir los cinco campos para los veinte RUC, sin intervención humana, y conservar el origen de cada dato.

## Rutas analizadas

1. **API de ficha completa.** Croma y ElRUC documentan la fecha exacta, pero sus APIs programáticas necesitan una credencial de cuenta. Croma ofrece un cupo gratuito, y ElRUC 150 consultas mensuales gratuitas; no se abrió una cuenta ni se contrató un plan. La herramienta web gratuita de Croma no pudo verificar la solicitud automatizada; no se intentó eludir esa protección.
2. **SOAP y datos oficiales existentes.** El contrato público de SUNAT no ofrece inicio de actividades. El padrón diario aporta domicilio y condición, pero carece de la fecha. El dataset mensual tampoco contiene ese campo. Fecha de inscripción, alta en un padrón o emisión electrónica no son sustitutos válidos.
3. **Ficha pública complementaria.** La página `/ruc/{RUC}` de ElRUC se obtiene sin cuenta y redirige a su URL canónica. Su robots.txt permite esas páginas y da la bienvenida a asistentes; prohíbe `/api/`, que no se usa. El bloque de identidad contiene RUC, razón social, inscripción e inicio por separado. Esta ruta funcionó para las veinte empresas con solicitudes normales y pausas, sin navegador, CAPTCHA ni token.

## Solución implementada

Se mantienen las consultas SOAP oficiales en vivo para RUC, razón social, estado, condición y UBIGEO, y el padrón oficial para domicilio. `sunat/activity.py` obtiene solo la fecha y los metadatos necesarios de la página pública. Exige RUC y razón social coincidentes, fecha completa válida y ausencia de restricciones. Se ignora el resumen superior que muestra únicamente el año.

Las observaciones se guardan con valor original, URL, timestamp, SHA256 de la respuesta y comprobación de robots. Se reutilizan hasta 24 horas; después se renuevan automáticamente. La fecha pública de B. Braun coincidió con `01/10/1997` en la ficha oficial guardada; su inscripción figura en una fecha distinta. No se transcribieron fechas a mano ni se usó inscripción como sustituto.

El resultado se identifica como **Consolidado multifuente**, con `ficha_oficial_directa=false`. El origen de la fecha es ElRUC.pe, un sitio independiente, y no se presenta como un campo que devolvió SOAP. Esta distinción debe conservarse en el Excel, API e informe. Si la consigna original exige que todos los campos se extraigan exclusivamente del portal SUNAT, corresponde contrastar esa condición con este método explícito.

Durante la integración, una respuesta SOAP correspondió a otro RUC: se rechazó antes de consolidar. El cliente ahora valida siempre identidad y permite un único reintento frente a respuesta cruzada, transporte o HTTP 5xx. No reintenta 401/403/429. Las filas incompletas pueden reanudarse con `--retry-errors`, sin volver a procesar las verificadas.

## Pruebas y reproducción

La fuente complementaria obtuvo veinte fechas, y la aceptación real de API comprobó los cinco campos en veinte RUC. El worker también completó el Excel. La suite añade casos de fecha anual frente a completa, inscripción distinta, RUC y nombre incompatibles, fecha imposible o futura, redirección ajena, robots que prohíbe acceso y rechazo HTTP. Son fixtures sintéticos; las integraciones reales están en `evidencias/sunat_fechas/`, `sunat_completo.json` y `sunat_resumen.json`.

```sh
docker compose run --rm --no-deps test-runner
docker compose up -d --wait sunat-api
docker compose run --rm --no-deps test-runner python -m tools.verify_sunat_complete
docker compose run --rm --no-deps sunat-worker
```

No se garantiza disponibilidad futura de fuentes externas. Un cambio de estructura, identidad o autorización produce un error o una fila pendiente explícita. La solución no agrega una tarea humana a cada consulta ni fabrica una fecha ante una caída.

Fuentes primarias: [Croma, esquema SUNAT](https://docs.usecroma.com/guides/peru/sunat), [ElRUC, contrato de API y autenticación](https://elruc.pe/api), [página pública de BCP](https://elruc.pe/ruc/20100047218-banco-de-credito-del-peru), [robots.txt](https://elruc.pe/robots.txt) y [contrato oficial SOAP](https://ww1.sunat.gob.pe/cl-ti-iaconsultaruc-ws/ServicioRucAdmColService.htm?wsdl).
