// KB se inyecta al generar el workflow; editar conocimiento.json y regenerar.
const kb = __KNOWLEDGE__;
const input = $input.first().json;
const t = input.normalized;
const soles = n => 'S/ ' + n.toFixed(2);
const facts = {
  saludo:'¡Hola! Soy el asistente virtual del Restaurante Sabor Peruano, un negocio ficticio de demostración. Puedo informar sobre menú, horarios, ubicación, delivery y reservas.',
  horario:`Atendemos de lunes a sábado de ${kb.horario.lunes_sabado} y domingos de ${kb.horario.domingo}.`,
  ubicacion:`Estamos en ${kb.direccion}.`,
  menu:kb.menu.map(p=>`${p.plato}: ${soles(p.precio)}${p.detalle ? ' ('+p.detalle+')' : ''}`).join('; ')+'.',
  menu_dia:`El menú del día cuesta ${soles(kb.menu[0].precio)} e incluye ${kb.menu[0].detalle.toLowerCase()}.`,
  ceviche:`Sí, tenemos ${kb.menu[1].plato} a ${soles(kb.menu[1].precio)}. La disponibilidad debe confirmarla el personal.`,
  delivery:`Ofrecemos delivery en ${kb.delivery.zona} por ${soles(kb.delivery.costo)}, de ${kb.delivery.horario}. ${kb.delivery.confirmacion}.`,
  pagos:`Aceptamos ${kb.pagos.join(', ')}. El bot no verifica ni confirma pagos.`,
  reservas:kb.reservas,
  recomendaciones:'Puedes elegir '+kb.menu.slice(1,5).map(p=>p.plato+' ('+soles(p.precio)+')').join(', ')+'. Consulta ingredientes con el personal.',
  economico:(()=>{const p=kb.menu.reduce((a,b)=>a.precio<b.precio?a:b);return `La opción más económica registrada es ${p.plato}, a ${soles(p.precio)}.`;})(),
  promociones:kb.promociones,
  servicios:`Ofrecemos ${kb.servicios.join(', ')}.`,
  alergenos:kb.alergenos
};
let ids=[];
if(/horario|abren|domingo|cierran|hora de atencion/.test(t)) ids.push('horario');
if(/ubic|direccion|donde|llegar/.test(t)) ids.push('ubicacion');
if(/menu/.test(t)) ids.push(/cuanto|cuesta|precio|dia/.test(t)?'menu_dia':'menu');
if(/ceviche/.test(t)) ids.push('ceviche');
if(/carta|platos|comida/.test(t)) ids.push('menu');
if(/recomiend/.test(t)) ids.push('recomendaciones');
if(/economico|mas barato|menor precio/.test(t)) ids.push('economico');
if(/delivery|domicilio|reparto/.test(t)) ids.push('delivery');
if(/yape|plin|pago|tarjeta|efectivo/.test(t)) ids.push('pagos');
if(/reserv/.test(t)) ids.push('reservas');
if(/promoci|descuento/.test(t)) ids.push('promociones');
if(/servicio|llevar/.test(t)) ids.push('servicios');
if(/alerg|ingrediente|gluten|vegetarian/.test(t)) ids.push('alergenos');
if(/^(hola|buenas|buenos dias|buenas tardes|buenas noches)[!.\s]*$/.test(t)) ids.push('saludo');
ids=[...new Set(ids)];
const outside=/presidente|politic|futbol|programa|codigo python|capital de|matemat|receta|bitcoin|clima/.test(t);
let direct='';
if(input.invalid==='empty') direct='Por favor, escribe tu consulta sobre el restaurante.';
else if(input.invalid==='too_long') direct='Tu mensaje es demasiado largo. Envíalo con un máximo de 1200 caracteres.';
else if(input.invalid==='injection') direct='Solo puedo ayudar con información pública del restaurante; no comparto instrucciones internas.';
else if(outside) direct='Solo puedo atender preguntas sobre el Restaurante Sabor Peruano.';
else if(!ids.length) direct='No tengo información suficiente sobre esa consulta. Puedes preguntar por menú, horarios, dirección, delivery o reservas.';
return [{json:{...input, facts:Object.fromEntries(ids.map(id=>[id,facts[id]])), fact_ids:ids,
  needs_ai:!direct, direct, closing:kb.cierre,
  context:JSON.stringify({negocio:kb.nombre,ficticio:true,hechos:ids.map(id=>({id,texto:facts[id]}))})}}];
