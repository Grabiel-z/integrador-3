# Trazabilidad del lote SUNAT

## Ejecución inicial, conservada como historia

El primer acceso al formulario se efectuó al preparar el RUC 20377339461. El portal mostró una verificación de seguridad y HTTP 403; se guardó la captura. No se rellenó una ficha y las siguientes filas se registraron sin enviar consultas. El checkpoint de ese momento está en `sunat_checkpoint_formulario_anterior.json`. Este resultado ya no describe la conexión actual por API.

En la auditoría de los datos de entrada se retiró al Banco Central de Reserva, por ser una entidad pública autónoma, y se incorporó a Interbank (20100053455), contrastado en la continuación oficial del listado de agentes de retención. Este cambio permite que el archivo final contenga veinte empresas. La nueva fila no originó una consulta adicional y su observación lo indica.

`sunat_ejecucion.log` conserva el registro inicial, que incluye la entidad retirada. No se presenta una línea de procesamiento como una solicitud real. Las fechas vacías y timestamps de procesamiento originales se conservan en el checkpoint histórico; no se atribuyen a las llamadas SOAP posteriores.

## Corrección del 2 de noviembre de 2026

1. La prueba puntual reprodujo el HTTP 403 del formulario anterior. El menú oficial enlazaba una entrada diferente, que también recibió restricciones en solicitudes HTTP simples.
2. Se inspeccionó el WSDL oficial público y se envió un POST SOAP real a `https://ww1.sunat.gob.pe/cl-ti-iaconsultaruc-ws/ServicioRucAdmColService.htm`, operación `buscarRuc`. BCP y BBVA devolvieron HTTP 200 con razón social, estado, condición y UBIGEO.
3. El lote realizó veinte consultas SOAP reales y satisfactorias. `sunat_soap/{RUC}.json` conserva exclusivamente una lista de campos públicos permitidos, URL, operación, fecha, estado HTTP y duración. No se guarda el XML íntegro ni otros campos del servicio.
4. Se descargó el padrón oficial de `https://www2.sunat.gob.pe/padron_reducido_ruc.zip`: HTTP 200, 394511100 bytes, versión `Mon, 02 Nov 2026 07:39:00 GMT`, SHA256 `fa5b8283e176ff95c34778a49eadc2ccae4cfdc28796beb8adb82f2dd96189b5`. La lectura hasta EOF verifica el CRC. Se conservaron únicamente las veinte empresas solicitadas. La caché completa está excluida de Git y ZIP.
5. Con Playwright 1.64.1 y Chromium completo actualizado, el navegador obtuvo automáticamente la ficha de 20377339461, con inicio de actividades `01/10/1997`. Se conservan HTML, captura y campos extraídos en `sunat_asistido/`; el nombre histórico del directorio no significa que una persona haya resuelto un control. En la segunda ficha apareció una verificación humana. No se pulsó ni resolvió. El usuario exige cero intervención durante consultas, por lo que el visor y su servicio fueron retirados.
6. `sunat-api` expone un cliente automático HTTP: cada RUC válido genera un POST SOAP oficial nuevo. Se probó realmente el endpoint y su acceso desde el runtime Docker de n8n. No se afirma que esa comprobación sea una conversación o una ejecución de workflow; ver `sunat_api/` y `sunat_n8n_http.json`.

Resultado: veinte consultas SOAP reales, veinte domicilios con datos y una ficha con los cinco campos. Faltan diecinueve fechas en el Excel. La API en vivo devuelve fecha `null` para todos, porque SOAP no la publica; tampoco utiliza la fecha de una ficha guardada como si acabara de devolverla SUNAT. Se necesita otra fuente autorizada que exponga ese campo automáticamente para cerrar el requisito completo. Ver `GUIA_SUNAT.md`.
