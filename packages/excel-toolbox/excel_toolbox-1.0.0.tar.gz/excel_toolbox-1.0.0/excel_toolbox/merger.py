"""
数据合并模块 - 提供 Excel 文件合并和表格关联功能
"""

import os
import warnings
from pathlib import Path
from typing import Optional, Union, List, Tuple, Literal

import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def merge_excel_files(
    folder_path: str,
    output_path: Optional[str] = None,
    include_all_sheets: bool = False
) -> pd.DataFrame:
    """
    合并文件夹内所有 Excel 文件
    
    Args:
        folder_path: 必须存在的文件夹路径
        output_path: 输出文件路径（None 时返回 DataFrame）
        include_all_sheets: False 仅合并首表，True 合并所有工作表
        
    Returns:
        pd.DataFrame: 合并后的数据框
        
    Raises:
        ValueError: 无效文件夹路径
        RuntimeError: 0 个有效 Excel 文件
        
    Examples:
        >>> df = merge_excel_files("/path/to/folder")
        >>> df = merge_excel_files("/path/to/folder", "merged.xlsx", True)
    """
    # 参数校验
    if not os.path.exists(folder_path):
        raise ValueError(f"文件夹路径不存在: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise ValueError(f"路径不是文件夹: {folder_path}")
    
    # 查找所有 Excel 文件
    excel_extensions = {'.xlsx', '.xls', '.xlsm', '.xlsb'}
    excel_files = [
        f for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in excel_extensions
    ]
    
    if not excel_files:
        raise RuntimeError(f"文件夹中未找到 Excel 文件: {folder_path}")
    
    console.print(f"[green]✓[/green] 找到 {len(excel_files)} 个 Excel 文件")
    
    # 合并数据
    all_dataframes = []
    failed_files = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"正在处理文件...", total=len(excel_files))
        
        for filename in excel_files:
            file_path = os.path.join(folder_path, filename)
            progress.update(task, description=f"处理: {filename}")
            
            try:
                # 读取 Excel 文件
                if include_all_sheets:
                    excel_file = pd.ExcelFile(file_path)
                    sheet_names = excel_file.sheet_names
                else:
                    sheet_names = [0]  # 只读取第一个工作表
                
                for sheet in sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet)
                        
                        if df.empty:
                            warnings.warn(f"工作表为空: {filename} - {sheet}")
                            continue
                        
                        # 添加元数据列
                        df['source_file'] = filename
                        df['source_sheet'] = sheet if isinstance(sheet, str) else f"Sheet{sheet + 1}"
                        
                        all_dataframes.append(df)
                        
                    except Exception as e:
                        warnings.warn(f"读取工作表失败: {filename} - {sheet}: {str(e)}")
                        continue
                        
            except Exception as e:
                failed_files.append(filename)
                warnings.warn(f"文件解析失败: {filename}: {str(e)}")
                continue
            
            progress.advance(task)
    
    # 检查是否有有效数据
    if not all_dataframes:
        raise RuntimeError("没有成功读取任何有效数据")
    
    # 合并所有数据框
    console.print(f"[green]✓[/green] 成功读取 {len(all_dataframes)} 个工作表")
    if failed_files:
        console.print(f"[yellow]⚠[/yellow] {len(failed_files)} 个文件处理失败: {', '.join(failed_files)}")
    
    result_df = pd.concat(all_dataframes, ignore_index=True)
    console.print(f"[green]✓[/green] 合并完成，总计 {len(result_df)} 行数据")
    
    # 保存结果
    if output_path:
        result_df.to_excel(output_path, index=False, engine='openpyxl')
        console.print(f"[green]✓[/green] 已保存到: {output_path}")
    
    return result_df


def join_tables(
    left_file: str,
    right_file: str,
    left_on: Union[str, List[str]],
    right_on: Union[str, List[str]],
    how: Literal["inner", "left", "right", "outer"] = "inner",
    suffixes: Tuple[str, str] = ("_left", "_right"),
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    两表关联合并（SQL JOIN 模拟）
    
    Args:
        left_file: 左表文件路径
        right_file: 右表文件路径
        left_on: 左表关联键（列名或列名列表）
        right_on: 右表关联键（列名或列名列表）
        how: 连接类型 ("inner", "left", "right", "outer")
        suffixes: 重名列后缀（默认 "_left", "_right"）
        output_path: 输出文件路径（None 时仅返回 DataFrame）
        
    Returns:
        pd.DataFrame: 关联后的数据框
        
    Raises:
        FileNotFoundError: 文件不存在
        KeyError: 关联键缺失
        
    Examples:
        >>> df = join_tables("left.xlsx", "right.xlsx", "id", "id")
        >>> df = join_tables("a.xlsx", "b.xlsx", ["key1", "key2"], ["k1", "k2"], how="left")
    """
    # 文件存在性检查
    if not os.path.exists(left_file):
        raise FileNotFoundError(f"左表文件不存在: {left_file}")
    if not os.path.exists(right_file):
        raise FileNotFoundError(f"右表文件不存在: {right_file}")
    
    # 读取文件
    console.print(f"[cyan]读取左表:[/cyan] {os.path.basename(left_file)}")
    left_df = pd.read_excel(left_file)
    console.print(f"  → {len(left_df)} 行 × {len(left_df.columns)} 列")
    
    console.print(f"[cyan]读取右表:[/cyan] {os.path.basename(right_file)}")
    right_df = pd.read_excel(right_file)
    console.print(f"  → {len(right_df)} 行 × {len(right_df.columns)} 列")
    
    # 转换关联键为列表
    left_keys = [left_on] if isinstance(left_on, str) else left_on
    right_keys = [right_on] if isinstance(right_on, str) else right_on
    
    # 检查关联键是否存在
    missing_left = set(left_keys) - set(left_df.columns)
    if missing_left:
        raise KeyError(f"左表缺少关联键: {missing_left}")
    
    missing_right = set(right_keys) - set(right_df.columns)
    if missing_right:
        raise KeyError(f"右表缺少关联键: {missing_right}")
    
    # 执行关联
    console.print(f"[cyan]关联模式:[/cyan] {how.upper()} JOIN")
    console.print(f"[cyan]关联键:[/cyan] {left_keys} ← → {right_keys}")
    
    result_df = pd.merge(
        left_df,
        right_df,
        left_on=left_keys,
        right_on=right_keys,
        how=how,
        suffixes=suffixes,
        indicator=True if how == "outer" else False
    )
    
    console.print(f"[green]✓[/green] 关联完成: {len(result_df)} 行 × {len(result_df.columns)} 列")
    
    # 输出统计信息
    if how == "outer" and "_merge" in result_df.columns:
        merge_stats = result_df["_merge"].value_counts()
        console.print("[cyan]关联统计:[/cyan]")
        if "both" in merge_stats.index:
            console.print(f"  • 两表都匹配: {merge_stats['both']} 行")
        if "left_only" in merge_stats.index:
            console.print(f"  • 仅左表: {merge_stats['left_only']} 行")
        if "right_only" in merge_stats.index:
            console.print(f"  • 仅右表: {merge_stats['right_only']} 行")
    
    # 保存结果
    if output_path:
        result_df.to_excel(output_path, index=False, engine='openpyxl')
        console.print(f"[green]✓[/green] 已保存到: {output_path}")
    
    return result_df
