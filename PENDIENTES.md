# Qué falta y cómo continuar

Este es un plan de trabajo, no una declaración de pruebas nuevas. El estado de referencia procede de las evidencias del **2 de noviembre de 2026**. Las prioridades siguientes mantienen el modelo local y la arquitectura Docker que ya funcionan.

## 1. Completar los datos SUNAT

**Estado: BLOQUEADO POR RESTRICCIÓN EXTERNA.** Hay veinte RUC contrastados en publicaciones oficiales y cero fichas completas. El primer acceso al formulario recibió HTTP 403; el resto del lote se registró sin nuevas solicitudes. No es correcto decir que se consultaron exitosamente veinte empresas.

**Siguiente acción:** una persona debe comprobar el acceso y el procedimiento oficial permitido siguiendo [GUIA_SUNAT_MANUAL.md](GUIA_SUNAT_MANUAL.md). Mientras persista el control, no ejecutar reintentos masivos ni cambiar de método para eludirlo. Si se consultan fichas manualmente, guardar HTML, fecha y responsable reales y usar el importador Docker documentado.

**Para cerrar:** cada fila debe contener datos observados o una limitación explícita; conservar las fuentes y distinguir consultas manuales de RPA. Para afirmar veinte consultas automatizadas satisfactorias se necesitan veinte fichas realmente obtenidas por el worker mediante acceso permitido. Si esto no es posible, informar la limitación al docente; no fabricar ese cumplimiento.

Archivos: `datos/RUC_resultados.xlsx`, `datos/sunat_checkpoint.json`, `evidencias/sunat_resumen.json`, `evidencias/SUNAT_TRAZABILIDAD.md` y las fichas/capturas auténticas disponibles.

## 2. Conectar Telegram y obtener evidencia final

**Estado: PENDIENTE DE TOKEN TELEGRAM.** El workflow existe, utiliza Chat ID dinámico y llama a CORE_CHATBOT. El túnel y su bloqueo de administración se probaron; no hay una conversación real del bot.

**Siguiente acción:** seguir [CONECTAR_TELEGRAM.md](CONECTAR_TELEGRAM.md). Crear el bot con BotFather, guardar el token únicamente como credencial Telegram de n8n, asignarla en ambos nodos, iniciar el túnel Docker y publicar el workflow. No pegar tokens en Git, documentación, capturas o mensajes del grupo.

**Para cerrar:** enviar mensajes reales de horario, menú, pago y tema ajeno; revisar las ejecuciones y el uso de IA; conservar capturas sin secretos. Solo después crear `evidencias/telegram/verificacion.json` con prueba, fecha y responsable reales. Regenerar el informe y revisar que las capturas se incorporaron.

## 3. Crear la cuenta propia de n8n en cada instalación

**Estado: PENDIENTE DE OTRA INTERVENCIÓN.** Se importa la lógica automáticamente, pero no se distribuye una identidad administradora.

**Siguiente acción:** abrir http://localhost:5678 y completar el formulario inicial cuando aparezca. Quien configura su instalación conserva sus credenciales y la clave de cifrado de su volumen.

**Para cerrar:** acceder a los tres workflows y poder asignar la credencial Telegram. No añadir la contraseña o la base privada al ZIP.

## 4. Identificar al equipo y contrastar la consigna

**Estado: PENDIENTE DE OTRA INTERVENCIÓN.** No se recibieron nombres reales ni se encontró el PDF original de la tarea.

**Siguiente acción:** completar `informe/equipo.json`; conseguir `TA4_INDICACIONES Y LISTA DE COTEJO_96SI.pdf`, leerlo completo y comparar sus campos, evidencias, formato y rúbrica con el proyecto. Los requisitos disponibles se tomaron del texto proporcionado por el solicitante.

**Para cerrar:** carátula con integrantes reales y una revisión explícita de la lista original. Corregir las diferencias que aparezcan y actualizar `CUMPLIMIENTO_RUBRICA.md` a través de su fuente en `tools/build_report.py` si cambia la matriz generada.

## 5. Revisar la entrega y ensayar

**Estado: PENDIENTE DE OTRA INTERVENCIÓN** para la revisión del grupo y su exposición. Las fuentes, investigación, diagramas, PDF y ZIP ya existen.

Después de cambiar código, ejecutar las pruebas afectadas. En un equipo nuevo, empezar por [INICIO_RAPIDO.md](INICIO_RAPIDO.md); las evidencias clonadas son históricas.

```sh
docker compose config --quiet
docker compose run --rm --no-deps test-runner
sh scripts/probar_ia.sh
sh scripts/probar_chatbot.sh
sh scripts/generar_entrega.sh
```

Estos comandos no ejecutan la consulta SUNAT real. No usar `scripts/probar_todo.sh` hasta revisar el acceso, porque también llama a ese proceso.

**Para cerrar:** revisar visualmente el PDF, comprobar sus afirmaciones contra evidencias, abrir el ZIP, verificar que incluye la configuración de ejemplo y las guías, y ensayar con `GUIA_EXPOSICION.md`. La máxima calificación es una aspiración; no se garantiza una nota.

## Opcionales que no bloquean la entrega local

- **OpenAI, Gemini y Anthropic:** **IMPLEMENTADO, NO VERIFICADO** en sus llamadas comerciales. Hay tests de adaptadores; no hacen falta esas claves para Gemma. Probarlos solo si el grupo elige usar uno y acepta su consumo. Ver `CAMBIAR_PROVEEDOR_IA.md`.
- **GPU NVIDIA:** **IMPLEMENTADO, NO VERIFICADO** mediante override opcional. La CPU ya fue probada; no instalar herramientas GPU si el equipo no las necesita.
- **Mejoras de lenguaje o nuevas funciones:** fuera del alcance necesario para cerrar los pendientes actuales. No transformar el bot informativo en un sistema de reservas o pagos sin requisitos nuevos y un proceso real.

## Qué ya no hace falta reconstruir

La arquitectura Compose, la persistencia, los tres workflows, el gateway local, la base JSON, los tests y los generadores ya están implementados y tienen evidencia. Mantener esas fuentes y modificar solo lo necesario. Un fallo en otra computadora se diagnostica con sus logs; no implica que haya que sustituir silenciosamente el modelo o mover las aplicaciones fuera de Docker.
