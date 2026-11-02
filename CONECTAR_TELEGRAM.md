# Conectar el bot de Telegram

Estado de la credencial: **PENDIENTE DE TOKEN TELEGRAM**. No se solicita ni se incluye un token en esta entrega. Los pasos deben realizarlos los compañeros con su bot.

1. Iniciar `docker compose up -d`. Esperar que el modelo esté listo y ejecutar `sh scripts/probar_chatbot.sh` antes de añadir Telegram.
2. Abrir http://localhost:5678. Crear la cuenta administradora si es la primera instalación y completar el acceso. La cuenta es propia de esta instalación; nunca compartir una contraseña en el ZIP.
3. En Telegram, abrir la cuenta oficial verificada **@BotFather**, enviar `/newbot`, elegir nombre y un usuario que termine en `bot` y obtener el token. No enviarlo al grupo ni fotografiarlo.
4. En n8n, abrir **Credentials**, crear una credencial **Telegram API** e introducir el token en **Access Token**. Guardarla y comprobar la conexión que ofrece n8n.
5. Abrir **CHATBOT_TELEGRAM**. En **Telegram Trigger** seleccionar esa credencial. Repetir la selección en **Telegram Send Message**. Guardar. No cambiar el Chat ID: es una expresión que toma el ID del mensaje recibido.
6. Ejecutar `sh scripts/iniciar_tunel.sh`. El servicio cloudflared usa Docker; no instalarlo en Debian. El script obtiene una URL temporal, actualiza `WEBHOOK_URL` en `.env` y recrea n8n. El proxy publica solo rutas de webhook Telegram; la administración y `/webhook/ta4-pruebas` deben devolver 404 desde Internet.
7. Volver a abrir el workflow y **publicarlo**. En n8n 2.x publicar sustituye al antiguo interruptor de activación. No ejecutar otro bot o instancia con el mismo token: Telegram solo conserva un webhook por bot. Si se estaba probando con “Listen for test event”, detener esa escucha antes de publicar.
8. Abrir el bot real, pulsar **Start** y enviar `¿Cuál es el horario?`. Comprobar horario de lunes a sábado y domingo y el mensaje de cierre. Probar también menú, Yape y una pregunta ajena al restaurante.
9. En **Executions**, comprobar que Telegram Trigger ejecutó CORE_CHATBOT y que el envío terminó sin error. Revisar si `ai_used=true` en el resultado del CORE. Una respuesta de fallback no demuestra inferencia correcta.
10. Tomar capturas auténticas del diálogo (sin token ni datos personales), del workflow conectado y de la ejecución. Guardarlas en `evidencias/telegram/` como PNG. Ejecutar `sh scripts/generar_entrega.sh` para incorporarlas al informe y al ZIP.

## URL temporal y comprobación del webhook

El túnel Quick Tunnel no necesita dominio ni cuenta Cloudflare y es para pruebas. La URL cambia al recrear el túnel; entonces ejecutar de nuevo `scripts/iniciar_tunel.sh` y volver a publicar el workflow para que Telegram registre la nueva dirección. No añadir autenticación por correo al túnel: Telegram necesita entregar el webhook sin interacción humana.

Si no llegan mensajes, comprobar logs de `cloudflared`, `webhook-proxy` y `n8n`, confirmar la nueva URL del Trigger y despublicar/publicar. La función `getWebhookInfo` de la API oficial permite comprobar URL y últimos errores; no pegar el token en comandos que queden en el historial. Usar preferentemente la verificación de credencial y las ejecuciones de n8n. No se afirma prueba real Telegram hasta completar estos pasos.

## Evidencias y estado de entrega

Añadir `evidencias/telegram/verificacion.json` con `{"probado": true, "fecha": "fecha real", "responsable": "nombre real"}` únicamente después de una prueba real. El generador mantiene Telegram pendiente mientras no exista esa declaración y capturas. Editar `informe/equipo.json` con los nombres reales y regenerar. No se inventan integrantes.
