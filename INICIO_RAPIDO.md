# Entrada rápida al proyecto

## En dos minutos

Estamos construyendo una entrega académica de automatización. Hay dos procesos independientes:

- **SUNAT:** veinte RUC de empresas peruanas → consulta oficial → Excel. El acceso automatizado fue bloqueado con HTTP 403; actualmente hay **cero fichas completas**.
- **Restaurante Sabor Peruano:** pregunta → workflow n8n → conocimiento estructurado → Gemma local → respuesta validada. Este recorrido pasó **18 pruebas reales** sin Telegram.

El negocio del restaurante es ficticio. Las empresas de entrada son reales. No confundir esos dos tipos de datos. La siguiente meta es completar los pendientes con evidencia, conservar la reproducibilidad Docker y preparar la entrega del grupo.

Si eres un modelo que continúa el trabajo, lee también **[AGENTS.md](AGENTS.md)**, **[CONTEXTO_PROYECTO.md](CONTEXTO_PROYECTO.md)** y **[PENDIENTES.md](PENDIENTES.md)** antes de editar.

## Primera instalación

Necesitas Docker Engine, Compose v2, navegador y conexión para construir imágenes y descargar Gemma. Git solo es necesario para clonar o publicar. Los programas Python, Chromium, Ollama y n8n se ejecutan en contenedores.

```sh
git clone git@github.com:Grabiel-z/integrador-3.git
cd integrador-3
sh scripts/verificar_entorno.sh
sh scripts/instalar.sh
docker compose logs -f model-init
```

Si obtuviste un ZIP, extraerlo y abrir una terminal en la carpeta que contiene `compose.yaml`; comenzar en `verificar_entorno.sh`.

El instalador construye la imagen, crea `.env` **solo si no existe**, genera su clave privada, prepara los workflows e inicia los servicios. `.env.example` se comparte en Git; `.env` permanece privado. Si ya copiaste el ejemplo manualmente, consulta [CONFIGURACION.md](CONFIGURACION.md) para revisar UID/GID y cifrado.

La primera descarga tarda según la conexión. Esperar `success` o `Modelo persistente ya presente` en el inicializador y salir del seguimiento con Ctrl+C. Los pesos se conservan; un arranque posterior no debe volver a descargarlos.

## Confirmar que funciona

1. Abrir **http://localhost:5678**. Si aparece el formulario de propietario, crear tu cuenta n8n; no hay una contraseña compartida.
2. En los workflows deben existir **CORE_CHATBOT**, **PRUEBAS_CHATBOT** y **CHATBOT_TELEGRAM**. Los dos primeros están publicados; Telegram queda pendiente de su credencial.
3. Ejecutar:

```sh
docker compose ps -a
sh scripts/probar_ia.sh
sh scripts/probar_chatbot.sh
```

En `ps`, n8n, Ollama y ai-gateway deben estar saludables. `Exited (0)` en los dos inicializadores es un final correcto. Las pruebas del chatbot deben aprobar 18/18 casos; revisar `ai_used=true` en los casos que necesitan el modelo. Cinco casos se resuelven deliberadamente mediante reglas.

Para ejecutar solo los tests con fixtures, sin llamar a SUNAT ni a una API comercial:

```sh
docker compose run --rm --no-deps test-runner
```

Los resultados originales están versionados en `evidencias/`. Que un archivo de evidencia exista tras clonar **no significa que sus pruebas se hayan ejecutado en tu equipo**. Los comandos anteriores producen nuevos registros.

## Qué hacer después

| Tu objetivo | Acción |
|---|---|
| Probar el chatbot sin Telegram | Completar las comprobaciones anteriores |
| Conectar Telegram | Seguir `CONECTAR_TELEGRAM.md`; crear bot y credencial propios |
| Completar SUNAT | Leer `GUIA_SUNAT_MANUAL.md` y comprobar que el método está permitido antes de reintentar |
| Cambiar carta, horarios o precios | Editar `chatbot/conocimiento.json`; ejecutar `sh scripts/importar_workflows.sh` |
| Completar el informe | Añadir nombres reales a `informe/equipo.json` y revisar pendientes/evidencias |
| Generar la entrega | `sh scripts/generar_entrega.sh` |

## Uso cotidiano

```sh
docker compose up -d       # iniciar o recuperar los servicios
docker compose ps -a      # ver estado, incluidos inicializadores terminados
sh scripts/detener.sh     # parar conservando modelos y configuración
```

No ejecutar `docker compose down -v`: elimina los volúmenes. No instalar las aplicaciones del proyecto en el anfitrión. No activar un proveedor comercial para resolver un error del modelo local sin haberlo seleccionado expresamente.

Si algo falla, revisar los logs del servicio implicado y [INSTALACION_DOCKER.md](INSTALACION_DOCKER.md). La lista completa de trabajo restante está en [PENDIENTES.md](PENDIENTES.md).
