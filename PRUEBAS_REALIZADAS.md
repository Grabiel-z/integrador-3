# Pruebas realizadas

Registro generado: 2026-11-02T09:32:21-05:00

Los tests unitarios usan fixtures. Las integraciones llaman servicios Docker reales. No se equiparan ambos tipos.

| Componente | Estado | Evidencia |
|---|---|---|
| Docker | VERIFICADO | evidencias/docker_verificacion.json, compose_ps.txt y recursos_docker.txt |
| Tests unitarios | VERIFICADO | evidencias/tests_unitarios.xml y tests_unitarios.log |
| API SUNAT automática | VERIFICADO | evidencias/sunat_soap/, sunat_api/ y sunat_n8n_http.json; SOAP real sin intervención humana |
| SUNAT | PENDIENTE DE OTRA INTERVENCIÓN | evidencias/sunat_resumen.json y datos/RUC_resultados.xlsx; faltan fechas de inicio |
| Gemma | VERIFICADO | evidencias/gemma_benchmark.json y modelo.json |
| Chatbot n8n + IA | VERIFICADO | evidencias/chatbot_normal.json |
| APIs comerciales | IMPLEMENTADO, NO VERIFICADO | pruebas/test_gateway.py; sin llamadas comerciales |
| Telegram | PENDIENTE DE TOKEN TELEGRAM | CONECTAR_TELEGRAM.md |
| Identificación de equipo | PENDIENTE DE OTRA INTERVENCIÓN | informe/equipo.json |
| Cuenta administradora n8n | PENDIENTE DE OTRA INTERVENCIÓN | Crear cuenta propia en http://localhost:5678; no se compartió una cuenta ficticia |
| Consigna PDF original | PENDIENTE DE OTRA INTERVENCIÓN | No localizada en carpetas revisadas |

Tests ejecutados: 50; fallos: 0; errores: 0; omitidos: 0.
RUC de entrada contrastados en fuente oficial: 20. Fichas completas obtenidas: 1/20. Las filas bloqueadas no contienen datos fiscales inferidos.
Pruebas de chatbot real: 18/18. Revisa cada respuesta, ai_used y latencia en el JSON.

## Fallos y límites

SUNAT: 20 respuestas SOAP oficiales satisfactorias; 20 domicilios con datos y 1 fechas de inicio. La ruta API es automática, sin navegador ni intervención humana. SOAP y padrón no publican inicio de actividades; HTTP 200 no acredita una ficha de cinco campos. El navegador fue retirado de la ruta operativa tras mostrar un control humano. Ver GUIA_SUNAT.md.
Los proveedores comerciales tienen tests de estructura y manejo de errores; no se probaron con credenciales reales. No se midió aceleración GPU.
El token Telegram, su webhook y la conversación real quedan pendientes. La cuenta administradora n8n debe crearla cada equipo al abrir la interfaz. Completar nombres reales y contrastar con el PDF original no disponible.

## Medidas de Gemma

Modelo: gemma4:e2b-it-q4_K_M. Media de tres generaciones: 3.500 s. Errores observados: 0.
| Ensayo | Primer contenido (s) | Duración (s) | Tokens salida |
|---|---:|---:|---:|
| 1 | 7.741 | 8.564 | 9 |
| 2 | 0.178 | 0.951 | 9 |
| 3 | 0.130 | 0.985 | 9 |

La primera medida del ensayo no implica arranque frío. Memoria del modelo en /api/ps y memoria del contenedor en docker stats se registran por separado.

## Errores provocados en servicios reales

{
  "fecha": "2026-11-02T07:43:41-05:00",
  "tipo": "gateway ejecutado en Docker mediante TestClient y solicitudes HTTP a Ollama real",
  "records": [
    {
      "caso": "modelo ausente en Ollama real",
      "http_status": 502,
      "body": {
        "detail": "MODELO_AUSENTE"
      },
      "passed": true
    },
    {
      "caso": "timeout real de 1 ms",
      "http_status": 504,
      "body": {
        "detail": "Tiempo de espera agotado en el proveedor de IA"
      },
      "passed": true
    }
  ]
}
