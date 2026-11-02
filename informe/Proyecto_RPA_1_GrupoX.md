# 1. Introducción

El proyecto aplica automatización robótica de procesos y orquestación con inteligencia artificial a dos casos: consolidación de información tributaria pública y atención de consultas frecuentes. Se utiliza un entorno Docker portable, con pruebas y registros que permiten diferenciar implementación de funcionamiento observado. La consigna original en PDF no fue localizada; el alcance se basa en el texto detallado proporcionado por el solicitante. Esta limitación debe contrastarse con la lista original antes de la entrega académica definitiva.

# 2. Objetivos

Implementar un proceso que valide veinte RUC y exporte los campos efectivamente observados en SUNAT; construir un chatbot con n8n, conocimiento estructurado y Gemma local; preparar Telegram sin compartir credenciales; y entregar código, diagramas, investigación, pruebas y documentación reproducibles. La aceptación exige evidencia, no solo contenedores iniciados. La calificación corresponde al docente.

# 3. Rutas laborales


Revisión: 2 de noviembre de 2026. Las funciones se sintetizan a partir de documentación profesional oficial. Las aplicaciones al proyecto y las progresiones propuestas son análisis académico; no constituyen promesas de empleo, salarios ni requisitos universales.

### Desarrollador RPA

Diseña robots para tareas repetitivas, implementa selectores, valida entradas y resuelve excepciones. Participa en pruebas, despliegue, mantenimiento y documentación. Necesita programación, análisis de procesos y comunicación con usuarios. Puede trabajar con UiPath Studio y Orchestrator, Python, Playwright y hojas de cálculo. En el caso SUNAT se responsabiliza de distinguir campos, conservar avances y respetar restricciones del portal. Una progresión posible pasa de desarrollador asociado a avanzado, experto, líder o arquitecto de soluciones; UiPath describe estos niveles. Fuente: https://academy.uipath.com/career-paths/automation-developer

### Especialista en inteligencia artificial

Integra modelos y datos, diseña evaluaciones y comprueba la calidad de las respuestas. Requiere desarrollo de software, manejo de datos y comprensión de modelos. Trabaja con Python, APIs, herramientas de evaluación y servidores de inferencia como Ollama. En este proyecto evalúa español, hechos comerciales, rechazo de preguntas ajenas y consumo de recursos. La responsabilidad incluye registrar límites y evitar que una respuesta plausible se trate como un hecho. Como propuesta de desarrollo profesional puede avanzar desde integración de modelos hacia ingeniería de IA y arquitectura de soluciones. Fuente: https://learn.microsoft.com/en-us/training/career-paths/ai-engineer

### Orquestador de automatizaciones

Conecta servicios, transforma datos y define condiciones, reintentos y rutas de error. Necesita HTTP, JSON, autenticación, diseño de flujos y observabilidad. Utiliza n8n, webhooks y subworkflows. Aquí mantiene CORE_CHATBOT como única lógica del restaurante y reutiliza ese flujo desde Telegram y las pruebas. Su responsabilidad es que cada componente reciba datos válidos y que los fallos no produzcan confirmaciones falsas. Se propone una progresión de implementador de integraciones a responsable de plataforma y arquitecto de automatización. Esta denominación describe una función transversal, no un título profesional estandarizado. Fuente técnica: https://docs.n8n.io/workflows/

### Consultor de automatización

Identifica oportunidades, levanta necesidades, delimita alcance y acuerda criterios de aceptación con el negocio. Documenta el proceso actual y propuesto, analiza riesgos y acompaña la adopción. Necesita entrevistas, modelado de procesos, evaluación de viabilidad y comunicación. Puede utilizar diagramas, matrices de requisitos y pruebas de concepto controladas. Para SUNAT debe advertir la dependencia del portal; para el restaurante debe evitar prometer reservas automáticas inexistentes. Una progresión sugerida va de analista de procesos a consultor y líder de transformación. Se relaciona con el perfil Automation Business Analyst de UiPath. Fuente: https://academy.uipath.com/certifications

### Ingeniero DevOps orientado a automatización

Prepara entornos reproducibles, automatiza despliegues y mantiene métricas, persistencia y recuperación. Necesita Linux, redes, contenedores, gestión de secretos y diagnóstico. Usa Docker, Compose, integración continua y observabilidad. En este proyecto fija versiones, limita puertos y recursos, y comprueba que reiniciar no elimine datos. La responsabilidad abarca operación y colaboración entre desarrollo y mantenimiento. Como trayectoria sugerida puede pasar de soporte de plataforma a ingeniería DevOps, SRE o arquitectura de infraestructura. Docker Compose basta para esta entrega; Kubernetes sería una ampliación, no una dependencia actual. Fuente: https://aws.amazon.com/devops/what-is-devops/

# 4. Certificaciones


Vigencia de la oferta comprobada en páginas oficiales el 2 de noviembre de 2026. Antes de pagar un examen debe revisarse nuevamente su disponibilidad y temario. Ninguna certificación es requisito para ejecutar este proyecto.

### UiPath Certified Professional Automation Developer Associate

Emisor: UiPath. Evalúa identificación de procesos, resolución de problemas y construcción de automatizaciones sencillas con Studio, Robots y Orchestrator. Es pertinente para iniciar una ruta de desarrollo RPA y participar en equipos que construyen soluciones más complejas. Su relación con esta tarea es el diseño de robots, el manejo de errores y las pruebas. Es una certificación de producto; dominar Python y Playwright exige práctica adicional. Se selecciona la denominación vigente y no las antiguas UiRPA/UiARD retiradas. Fuente oficial: https://academy.uipath.com/certifications

### AWS Certified AI Practitioner

Emisor: Amazon Web Services. Acredita comprensión fundamental de IA, aprendizaje automático e IA generativa y sus casos de uso. Resulta pertinente para personas de negocio y tecnología que necesitan evaluar soluciones de IA, su utilidad y sus límites. Complementa la discusión del chatbot, los riesgos y la selección de servicios. No acredita por sí sola capacidad de entrenar modelos ni administración avanzada de Ollama. El proyecto sigue siendo local y no requiere usar AWS. Fuente oficial: https://aws.amazon.com/certification/certified-ai-practitioner/

### Certified Kubernetes Administrator (CKA)

Emisores: Cloud Native Computing Foundation y The Linux Foundation. Evalúa administración práctica de clústeres, cargas de trabajo, redes, almacenamiento y solución de problemas. Es relevante para una progresión DevOps hacia operación de plataformas de contenedores. En esta tarea aporta una referencia de crecimiento profesional más allá de Compose, aunque no se implementa Kubernetes. Corresponde a un perfil con experiencia operativa; no se propone como primer paso obligatorio para quien recién aprende Docker. Fuente oficial: https://www.cncf.io/training/certification/cka/

# 5. Análisis de negocio


### Caso A. Validación administrativa de RUC

Contexto: un área administrativa consulta fichas de proveedores y consolida información. El proceso actual consiste en abrir el portal, buscar un RUC, leer varios campos y transcribirlos a una hoja. El problema es la repetición y la posibilidad de mezclar estado con condición o inscripción con inicio de actividades. Se necesita una entrada validada, trazabilidad de cada consulta y un resultado revisable.

El proceso propuesto valida veinte RUC de una relación oficial, abre Chromium en Docker, usa la consulta pública individual y registra solo los campos observados. Guarda un checkpoint y el Excel después de cada RUC; las filas incompletas se distinguen de las completas. Ante un control de seguridad se detiene el acceso automatizado y conserva las filas pendientes con su causa.

El beneficio esperado es reducir transcripciones y facilitar auditoría. No se calculan porcentajes de ahorro porque no se dispone de una medición del proceso manual. Los riesgos son cambios de interfaz, indisponibilidad, restricciones del portal e interpretación errónea de campos. Se mitigan con pruebas de extracción, evidencia HTML, límites de reintento y revisión humana. La automatización no certifica la situación tributaria de un proveedor ni sustituye una evaluación comercial.

### Caso B. Consultas frecuentes de un restaurante

Contexto: Sabor Peruano es un negocio ficticio con consultas repetidas sobre horarios, carta, precios y delivery. En un proceso manual, una persona lee cada mensaje y redacta información que ya existe. Se necesita consistencia, límites claros y un mecanismo que no prometa disponibilidad o reservas sin confirmación real.

El proceso propuesto recibe Telegram, valida el texto y ejecuta CORE_CHATBOT. n8n recupera hechos estructurados y solicita a la IA seleccionar identificadores relevantes. Solo presenta hechos autorizados, agrega un cierre y registra si la IA falló. Las pruebas locales recorren el mismo subworkflow. La base JSON permite revisar y actualizar el contenido sin una base vectorial externa.

Los beneficios esperados son uniformidad y disponibilidad de información básica. No se inventan volúmenes de consultas ni ahorros. Los riesgos son instrucciones maliciosas, datos desactualizados, errores del modelo y fallos de conectividad. La validación de identificadores, los mensajes predeterminados y el fallback a hechos conocidos reducen estos riesgos. El bot no cobra, no registra pedidos y no confirma reservas. Un negocio real necesitaría responsables del contenido y procesos transaccionales adicionales.

# 6. Automatización SUNAT

El worker lee RUC como texto, verifica longitud, dígito de control y duplicados, y abre Chromium instalado dentro de la imagen. Utiliza el formulario individual público y extrae razón social, domicilio fiscal, condición e inicio de actividades. La fecha de inscripción y el estado del contribuyente no se sustituyen por los campos solicitados. Cada consulta conserva evidencia y guarda un checkpoint y un Excel de forma progresiva.

La consulta múltiple oficial admite hasta cien RUC mediante TXT comprimido y exige código de seguridad. Su descripción no asegura todos los campos requeridos. La implementación no evade CAPTCHA ni controles de acceso. Si el acceso es impedido, registra la restricción y documenta un procedimiento oficial manual como contingencia; no fabrica resultados. Los RUC de entrada se contrastaron con una publicación oficial de agentes de retención, que no acredita por sí misma la situación tributaria actual.

![Diagrama: sunat](diagramas/sunat.png)

# 7. Resultados de RUC

Estado: BLOQUEADO POR RESTRICCIÓN EXTERNA. Veinte RUC de entrada contrastados en publicación oficial; 0 fichas completas de veinte. El Excel diferencia una ficha completa de una restricción externa y conserva fecha y observaciones. En el lote observado, el primer acceso fue rechazado con HTTP 403 y se aplicó un corte de solicitudes. La captura es evidencia del bloqueo, no de una consulta completada.

| RUC | Estado de consulta |
|---|---|
| 20377339461 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20605820817 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20602207138 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20342347950 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20523491840 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20538658368 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20607481491 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20517320570 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20102179898 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20605530509 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20609986442 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20504565794 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20100130204 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20608551701 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20100053455 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20509507199 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20100047218 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20100030595 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20330401991 | BLOQUEADO POR RESTRICCIÓN EXTERNA |
| 20513074370 | BLOQUEADO POR RESTRICCIÓN EXTERNA |

# 8. Implementación del chatbot

Sabor Peruano es un restaurante ficticio. CORE_CHATBOT normaliza el texto, filtra entradas, reconoce intenciones, recupera hechos del JSON, invoca al gateway y valida los identificadores seleccionados. Solo presenta hechos autorizados y agrega un cierre cordial. Los mensajes vacíos, extensos, ajenos o maliciosos tienen respuestas predeterminadas. La clasificación por palabras clave tiene límites semánticos; una consulta no reconocida solicita aclaración. No se gestiona ni confirma una reserva o un pago.

![Diagrama: chatbot](diagramas/chatbot.png)

# 9. Arquitectura Docker

Todos los componentes de ejecución son contenedores. n8n y Ollama conservan datos en volúmenes distintos; SQLite evita añadir un servidor de base de datos innecesario para una única instancia. La red interna conecta servicios por nombre; solo n8n publica un puerto en localhost. El gateway y Ollama no se publican. Los trabajos SUNAT, pruebas e informe terminan al completar su función. Cloudflared y el proxy de webhooks se habilitan opcionalmente para Telegram. No se monta el socket Docker.

![Diagrama: docker](diagramas/docker.png)

# 10. Inteligencia artificial

El gateway adapta exclusivamente el intercambio con el proveedor elegido. El prompt restringe el alcance al restaurante y solicita una salida JSON con identificadores de hechos. n8n verifica que pertenezcan al contexto y compone la respuesta con textos de la base. Esta restricción reduce flexibilidad de redacción, pero permite comprobar precios y horarios. Un fallback conserva información conocida ante un fallo; no se contabiliza como uso satisfactorio de IA.

# 11. Gemma 4 E2B Q4

Se configura el identificador obligatorio gemma4:e2b-it-q4_K_M en Ollama dentro de Docker. El inicializador comprueba recursos, descarga una sola vez y conserva pesos en un volumen. La configuración inicial utiliza CPU, contexto 2048, temperatura 0.2, máximo 192 tokens, seis hilos y una generación simultánea. El modo sin razonamiento se solicita mediante la opción oficial think:false. Los ajustes son puntos iniciales evaluables, no un óptimo universal. Los resultados medidos se presentan en las secciones de pruebas y resultados.

# 12. Alternativas de APIs

Los adaptadores opcionales usan Responses API de OpenAI, generateContent de Gemini y Messages API de Anthropic, sin intermediarios ni scraping de interfaces de chat. Se exige seleccionar explícitamente el proveedor y configurar su clave y modelo. Si faltan datos, se rechaza la solicitud antes de consumir la API. Los modelos comerciales se ejecutan en el proveedor externo; solo su cliente e integración están dockerizados. No se presume que una suscripción de chat incluya crédito de API. Sin credenciales únicamente se verifican contratos y errores con fixtures.

![Diagrama: proveedores](diagramas/proveedores.png)

# 13. Base de conocimiento

La base JSON registra nombre, descripción, dirección ficticia, horarios, seis opciones de carta, precios en soles, delivery, reservas, pagos, servicios, promociones y alérgenos. El menú del día cuesta S/ 18.00; el ceviche S/ 32.00; el lomo saltado S/ 35.00; el ají de gallina S/ 26.00; el arroz con pollo S/ 24.00 y la causa limeña S/ 16.00. Delivery en Miraflores cuesta S/ 6.00 sujeto a confirmación del personal. La información se actualiza en un archivo y se regenera el workflow, sin una base vectorial externa.

# 14. Workflows

CORE_CHATBOT centraliza la lógica. PRUEBAS_CHATBOT ofrece webhook local y trigger manual que llaman al mismo subworkflow. CHATBOT_TELEGRAM recibe el mensaje, valida texto, toma el Chat ID del evento, ejecuta CORE y envía la respuesta al mismo chat. Los archivos JSON contienen conexiones y parámetros; las credenciales Telegram deben asignarse en los dos nodos. La importación es idempotente y no incorpora tokens. La interfaz requiere una cuenta administradora creada por el equipo en su propia instalación.

# 15. Pruebas

La suite unitaria registró 37 casos, 0 fallos y 0 errores. Incluye checksum, entradas inválidas, duplicados, extracción con fixture sintético, separación de fechas y condición, exportación segura y contratos de cuatro adaptadores. Estos casos no son consultas SUNAT ni llamadas comerciales reales. Las pruebas reales mediante n8n registraron 18 de 18 casos aprobados; cada caso comprueba contenido y uso de IA cuando corresponde. Se incluyen las quince consultas requeridas, mensaje largo, instrucciones maliciosas y una pregunta con datos contradictorios.

# 16. Resultados y evidencias

Estado de Gemma: VERIFICADO. Estado de integración n8n: VERIFICADO. Modelo gemma4:e2b-it-q4_K_M; cuantización observada Q4_K_M. Promedio de tres generaciones: 3.500 segundos; errores de validación: 0.

| Ensayo | Primer contenido (s) | Duración total (s) | Tokens de salida |
|---|---|---|---|
| 1 | 7.741 | 8.564 | 9 |
| 2 | 0.178 | 0.951 | 9 |
| 3 | 0.130 | 0.985 | 9 |

Ollama informó 1.01 GiB de tamaño de memoria del modelo cargado. La memoria del contenedor, registrada separadamente en recursos_docker.txt, incluye otros componentes y cachés. No se extrapola a otro hardware. En la muestra registrada, docker stats midió 5.026GiB de memoria del contenedor Ollama con límite 7GiB. La latencia media del conjunto de casos n8n fue 4.895 segundos; incluye rechazos directos y llamadas a IA.

Telegram: PENDIENTE DE TOKEN TELEGRAM. Sus capturas se incorporarán cuando el equipo conecte un bot y complete una prueba real.

![Captura auténtica del acceso SUNAT desde Chromium en Docker.](evidencias/sunat/20377339461.png)

![Interfaz real de n8n de esta instalación.](evidencias/n8n_interfaz.png)

![Vista de los resultados registrados, generada desde evidencias; no representa la interfaz de Telegram.](evidencias/pruebas_resumen.png)



# 17. Conclusiones

El diseño hace portable la automatización y permite rastrear datos comerciales y errores. Las pruebas unitarias aíslan reglas de validación y adaptadores; las integraciones requieren ejecutar los servicios reales. Los resultados se limitan a las evidencias registradas en esta instalación y no garantizan rendimiento en otras computadoras. El control de acceso de SUNAT, la disponibilidad del modelo y la conexión real de Telegram son condiciones observables que deben informarse por separado. Antes de entregar, el equipo debe completar su identidad, contrastar la consigna original y resolver los pendientes indicados, sin atribuir al sistema capacidades transaccionales que no implementa.

# 18. Referencias

Revisión de fuentes: 2 de noviembre de 2026.

[1] SUNAT: consultar RUC. https://www.gob.pe/es/565-verificar-el-estado-del-ruc

[2] SUNAT: consulta múltiple hasta 100 RUC. https://www.gob.pe/13397-consultar-el-estado-de-hasta-100-n-meros-de-ruc

[3] SUNAT: relación de agentes de retención. https://ww3.sunat.gob.pe/descarga/AgentRet/AgenRet31.html

[4] SUNAT: agentes de retención, continuación (Interbank). https://ww3.sunat.gob.pe/descarga/AgentRet/AgenRet32.html

[5] Ollama: modelo exacto Gemma 4 E2B Q4_K_M. https://ollama.com/library/gemma4:e2b-it-q4_K_M

[6] Ollama: contrato de chat. https://docs.ollama.com/api/chat

[7] Ollama: releases oficiales. https://github.com/ollama/ollama/releases/tag/v0.40.13

[8] n8n: releases oficiales. https://github.com/n8n-io/n8n/releases/tag/n8n%402.45.7

[9] n8n: importación y publicación por CLI. https://docs.n8n.io/hosting/cli-commands/

[10] n8n: workflows. https://docs.n8n.io/workflows/

[11] UiPath: carrera de desarrollador. https://academy.uipath.com/career-paths/automation-developer

[12] Microsoft: ingeniería de IA. https://learn.microsoft.com/en-us/training/career-paths/ai-engineer

[13] AWS: DevOps. https://aws.amazon.com/devops/what-is-devops/

[14] UiPath: certificaciones. https://academy.uipath.com/certifications

[15] AWS Certified AI Practitioner. https://aws.amazon.com/certification/certified-ai-practitioner/

[16] CNCF: Certified Kubernetes Administrator. https://www.cncf.io/training/certification/cka/

[17] OpenAI: generación de texto y Responses API. https://developers.openai.com/api/docs/guides/text

[18] Google: modelos Gemini API. https://ai.google.dev/gemini-api/docs/models

[19] Anthropic: modelos Claude. https://platform.claude.com/docs/en/models/overview

[20] Telegram: webhooks de bots. https://core.telegram.org/bots/api#setwebhook

[21] Cloudflare: Quick Tunnels. https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/
