# Acceso oficial y contingencia SUNAT

**Documento histórico.** El usuario exige consultas sin intervención humana. La solución operativa actual es [GUIA_SUNAT.md](GUIA_SUNAT.md), con SOAP oficial y padrón diario. El procedimiento manual de este archivo no cierra ese requisito y no es un paso del chatbot ni de la API.

La consulta individual de https://www.gob.pe/es/565-verificar-el-estado-del-ruc conduce al formulario público. La consulta múltiple de https://www.gob.pe/13397-consultar-el-estado-de-hasta-100-n-meros-de-ruc permite introducir diez RUC o subir un TXT comprimido con hasta cien, e incluye código de seguridad. Su descripción no garantiza que se entregue la fecha de inicio; por eso no se presupone que cubre todos los campos de la tarea.

El worker original utilizaba el formulario individual normal; se conserva como diagnóstico separado con `--source formulario`. No emplea endpoints privados, evasión de huella, resolución automática de CAPTCHA ni servicios de scraping. Ante un bloqueo se conserva la evidencia y se marca el lote pendiente. La ruta principal ya no utiliza ese formulario ni espera que una persona resuelva controles.

## Si el portal requiere intervención

1. Abrir desde un navegador la ruta oficial anterior. Comprobar que el sitio admite la consulta manual, leer las condiciones vigentes y resolver personalmente cualquier control de seguridad autorizado.
2. Consultar cada RUC del Excel de entrada. Revisar **Domicilio Fiscal**, **Condición del Contribuyente** e **Inicio de Actividades**. No tomar Estado como Condición ni Fecha de Inscripción como Inicio.
3. Guardar cada ficha oficial como HTML completo o HTML único, usando el RUC como nombre en `datos/manual/`. Añadir un archivo con el mismo nombre y extensión `.json`, por ejemplo `20100047218.json`, con `{"fecha_consulta":"fecha real ISO 8601", "responsable":"nombre real"}`. Guardar su captura o PDF original para trazabilidad. No renombrar un sitio ajeno como evidencia SUNAT.
4. Ejecutar `docker compose run --rm sunat-worker python -m sunat.import_manual`. Solo el procesamiento de archivos guardados y la generación Excel se realizan de forma automatizada; la consulta fue manual y así queda indicada.
5. Revisar las filas incompletas y regenerar el informe. Si una ficha no contiene un dato, dejarlo vacío con observación y no inventarlo.

El navegador del anfitrión está permitido por la arquitectura como interfaz humana. Este procedimiento es una contingencia manual explícita, no una prueba de que las veinte consultas RPA funcionaron. La automatización sigue ejecutando Chromium dentro de Docker cuando el acceso normal está permitido. No se ha implementado una interfaz noVNC porque no se automatiza la intervención sobre controles del sitio.
