# Análisis de negocio

## Caso A. Validación administrativa de RUC

Contexto: un área administrativa consulta fichas de proveedores y consolida información. El proceso actual consiste en abrir el portal, buscar un RUC, leer varios campos y transcribirlos a una hoja. El problema es la repetición y la posibilidad de mezclar estado con condición o inscripción con inicio de actividades. Se necesita una entrada validada, trazabilidad de cada consulta y un resultado revisable.

El proceso propuesto valida veinte RUC de una relación oficial, abre Chromium en Docker, usa la consulta pública individual y registra solo los campos observados. Guarda un checkpoint y el Excel después de cada RUC; las filas incompletas se distinguen de las completas. Ante un control de seguridad se detiene el acceso automatizado y conserva las filas pendientes con su causa.

El beneficio esperado es reducir transcripciones y facilitar auditoría. No se calculan porcentajes de ahorro porque no se dispone de una medición del proceso manual. Los riesgos son cambios de interfaz, indisponibilidad, restricciones del portal e interpretación errónea de campos. Se mitigan con pruebas de extracción, evidencia HTML, límites de reintento y revisión humana. La automatización no certifica la situación tributaria de un proveedor ni sustituye una evaluación comercial.

## Caso B. Consultas frecuentes de un restaurante

Contexto: Sabor Peruano es un negocio ficticio con consultas repetidas sobre horarios, carta, precios y delivery. En un proceso manual, una persona lee cada mensaje y redacta información que ya existe. Se necesita consistencia, límites claros y un mecanismo que no prometa disponibilidad o reservas sin confirmación real.

El proceso propuesto recibe Telegram, valida el texto y ejecuta CORE_CHATBOT. n8n recupera hechos estructurados y solicita a la IA seleccionar identificadores relevantes. Solo presenta hechos autorizados, agrega un cierre y registra si la IA falló. Las pruebas locales recorren el mismo subworkflow. La base JSON permite revisar y actualizar el contenido sin una base vectorial externa.

Los beneficios esperados son uniformidad y disponibilidad de información básica. No se inventan volúmenes de consultas ni ahorros. Los riesgos son instrucciones maliciosas, datos desactualizados, errores del modelo y fallos de conectividad. La validación de identificadores, los mensajes predeterminados y el fallback a hechos conocidos reducen estos riesgos. El bot no cobra, no registra pedidos y no confirma reservas. Un negocio real necesitaría responsables del contenido y procesos transaccionales adicionales.
