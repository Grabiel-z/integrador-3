"""Obtiene 20 empresas de una relación pública oficial; no es una consulta RUC."""
import argparse
import json
from pathlib import Path
import httpx
from bs4 import BeautifulSoup
from openpyxl import Workbook
from sunat.excel import valid_ruc, style_sheet, now

SOURCE = "https://ww3.sunat.gob.pe/descarga/AgentRet/AgenRet31.html"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--refresh",action="store_true",help="Volver a descargar la relación oficial")
    args=parser.parse_args()
    seed=json.loads(Path("datos/ruc_semilla.json").read_text())
    records=[{"ruc":r,"razon_social_fuente":n,"fuente":seed.get("fuentes_adicionales",{}).get(r,seed["fuente"]),"fecha_verificacion_fuente":seed["fecha_revision"],"metodo":seed["metodo"]} for r,n in seed["empresas"]]
    if args.refresh:
        response = httpx.get(SOURCE, timeout=60, follow_redirects=True)
        response.raise_for_status()
        html = response.content.decode("latin-1")
        Path("evidencias/fuente_ruc.html").write_text(html)
        soup = BeautifulSoup(html, "html.parser")
        records = []
        for tr in soup.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
            for i, value in enumerate(cells[:-1]):
                if valid_ruc(value) and value not in [r["ruc"] for r in records]:
                    records.append({"ruc":value,"razon_social_fuente":cells[i+1],"fuente":SOURCE,"fecha_verificacion_fuente":now()})
    if len(records) < 20:
        raise RuntimeError("La fuente no contiene 20 RUC verificables. No se inventaron registros.")
    records = records[:20]
    assert len({r["ruc"] for r in records})==20 and all(valid_ruc(r["ruc"]) for r in records)
    Path("datos/ruc_fuentes.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
    wb = Workbook()
    ws = wb.active
    ws.title = "Entrada"
    ws.append(["RUC", "Razón social en fuente pública", "Fuente oficial", "Verificación de fuente"])
    for r in records:
        ws.append([r["ruc"], r["razon_social_fuente"], r["fuente"], r["fecha_verificacion_fuente"]])
    style_sheet(ws, {"A":18, "B":60, "C":75, "D":30})
    wb.save("datos/RUC_entrada.xlsx")
    print("20 RUC contrastados en listado oficial; no se presume su estado tributario actual.")


if __name__ == "__main__":
    main()
