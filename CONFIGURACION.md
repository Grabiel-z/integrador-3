# Configuración del entorno

## Qué archivo se comparte

**`.env.example` es la plantilla pública. `.env` es la configuración privada de cada computadora.** El ejemplo está versionado y no contiene claves reales. Git y el generador del ZIP excluyen `.env`; no hay que pedir el archivo privado de otro compañero para iniciar el modo local.

El modo predeterminado es `LLM_PROVIDER=ollama`, con Gemma local. No requiere claves de OpenAI, Gemini o Anthropic. El token Telegram se guarda en una credencial de n8n, no en una variable del ejemplo.

## Si no tienes `.env`: camino recomendado

Desde la carpeta que contiene `compose.yaml`:

```sh
sh scripts/instalar.sh
```

El instalador construye la imagen y ejecuta `tools.configure` dentro de Docker con tu usuario Linux. Si `.env` falta, copia la plantilla, sustituye UID/GID, genera una clave aleatoria de cifrado y crea el archivo con permisos `600`. No muestra la clave. Si `.env` ya existe, se conserva sin cambiar valores ni claves.

Después del primer arranque solo necesitas `docker compose up -d`. Conservar la configuración privada y los volúmenes para mantener workflows, credenciales y modelos.

## Alternativa manual antes del primer arranque

Solo si `.env` todavía no existe:

```sh
cp .env.example .env
chmod 600 .env
id -u
id -g
```

Editar `LOCAL_UID` y `LOCAL_GID` con los números mostrados. Conservar `LLM_PROVIDER=ollama` y dejar vacías las seis variables comerciales si no vas a utilizarlas. Para un puerto diferente, cambiar tanto `N8N_PORT` como la URL local de `WEBHOOK_URL`.

**Cifrado:** si copiaste manualmente la plantilla y dejaste `N8N_ENCRYPTION_KEY` vacía, n8n crea una clave en su volumen durante la inicialización. El instalador no rellena un archivo ya existente. Esa modalidad también funciona, pero después no debes introducir una clave distinta: impediría descifrar las credenciales guardadas. Si el instalador creó `.env`, la clave ya fue generada allí. No cambiar de una modalidad a otra después de inicializar sin conservar la clave original.

Si ya existe una instalación con credenciales y perdiste `.env`, consultar la recuperación de configuración en `INSTALACION_DOCKER.md` antes de crear una clave nueva. No se comparten claves ni bases privadas en el repositorio.

## Variables del ejemplo

| Variable | Valor inicial | Para qué sirve |
|---|---|---|
| `LOCAL_UID` / `LOCAL_GID` | `1000` / `1000` | Identidad del usuario Linux que escribe archivos montados; el instalador detecta la real al crear `.env` |
| `N8N_PORT` | `5678` | Puerto publicado solo en `127.0.0.1`; interfaz local de n8n |
| `N8N_ENCRYPTION_KEY` | Vacía en la plantilla | Cifrado de credenciales; generación y conservación explicadas arriba |
| `WEBHOOK_URL` | `http://localhost:5678/` | URL base de los webhooks; el script de túnel la actualiza para Telegram |
| `LLM_PROVIDER` | `ollama` | Selección explícita: `ollama`, `openai`, `gemini` o `anthropic` |
| `OLLAMA_MODEL` | `gemma4:e2b-it-q4_K_M` | Referencia informativa del modelo obligatorio; está fijado también en Compose, no es un selector libre |
| `LLM_TIMEOUT` | `120` | Límite de segundos de la solicitud al proveedor, incluida la cola del gateway |
| `LLM_TEMPERATURE` | `0.2` | Temperatura que recibe el adaptador Ollama; no se aplica uniformemente a las APIs externas |
| `LLM_NUM_CTX` | `2048` | Contexto por solicitud Ollama; las APIs externas gestionan su contexto |
| `LLM_MAX_TOKENS` | `192` | Límite de salida enviado mediante el parámetro correspondiente de cada proveedor |
| `OPENAI_API_KEY` / `OPENAI_MODEL` | Vacías | Solo necesarias al elegir `openai` |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | Vacías | Solo necesarias al elegir `gemini` |
| `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` | Vacías | Solo necesarias al elegir `anthropic` |

Los nombres de servicios internos no requieren configuración en el anfitrión: n8n llama a `http://ai-gateway:8000` y el gateway a `http://ollama:11434`. La zona horaria `America/Lima` se configura en Compose.

Ollama mantiene además un contexto inicial `2048`, seis CPU, un solo modelo y concurrencia uno. Esos límites del servidor se fijan en `compose.yaml`; cambiar `LLM_NUM_CTX` afecta la solicitud del gateway, no todos los comandos de benchmark. `tools/test_live.py` conserva explícitamente los parámetros de su ensayo para que la medición sea interpretable.

## Aplicar cambios

- **Proveedor, clave comercial o parámetros del gateway:** editar `.env` y ejecutar `docker compose up -d --no-deps ai-gateway`.
- **Puerto o URL webhook:** editar `.env` y ejecutar `docker compose up -d --no-deps n8n`. Si cambiaste el puerto local, abrir la nueva URL.
- **Telegram:** seguir `CONECTAR_TELEGRAM.md`. `sh scripts/iniciar_tunel.sh` obtiene HTTPS temporal, modifica `WEBHOOK_URL` y recrea n8n; después publicar el flujo con su credencial.
- **Conocimiento del restaurante:** no se edita en `.env`; modificar `chatbot/conocimiento.json` y ejecutar el importador de workflows.
- **Clave de cifrado:** no cambiarla en una instalación inicializada.

Editar `.env` no cambia automáticamente el entorno de un contenedor que ya está ejecutándose. Los comandos anteriores lo recrean cuando su configuración cambia. Elegir un proveedor comercial sin clave o modelo devuelve un error; no activa otro proveedor de forma automática.

## Comprobar sin mostrar secretos

```sh
docker compose config --quiet
docker compose ps -a
sh scripts/probar_ia.sh
sh scripts/probar_chatbot.sh
```

`config --quiet` valida sin imprimir la configuración expandida. Evitar publicar la salida completa de `docker compose config` o la inspección de entornos cuando haya claves. Una respuesta correcta de fallback debe seguir identificándose como fallo de IA, no como prueba aprobada de inferencia.

Las pruebas originales y los pasos pendientes se documentan en `PRUEBAS_REALIZADAS.md` y `PENDIENTES.md`. Las APIs y sus costos son opcionales; la configuración local es suficiente para completar las pruebas del chatbot sin Telegram.
