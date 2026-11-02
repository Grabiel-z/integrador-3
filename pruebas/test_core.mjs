// Pruebas unitarias de los nodos reales exportados. Respuestas LLM sintéticas.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const core=JSON.parse(fs.readFileSync('/workflows/CORE_CHATBOT.json','utf8'));
const code=name=>core.nodes.find(n=>n.name===name).parameters.jsCode;
const run=(name,input,base)=>new Function('$input','$',code(name))({first:()=>({json:input})},()=>({first:()=>({json:base})}))[0].json;
const normalized=run('Normalizar mensaje',{message:'¿Cuánto cuesta el menú?'});
const base=run('Recuperar conocimiento',normalized);
const fixtures=[
  {name:'JSON válido',response:'{"fact_ids":["menu_dia"]}',status:'verificado'},
  {name:'Hecho inventado y precio contradictorio',response:'{"fact_ids":["menu_a_1_sol"],"precio":1}',status:'respuesta_invalida'},
  {name:'Texto contradictorio fuera del contrato',response:'El menú cuesta S/ 1.00 y abrimos a las 23:00',status:'respuesta_invalida'},
  {name:'JSON vacío',response:'{"fact_ids":[]}',status:'respuesta_invalida'},
  {name:'Error del proveedor',error:'fixture de error',status:'error_proveedor'}
];
const records=[];
for(const fixture of fixtures){
  const out=run('Validar y cerrar',fixture,base);
  assert.equal(out.ai_status,fixture.status);
  assert.ok(out.response.includes('18.00'));
  assert.ok(!out.response.includes('S/ 1.00'));
  records.push({name:fixture.name,passed:true,ai_status:out.ai_status});
}
process.stdout.write(JSON.stringify({tipo:'pruebas unitarias con respuestas LLM sintéticas; código real de n8n',records},null,2)+'\n');
