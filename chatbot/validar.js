const base = $('Recuperar conocimiento').first().json;
const llm = $input.first().json;
let selected=[];
let status=base.needs_ai ? 'error_proveedor' : 'regla';
if(base.needs_ai && typeof llm.response==='string') {
  try {
    const parsed=JSON.parse(llm.response);
    if(Array.isArray(parsed.fact_ids) && parsed.fact_ids.length && parsed.fact_ids.every(id=>Object.hasOwn(base.facts,id))) {
      selected=[...new Set(parsed.fact_ids)]; status='verificado';
    } else status='respuesta_invalida';
  } catch {status='respuesta_invalida';}
}
// Se conservan todos los hechos detectados para no omitir horarios ni precios.
const ids = base.needs_ai ? [...new Set([...base.fact_ids,...selected])] : [];
let answer = base.direct || ids.map(id=>base.facts[id]).join('\n');
if(base.needs_ai && status!=='verificado') answer+='\nLa IA no está disponible o no validó su respuesta; esta información procede de nuestra base de conocimiento.';
return [{json:{response:answer+'\n\n'+base.closing, ai_status:status, ai_used:status==='verificado',
  provider:llm.provider ?? null, model:llm.model ?? null, fact_ids:ids, ai_elapsed_seconds:llm.elapsed_seconds ?? null,
  metrics:llm.metrics ?? {}, conversation_id:base.conversation_id}}];
