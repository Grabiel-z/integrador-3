# TA4 | Automatización SUNAT y chatbot con IA local

Proyecto académico del Restaurante Sabor Peruano (ficticio) y consulta de veinte RUC. Toda ejecución, pruebas y generación de entregables ocurre en Docker. El modo predeterminado usa **gemma4:e2b-it-q4_K_M** mediante Ollama y no consume APIs comerciales.

**El chatbot local y la consulta automática de veinte RUC con los cinco campos se probaron con éxito.** El resultado tributario consolida SOAP y padrón oficiales de SUNAT con la fecha publicada por ElRUC.pe, sin navegador, CAPTCHA ni token comercial. Telegram todavía requiere conectar un bot real. Descargar el repositorio no ejecuta sus pruebas en tu equipo.

## Empieza aquí

| Si necesitas… | Lee primero |
|---|---|
| Entender y arrancar el proyecto en pocos minutos | [INICIO_RAPIDO.md](INICIO_RAPIDO.md) |
| Continuar como desarrollador o modelo de IA | [AGENTS.md](AGENTS.md) y [CONTEXTO_PROYECTO.md](CONTEXTO_PROYECTO.md) |
| Saber exactamente qué falta y cómo cerrarlo | [PENDIENTES.md](PENDIENTES.md) |
| Crear o revisar las variables de entorno | [.env.example](.env.example) y [CONFIGURACION.md](CONFIGURACION.md) |
| Revisar pruebas auténticas y sus límites | [PRUEBAS_REALIZADAS.md](PRUEBAS_REALIZADAS.md) y [ESTADO_FINAL.json](ESTADO_FINAL.json) |

## Qué se quiere lograr

1. **SUNAT:** leer veinte RUC válidos, consultar la fuente oficial y generar un Excel con RUC, razón social, domicilio fiscal, condición del domicilio e inicio de actividades. Conservar avances, errores y evidencia. Nunca completar un dato no observado.
2. **Restaurante:** responder consultas de horarios, carta, precios, ubicación, delivery, pagos y reservas. Telegram y las pruebas locales utilizan la misma lógica de n8n. La IA no puede inventar datos comerciales ni confirmar operaciones inexistentes.
3. **Entrega:** conservar fuentes, configuración, investigación, diagramas, pruebas, informe PDF, Excel y ZIP, para reproducir el trabajo con Docker y cubrir la rúbrica académica.

## Qué funciona y qué falta

Estado respaldado por evidencias del **2 de noviembre de 2026**, en el equipo donde se desarrolló. Una instalación nueva debe repetir las comprobaciones.

| Parte | Estado | Evidencia |
|---|---|---|
| Docker, persistencia, n8n, gateway y Gemma | **VERIFICADO** | Arranque real, inferencia y recuperación tras reiniciar |
| Chatbot local | **VERIFICADO** | 18/18 casos por n8n: 13 con IA y 5 mediante reglas |
| Tests y manejo de fallos | **VERIFICADO** | Suite ampliada de 63 tests, 5 casos sintéticos de nodos y errores provocados |
| SUNAT: conexión automática | **VERIFICADO** | Veinte respuestas SOAP oficiales HTTP 200; veinte domicilios del padrón diario |
| RUC: consolidación de cinco campos | **VERIFICADO** | 20/20 registros por API y Excel; fecha de fuente pública complementaria, con procedencia explícita |
| Telegram | **PENDIENTE DE TOKEN TELEGRAM** | Flujo preparado; falta credencial y conversación real |
| APIs comerciales | **IMPLEMENTADO, NO VERIFICADO** | Adaptadores con tests de contrato; sin llamadas comerciales |
| Cuenta n8n, nombres del equipo y PDF original | **PENDIENTE DE OTRA INTERVENCIÓN** | Pasos de cierre en [PENDIENTES.md](PENDIENTES.md) |

Los estados y resultados de esta ejecución se encuentran en **PRUEBAS_REALIZADAS.md** y **evidencias/**. El código disponible no equivale a una integración aprobada. Las filas SUNAT conservan datos vacíos si no fue posible consultar la fuente.

## Inicio desde cero

Se requiere Linux x86-64 con Docker Engine y Compose v2, navegador e Internet para la primera construcción y descarga. Recomendación: 16 GiB de RAM total, 6 GiB disponibles como mínimo para el conjunto y 20 GiB de disco libre. El modelo tiene un volumen independiente. ARM64 requiere verificar imágenes y Chromium en ese equipo; no se afirma compatibilidad ensayada.

```sh
git clone git@github.com:Grabiel-z/integrador-3.git
cd integrador-3
sh scripts/verificar_entorno.sh
sh scripts/instalar.sh
docker compose logs -f model-init
```

**Si no tienes `.env`, el instalador lo crea desde `.env.example` con una clave privada aleatoria.** Si ya existe, se conserva. No necesitas claves comerciales ni token Telegram para las pruebas locales. Si usas el ZIP, omite la clonación y abre una terminal en la carpeta que contiene `compose.yaml`.

La primera descarga puede tardar según la conexión. Cuando termine, abrir http://localhost:5678 y crear la cuenta administradora personal de n8n. Las pruebas locales no necesitan Telegram. Los workflows se importan automáticamente, CORE y pruebas se publican y Telegram queda sin publicar. No se crea una cuenta con contraseña compartida.

Esperar `success` o `Modelo persistente ya presente` y salir del seguimiento de logs con Ctrl+C; los servicios continúan ejecutándose. En `docker compose ps -a`, los cuatro servicios permanentes deben estar saludables y los dos inicializadores deben finalizar con `Exited (0)`.

Para usos posteriores:

```sh
docker compose up -d
sh scripts/probar_ia.sh
sh scripts/probar_chatbot.sh
sh scripts/generar_entrega.sh
sh scripts/detener.sh
```

Las pruebas del chatbot deben aprobar 18/18 casos; consultar `ai_used` en el JSON de resultados. SUNAT usa ahora una API oficial independiente del formulario bloqueado. No repetir masivamente las solicitudes rechazadas al portal.

## Cómo funciona

```text
Telegram o webhook local → n8n: CORE_CHATBOT
  → normalización, intención y hechos de conocimiento.json
  → AI Gateway → proveedor elegido (Gemma local por defecto)
  → validación, respuesta con hechos autorizados y cierre

Excel de entrada → Worker → SOAP SUNAT + padrón oficial + fecha pública ElRUC
  → validación de identidad y de los cinco campos → checkpoint y Excel
n8n o cliente HTTP → API interna → las mismas fuentes (sin navegador)
```

n8n orquesta el negocio; el gateway adapta los proveedores. Los precios y horarios salen del JSON, no de texto libre del modelo. Los servicios se comunican por nombres internos. n8n y la API tributaria publican puertos solo en localhost. n8n y Ollama conservan sus datos en volúmenes independientes. Ver [ARQUITECTURA.md](ARQUITECTURA.md).

## Contenido

- `sunat/`: cliente SOAP, padrón oficial, API HTTP, validación y exportación con openpyxl; navegador como diagnóstico histórico.
- `datos/`: entrada, procedencia y resultados SUNAT, más checkpoint reanudable.
- `chatbot/`: base JSON, prompt, código de nodos y tres workflows importables.
- `gateway/`: contrato FastAPI y adaptadores oficiales de IA.
- `pruebas/`: tests unitarios y fixtures identificados como sintéticos.
- `tools/`: generación, integración real, informe y ZIP.
- `investigacion/`: cinco rutas profesionales, tres certificaciones y dos casos.
- `diagramas/`: fuentes editables DOT, SVG y PNG.
- `evidencias/`: resultados auténticos y registros de la ejecución.
- `output/pdf/Proyecto_RPA_1_GrupoX.pdf`: informe regenerable.
- `GrupoX_TA4.zip`: paquete sin secretos ni modelos.

## Actualizar el restaurante

Editar `chatbot/conocimiento.json` y ejecutar `sh scripts/importar_workflows.sh`. Este comando actualiza exclusivamente los tres workflows TA4 de ID estable: respalda primero las modificaciones hechas en su interfaz. La importación se realiza con n8n detenido para evitar escrituras concurrentes a SQLite. No modifica otros workflows.

## SUNAT y resultados

```sh
docker compose run --rm sunat-worker
docker compose up -d --wait sunat-api
docker compose run --rm --no-deps test-runner python -m tools.verify_sunat_complete
```

Ver **[GUIA_SUNAT.md](GUIA_SUNAT.md)**. La consulta no necesita intervención humana ni claves comerciales. En n8n se usa `http://sunat-api:8001/ruc/20100047218`; desde el anfitrión, http://localhost:8001/ruc/20100047218. Cada llamada válida consulta realmente el SOAP de SUNAT. El domicilio procede del padrón oficial y la fecha de la ficha pública de ElRUC.pe, cotejada por RUC y razón social y conservada hasta 24 horas. `tipo_resultado=Consolidado multifuente` distingue este resultado de una ficha íntegra obtenida directamente del portal SUNAT. La aceptación comprobó los cinco campos en 20/20 RUC. El worker devuelve 0 únicamente si están completos; `--retry-errors` reanuda solo los pendientes.

## Guías

`INSTALACION_DOCKER.md`, `ARQUITECTURA.md`, `MODELOS_IA.md`, `CAMBIAR_PROVEEDOR_IA.md`, `CONECTAR_TELEGRAM.md`, `PRUEBAS_REALIZADAS.md`, `CUMPLIMIENTO_RUBRICA.md` y `GUIA_EXPOSICION.md` cubren operación, evidencias y entrega.

Para editar el informe, modificar `informe/informe_base.md`, los textos en `investigacion/` y los nombres reales en `informe/equipo.json`. `sh scripts/generar_pdf.sh` vuelve a producir el Markdown completo y el PDF a partir de esas fuentes y de las evidencias actuales. El Markdown generado se sobrescribe al regenerar; la fuente base conserva las ediciones. `sh scripts/generar_entrega.sh` además actualiza el ZIP y comprueba su integridad.

Para continuar el proyecto, seguir las prioridades y criterios de aceptación de [PENDIENTES.md](PENDIENTES.md). El detalle de cada variable y el comportamiento cuando falta `.env` están en [CONFIGURACION.md](CONFIGURACION.md).

No ejecutar `docker compose down -v`: elimina los volúmenes del proyecto. Los scripts no borran modelos, cuentas ni bases de datos.
