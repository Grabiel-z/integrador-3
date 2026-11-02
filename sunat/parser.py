import re
import unicodedata
from bs4 import BeautifulSoup


def normalize(value):
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def key(value):
    return "".join(c for c in unicodedata.normalize("NFD", normalize(value).lower()) if unicodedata.category(c) != "Mn").rstrip(":")


def extract(html, expected_ruc):
    soup = BeautifulSoup(html, "html.parser")
    values = {}
    for heading in soup.find_all(["h4", "h3", "label", "th"]):
        label = key(heading.get_text(" ", strip=True))
        if label not in {"numero de ruc", "razon social", "direccion del domicilio fiscal", "domicilio fiscal",
                         "condicion del contribuyente", "condicion del domicilio fiscal", "fecha de inicio de actividades"}:
            continue
        parent = heading.parent
        sibling = parent.find_next_sibling()
        if sibling:
            values[label] = normalize(sibling.get_text(" ", strip=True))
    ruc_name = values.get("numero de ruc", "")
    match = re.match(r"(\d{11})\s*-\s*(.+)", ruc_name)
    if match and match[1] != expected_ruc:
        raise ValueError("La respuesta corresponde a un RUC distinto")
    name = match[2] if match else values.get("razon social", "")
    result = {"RUC": expected_ruc, "Razón social": name,
        "Dirección fiscal": values.get("direccion del domicilio fiscal", values.get("domicilio fiscal", "")),
        "Condición del domicilio fiscal": values.get("condicion del contribuyente", values.get("condicion del domicilio fiscal", "")),
        "Fecha de inicio de actividades": values.get("fecha de inicio de actividades", "")}
    if not name:
        raise ValueError("No se encontró razón social en la ficha oficial")
    missing = [k for k,v in result.items() if not v]
    result["Estado de consulta"] = "VERIFICADO" if not missing else "ERROR IDENTIFICADO"
    result["Observaciones"] = "Consulta individual oficial SUNAT" if not missing else "Respuesta incompleta; faltan: " + ", ".join(missing)
    return result
