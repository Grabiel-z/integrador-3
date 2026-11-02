# 1. Introducción

El proyecto aplica automatización robótica de procesos y orquestación con inteligencia artificial a dos casos: consolidación de información tributaria pública y atención de consultas frecuentes. Se utiliza un entorno Docker portable, con pruebas y registros que permiten diferenciar implementación de funcionamiento observado. La consigna original en PDF no fue localizada; el alcance se basa en el texto detallado proporcionado por el solicitante. Esta limitación debe contrastarse con la lista original antes de la entrega académica definitiva.

# 2. Objetivos

Implementar un proceso que valide veinte RUC y exporte los campos efectivamente observados en SUNAT; construir un chatbot con n8n, conocimiento estructurado y Gemma local; preparar Telegram sin compartir credenciales; y entregar código, diagramas, investigación, pruebas y documentación reproducibles. La aceptación exige evidencia, no solo contenedores iniciados. La calificación corresponde al docente.

# 3. Rutas laborales

{{RUTAS}}

# 4. Certificaciones

{{CERTIFICACIONES}}

# 5. Análisis de negocio

{{CASOS}}

# 6. Automatización SUNAT

El worker lee RUC como texto y verifica longitud, dígito de control y duplicados. Su ruta principal realiza consultas SOAP oficiales en vivo y descarga el padrón diario de SUNAT para las direcciones. La API interna permite consumir ese resultado desde n8n sin navegador, CAPTCHA ni intervención humana. Cada dato conserva su procedencia y se guarda un checkpoint y un Excel de forma progresiva. La fecha de inicio de actividades no está publicada en estas dos fuentes: queda pendiente y no se sustituye por inscripción ni por fecha de descarga.

El formulario público fue diagnosticado con Chromium actualizado: obtuvo una ficha completa automáticamente y luego mostró una verificación humana. Ese método fue retirado de la ruta operativa por requisito del usuario. El proceso actual no evade CAPTCHA ni controles y no ofrece intervención manual como solución. Se distinguen veinte respuestas SOAP reales de veinte fichas completas con los cinco campos académicos. Los RUC de entrada proceden de una publicación oficial de agentes de retención, contrastados posteriormente mediante las llamadas SOAP.

{{DIAGRAMA_SUNAT}}

# 7. Resultados de RUC

{{RESULTADOS_SUNAT}}

# 8. Implementación del chatbot

Sabor Peruano es un restaurante ficticio. CORE_CHATBOT normaliza el texto, filtra entradas, reconoce intenciones, recupera hechos del JSON, invoca al gateway y valida los identificadores seleccionados. Solo presenta hechos autorizados y agrega un cierre cordial. Los mensajes vacíos, extensos, ajenos o maliciosos tienen respuestas predeterminadas. La clasificación por palabras clave tiene límites semánticos; una consulta no reconocida solicita aclaración. No se gestiona ni confirma una reserva o un pago.

{{DIAGRAMA_CHATBOT}}

# 9. Arquitectura Docker

Todos los componentes de ejecución son contenedores. n8n y Ollama conservan datos en volúmenes distintos; SQLite evita añadir un servidor de base de datos innecesario para una única instancia. La red interna conecta servicios por nombre; n8n y SUNAT API publican puertos solo en localhost. El gateway y Ollama no se publican. Los trabajos SUNAT, pruebas e informe terminan al completar su función; SUNAT API permanece disponible para las consultas HTTP. Cloudflared y el proxy de webhooks se habilitan opcionalmente para Telegram. No se monta el socket Docker.

{{DIAGRAMA_DOCKER}}

# 10. Inteligencia artificial

El gateway adapta exclusivamente el intercambio con el proveedor elegido. El prompt restringe el alcance al restaurante y solicita una salida JSON con identificadores de hechos. n8n verifica que pertenezcan al contexto y compone la respuesta con textos de la base. Esta restricción reduce flexibilidad de redacción, pero permite comprobar precios y horarios. Un fallback conserva información conocida ante un fallo; no se contabiliza como uso satisfactorio de IA.

# 11. Gemma 4 E2B Q4

Se configura el identificador obligatorio gemma4:e2b-it-q4_K_M en Ollama dentro de Docker. El inicializador comprueba recursos, descarga una sola vez y conserva pesos en un volumen. La configuración inicial utiliza CPU, contexto 2048, temperatura 0.2, máximo 192 tokens, seis hilos y una generación simultánea. El modo sin razonamiento se solicita mediante la opción oficial think:false. Los ajustes son puntos iniciales evaluables, no un óptimo universal. Los resultados medidos se presentan en las secciones de pruebas y resultados.

# 12. Alternativas de APIs

Los adaptadores opcionales usan Responses API de OpenAI, generateContent de Gemini y Messages API de Anthropic, sin intermediarios ni scraping de interfaces de chat. Se exige seleccionar explícitamente el proveedor y configurar su clave y modelo. Si faltan datos, se rechaza la solicitud antes de consumir la API. Los modelos comerciales se ejecutan en el proveedor externo; solo su cliente e integración están dockerizados. No se presume que una suscripción de chat incluya crédito de API. Sin credenciales únicamente se verifican contratos y errores con fixtures.

{{DIAGRAMA_PROVEEDORES}}

# 13. Base de conocimiento

La base JSON registra nombre, descripción, dirección ficticia, horarios, seis opciones de carta, precios en soles, delivery, reservas, pagos, servicios, promociones y alérgenos. El menú del día cuesta S/ 18.00; el ceviche S/ 32.00; el lomo saltado S/ 35.00; el ají de gallina S/ 26.00; el arroz con pollo S/ 24.00 y la causa limeña S/ 16.00. Delivery en Miraflores cuesta S/ 6.00 sujeto a confirmación del personal. La información se actualiza en un archivo y se regenera el workflow, sin una base vectorial externa.

# 14. Workflows

CORE_CHATBOT centraliza la lógica. PRUEBAS_CHATBOT ofrece webhook local y trigger manual que llaman al mismo subworkflow. CHATBOT_TELEGRAM recibe el mensaje, valida texto, toma el Chat ID del evento, ejecuta CORE y envía la respuesta al mismo chat. Los archivos JSON contienen conexiones y parámetros; las credenciales Telegram deben asignarse en los dos nodos. La importación es idempotente y no incorpora tokens. La interfaz requiere una cuenta administradora creada por el equipo en su propia instalación.

# 15. Pruebas

{{RESULTADOS_TESTS}}

# 16. Resultados y evidencias

{{RESULTADOS_IA}}

{{EVIDENCIAS}}

# 17. Conclusiones

El diseño hace portable la automatización y permite rastrear datos comerciales y errores. Las pruebas unitarias aíslan reglas de validación y adaptadores; las integraciones requieren ejecutar los servicios reales. Los resultados se limitan a las evidencias registradas en esta instalación y no garantizan rendimiento en otras computadoras. El control de acceso de SUNAT, la disponibilidad del modelo y la conexión real de Telegram son condiciones observables que deben informarse por separado. Antes de entregar, el equipo debe completar su identidad, contrastar la consigna original y resolver los pendientes indicados, sin atribuir al sistema capacidades transaccionales que no implementa.

# 18. Referencias

{{REFERENCIAS}}
