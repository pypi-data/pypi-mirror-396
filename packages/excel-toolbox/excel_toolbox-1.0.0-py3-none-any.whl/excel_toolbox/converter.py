"""
格式转换模块 - 提供 CSV/JSON/Excel 格式互转功能
"""

import os
import json
import warnings
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from rich.console import Console

console = Console()


def csv_to_excel(
    csv_path: str,
    output_path: Optional[str] = None,
    encoding: str = "utf-8",
    delimiter: str = ",",
    include_index: bool = False
) -> pd.DataFrame:
    """
    CSV 转 Excel
    
    Args:
        csv_path: CSV 文件路径
        output_path: 输出文件路径（默认生成同目录 .xlsx 文件）
        encoding: 文件编码（支持 "utf-8", "gbk", "utf-16" 等）
        delimiter: CSV 分隔符
        include_index: 输出是否含 DataFrame 索引
        
    Returns:
        pd.DataFrame: 转换后的数据框
        
    Raises:
        FileNotFoundError: 文件不存在
        UnicodeDecodeError: 编码错误
        pd.errors.ParserError: 无效 CSV
        
    Examples:
        >>> df = csv_to_excel("data.csv")
        >>> df = csv_to_excel("data.csv", "output.xlsx", encoding="gbk")
    """
    # 文件存在性检查
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV 文件不存在: {csv_path}")
    
    console.print(f"[cyan]读取 CSV:[/cyan] {os.path.basename(csv_path)}")
    console.print(f"  • 编码: {encoding}")
    console.print(f"  • 分隔符: '{delimiter}'")
    
    try:
        # 读取 CSV
        df = pd.read_csv(
            csv_path,
            encoding=encoding,
            delimiter=delimiter,
            # 尝试自动推断数据类型
            low_memory=False
        )
        
        console.print(f"  → {len(df)} 行 × {len(df.columns)} 列")
        
        # 检查超长文本（Excel 32767 字符限制）
        for col in df.select_dtypes(include=['object']).columns:
            max_len = df[col].astype(str).str.len().max()
            if max_len > 32767:
                warnings.warn(
                    f"列 '{col}' 包含超长文本（{max_len} 字符），"
                    f"Excel 可能截断超过 32767 字符的内容"
                )
        
        # 确定输出路径
        if output_path is None:
            output_path = str(Path(csv_path).with_suffix('.xlsx'))
        
        # 保存为 Excel
        df.to_excel(output_path, index=include_index, engine='openpyxl')
        console.print(f"[green]✓[/green] 已保存到: {output_path}")
        
        return df
        
    except UnicodeDecodeError as e:
        console.print(f"[red]✗[/red] 编码错误，建议尝试: 'gbk', 'latin1', 'utf-16'")
        raise
    except pd.errors.ParserError as e:
        console.print(f"[red]✗[/red] CSV 解析失败: {str(e)}")
        raise


def json_to_excel(
    json_path: str,
    output_path: Optional[str] = None,
    json_pointer: Optional[str] = None,
    include_index: bool = False
) -> pd.DataFrame:
    """
    JSON 转 Excel
    
    Args:
        json_path: JSON 文件路径
        output_path: 输出文件路径（默认生成同目录 .xlsx 文件）
        json_pointer: JSON 路径（e.g. "data.items"），用点分隔
        include_index: 输出是否含 DataFrame 索引
        
    Returns:
        pd.DataFrame: 转换后的数据框
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: 无效 JSON
        KeyError: 路径不存在
        ValueError: 非数组终端节点
        
    Examples:
        >>> df = json_to_excel("data.json")
        >>> df = json_to_excel("api.json", json_pointer="data.items")
    """
    # 文件存在性检查
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON 文件不存在: {json_path}")
    
    console.print(f"[cyan]读取 JSON:[/cyan] {os.path.basename(json_path)}")
    
    try:
        # 读取 JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理 JSON 路径
        if json_pointer:
            console.print(f"  • JSON 路径: {json_pointer}")
            path_parts = json_pointer.split('.')
            
            current = data
            for part in path_parts:
                if isinstance(current, dict):
                    if part not in current:
                        raise KeyError(f"路径 '{json_pointer}' 无效：键 '{part}' 不存在")
                    current = current[part]
                elif isinstance(current, list):
                    try:
                        index = int(part)
                        current = current[index]
                    except (ValueError, IndexError):
                        raise KeyError(f"路径 '{json_pointer}' 无效：无法访问索引 '{part}'")
                else:
                    raise KeyError(f"路径 '{json_pointer}' 无效：'{part}' 无法继续访问")
            
            data = current
        
        # 检查数据类型
        if isinstance(data, list):
            df = pd.json_normalize(data)
        elif isinstance(data, dict):
            # 尝试扁平化字典
            df = pd.json_normalize(data)
            if len(df) == 0:
                raise ValueError("JSON 对象无法转换为表格，请使用 json_pointer 指向数组")
        else:
            raise ValueError("目标必须是 JSON 数组或对象")
        
        console.print(f"  → {len(df)} 行 × {len(df.columns)} 列")
        
        # 确定输出路径
        if output_path is None:
            output_path = str(Path(json_path).with_suffix('.xlsx'))
        
        # 保存为 Excel
        df.to_excel(output_path, index=include_index, engine='openpyxl')
        console.print(f"[green]✓[/green] 已保存到: {output_path}")
        
        return df
        
    except json.JSONDecodeError as e:
        console.print(f"[red]✗[/red] JSON 解析失败: {str(e)}")
        raise


def excel_to_json(
    excel_path: str,
    output_path: Optional[str] = None,
    sheet_name: Union[str, int] = 0,
    indent: Optional[int] = 2,
    date_format: str = "iso"
) -> str:
    """
    Excel 转 JSON
    
    Args:
        excel_path: Excel 文件路径
        output_path: 输出文件路径（默认生成同目录 .json 文件）
        sheet_name: 工作表名称或索引
        indent: 缩进空格数（None=紧凑格式，2=美化格式）
        date_format: 日期格式化规则 ("iso", "epoch")
        
    Returns:
        str: JSON 字符串
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 无效工作表
        TypeError: 不可序列化对象
        
    Examples:
        >>> json_str = excel_to_json("data.xlsx")
        >>> json_str = excel_to_json("data.xlsx", sheet_name="Sheet2", indent=None)
    """
    # 文件存在性检查
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel 文件不存在: {excel_path}")
    
    console.print(f"[cyan]读取 Excel:[/cyan] {os.path.basename(excel_path)}")
    
    try:
        # 读取 Excel
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        if isinstance(sheet_name, int):
            console.print(f"  • 工作表: Sheet{sheet_name + 1}")
        else:
            console.print(f"  • 工作表: {sheet_name}")
        
        console.print(f"  → {len(df)} 行 × {len(df.columns)} 列")
        
        # 处理日期格式
        if date_format == "iso":
            # 转换日期为 ISO 8601 字符串
            for col in df.select_dtypes(include=['datetime64']).columns:
                df[col] = df[col].dt.strftime('%Y-%m-%dT%H:%M:%S')
        
        # 转换为 JSON（orient='records' 生成数组格式）
        json_str = df.to_json(
            orient='records',
            date_format=date_format,
            indent=indent,
            force_ascii=False,  # 保留中文等非 ASCII 字符
            double_precision=10  # 数字精度
        )
        
        # 确定输出路径
        if output_path is None:
            output_path = str(Path(excel_path).with_suffix('.json'))
        
        # 保存 JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_str)
        
        console.print(f"[green]✓[/green] 已保存到: {output_path}")
        
        return json_str
        
    except ValueError as e:
        if "Worksheet" in str(e):
            console.print(f"[red]✗[/red] 工作表 '{sheet_name}' 不存在")
        raise
    except TypeError as e:
        console.print(f"[red]✗[/red] 数据包含不可序列化对象: {str(e)}")
        raise
