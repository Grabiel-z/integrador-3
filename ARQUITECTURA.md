# Arquitectura y decisiones

Compose proporciona DNS por nombre de servicio. n8n usa `http://ai-gateway:8000/chat`; el gateway usa `http://ollama:11434/api/chat`. `localhost` dentro de un contenedor es ese mismo contenedor, por lo que no se utiliza para comunicar servicios.

La red `backend` es interna. `egress` permite descargar modelos y consumir servicios oficiales desde los contenedores que lo requieren. Se publican exclusivamente en localhost n8n (`5678`) y SUNAT API (`8001`). Ollama y el gateway carecen de puertos publicados. No se monta el socket Docker en ningún contenedor.

n8n mantiene SQLite en `n8n_data`: una instancia y concurrencia reducida no justifican PostgreSQL. Este almacenamiento nativo satisface la persistencia sin otro servicio permanente. Ollama usa `ollama_data`; los Excel, informes y evidencias van a carpetas del proyecto. `model-init` y `n8n-bootstrap` son tareas finitas. SUNAT, tests e informe usan el perfil `tasks` y `run --rm`.

Se comparte la imagen Python por simplicidad de mantenimiento. Ejecuta las aplicaciones como usuario sin privilegios y sin capacidades Linux. Chromium y sus bibliotecas se conservan para diagnóstico; la ruta SUNAT principal usa SOAP y padrón oficial, sin navegador ni intervención humana. La API limita a una consulta en curso y devuelve errores explícitos. Ollama usa el usuario y volumen de su imagen oficial; no se concede modo privilegiado. Los servicios tienen límites de memoria; Ollama usa seis CPU lógicas y una sola generación simultánea.

La lógica central pertenece a CORE_CHATBOT: normalización, clasificación por palabras clave, recuperación, llamada HTTP, validación y cierre. El gateway solo adapta peticiones y respuestas. La IA selecciona identificadores; n8n comprueba que existan y muestra sus hechos literales. Esta decisión sacrifica redacción libre a cambio de precios y horarios trazables. Si el modelo falla se ofrece información conocida con un aviso explícito; una respuesta de fallback no cuenta como integración de IA aprobada.

Telegram y PRUEBAS_CHATBOT ejecutan el mismo ID de subworkflow. El webhook de pruebas se mantiene local. El perfil `telegram` añade un proxy que solo permite POST al patrón de webhook Telegram de n8n y responde 404 a administración y pruebas. Cloudflared apunta exclusivamente a ese proxy. Las APIs OpenAI, Gemini y Claude se ejecutan en sus proveedores; el cliente que las consume permanece en Docker.

Los diagramas editables están en `diagramas/*.dot`. `report-builder` genera SVG y PNG. No se implementa memoria conversacional persistente del cliente: `conversation_id` permite correlación, y no se guarda historial privado fuera de los registros de n8n. No se confirman operaciones comerciales.
