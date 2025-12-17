"""
credit: https://pypi.org/project/xdat/
credit: https://stackoverflow.com/questions/33470130/read-excel-xml-xls-file-with-pandas
"""

import io
import pandas as pd
from xml.sax import parse
from xml.sax.handler import ContentHandler


# Reference https://goo.gl/KaOBG3
class ExcelHandler(ContentHandler):
    def __init__(self):
        super().__init__()
        self.chars = []
        self.cells = []
        self.rows = []
        self.tables = []

    def characters(self, content):
        self.chars.append(content)

    def startElement(self, name, atts):
        if name == "Cell":
            self.chars = []
        elif name == "Row":
            self.cells = []
        elif name == "Table":
            self.rows = []

    def endElement(self, name):
        if name == "Cell":
            cell = ''.join(self.chars)
            cell = cell.strip()
            self.cells.append(cell)
        elif name == "Row":
            if self.cells:
                self.rows.append(self.cells)
        elif name == "Table":
            if self.rows:
                self.tables.append(self.rows)


def read_excel_xml_raw(xls_path):
    if isinstance(xls_path, io.BytesIO):
        xls_path_orig = xls_path
        xls_path = io.BytesIO(xls_path_orig.read())
        xls_path_orig.seek(0)
        xls_path.seek(0)

    h = ExcelHandler()
    if not isinstance(xls_path, str):
        xls_path.seek(0)

    parse(xls_path, h)
    return h


def read_excel_xml(xls_path, table=0, header_row=None, data_start=None):
    h = read_excel_xml_raw(xls_path)
    t = h.tables[table]
    header = None
    if header_row is not None:
        header = t[header_row]
        if data_start is None or data_start <= header_row:
            data_start = header_row + 1

    rows = t[:]
    if data_start is not None:
        rows = rows[data_start:]

    if header:
        max_cols = max([len(r) for r in rows])
        header = header[:max_cols]
        df = pd.DataFrame(data=rows, columns=header)

    else:
        df = pd.DataFrame(data=rows)

    return df

