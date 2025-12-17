"""
Excel Toolbox - 一体化 Excel 数据处理工具集
"""

__version__ = "1.0.0"
__author__ = "Chandler"

from excel_toolbox.merger import merge_excel_files, join_tables
from excel_toolbox.cleaner import remove_duplicates, sort_by_template
from excel_toolbox.converter import csv_to_excel, json_to_excel, excel_to_json

__all__ = [
    "merge_excel_files",
    "join_tables",
    "remove_duplicates",
    "sort_by_template",
    "csv_to_excel",
    "json_to_excel",
    "excel_to_json",
]
