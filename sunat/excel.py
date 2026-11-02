import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo

HEADERS = ["RUC", "Razón social", "Dirección fiscal", "Condición del domicilio fiscal",
           "Fecha de inicio de actividades", "Estado de consulta", "Fecha de consulta", "Observaciones"]


def valid_ruc(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{11}", value):
        return False
    total = sum(int(n)*w for n, w in zip(value[:10], [5,4,3,2,7,6,5,4,3,2]))
    return int(value[-1]) == (11-total % 11) % 10


def read_input(path):
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb.active
        if ws.cell(1, 1).value != "RUC":
            raise ValueError("La primera columna debe tener encabezado RUC")
        rows = list(ws.iter_rows(min_row=2, values_only=True))
        seen, result = set(), []
        for index, row in enumerate(rows, 2):
            value = row[0]
            if not valid_ruc(value):
                raise ValueError(f"Fila {index}: RUC vacío, numérico o con dígito verificador incorrecto")
            if value in seen:
                raise ValueError(f"Fila {index}: RUC duplicado {value}")
            seen.add(value)
            result.append(value)
        if not result:
            raise ValueError("Excel sin RUC")
        return result
    finally:
        wb.close()


def style_sheet(ws, widths):
    ws.freeze_panes = "B2"
    ws.sheet_view.showGridLines = False
    ws.row_dimensions[1].height = 36
    for cell in ws[1]:
        cell.font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
        cell.fill = PatternFill("solid", fgColor="183D4B")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    for row in ws.iter_rows(min_row=2):
        ws.row_dimensions[row[0].row].height = 48
        for cell in row:
            cell.font = Font(name="Calibri", size=11)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.fill = PatternFill("solid", fgColor="EDF4F5" if cell.row % 2 == 0 else "FFFFFF")
        row[0].number_format = "@"
    if ws.max_row > 1:
        table = Table(displayName="Datos" + ws.title.replace(" ", ""), ref=ws.dimensions)
        table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws.add_table(table)
    ws.print_title_rows = "1:1"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A3
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0


def safe(value):
    # Evita fórmulas inyectadas por contenidos de páginas externas.
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def write_results(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados"
    ws.append(HEADERS)
    for record in records:
        ws.append([safe(record.get(h, "")) for h in HEADERS])
    style_sheet(ws, dict(zip("ABCDEFGH", [18, 48, 65, 25, 24, 32, 28, 70])))
    tmp = path.with_suffix(".tmp.xlsx")
    wb.save(tmp)
    tmp.replace(path)


def now():
    return datetime.now(ZoneInfo("America/Lima")).isoformat(timespec="seconds")
