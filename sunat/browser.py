import argparse
import json
import time
import urllib.robotparser
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from sunat.excel import read_input, write_results, now
from sunat.parser import extract

URL = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"


def restriction(page):
    text = page.locator("body").inner_text().lower()
    for token in ["access denied", "request rejected", "forbidden", "captcha", "código de seguridad", "codigo de seguridad", "verify you are human", "verificación de seguridad", "security verification"]:
        if token in text:
            return token
    if page.locator("iframe[src*='recaptcha'], iframe[src*='hcaptcha']").count():
        return "CAPTCHA"
    return ""


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="datos/RUC_entrada.xlsx")
    parser.add_argument("--output", default="datos/RUC_resultados.xlsx")
    parser.add_argument("--retry-errors", action="store_true")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    rucs = read_input(args.input)[:args.limit]
    checkpoint = Path("datos/sunat_checkpoint.json")
    old = json.loads(checkpoint.read_text()) if checkpoint.exists() else []
    records = {r["RUC"]:r for r in old if r["RUC"] in rucs}
    if args.retry_errors:
        records = {k:v for k,v in records.items() if v["Estado de consulta"] == "VERIFICADO"}
    Path("evidencias/sunat").mkdir(parents=True, exist_ok=True)
    blocked = ""
    try:
        robots = httpx.get("https://e-consultaruc.sunat.gob.pe/robots.txt", timeout=20)
        if robots.status_code == 200:
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(robots.text.splitlines())
            if not rp.can_fetch("*", URL):
                blocked = "robots.txt no permite automatizar esta ruta; usar procedimiento oficial manual"
    except httpx.HTTPError:
        # La ausencia de robots no se interpreta como una autorización especial.
        pass
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="es-PE", viewport={"width":1366,"height":900})
        page = context.new_page()
        page.set_default_timeout(20000)
        for ruc in rucs:
            if ruc in records:
                continue
            record = {"RUC": ruc, "Fecha de consulta": "", "Fecha de procesamiento": now()}
            start = time.monotonic()
            if blocked:
                record.update({"Estado de consulta":"BLOQUEADO POR RESTRICCIÓN EXTERNA", "Observaciones": blocked + "; no se intentó eludir el control"})
            else:
                for attempt in range(2):
                    try:
                        record["Fecha de consulta"] = now()
                        response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                        denied = restriction(page)
                        if denied or (response and response.status in (403, 429)):
                            blocked = "Servicio oficial requiere intervención o restringe acceso: " + (denied or str(response.status))
                            record.update({"Estado de consulta":"BLOQUEADO POR RESTRICCIÓN EXTERNA", "Observaciones":blocked})
                            break
                        field = page.locator("#txtRuc, input[name='search1']").first
                        field.fill(ruc)
                        page.get_by_role("button", name="Buscar", exact=True).click()
                        page.wait_for_load_state("domcontentloaded")
                        page.locator(".list-group").first.wait_for(timeout=30000)
                        denied = restriction(page)
                        if denied:
                            blocked = "Control del servicio: " + denied
                            record.update({"Estado de consulta":"BLOQUEADO POR RESTRICCIÓN EXTERNA", "Observaciones":blocked})
                            break
                        html = page.content()
                        Path(f"evidencias/sunat/{ruc}.html").write_text(html)
                        record.update(extract(html, ruc))
                        break
                    except (PlaywrightTimeout, ValueError) as exc:
                        record.update({"Estado de consulta":"ERROR IDENTIFICADO", "Observaciones": f"Intento {attempt+1}/2: {type(exc).__name__}: {str(exc)[:250]}"})
                        if attempt == 0:
                            time.sleep(3)
                    except Exception as exc:
                        record.update({"Estado de consulta":"ERROR IDENTIFICADO", "Observaciones":f"{type(exc).__name__}: {str(exc)[:250]}"})
                        break
                try:
                    page.screenshot(path=f"evidencias/sunat/{ruc}.png", full_page=True)
                except Exception:
                    pass
            record["Observaciones"] += f"; duración {time.monotonic()-start:.2f}s"
            records[ruc] = record
            ordered = [records[x] for x in rucs if x in records]
            tmp = checkpoint.with_suffix(".tmp")
            tmp.write_text(json.dumps(ordered, ensure_ascii=False, indent=2))
            tmp.replace(checkpoint)
            write_results(args.output, ordered)
            print(ruc, record["Estado de consulta"], flush=True)
            if not blocked:
                time.sleep(3)
        browser.close()
    summary = {"fecha":now(), "total":len(rucs), "completos":sum(r.get("Estado de consulta")=="VERIFICADO" for r in records.values()),
               "bloqueados":sum(r.get("Estado de consulta")=="BLOQUEADO POR RESTRICCIÓN EXTERNA" for r in records.values()), "registros":list(records.values())}
    Path("evidencias/sunat_resumen.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print("Consultas completas:",summary["completos"],"de",len(rucs))
    if summary["completos"] != len(rucs):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
