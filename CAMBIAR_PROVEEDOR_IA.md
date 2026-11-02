# Cambiar proveedor de IA

Solo se llama al proveedor indicado en `LLM_PROVIDER`. No hay fallback automático a una API comercial. Las variables externas vacías son intencionales; el modo Ollama no necesita ninguna.

Editar `.env` y elegir **uno**:

```dotenv
LLM_PROVIDER=ollama
```

Para un proveedor externo, establecer `LLM_PROVIDER=openai`, `gemini` o `anthropic`, y únicamente su par `*_API_KEY` y `*_MODEL`. Reiniciar el gateway:

```sh
docker compose up -d --no-deps ai-gateway
sh scripts/probar_chatbot.sh
```

Identificadores observados en catálogos oficiales el 02/11/2026: OpenAI `gpt-6.1-sol`; Gemini `gemini-3.8-flash`; Anthropic `claude-haiku-5-5`. Son ejemplos de catálogo, no recomendaciones de precio ni garantías de acceso de una cuenta. Elegir en el catálogo vigente y revisar límites, compatibilidad de salida JSON y costos. Los adaptadores admiten un identificador configurable; no se ejecutaron APIs sin credenciales. En modelos OpenAI que gasten tokens de razonamiento puede necesitarse aumentar `LLM_MAX_TOKENS` para que haya texto final.

Sin clave o modelo devuelve un 503 claro antes de llamar al proveedor. Los errores 502/504 se manejan en n8n y no alteran la configuración local. Para volver a Gemma, restaurar `LLM_PROVIDER=ollama` y recrear el gateway. Sus pesos y volumen permanecen intactos.

Las claves se guardan en `.env` privado, excluido del ZIP. No publicarlas en capturas. Una suscripción de ChatGPT no debe interpretarse como créditos de API. Las llamadas comerciales requieren credenciales y facturación propias.

Fuentes oficiales: https://developers.openai.com/api/docs/guides/text ; https://ai.google.dev/gemini-api/docs/models ; https://platform.claude.com/docs/en/models/overview .

## Contrato interno

`POST http://ai-gateway:8000/chat` recibe `message` (1 a 1200 caracteres), `context` (1 a 16000) y `conversation_id` opcional. Devuelve `response` (texto JSON del modelo), `provider`, `model`, `elapsed_seconds` y `metrics`. El contexto lo prepara n8n. `response` no es texto comercial validado hasta que CORE_CHATBOT comprueba sus identificadores. La documentación OpenAPI está en `/docs` dentro de la red Docker, sin publicación al host.
