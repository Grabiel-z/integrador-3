import html
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1366,'height':900},locale='es-PE')
        page.goto('http://n8n:5678',wait_until='networkidle',timeout=60000)
        page.screenshot(path='evidencias/n8n_interfaz.png',full_page=True)
        evidence=Path('evidencias/chatbot_normal.json')
        if evidence.exists():
            data=json.loads(evidence.read_text())
            rows=''.join('<tr><td>'+html.escape(r['message'][:110] or '[vacío]')+'</td><td>'+html.escape(r.get('response',{}).get('response',r.get('error','')).split('\n\n')[0])+'</td><td>'+str(r['passed'])+'</td></tr>' for r in data['records'][1:4])
            page.set_viewport_size({'width':1000,'height':600})
            page.set_content('<html lang="es"><meta charset="utf-8"><style>body{font:23px Arial;margin:28px;color:#183d4b}h1{font-size:29px}p{font-size:19px}td,th{padding:15px;border-bottom:1px solid #dbe9ec;vertical-align:top}table{border-collapse:collapse;width:100%}th{background:#edf4f5}</style><h1>Resultados de integración registrados</h1><p>Tres casos extraídos de evidencias/chatbot_normal.json. No es la interfaz de Telegram.</p><table><tr><th>Consulta real a n8n</th><th>Respuesta registrada</th><th>Aprobada</th></tr>'+rows+'</table></html>')
            page.screenshot(path='evidencias/pruebas_resumen.png',full_page=True)
        browser.close()


if __name__=='__main__':main()
