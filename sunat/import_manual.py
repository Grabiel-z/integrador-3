"""Importación explícita de HTML oficial guardado por una persona."""
import json
from pathlib import Path
from sunat.excel import read_input, write_results, now
from sunat.parser import extract


def main():
    rucs=read_input("datos/RUC_entrada.xlsx")
    checkpoint=Path("datos/sunat_checkpoint.json")
    records={r["RUC"]:r for r in json.loads(checkpoint.read_text())} if checkpoint.exists() else {}
    imported=0
    for ruc in rucs:
        path=Path(f"datos/manual/{ruc}.html")
        if not path.exists():continue
        # No se presume fecha de consulta: se pide un registro explícito del responsable.
        meta=path.with_suffix(".json")
        if not meta.exists():
            print(f"Falta {meta}: incluir fecha_consulta ISO y responsable real")
            continue
        metadata=json.loads(meta.read_text())
        if not metadata.get("fecha_consulta") or not metadata.get("responsable"):
            raise ValueError(f"Metadatos incompletos: {meta}")
        result=extract(path.read_text(encoding="utf-8"),ruc)
        result["Fecha de consulta"]=metadata["fecha_consulta"]
        result["Observaciones"]+='; consulta manual; HTML importado en Docker; responsable: '+metadata["responsable"]
        records[ruc]=result;imported+=1
    ordered=[records.get(ruc,{"RUC":ruc,"Estado de consulta":"PENDIENTE DE OTRA INTERVENCIÓN","Observaciones":"Falta ficha oficial"}) for ruc in rucs]
    checkpoint.write_text(json.dumps(ordered,ensure_ascii=False,indent=2))
    write_results("datos/RUC_resultados.xlsx",ordered)
    Path("evidencias/sunat_resumen.json").write_text(json.dumps({"fecha":now(),"total":len(rucs),
        "completos":sum(r["Estado de consulta"]=="VERIFICADO" for r in ordered),"manuales_importados":imported,"registros":ordered},ensure_ascii=False,indent=2))
    print("Fichas manuales importadas:",imported)


if __name__=="__main__":main()
