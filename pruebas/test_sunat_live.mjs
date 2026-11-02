// Integración real desde el contenedor n8n; no es una ejecución de workflow.
const cases = ['20100047218', '20100130204'];
const results = [];
for (const ruc of cases) {
  const response = await fetch(`http://sunat-api:8001/ruc/${ruc}`, {signal: AbortSignal.timeout(40000)});
  const data = await response.json();
  const passed = response.status === 200 && data.datos?.ruc === ruc
    && data.estado_consulta_api === 'VERIFICADO' && data.intervencion_humana === false
    && data.fuentes?.consulta_en_vivo?.http_status === 200
    && Boolean(data.datos.razon_social) && Boolean(data.datos.condicion);
  results.push({ruc, http_status: response.status, passed, respuesta: data});
}
const invalid = await fetch('http://sunat-api:8001/ruc/20100047219');
const passed = results.every(r => r.passed) && invalid.status === 422;
console.log(JSON.stringify({fecha: new Date().toISOString(),
  contexto: 'HTTP real desde el runtime de n8n; no se afirma ejecución de workflow',
  intervencion_humana: false, passed, invalido_http_status: invalid.status, resultados: results}, null, 2));
if (!passed) process.exitCode = 1;
