# Trazabilidad del lote SUNAT

El único acceso real al formulario en esta ejecución se efectuó al preparar el primer RUC, 20377339461. El portal mostró una verificación de seguridad y HTTP 403; se guardó la captura. No se rellenó una ficha ni se obtuvieron campos fiscales. Las demás filas fueron registradas bajo el mismo bloqueo sin enviar nuevas consultas.

En la auditoría de los datos de entrada se retiró al Banco Central de Reserva, por ser una entidad pública autónoma, y se incorporó a Interbank (20100053455), contrastado en la continuación oficial del listado de agentes de retención. Este cambio permite que el archivo final contenga veinte empresas. La nueva fila no originó una consulta adicional y su observación lo indica.

`sunat_ejecucion.log` conserva el registro original de procesamiento, que incluye la entidad retirada. El Excel, `datos/ruc_fuentes.json`, el checkpoint y `sunat_resumen.json` contienen el listado final. No se presenta una línea de procesamiento como una solicitud real a SUNAT. Las diecinueve filas sin intento tienen fecha de consulta vacía; los timestamps de procesamiento se conservan separadamente en el checkpoint.

Resultado verificable: veinte RUC con procedencia y checksum válidos; un acceso al portal bloqueado; cero fichas completas. La importación de futuras fichas manuales exige fecha y responsable reales y queda etiquetada como consulta manual.
