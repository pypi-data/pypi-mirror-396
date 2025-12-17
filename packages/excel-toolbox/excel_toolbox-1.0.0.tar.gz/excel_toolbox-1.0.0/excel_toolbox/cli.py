"""
CLI 命令行接口 - 使用 Typer 实现
"""

from typing import Optional, List
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from excel_toolbox import __version__
from excel_toolbox.merger import merge_excel_files, join_tables
from excel_toolbox.cleaner import remove_duplicates, sort_by_template
from excel_toolbox.converter import csv_to_excel, json_to_excel, excel_to_json

app = typer.Typer(
    name="excel-toolbox",
    help="🚀 一体化 Excel 数据处理工具集 - 数据整合、清洗、转换全流程解决方案",
    add_completion=False,
)

console = Console()


def version_callback(value: bool):
    """显示版本信息"""
    if value:
        rprint(f"[bold cyan]Excel Toolbox[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="显示版本信息",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    Excel Toolbox - 一体化数据处理工具集
    
    支持数据合并、清洗、转换等全流程操作
    """
    pass


# ===== 合并模块 =====

@app.command("merge")
def merge_cmd(
    folder: str = typer.Argument(..., help="包含 Excel 文件的文件夹路径"),
    output: str = typer.Argument(..., help="输出文件路径"),
    all_sheets: bool = typer.Option(False, "--all-sheets", "-a", help="合并所有工作表（默认仅首表）"),
):
    """
    合并文件夹内所有 Excel 文件
    
    示例:
        excel-toolbox merge ./data merged.xlsx
        excel-toolbox merge ./data merged.xlsx --all-sheets
    """
    try:
        console.print(Panel.fit(
            "[bold cyan]合并 Excel 文件[/bold cyan]",
            border_style="cyan"
        ))
        
        merge_excel_files(folder, output, all_sheets)
        
    except Exception as e:
        console.print(f"[bold red]错误:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command("join")
def join_cmd(
    left: str = typer.Argument(..., help="左表文件路径"),
    right: str = typer.Argument(..., help="右表文件路径"),
    output: str = typer.Argument(..., help="输出文件路径"),
    left_on: str = typer.Option(..., "--left-on", "-l", help="左表关联键"),
    right_on: str = typer.Option(..., "--right-on", "-r", help="右表关联键"),
    how: str = typer.Option("inner", "--how", "-h", help="连接类型: inner/left/right/outer"),
):
    """
    两表关联合并（SQL JOIN）
    
    示例:
        excel-toolbox join left.xlsx right.xlsx output.xlsx --left-on id --right-on user_id
        excel-toolbox join a.xlsx b.xlsx result.xlsx -l id -r id --how left
    """
    try:
        console.print(Panel.fit(
            "[bold cyan]表格关联合并[/bold cyan]",
            border_style="cyan"
        ))
        
        if how not in ["inner", "left", "right", "outer"]:
            console.print(f"[bold red]错误:[/bold red] 无效的连接类型: {how}")
            raise typer.Exit(code=1)
        
        join_tables(left, right, left_on, right_on, how, output_path=output)
        
    except Exception as e:
        console.print(f"[bold red]错误:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


# ===== 清洗模块 =====

@app.command("dedup")
def dedup_cmd(
    input_file: str = typer.Argument(..., help="输入文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    subset: Optional[str] = typer.Option(None, "--subset", "-s", help="去重依据列（逗号分隔，默认全行）"),
    keep: str = typer.Option("first", "--keep", "-k", help="保留策略: first/last/false"),
    inplace: bool = typer.Option(False, "--inplace", "-i", help="覆盖原文件"),
):
    """
    去除重复数据
    
    示例:
        excel-toolbox dedup data.xlsx --output cleaned.xlsx
        excel-toolbox dedup data.xlsx --subset ID,Name --keep last -o result.xlsx
        excel-toolbox dedup data.xlsx --inplace
    """
    try:
        console.print(Panel.fit(
            "[bold cyan]去除重复数据[/bold cyan]",
            border_style="cyan"
        ))
        
        # 处理 subset
        subset_list = None
        if subset:
            subset_list = [s.strip() for s in subset.split(',')]
        
        # 处理 keep
        keep_value = keep if keep != "false" else False
        
        remove_duplicates(input_file, subset_list, keep_value, inplace, output)
        
    except Exception as e:
        console.print(f"[bold red]错误:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command("sort")
def sort_cmd(
    main_file: str = typer.Argument(..., help="主数据文件路径"),
    template: str = typer.Argument(..., help="模板文件路径"),
    output: str = typer.Argument(..., help="输出文件路径"),
    main_col: str = typer.Option(..., "--main-col", "-m", help="主数据匹配列"),
    template_col: str = typer.Option(..., "--template-col", "-t", help="模板匹配列"),
    unmatched: str = typer.Option("top", "--unmatched", "-u", help="未匹配项位置: top/bottom"),
):
    """
    按模板文件自定义排序
    
    示例:
        excel-toolbox sort data.xlsx template.xlsx sorted.xlsx --main-col id --template-col id
        excel-toolbox sort data.xlsx order.xlsx result.xlsx -m name -t name --unmatched bottom
    """
    try:
        console.print(Panel.fit(
            "[bold cyan]自定义排序[/bold cyan]",
            border_style="cyan"
        ))
        
        if unmatched not in ["top", "bottom"]:
            console.print(f"[bold red]错误:[/bold red] 无效的未匹配项位置: {unmatched}")
            raise typer.Exit(code=1)
        
        sort_by_template(main_file, template, main_col, template_col, unmatched, output)
        
    except Exception as e:
        console.print(f"[bold red]错误:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


# ===== 转换模块 =====

@app.command("csv2excel")
def csv2excel_cmd(
    csv_file: str = typer.Argument(..., help="CSV 文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径（默认同目录 .xlsx）"),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="文件编码"),
    delimiter: str = typer.Option(",", "--delimiter", "-d", help="CSV 分隔符"),
    index: bool = typer.Option(False, "--index", help="包含索引列"),
):
    """
    CSV 转 Excel
    
    示例:
        excel-toolbox csv2excel data.csv
        excel-toolbox csv2excel data.csv --output result.xlsx --encoding gbk
    """
    try:
        console.print(Panel.fit(
            "[bold cyan]CSV → Excel[/bold cyan]",
            border_style="cyan"
        ))
        
        csv_to_excel(csv_file, output, encoding, delimiter, index)
        
    except Exception as e:
        console.print(f"[bold red]错误:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command("json2excel")
def json2excel_cmd(
    json_file: str = typer.Argument(..., help="JSON 文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径（默认同目录 .xlsx）"),
    pointer: Optional[str] = typer.Option(None, "--pointer", "-p", help="JSON 路径（如 data.items）"),
    index: bool = typer.Option(False, "--index", help="包含索引列"),
):
    """
    JSON 转 Excel
    
    示例:
        excel-toolbox json2excel data.json
        excel-toolbox json2excel api.json --output result.xlsx --pointer data.items
    """
    try:
        console.print(Panel.fit(
            "[bold cyan]JSON → Excel[/bold cyan]",
            border_style="cyan"
        ))
        
        json_to_excel(json_file, output, pointer, index)
        
    except Exception as e:
        console.print(f"[bold red]错误:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command("excel2json")
def excel2json_cmd(
    excel_file: str = typer.Argument(..., help="Excel 文件路径"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径（默认同目录 .json）"),
    sheet: str = typer.Option("0", "--sheet", "-s", help="工作表名称或索引"),
    indent: Optional[int] = typer.Option(2, "--indent", help="缩进空格数（None=紧凑）"),
):
    """
    Excel 转 JSON
    
    示例:
        excel-toolbox excel2json data.xlsx
        excel-toolbox excel2json data.xlsx --output result.json --sheet Sheet2
    """
    try:
        console.print(Panel.fit(
            "[bold cyan]Excel → JSON[/bold cyan]",
            border_style="cyan"
        ))
        
        # 尝试将 sheet 转换为整数
        try:
            sheet_value = int(sheet)
        except ValueError:
            sheet_value = sheet
        
        excel_to_json(excel_file, output, sheet_value, indent)
        
    except Exception as e:
        console.print(f"[bold red]错误:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
