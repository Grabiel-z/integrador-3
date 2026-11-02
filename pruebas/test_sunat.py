from pathlib import Path
import pytest
from openpyxl import Workbook, load_workbook
from sunat.excel import valid_ruc, read_input, write_results
from sunat.parser import extract, normalize


@pytest.mark.parametrize("value,expected",[("20100047218",True),("20100130204",True),("20100047219",False),
    ("",False),(None,False),(20100047218,False),("2010004721",False),("2010004721x",False)])
def test_ruc(value,expected):
    assert valid_ruc(value) is expected


def test_extract_does_not_confuse_dates_or_status():
    data=extract(Path("pruebas/fixtures/ficha_sintetica.html").read_text(),"20100047218")
    assert data["Condición del domicilio fiscal"]=="HABIDO"
    assert data["Fecha de inicio de actividades"]=="02/02/1991"
    assert data["Dirección fiscal"]=="AV. PRUEBA 100"


def test_different_ruc_rejected():
    with pytest.raises(ValueError,match="distinto"):
        extract(Path("pruebas/fixtures/ficha_sintetica.html").read_text(),"20100130204")


def test_incomplete_rejected():
    with pytest.raises(ValueError):
        extract("<html>Access denied</html>","20100047218")


@pytest.mark.parametrize("rows",[["20100047218","20100047218"],[None],[20100047218],[]])
def test_invalid_excel(tmp_path,rows):
    w=Workbook();w.active.append(["RUC"])
    for r in rows: w.active.append([r])
    p=tmp_path/"entrada.xlsx";w.save(p)
    with pytest.raises(ValueError): read_input(p)


def test_excel_roundtrip_and_formula_protection(tmp_path):
    w=Workbook();w.active.append(["RUC"]);w.active.append(["20100047218"])
    p=tmp_path/"in.xlsx";w.save(p)
    assert read_input(p)==["20100047218"]
    out=tmp_path/"out.xlsx"
    write_results(out,[{"RUC":"20100047218","Razón social":"=DANGEROUS()"}])
    ws=load_workbook(out).active
    assert ws["A2"].data_type=="s"
    assert ws["B2"].value.startswith("'")
    assert ws.freeze_panes=="B2"


def test_normalize():
    assert normalize(" A\n B\xa0 C ")=="A B C"
