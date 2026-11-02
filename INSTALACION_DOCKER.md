# Instalación reproducible

1. Instalar Docker Engine y el plugin Compose v2 siguiendo https://docs.docker.com/engine/install/debian/ . Es el único entorno de ejecución requerido en el anfitrión. No instalar Python, Node, Ollama ni Chromium en Debian.
2. Comprobar `docker version`, `docker compose version` y acceso al motor. Si no tienes permiso, seguir las indicaciones de seguridad del instalador oficial; no hacer público el socket. Cerrar y volver a iniciar sesión si se modifica la pertenencia a grupos.
3. Extraer el ZIP en una carpeta propia con permisos de escritura. Ejecutar todos los comandos desde esa carpeta.
4. Ejecutar `sh scripts/instalar.sh`. Construye la imagen, crea `.env` privado con clave de cifrado aleatoria, conserva el usuario local y prepara los datos. No muestra secretos.
5. Esperar el final de `docker compose logs -f model-init`. La descarga de pesos está en un volumen Docker y no se repite si el modelo ya existe.
6. Abrir http://localhost:5678 y crear tu cuenta administradora. No se entrega una identidad ficticia ni una contraseña común.
7. Verificar `docker compose ps -a`, `sh scripts/probar_ia.sh` y `sh scripts/probar_chatbot.sh`.
8. Seguir `GUIA_SUNAT.md` para probar la API automática. `sh scripts/probar_sunat.sh` consulta SOAP y padrón reales; devuelve código 2 mientras falten fechas de inicio en el requisito académico. No requiere intervención humana durante las consultas.
9. Seguir `CONECTAR_TELEGRAM.md` para el único secreto externo previsto.

La primera construcción requiere conectividad a Docker Hub, al registro oficial de n8n, a PyPI, Debian y al repositorio de Chromium. Ollama necesita acceso a su registro de modelos. Errores de DNS, proxy, certificados o espacio deben resolverse en el entorno y quedan registrados si ocurren.

Versiones fijadas: Python 3.12.12, Playwright 1.64.1 (Chromium correspondiente descargado durante la construcción), n8n 2.45.7 y Ollama 0.40.13. Dependencias directas en `requirements.txt`; `requirements.lock` fija también todas las transitivas y es el archivo utilizado al construir. La lista realmente instalada se exporta en `evidencias/dependencias.txt`. Las imágenes y sus digest descargados se registran en `evidencias/imagenes.txt`. Para reproducibilidad estricta frente a cambios en repositorios, conservar esos digest y el registro completo de dependencias.

## Diagnóstico

- Puerto 5678 ocupado: cambiar `N8N_PORT` y la URL local en `.env`, y recrear n8n con `docker compose up -d n8n`.
- Modelo ausente: `docker compose logs model-init`; liberar RAM/disco y ejecutar `docker compose run --rm model-init`.
- Gateway vivo pero modelo no listo: `/health` comprueba el proceso; `/ready` comprueba configuración y presencia del modelo, no la inferencia completa. Ejecutar las pruebas reales.
- Sin memoria: cerrar aplicaciones, reducir contexto si sigue en 4096 o volver a 2048. El modelo obligatorio no se sustituye. El límite de Ollama es 7 GiB; un OOM exige revisar hardware antes de elevarlo.
- Permisos de archivos: `.env` debe contener tu UID/GID. La cuenta del host conserva los Excel y evidencias. No usar permisos universales de escritura.
- No recuperar una clave de cifrado perdida: conservar `.env` de forma privada junto con una copia segura del volumen n8n.

## Copias y portabilidad

El ZIP comparte fuentes y workflows sin credenciales. Los volúmenes son específicos de cada instalación. Para una copia privada completa, detener n8n y respaldar `n8n_data` y `.env` en almacenamiento seguro; nunca añadirla al ZIP académico. Ollama puede volver a descargar los pesos. Exportar los workflows desde la interfaz sin credenciales; `scripts/exportar_workflows.sh` ofrece una exportación sanitizada de los tres IDs TA4. La configuración SQLite permanece en el volumen; no se exportan credenciales descifradas.
