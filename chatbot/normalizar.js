const raw = $input.first().json;
const value = raw.message ?? raw.body?.message ?? '';
const text = typeof value === 'string' ? value.trim() : '';
const normalized = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const injection = /ignora|ignore|system prompt|prompt del sistema|revela|reveal|instrucciones internas|actua como|olvida tus|<\|/.test(normalized);
return [{json:{message:text, normalized, conversation_id:String(raw.conversation_id ?? raw.body?.conversation_id ?? ''),
  invalid:!text ? 'empty' : text.length > 1200 ? 'too_long' : injection ? 'injection' : ''}}];
