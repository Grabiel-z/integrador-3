# TA4 | Automatización y atención con IA local

Proyecto académico del Restaurante Sabor Peruano (ficticio) y consulta de veinte RUC. Toda ejecución, pruebas y generación de entregables ocurre en Docker. El modo predeterminado usa **gemma4:e2b-it-q4_K_M** mediante Ollama y no consume APIs comerciales.

Los estados y resultados de esta ejecución se encuentran en **PRUEBAS_REALIZADAS.md** y **evidencias/**. El código disponible no equivale a una integración aprobada. Las filas SUNAT conservan datos vacíos si no fue posible consultar la fuente.

## Inicio desde cero

Se requiere Linux x86-64 con Docker Engine y Compose v2, navegador e Internet para la primera construcción y descarga. Recomendación: 16 GiB de RAM total, 6 GiB disponibles como mínimo para el conjunto y 20 GiB de disco libre. El modelo tiene un volumen independiente. ARM64 requiere verificar imágenes y Chromium en ese equipo; no se afirma compatibilidad ensayada.

```sh
sh scripts/verificar_entorno.sh
sh scripts/instalar.sh
docker compose logs -f model-init
```

La primera descarga puede tardar según la conexión. Cuando termine, abrir http://localhost:5678 y crear la cuenta administradora personal de n8n. Las pruebas locales no necesitan Telegram. Los workflows se importan automáticamente, CORE y pruebas se publican y Telegram queda sin publicar. No se crea una cuenta con contraseña compartida.

Para usos posteriores:

```sh
docker compose up -d
sh scripts/probar_ia.sh
sh scripts/probar_chatbot.sh
sh scripts/probar_sunat.sh
sh scripts/generar_entrega.sh
sh scripts/detener.sh
```

## Contenido

- `sunat/`: Playwright, validación, extracción y exportación con openpyxl.
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
# Reintentar solo errores, después de comprobar que el acceso está permitido:
docker compose run --rm sunat-worker python -m sunat.main --retry-errors
```

El worker consulta con el formulario público, sin resolver CAPTCHA. Si el portal impide el acceso, revisar `GUIA_SUNAT_MANUAL.md`; no completar datos por deducción. El listado oficial de agentes de retención acredita los RUC de entrada, no el estado actual ni el domicilio de la ficha.

## Guías

`INSTALACION_DOCKER.md`, `ARQUITECTURA.md`, `MODELOS_IA.md`, `CAMBIAR_PROVEEDOR_IA.md`, `CONECTAR_TELEGRAM.md`, `PRUEBAS_REALIZADAS.md`, `CUMPLIMIENTO_RUBRICA.md` y `GUIA_EXPOSICION.md` cubren operación, evidencias y entrega.

Para editar el informe, modificar `informe/informe_base.md`, los textos en `investigacion/` y los nombres reales en `informe/equipo.json`. `sh scripts/generar_pdf.sh` vuelve a producir el Markdown completo y el PDF a partir de esas fuentes y de las evidencias actuales. El Markdown generado se sobrescribe al regenerar; la fuente base conserva las ediciones. `sh scripts/generar_entrega.sh` además actualiza el ZIP y comprueba su integridad.

No ejecutar `docker compose down -v`: elimina los volúmenes del proyecto. Los scripts no borran modelos, cuentas ni bases de datos.
