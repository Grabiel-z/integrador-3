# Guía para agentes y modelos que continúan este repositorio

## Lectura inicial

Antes de modificar archivos, leer en este orden:

1. [README.md](README.md): objetivo, arranque y mapa de carpetas.
2. [CONTEXTO_PROYECTO.md](CONTEXTO_PROYECTO.md): alcance, fuentes de verdad y funcionamiento.
3. [PENDIENTES.md](PENDIENTES.md): trabajo restante y pruebas necesarias para cerrarlo.
4. [ESTADO_FINAL.json](ESTADO_FINAL.json) y [PRUEBAS_REALIZADAS.md](PRUEBAS_REALIZADAS.md): resultados históricos, no estado en vivo.
5. [.env.example](.env.example) y [CONFIGURACION.md](CONFIGURACION.md) si la tarea afecta al entorno.
6. Los archivos fuente y evidencias concretos del componente que se vaya a tocar.

El objetivo de la petición actual determina el trabajo a realizar. La existencia de un pendiente no autoriza por sí sola a activar servicios comerciales, publicar cambios o reconstruir todo el proyecto. Avanzar autónomamente dentro del alcance solicitado.

## Invariantes del proyecto

- Toda aplicación, navegador automatizado, prueba, Excel, PDF y ZIP se ejecuta o genera **dentro de Docker**. El anfitrión solo necesita Docker/Compose, navegador y Git opcional. No instalar Python, Node, Ollama ni Chromium en el anfitrión.
- Modelo local obligatorio: `gemma4:e2b-it-q4_K_M`. No sustituirlo silenciosamente. La CPU es la opción predeterminada; no exigir GPU.
- `LLM_PROVIDER=ollama` por defecto. Las APIs comerciales solo se usan cuando el usuario las selecciona expresamente y dispone de credenciales propias. No hacer fallback automático a una API de pago.
- n8n mantiene la lógica de negocio. El gateway solo adapta los proveedores. Telegram y las pruebas locales deben invocar el mismo `CORE_CHATBOT`.
- Los datos del restaurante proceden de `chatbot/conocimiento.json`. No inventar precios, horarios, promociones ni disponibilidad; no confirmar pagos o reservas.
- SUNAT: respetar el acceso oficial. No eludir CAPTCHA, verificaciones de seguridad o restricciones. No insistir automáticamente ante el bloqueo HTTP 403 documentado.
- Veinte RUC validados en una fuente pública **no equivalen** a veinte fichas SUNAT consultadas. Actualmente hay cero fichas completas; ver `evidencias/SUNAT_TRAZABILIDAD.md`.
- No inventar benchmarks, capturas, nombres de integrantes ni pruebas. Distinguir fixtures, respuestas por reglas, fallback e inferencia real.
- No leer ni mostrar secretos salvo que sea estrictamente necesario para una operación autorizada. `.env`, credenciales, `evidencias/privadas/` y volúmenes no se publican. No sustituir la clave de cifrado de una instancia existente.
- No borrar volúmenes ni ejecutar `docker compose down -v`. Conservar cambios del usuario y respaldar workflows antes de reimportar versiones que haya editado en n8n.

## Dónde editar

| Cambio | Fuente que se modifica | Paso posterior |
|---|---|---|
| Carta, precios, horarios, servicios | `chatbot/conocimiento.json` | Regenerar e importar workflows; probar chatbot |
| Intenciones, validación o cierre | `chatbot/normalizar.js`, `recuperar.js`, `validar.js` | Regenerar workflows y probar nodos e integración |
| Nodos o conexiones | `tools/build_workflows.py` | Regenerar JSON e importar con el script |
| Prompt del modelo | `chatbot/prompts/system_prompt.txt` | Recrear gateway si procede; repetir pruebas afectadas |
| Proveedores de IA | `gateway/app.py` | Tests de adaptadores y prueba real del proveedor disponible |
| Consulta y Excel SUNAT | `sunat/` | Tests con fixtures; acceso real solo si está permitido |
| Servicios o dependencias | `compose.yaml`, `sunat/Dockerfile`, `requirements.lock` | Validar Compose y construir la imagen |
| Informe | `informe/informe_base.md`, `informe/equipo.json`, `investigacion/` | Regenerar; revisar el PDF visualmente |

Los JSON en `chatbot/workflows/` son generados. No aplicar allí una corrección que se pierda al regenerar. `informe/Proyecto_RPA_1_GrupoX.md`, el PDF y los estados finales también se generan; cambiar sus fuentes o las evidencias correspondientes.

## Comprobación mínima según el cambio

```sh
docker compose config --quiet
docker compose run --rm --no-deps test-runner
```

Para cambios de chatbot o gateway, con el modelo disponible:

```sh
sh scripts/probar_ia.sh
sh scripts/probar_chatbot.sh
```

Para cambios de nodos, importar mediante `sh scripts/importar_workflows.sh` después de exportar las ediciones locales que deban conservarse. Los tests con respuestas sintéticas de esos nodos se ejecutan dentro de n8n:

```sh
docker compose exec -T n8n node --input-type=module < pruebas/test_core.mjs
```

No ejecutar la consulta SUNAT ni `scripts/probar_todo.sh` indiscriminadamente mientras el acceso siga bloqueado. `scripts/probar_errores.sh` detiene Ollama temporalmente; ejecutarlo solo cuando no interrumpa otro trabajo y comprobar su restauración.

Los cambios de documentación requieren revisar enlaces, comandos y coherencia con el código; no requieren repetir toda la inferencia. Si se actualiza la entrega, regenerar el ZIP con `docker compose run --rm --no-deps report-builder python -m tools.package` o el flujo completo documentado, y verificar su contenido.

## Cómo informar el resultado

Usar los estados del proyecto: **VERIFICADO**, **IMPLEMENTADO, NO VERIFICADO**, **PENDIENTE DE TOKEN TELEGRAM**, **PENDIENTE DE OTRA INTERVENCIÓN**, **BLOQUEADO POR RESTRICCIÓN EXTERNA** o **ERROR IDENTIFICADO**.

Explicar qué cambió, qué se ejecutó realmente y qué sigue pendiente. No trasladar un estado histórico a otra computadora sin repetir la prueba. No marcar un requisito como cumplido solamente porque existe su código o porque un contenedor arrancó. La calificación corresponde al docente.
