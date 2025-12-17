"""
credit: https://pypi.org/project/xdat/
"""
import sys

try:
    import inspect
    import pandas as pd
    import openpyxl
    import excelrd
    import xlrd2
    import xlrd
    import pyexcel
    import pyexcel_xls
    import pyexcel_xlsx
    import pyxlsb
    import pylightxl
    # import odfpy
    # import excel
    import lxml
except ImportError as e:
    print(f"Hi Excel reader explore: {e}")

import excel_xml_reader


def get_short_lambda_source(lambda_func):
    try:
        source_lines, _ = inspect.getsourcelines(lambda_func)
    except IOError:
        return None
    if len(source_lines) > 1:
        return None
    return source_lines[0].strip().split(':', maxsplit=2)[-1].strip()


def try_to_open(excel_path):
    excel_path = str(excel_path)
    print(f"{excel_path} --")
    tries = [
        # lambda: excel.OpenExcel(excel_path),
        lambda: pylightxl.readxl(excel_path),
        lambda: pyexcel.get_book(excel_path),
        lambda: pyexcel_xls.get_data(excel_path),
        lambda: pyexcel_xlsx.get_data(excel_path),
        lambda: openpyxl.load_workbook(excel_path),
        lambda: excelrd.open_workbook(excel_path),
        lambda: xlrd2.open_workbook(excel_path),
        lambda: xlrd.open_workbook(excel_path),
        lambda: pyxlsb.open_workbook(excel_path),
        lambda: excel_xml_reader.read_excel_xml(excel_path),
        lambda: pd.read_csv(excel_path),
        lambda: pd.read_html(excel_path),
        lambda: pd.read_xml(excel_path),
        lambda: pd.read_excel(excel_path),
        lambda: pd.read_excel(excel_path, engine='xlrd'),
        lambda: pd.read_excel(excel_path, engine='openpyxl'),
        lambda: pd.read_excel(excel_path, engine='odf'),
        lambda: pd.read_excel(excel_path, engine='pyxlsb'),
    ]

    for func in tries:
        func_text = get_short_lambda_source(func)
        try:
            res = func()
        except Exception as e:
            print(f"ERR {func_text}: {repr(e)[:120]}")
        else:
            print(f"OK  {func_text}")
            try:
                print(f"    type={type(res)}")
                print(f"    len={len(res)}")
            except:
                pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: try_excel_open.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    try_to_open(file_path)