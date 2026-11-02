"""Informe y matriz basados en evidencia registrada; todo se ejecuta en Docker."""
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, KeepTogether
from sunat.excel import now


def load(path,default=None):
    p=Path(path)
    return json.loads(p.read_text()) if p.exists() else (default or {})


def unit_results():
    p=Path("evidencias/tests_unitarios.xml")
    if not p.exists():return {"tests":0,"failures":0,"errors":0,"skipped":0}
    root=ET.parse(p).getroot()
    suites=[root] if root.tag=="testsuite" else list(root.iter("testsuite"))
    return {k:sum(int(s.get(k,"0")) for s in suites) for k in ("tests","failures","errors","skipped")}


def evidence_state():
    units=unit_results();sunat=load("evidencias/sunat_resumen.json");model=load("evidencias/gemma_benchmark.json")
    bot=load("evidencias/chatbot_normal.json");docker=load("evidencias/docker_verificacion.json")
    faults=load("evidencias/fallos_reales.json")
    telegram=load("evidencias/telegram/verificacion.json")
    state={"fecha":now(),"tests_unitarios":units,"sunat":{k:sunat.get(k) for k in ("total","completos","bloqueados","manuales_importados")},
        "modelo":model.get("model","gemma4:e2b-it-q4_K_M"),"docker":docker,"chatbot":{"total":bot.get("total",0),"aprobados":bot.get("passed",0)},
        "estados":{
            "Docker":"VERIFICADO" if docker.get("reinicio_persistencia") else "IMPLEMENTADO, NO VERIFICADO",
            "Tests unitarios":"VERIFICADO" if units["tests"]>0 and not units["failures"] and not units["errors"] else "ERROR IDENTIFICADO",
            "SUNAT":"VERIFICADO" if sunat.get("completos")==20 else "BLOQUEADO POR RESTRICCIÓN EXTERNA" if sunat.get("bloqueados") else "IMPLEMENTADO, NO VERIFICADO",
            "Gemma":"VERIFICADO" if model and model.get("errors")==0 else "IMPLEMENTADO, NO VERIFICADO",
            "Chatbot n8n + IA":"VERIFICADO" if bot.get("total",0)>0 and bot.get("passed")==bot.get("total") else "IMPLEMENTADO, NO VERIFICADO",
            "APIs comerciales":"IMPLEMENTADO, NO VERIFICADO",
            "Telegram":"VERIFICADO" if telegram.get("probado") and list(Path("evidencias/telegram").glob("*.png")) else "PENDIENTE DE TOKEN TELEGRAM",
            "Identificación de equipo":"VERIFICADO" if load("informe/equipo.json").get("integrantes") else "PENDIENTE DE OTRA INTERVENCIÓN",
            "Cuenta administradora n8n":"PENDIENTE DE OTRA INTERVENCIÓN",
            "Consigna PDF original":"PENDIENTE DE OTRA INTERVENCIÓN"}}
    Path("ESTADO_FINAL.json").write_text(json.dumps(state,ensure_ascii=False,indent=2))
    lines=["# Pruebas realizadas", "", "Registro generado: "+now(),"", "Los tests unitarios usan fixtures. Las integraciones llaman servicios Docker reales. No se equiparan ambos tipos.","",
        "| Componente | Estado | Evidencia |","|---|---|---|"]
    refs={"Docker":"evidencias/docker_verificacion.json, compose_ps.txt y recursos_docker.txt","Tests unitarios":"evidencias/tests_unitarios.xml y tests_unitarios.log",
          "SUNAT":"evidencias/sunat_resumen.json y captura del rechazo; datos/RUC_resultados.xlsx","Gemma":"evidencias/gemma_benchmark.json y modelo.json",
          "Chatbot n8n + IA":"evidencias/chatbot_normal.json","APIs comerciales":"pruebas/test_gateway.py; sin llamadas comerciales",
          "Telegram":"CONECTAR_TELEGRAM.md","Identificación de equipo":"informe/equipo.json","Cuenta administradora n8n":"Crear cuenta propia en http://localhost:5678; no se compartió una cuenta ficticia","Consigna PDF original":"No localizada en carpetas revisadas"}
    lines += [f"| {k} | {v} | {refs[k]} |" for k,v in state["estados"].items()]
    lines += ["",f"Tests ejecutados: {units['tests']}; fallos: {units['failures']}; errores: {units['errors']}; omitidos: {units['skipped']}.",
        f"RUC de entrada contrastados en fuente oficial: 20. Fichas completas obtenidas: {sunat.get('completos',0)}/20. Las filas bloqueadas no contienen datos fiscales inferidos.",
        f"Pruebas de chatbot real: {bot.get('passed',0)}/{bot.get('total',0)}. Revisa cada respuesta, ai_used y latencia en el JSON.", "",
        "## Fallos y límites", "", "SUNAT devolvió HTTP 403 en esta ejecución. No se eludieron controles; las siguientes filas se registraron bajo el mismo bloqueo sin nuevas solicitudes. La contingencia manual está documentada.",
        "Los proveedores comerciales tienen tests de estructura y manejo de errores; no se probaron con credenciales reales. No se midió aceleración GPU.",
        "El token Telegram, su webhook y la conversación real quedan pendientes. La cuenta administradora n8n debe crearla cada equipo al abrir la interfaz. Completar nombres reales y contrastar con el PDF original no disponible."]
    if model:
        lines += ["", "## Medidas de Gemma", "",f"Modelo: {model['model']}. Media de tres generaciones: {model['average_seconds']:.3f} s. Errores observados: {model['errors']}.",
          "| Ensayo | Primer contenido (s) | Duración (s) | Tokens salida |","|---|---:|---:|---:|"]
        for r in model["runs"]:
            lines.append(f"| {r['run']} | {r['first_token_seconds']:.3f} | {r['elapsed_seconds']:.3f} | {r['metrics'].get('eval_count','')} |")
        lines += ["","La primera medida del ensayo no implica arranque frío. Memoria del modelo en /api/ps y memoria del contenedor en docker stats se registran por separado."]
    if faults:lines += ["","## Errores provocados en servicios reales","",json.dumps(faults,ensure_ascii=False,indent=2)]
    Path("PRUEBAS_REALIZADAS.md").write_text("\n".join(lines)+"\n")
    rubric="""# Cumplimiento de la rúbrica

La lista original no estuvo disponible. Esta matriz cubre los requisitos del texto recibido; debe contrastarse con la consigna original. La nota corresponde exclusivamente al docente.

| Criterio | Puntaje de referencia | Entregables | Límite que debe revisarse |
|---|---:|---|---|
| Investigación | 5 | investigacion/rutas_laborales.md y certificaciones.md; cinco rutas, tres certificados y fuentes oficiales | Volver a revisar vigencia antes de presentar |
| Análisis de negocio | 5 | investigacion/casos_empresariales.md; problemas, procesos, necesidades, riesgos y límites | No se cuantifica ahorro sin mediciones |
| Flujos automatizados | 6 | SUNAT, Excel, tres workflows n8n y gateway real | SUNAT y Telegram dependen de las evidencias reales; ver estados abajo |
| Presentación | 2 | GUIA_EXPOSICION.md y cuatro diagramas editables | Ensayo y exposición a cargo del grupo |
| Informe | 2 | PDF, fuente Markdown, ZIP, configuración y pruebas | Completar identidad y evidencias pendientes |

"""
    rubric += "\n".join(f"- {k}: **{v}**." for k,v in state["estados"].items())+"\n"
    Path("CUMPLIMIENTO_RUBRICA.md").write_text(rubric)
    return state,units,sunat,model,bot


def strip_title(path):
    lines=Path(path).read_text().splitlines()
    return "\n".join(lines[1:]).replace("\n## ","\n### ")


def diagrams():
    for path in Path("diagramas").glob("*.dot"):
        for fmt in ("svg","png"):
            subprocess.run(["dot","-T"+fmt,str(path),"-o",str(path.with_suffix("."+fmt))],check=True)


def report_source(state,units,sunat,model,bot):
    source=Path("informe/informe_base.md").read_text()
    results_sunat=f"Estado: {state['estados']['SUNAT']}. Veinte RUC de entrada contrastados en publicación oficial; {sunat.get('completos',0)} fichas completas de veinte."
    results_sunat+=" El Excel diferencia una ficha completa de una restricción externa y conserva fecha y observaciones."
    if sunat.get('bloqueados'):
        results_sunat+=" En el lote observado, el primer acceso fue rechazado con HTTP 403 y se aplicó un corte de solicitudes. La captura es evidencia del bloqueo, no de una consulta completada."
    if sunat.get('manuales_importados'):
        results_sunat+=f" Se importaron {sunat['manuales_importados']} fichas de consulta manual; no se contabilizan como consultas RPA realizadas automáticamente."
    if sunat.get("registros"):
        results_sunat+="\n\n| RUC | Estado de consulta |\n|---|---|\n"
        results_sunat+="\n".join(f"| {r['RUC']} | {r['Estado de consulta']} |" for r in sunat["registros"])
    tests=f"La suite unitaria registró {units['tests']} casos, {units['failures']} fallos y {units['errors']} errores. Incluye checksum, entradas inválidas, duplicados, extracción con fixture sintético, separación de fechas y condición, exportación segura y contratos de cuatro adaptadores. Estos casos no son consultas SUNAT ni llamadas comerciales reales."
    tests+=f" Las pruebas reales mediante n8n registraron {bot.get('passed',0)} de {bot.get('total',0)} casos aprobados; cada caso comprueba contenido y uso de IA cuando corresponde. Se incluyen las quince consultas requeridas, mensaje largo, instrucciones maliciosas y una pregunta con datos contradictorios."
    ai="Estado de Gemma: "+state["estados"]["Gemma"]+". Estado de integración n8n: "+state["estados"]["Chatbot n8n + IA"]+"."
    if model:
        ai+=f" Modelo {model['model']}; cuantización observada {model['details']['quantization_level']}. Promedio de tres generaciones: {model['average_seconds']:.3f} segundos; errores de validación: {model['errors']}."
        ai+="\n\n| Ensayo | Primer contenido (s) | Duración total (s) | Tokens de salida |\n|---|---|---|---|\n"
        ai+="\n".join(f"| {r['run']} | {r['first_token_seconds']:.3f} | {r['elapsed_seconds']:.3f} | {r['metrics'].get('eval_count','')} |" for r in model["runs"])
        loaded=model.get("loaded_model_memory",{}).get("models",[])
        if loaded:ai+=f"\n\nOllama informó {loaded[0].get('size',0)/1024**3:.2f} GiB de tamaño de memoria del modelo cargado. La memoria del contenedor, registrada separadamente en recursos_docker.txt, incluye otros componentes y cachés. No se extrapola a otro hardware."
        stats=Path('evidencias/recursos_docker.txt')
        if stats.exists():
            sample=next((line for line in stats.read_text().splitlines() if 'ta4-ollama-1' in line),'')
            match=re.search(r'(\d+(?:\.\d+)?[GM]iB)\s*/\s*(\d+(?:\.\d+)?[GM]iB)',sample)
            if match:ai+=f" En la muestra registrada, docker stats midió {match[1]} de memoria del contenedor Ollama con límite {match[2]}."
        if bot.get("average_seconds") is not None:ai+=f" La latencia media del conjunto de casos n8n fue {bot['average_seconds']:.3f} segundos; incluye rechazos directos y llamadas a IA."
    evidences="Telegram: "+state["estados"]["Telegram"]+". Sus capturas se incorporarán cuando el equipo conecte un bot y complete una prueba real.\n\n"
    screenshots=[("evidencias/sunat/20377339461.png","Captura auténtica del acceso SUNAT desde Chromium en Docker."),
        ("evidencias/n8n_interfaz.png","Interfaz real de n8n de esta instalación."),
        ("evidencias/pruebas_resumen.png","Vista de los resultados registrados, generada desde evidencias; no representa la interfaz de Telegram.")]
    screenshots += [(str(p),"Evidencia Telegram aportada por el equipo.") for p in Path("evidencias/telegram").glob("*.png")]
    for path,caption in screenshots:
        if Path(path).exists():evidences+=f"![{caption}]({path})\n\n"
    refs=load("investigacion/fuentes.json")["fuentes"]
    references="Revisión de fuentes: 2 de noviembre de 2026.\n\n"+"\n\n".join(f"[{i}] {s['titulo']}. {s['url']}" for i,s in enumerate(refs,1))
    values={"RUTAS":strip_title("investigacion/rutas_laborales.md"),"CERTIFICACIONES":strip_title("investigacion/certificaciones.md"),
        "CASOS":strip_title("investigacion/casos_empresariales.md"),"RESULTADOS_SUNAT":results_sunat,"RESULTADOS_TESTS":tests,
        "RESULTADOS_IA":ai,"EVIDENCIAS":evidences,"REFERENCIAS":references}
    for key,name in [("SUNAT","sunat"),("CHATBOT","chatbot"),("DOCKER","docker"),("PROVEEDORES","proveedores")]:
        values["DIAGRAMA_"+key]=f"![Diagrama: {name}](diagramas/{name}.png)"
    for key,value in values.items():source=source.replace("{{"+key+"}}",value)
    if "{{" in source:raise ValueError("Marcador de informe sin resolver")
    Path("informe/Proyecto_RPA_1_GrupoX.md").write_text(source)
    return source


def pdf(source):
    fontdir=Path("/usr/share/fonts/truetype/dejavu")
    for name,file in [("DejaVu","DejaVuSans.ttf"),("DejaVu-Bold","DejaVuSans-Bold.ttf")]:
        pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
    pdfmetrics.registerFontFamily("DejaVu",normal="DejaVu",bold="DejaVu-Bold",italic="DejaVu",boldItalic="DejaVu-Bold")
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BodyES",fontName="DejaVu",fontSize=9.5,leading=14,spaceAfter=8,textColor=colors.HexColor("#243B45")))
    styles.add(ParagraphStyle(name="TitleES",fontName="DejaVu-Bold",fontSize=29,leading=36,textColor=colors.HexColor("#183D4B"),spaceAfter=20))
    styles.add(ParagraphStyle(name="H1ES",fontName="DejaVu-Bold",fontSize=15,leading=20,spaceBefore=16,spaceAfter=9,textColor=colors.HexColor("#183D4B"),keepWithNext=True))
    styles.add(ParagraphStyle(name="H2ES",fontName="DejaVu-Bold",fontSize=11,leading=16,spaceBefore=10,spaceAfter=6,keepWithNext=True))
    styles.add(ParagraphStyle(name="CaptionES",fontName="DejaVu",fontSize=8,leading=11,alignment=TA_CENTER,spaceAfter=12))
    styles.add(ParagraphStyle(name="SmallES",fontName="DejaVu",fontSize=7.5,leading=11,wordWrap="CJK"))
    team=load("informe/equipo.json")
    story=[Spacer(1,50),Paragraph("TAREA ACADÉMICA 4",styles["H2ES"]),Paragraph("Automatización<br/>con IA local",styles["TitleES"]),
        Paragraph("Consulta SUNAT · Restaurante Sabor Peruano",styles["H2ES"]),Spacer(1,22),
        Paragraph(escape(team["equipo"]),styles["BodyES"]),
        Paragraph("Integrantes: "+escape(", ".join(team["integrantes"]) if team["integrantes"] else "pendientes de identificación por el equipo"),styles["BodyES"]),
        Paragraph("Fecha: "+team["fecha"]+" · Zona horaria America/Lima",styles["BodyES"]),Spacer(1,15),
        Paragraph(escape(team["herramientas"]),styles["BodyES"]),Spacer(1,28),
        Paragraph("Informe generado desde fuentes y evidencias del proyecto. Los estados de verificación y pendientes se explicitan en el documento; no se atribuye una calificación.",styles["BodyES"]),PageBreak()]
    lines=source.splitlines();i=0
    def para(s,style="BodyES"):
        s=escape(s).replace("`","")
        s=re.sub(r"\*\*(.+?)\*\*",r"<b>\1</b>",s)
        return Paragraph(s,styles[style])
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line.startswith("# "):story.append(para(line[2:],"H1ES"));continue
        if line.startswith("### ") or line.startswith("## "):
            story.append(para(line.lstrip("# "),"H2ES"));continue
        match=re.match(r"!\[(.*?)\]\((.*?)\)",line)
        if match:
            p=Path(match[2]);w,h=ImageReader(str(p)).getSize();scale=min(475/w,(420 if p.stem=='docker' else 300)/h,1)
            story.append(KeepTogether([Image(str(p),width=w*scale,height=h*scale),para(match[1],"CaptionES")]))
            continue
        if line.startswith("|"):
            rows=[line]
            while i<len(lines) and lines[i].strip().startswith("|"):rows.append(lines[i].strip());i+=1
            parsed=[[para(c.strip(),"SmallES") for c in row.strip("|").split("|")] for row in rows if not re.fullmatch(r"[|:\-\s]+",row)]
            cols=len(parsed[0]);widths=[475/cols]*cols
            if cols==2:widths=[110,365]
            table=Table(parsed,colWidths=widths,repeatRows=1,hAlign="LEFT")
            table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#DBE9EC")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F2F6F7")]),
                ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
            story.extend([table,Spacer(1,12)]);continue
        text=[line]
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(("#","|","![")):
            text.append(lines[i].strip());i+=1
        story.append(para(" ".join(text),"SmallES" if line.startswith("[") or "https://" in " ".join(text) and len(" ".join(text))<300 else "BodyES"))
    out=Path("output/pdf/Proyecto_RPA_1_GrupoX.pdf");out.parent.mkdir(parents=True,exist_ok=True)
    def page(canvas,doc):
        canvas.setStrokeColor(colors.HexColor("#DAE5E8"));canvas.line(52,48,543,48)
        canvas.setFont("DejaVu",7);canvas.setFillColor(colors.HexColor("#52727B"))
        canvas.drawString(52,34,"TA4 | Automatización SUNAT y chatbot con IA local")
        canvas.drawRightString(543,34,str(doc.page))
    SimpleDocTemplate(str(out),pagesize=A4,rightMargin=60,leftMargin=60,topMargin=45,bottomMargin=63,
        title="TA4 - Automatización SUNAT y chatbot con IA local",author=team["equipo"]).build(story,onFirstPage=page,onLaterPages=page)
    print(out)


def main():
    diagrams()
    data=evidence_state()
    source=report_source(*data)
    pdf(source)


if __name__=="__main__":main()
