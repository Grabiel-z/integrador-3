# Modelo local y recursos

Modelo exacto: `gemma4:e2b-it-q4_K_M`. Publicación oficial: https://ollama.com/library/gemma4:e2b-it-q4_K_M . Nunca se reemplaza por un alias u otro tamaño. Las pruebas comprueban `quantization_level=Q4_K_M` mediante `/api/show`.

Configuración inicial: CPU, `num_ctx=2048`, temperatura 0.2, máximo 192 tokens, seis hilos, concurrencia uno, un modelo cargado y permanencia diez minutos. Se utiliza la opción oficial `think:false`; no se insertan tokens especiales. El modelo devuelve JSON breve con identificadores y no se muestra razonamiento al cliente. La temperatura es una decisión inicial para clasificación factual; no se afirma que sea universalmente óptima.

El inicializador comprueba RAM disponible y disco del volumen antes de descargar. Se requieren como salvaguarda 5 GiB de RAM disponible y 9 GiB de disco para la descarga y el modelo; el conjunto necesita margen adicional para n8n, Chromium y el sistema. La recomendación de instalación es 16 GiB totales y 20 GiB libres. El almacenamiento y el uso real se revisan en las evidencias; el tamaño del archivo no es igual al consumo en inferencia.

`sh scripts/probar_ia.sh` mide tres generaciones reales: tiempo al primer fragmento de contenido, duración total, tokens y métricas de Ollama. La primera del ensayo puede incluir carga del modelo; no se denomina arranque frío si ya estaba cargado. El consumo de `/api/ps` es tamaño de memoria del modelo informado por Ollama; `docker stats` registra memoria del contenedor. Son medidas distintas, no intercambiables. No se infieren benchmarks de otro equipo.

La configuración CPU es la predeterminada. NVIDIA es opcional: solo después de verificar GPU y soporte de contenedores, puede aplicarse `compose.gpu.yaml` con el runtime de GPU compatible. No instalar CUDA para una laptop sin NVIDIA. No se afirma aceleración comprobada si no aparece en las evidencias.

```sh
docker compose -f compose.yaml -f compose.gpu.yaml up -d ollama
```

Una actualización de Ollama debe validar nuevamente modelo, opciones y resultados antes de cambiar la versión fijada.
