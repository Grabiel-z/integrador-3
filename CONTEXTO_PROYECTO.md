# Contexto para continuar el proyecto

## Propósito y alcance

Este repositorio contiene la Tarea Académica 4 de automatización. Debe permitir que un grupo entregue y explique dos procesos reproducibles: consulta de veinte RUC peruanos con exportación a Excel y chatbot de un restaurante ficticio con n8n, IA y Telegram. El entorno de ejecución es Docker; el trabajo incluye investigación, análisis de negocio, diagramas, informe y evidencias.

La finalidad inmediata al continuar es **cerrar los pendientes con resultados auténticos**, sin sustituir la arquitectura que ya funciona ni presentar restricciones externas como éxitos. No es un sistema real de ventas, cobros o reservas. No hay una integración comercial del restaurante.

## Fuentes de verdad

| Tema | Fuente |
|---|---|
| Requisitos académicos disponibles | Este contexto, `CUMPLIMIENTO_RUBRICA.md` y las guías del proyecto; se basan en el texto detallado entregado por el solicitante |
| Consigna original | El PDF `TA4_INDICACIONES Y LISTA DE COTEJO_96SI.pdf` no fue localizado; si se obtiene, leerlo completo y contrastar el alcance |
| Comportamiento implementado | Código fuente, `compose.yaml` y workflows generados |
| Datos del restaurante | `chatbot/conocimiento.json`; negocio, dirección y menú de demostración |
| Procedencia de los RUC | `datos/ruc_semilla.json`, `datos/ruc_fuentes.json` y fuentes oficiales citadas |
| Lo realmente observado | `evidencias/`, con fechas y distinción entre integración real y fixtures |
| Resumen del estado | `ESTADO_FINAL.json` y `PRUEBAS_REALIZADAS.md`; se generan desde evidencias |
| Trabajo restante | `PENDIENTES.md` |

Los resultados versionados corresponden al equipo original el 2 de noviembre de 2026. Una copia nueva no hereda su cuenta n8n, credenciales, modelos descargados ni volúmenes Docker. La interfaz n8n de cada equipo requiere crear un propietario propio.

## Proceso SUNAT

1. `tools/prepare_input.py` prepara el Excel de veinte RUC como texto, a partir de empresas contrastadas en publicaciones oficiales. No consulta sus fichas tributarias.
2. `sunat/excel.py` valida once dígitos, dígito verificador, vacíos y duplicados.
3. `sunat/main.py` usa `sunat/official.py`: POST SOAP oficial en vivo y descarga versionada del padrón diario. `sunat/activity.py` completa inicio de actividades desde páginas públicas de ElRUC.pe permitidas por robots.txt, sin utilizar su API autenticada. No requiere navegador, CAPTCHA ni token comercial. `sunat/api.py` expone el mismo consolidado a n8n en `http://sunat-api:8001/ruc/{ruc}`.
4. SOAP devuelve razón social, estado, condición y UBIGEO. El padrón aporta domicilio para las empresas del lote. La fecha complementaria se coteja por RUC y razón social y conserva valor observado, URL, fecha y hash de la respuesta. Su caché dura 24 horas; al faltar o caducar se consulta automáticamente. Inscripción y un año aislado no sustituyen la fecha completa de inicio.
5. El worker conserva `datos/sunat_checkpoint.json` y reescribe el Excel progresivamente. Las filas incompletas y bloqueadas deben ser visibles.

La primera versión quedó bloqueada por el formulario; sus registros se conservaron como historia. Un navegador obtuvo una ficha completa y luego recibió un control humano; el visor se retiró. SOAP y padrón resolvieron cuatro campos; la integración pública complementaria completó las veinte fechas. La aceptación real por HTTP exige los cinco campos en 20/20 RUC y cero intervención humana. El Excel contiene veinte consolidados multifuente, no veinte fichas íntegras descargadas directamente del portal SUNAT. Ver `GUIA_SUNAT.md`, `evidencias/sunat_completo.json` y `evidencias/SUNAT_TRAZABILIDAD.md`.

El importador manual se conserva como herramienta histórica y no forma parte de la solución operativa. Una fecha pública se contrastó con la ficha oficial guardada de B. Braun, con coincidencia exacta. El servicio SOAP devolvió una vez un RUC cruzado: se rechazó y se cubrió con validación y un único reintento acotado. La reanudación `--retry-errors` conserva las filas completas. No se reintentan controles 401/403/429 ni se resuelve CAPTCHA.

## Proceso del chatbot

Los tres workflows tienen IDs estables:

| Workflow | ID | Función |
|---|---|---|
| CORE_CHATBOT | `TA4CORE0000000001` | Lógica central compartida |
| PRUEBAS_CHATBOT | `TA4TEST0000000001` | Webhook local y entrada manual |
| CHATBOT_TELEGRAM | `TA4TELE0000000001` | Recibir y responder al Chat ID del evento |

Recorrido de CORE: normalizar texto → detectar entrada inválida o intención → recuperar hechos del JSON → decidir si necesita IA → llamar al gateway → validar → componer respuesta literal y cierre.

El modelo devuelve JSON del tipo `{"fact_ids":["horario"]}`. n8n admite únicamente IDs presentes en el contexto y presenta los hechos estructurados. Así evita incorporar precios inventados. Los casos vacíos, extensos, desconocidos, ajenos o maliciosos usan reglas. Cuando falla la IA y existen hechos conocidos, se devuelven con un aviso de fallback. `ai_used=false` en ese caso: la respuesta útil no demuestra una integración IA satisfactoria.

La base JSON y los archivos `chatbot/*.js` se incorporan a los workflows con `tools/build_workflows.py`. Editar el JSON generado sin corregir esas fuentes produciría cambios que se perderían. `scripts/importar_workflows.sh` genera, detiene n8n, importa y reinicia; puede actualizar los tres workflows del proyecto. Exportar antes los cambios de interfaz que deban conservarse.

## Gateway y modelo

`gateway/app.py` expone internamente `POST /chat`: recibe `message`, `context` y `conversation_id` opcional; devuelve `response`, `provider`, `model`, duración y métricas. No reemplaza a n8n.

Proveedor predeterminado: Ollama con **`gemma4:e2b-it-q4_K_M`**, CPU, contexto 2048, temperatura 0.2, máximo 192 tokens, seis hilos y concurrencia uno. `model-init` descarga dentro de Docker, comprueba recursos y reutiliza los pesos persistentes.

Los adaptadores alternativos son OpenAI Responses, Gemini generateContent y Anthropic Messages. Solo se llama al proveedor elegido en `LLM_PROVIDER`; sin su clave y modelo se devuelve un error claro. Sus tests de contrato no equivalen a haber consumido las APIs. No se ejecutó una prueba comercial ni aceleración GPU.

## Servicios, puertos y persistencia

- **Permanentes:** `n8n`, `ollama`, `ai-gateway`, `sunat-api`.
- **Inicializadores finitos:** `n8n-bootstrap` importa los workflows; `model-init` descarga o reutiliza Gemma. Su `Exited (0)` es correcto.
- **Tareas del perfil `tasks`:** `sunat-worker`, `test-runner`, `report-builder` mediante `run --rm`.
- **Perfil opcional `telegram`:** `webhook-proxy` y `cloudflared`; el túnel solo apunta al proxy de webhook y no publica la administración.
- **Persistencia:** SQLite n8n en `n8n_data`, pesos en `ollama_data`, Excel/informes/evidencias en carpetas montadas. No se necesita PostgreSQL para esta instancia.

Dentro de Docker, n8n usa `http://ai-gateway:8000` y el gateway `http://ollama:11434`. SUNAT API usa el puerto interno 8001. `localhost` dentro de un contenedor no es otro servicio. Se publican `127.0.0.1:5678` para n8n y `127.0.0.1:8001` para consultar la API local. No se monta el socket Docker.

## Evidencia disponible y criterios de cierre

Las evidencias originales registran 37 tests unitarios, 5 casos sintéticos de validación de nodos y 18 casos reales por n8n, de los cuales 13 usaron IA. Incluyen generación en español, cuantización Q4_K_M, modelo ausente, timeout, Ollama detenido y persistencia tras reiniciar. Los benchmarks son mediciones de esa máquina, no garantías para otra.

Para cerrar la entrega se necesita resolver o declarar con precisión la limitación SUNAT, probar Telegram con un bot real, completar identidad y contrastar la consigna original. Las APIs comerciales son opcionales y no bloquean el modo local. La rúbrica de referencia es investigación 5, análisis de negocio 5, flujos 6, presentación 2 e informe 2; la nota la decide el docente.

Las acciones y condiciones verificables de cierre están en [PENDIENTES.md](PENDIENTES.md). La exposición se prepara con `GUIA_EXPOSICION.md`.

## Actualizar los entregables

Editar `informe/informe_base.md`, `informe/equipo.json`, investigación y diagramas DOT. Con evidencias nuevas y revisadas, ejecutar `sh scripts/generar_entrega.sh`. Genera diagramas, resumen de estados, informe Markdown/PDF y ZIP sin secretos. El PDF debe revisarse visualmente después de cambiar su contenido.

No reescribir resultados históricos como si se hubieran ejecutado pruebas nuevas. Si una nueva ejecución sustituye los JSON o logs, registrar su fecha y verificar las afirmaciones del informe. La importación manual de SUNAT y la declaración de una prueba Telegram requieren responsable y fecha reales.
