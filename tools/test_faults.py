"""Errores reales del adaptador Ollama; no usa respuestas simuladas ni claves."""
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
from gateway.app import app
from sunat.excel import now


def main():
    original=dict(os.environ)
    records=[]
    try:
        os.environ['LLM_PROVIDER']='ollama'
        os.environ['OLLAMA_MODEL']='ta4-modelo-inexistente'
        with TestClient(app) as client:
            r=client.post('/chat',json={'message':'Hola','context':'Restaurante Sabor Peruano'})
            records.append({'caso':'modelo ausente en Ollama real','http_status':r.status_code,'body':r.json(),'passed':r.status_code==502 and r.json()['detail']=='MODELO_AUSENTE'})
        os.environ['OLLAMA_MODEL']='gemma4:e2b-it-q4_K_M'
        os.environ['LLM_TIMEOUT']='0.001'
        with TestClient(app) as client:
            r=client.post('/chat',json={'message':'¿Cuál es el horario?','context':'Restaurante Sabor Peruano: abre a las 12:00'})
            records.append({'caso':'timeout real de 1 ms','http_status':r.status_code,'body':r.json(),'passed':r.status_code==504})
    finally:
        os.environ.clear();os.environ.update(original)
    result={'fecha':now(),'tipo':'gateway ejecutado en Docker mediante TestClient y solicitudes HTTP a Ollama real','records':records}
    Path('evidencias/fallos_reales.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if all(r['passed'] for r in records) else 1)


if __name__=='__main__':main()
