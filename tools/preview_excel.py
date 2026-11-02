"""Vista de datos y estilos guardados. No simula una aplicación de Excel."""
import html
from pathlib import Path
from openpyxl import load_workbook
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for name in ('RUC_entrada','RUC_resultados'):
            wb=load_workbook('datos/'+name+'.xlsx');ws=wb.active
            headers=''.join('<col style="width:'+str(int(ws.column_dimensions[c.column_letter].width*7))+'px">' for c in ws[1])
            rows=''
            for row in ws.iter_rows(max_row=min(ws.max_row,9)):
                cells=''
                for cell in row:
                    color=cell.fill.fgColor.rgb if cell.fill.patternType=='solid' and cell.fill.fgColor.type=='rgb' else 'FFFFFFFF'
                    textcolor=cell.font.color.rgb if cell.font.color and cell.font.color.type=='rgb' else 'FF243B45'
                    cells+='<td style="background:#'+str(color)[-6:]+';color:#'+str(textcolor)[-6:]+';font-weight:'+('700' if cell.font.bold else '400')+'">'+html.escape(str(cell.value or ''))+'</td>'
                rows+='<tr>'+cells+'</tr>'
            width=sum(int(ws.column_dimensions[c.column_letter].width*7) for c in ws[1])+80
            page=browser.new_page(viewport={'width':width,'height':800})
            page.set_content('<meta charset="utf-8"><style>body{font:15px Arial;margin:24px;color:#183d4b}table{table-layout:fixed;border-collapse:collapse}td{padding:9px;vertical-align:top;overflow-wrap:anywhere;border-bottom:1px solid #dbe9ec;line-height:21px}h1{font-size:24px}</style><h1>'+name+'</h1><p>Vista de datos y estilos del archivo XLSX guardado; primeras ocho filas. RUC conservado como texto.</p><table><colgroup>'+headers+'</colgroup>'+rows+'</table>')
            page.screenshot(path='evidencias/'+name+'_vista.png',full_page=True)
            page.close();wb.close()
        browser.close()


if __name__=='__main__':main()
