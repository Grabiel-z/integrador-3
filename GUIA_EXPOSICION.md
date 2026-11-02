# Guía de exposición | 12 minutos sugeridos

Distribuir los apartados entre integrantes reales. No se asignan nombres desconocidos.

1. **Problemas y objetivos (1 min).** Explicar la transcripción repetitiva de RUC y las consultas frecuentes del restaurante ficticio. No presentar estimaciones de ahorro como mediciones.
2. **Rutas y certificaciones (2 min).** Comparar desarrollo RPA, IA, orquestación, consultoría y DevOps. Presentar UiPath Automation Developer Associate, AWS Certified AI Practitioner y CKA con sus emisores y relación con el trabajo.
3. **Arquitectura (2 min).** Mostrar el diagrama Compose y explicar DNS de servicios, red privada, volúmenes y tareas puntuales. Solo la administración local publica un puerto.
4. **SUNAT (2 min).** Mostrar los veinte RUC de fuente oficial, la validación y el Excel resultante. Explicar la diferencia entre campos y mostrar el número real de consultas completas. Si hubo bloqueo, mostrarlo y explicar la contingencia, sin representarlo como éxito.
5. **Chatbot (3 min).** Abrir CORE_CHATBOT y recorrer una pregunta local por n8n. Mostrar el contexto y la selección real de hechos por Gemma. Mostrar un mensaje ajeno y uno malicioso. Demostrar Telegram solo después de conectar el token.
6. **Pruebas y límites (2 min).** Mostrar métricas propias, pruebas con fixtures separadas de integración real, pendientes y conclusiones.

## Preguntas para preparar

- ¿Por qué Docker? Incluye navegador y dependencias en imágenes reproducibles y mantiene persistencia independiente del contenedor.
- ¿Cómo se comunican los servicios? Mediante nombres DNS y puertos internos, no mediante localhost entre contenedores.
- ¿Qué hace n8n y qué hace el gateway? n8n decide el flujo; el gateway adapta la comunicación con el proveedor elegido.
- ¿Por qué no una base vectorial? La base del restaurante es pequeña y estructurada; recuperar hechos por intención evita complejidad innecesaria.
- ¿Cómo evitan precios inventados? La IA devuelve IDs; n8n verifica el conjunto permitido y muestra datos literales de la base.
- ¿Hay IA real si el texto final es predeterminado? El modelo hace selección de hechos a partir de contexto. La salida comercial se restringe deliberadamente; los logs permiten distinguir el uso real de IA del fallback.
- ¿Qué sucede si Ollama cae? Se conserva la respuesta factual conocida, con aviso, y la prueba no se cuenta como IA funcional.
- ¿Se usó OpenAI/Gemini/Claude? Solo si las evidencias registran llamadas reales; los adaptadores sin credenciales se validan con tests de contrato.
- ¿Por qué no PostgreSQL? Una sola instancia con volumen SQLite es suficiente para esta carga académica; no hay múltiples escritores permanentes.
- ¿Qué pasa con CAPTCHA? No se elude; se documenta y se usa el procedimiento oficial permitido.
- ¿Qué falta antes de entregar? Identificar al equipo, completar evidencias reales de Telegram y resolver cualquier pendiente que aparezca en el informe de pruebas.

Ensayar con `docker compose up -d` antes de exponer. Llevar PDF y evidencias locales por si falla Internet; no presentar una captura anterior como demostración en vivo.
