"""
数据清洗模块 - 提供去重和自定义排序功能
"""

import os
from typing import Optional, Union, List, Literal, Dict

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()


def remove_duplicates(
    input_file: str,
    subset: Optional[Union[str, List[str]]] = None,
    keep: Literal["first", "last", False] = "first",
    inplace: bool = False,
    output_path: Optional[str] = None
) -> Dict[str, int]:
    """
    去除重复数据
    
    Args:
        input_file: 输入文件路径
        subset: 用于判断重复的列（None 时全行去重）
        keep: 保留策略 ("first": 保留第一次出现, "last": 保留最后一次, False: 删除所有重复)
        inplace: True 时覆盖原文件
        output_path: 输出文件路径（inplace=True 时必须为 None）
        
    Returns:
        dict: 包含 original_count, dedup_count, dropped_count 的统计信息
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 参数冲突
        KeyError: 无效列名
        
    Examples:
        >>> stats = remove_duplicates("data.xlsx", subset="ID")
        >>> stats = remove_duplicates("data.xlsx", keep="last", output_path="cleaned.xlsx")
    """
    # 参数校验
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"文件不存在: {input_file}")
    
    if inplace and output_path is not None:
        raise ValueError("inplace=True 时 output_path 必须为 None")
    
    if not inplace and output_path is None:
        raise ValueError("inplace=False 时必须指定 output_path")
    
    # 读取文件
    console.print(f"[cyan]读取文件:[/cyan] {os.path.basename(input_file)}")
    df = pd.read_excel(input_file)
    original_count = len(df)
    console.print(f"  → 原始数据: {original_count} 行")
    
    # 转换 subset 为列表
    if subset is not None:
        subset_cols = [subset] if isinstance(subset, str) else subset
        
        # 检查列是否存在
        missing_cols = set(subset_cols) - set(df.columns)
        if missing_cols:
            raise KeyError(f"列不存在: {missing_cols}")
        
        console.print(f"[cyan]去重依据:[/cyan] {subset_cols}")
    else:
        subset_cols = None
        console.print(f"[cyan]去重依据:[/cyan] 全行去重")
    
    # 执行去重
    keep_str = "保留第一次出现" if keep == "first" else "保留最后一次出现" if keep == "last" else "删除所有重复"
    console.print(f"[cyan]保留策略:[/cyan] {keep_str}")
    
    df_dedup = df.drop_duplicates(subset=subset_cols, keep=keep)
    dedup_count = len(df_dedup)
    dropped_count = original_count - dedup_count
    
    # 输出统计表格
    table = Table(title="去重统计", show_header=True, header_style="bold magenta")
    table.add_column("指标", style="cyan", width=20)
    table.add_column("数值", justify="right", style="green")
    
    table.add_row("原始行数", str(original_count))
    table.add_row("去重后行数", str(dedup_count))
    table.add_row("删除行数", str(dropped_count))
    table.add_row("保留比例", f"{dedup_count/original_count*100:.2f}%")
    
    console.print(table)
    
    # 保存结果
    save_path = input_file if inplace else output_path
    df_dedup.to_excel(save_path, index=False, engine='openpyxl')
    
    if inplace:
        console.print(f"[green]✓[/green] 已覆盖原文件: {input_file}")
    else:
        console.print(f"[green]✓[/green] 已保存到: {output_path}")
    
    return {
        "original_count": original_count,
        "dedup_count": dedup_count,
        "dropped_count": dropped_count
    }


def sort_by_template(
    main_file: str,
    template_file: str,
    main_col: str,
    template_col: str,
    unmatched_position: Literal["top", "bottom"] = "top",
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    按模板文件自定义排序
    
    Args:
        main_file: 主数据文件路径
        template_file: 模板文件路径
        main_col: 主数据用于匹配的列名
        template_col: 模板文件用于匹配的列名
        unmatched_position: 未匹配项位置 ("top": 顶部, "bottom": 底部)
        output_path: 输出文件路径（None 时仅返回 DataFrame）
        
    Returns:
        pd.DataFrame: 排序后的数据框
        
    Raises:
        FileNotFoundError: 文件不存在
        KeyError: 列不存在
        ValueError: 空模板文件
        
    Examples:
        >>> df = sort_by_template("data.xlsx", "template.xlsx", "product_id", "id")
        >>> df = sort_by_template("data.xlsx", "order.xlsx", "name", "name", "bottom")
    """
    # 文件存在性检查
    if not os.path.exists(main_file):
        raise FileNotFoundError(f"主数据文件不存在: {main_file}")
    if not os.path.exists(template_file):
        raise FileNotFoundError(f"模板文件不存在: {template_file}")
    
    # 读取文件
    console.print(f"[cyan]读取主数据:[/cyan] {os.path.basename(main_file)}")
    main_df = pd.read_excel(main_file)
    console.print(f"  → {len(main_df)} 行")
    
    console.print(f"[cyan]读取模板:[/cyan] {os.path.basename(template_file)}")
    template_df = pd.read_excel(template_file)
    console.print(f"  → {len(template_df)} 行")
    
    # 检查列是否存在
    if main_col not in main_df.columns:
        raise KeyError(f"主数据文件缺少列: {main_col}")
    if template_col not in template_df.columns:
        raise KeyError(f"模板文件缺少列: {template_col}")
    
    # 检查模板是否为空
    if template_df.empty:
        raise ValueError("模板文件没有数据")
    
    # 建立模板顺序映射
    console.print(f"[cyan]排序依据:[/cyan] {main_col} ← {template_col}")
    
    # 获取模板列的唯一值并建立序号映射
    template_order = {value: idx for idx, value in enumerate(template_df[template_col].unique())}
    
    # 创建排序键
    if unmatched_position == "top":
        # 未匹配项使用负数，排在最前
        main_df['_sort_key'] = main_df[main_col].map(
            lambda x: template_order.get(x, -1)
        )
    else:  # bottom
        # 未匹配项使用最大值+1，排在最后
        max_order = len(template_order)
        main_df['_sort_key'] = main_df[main_col].map(
            lambda x: template_order.get(x, max_order)
        )
    
    # 执行排序
    sorted_df = main_df.sort_values('_sort_key').drop(columns=['_sort_key'])
    sorted_df = sorted_df.reset_index(drop=True)
    
    # 统计匹配情况
    matched_count = main_df[main_col].isin(template_order.keys()).sum()
    unmatched_count = len(main_df) - matched_count
    
    table = Table(title="排序统计", show_header=True, header_style="bold magenta")
    table.add_column("指标", style="cyan", width=20)
    table.add_column("数值", justify="right", style="green")
    
    table.add_row("总行数", str(len(main_df)))
    table.add_row("匹配项", str(matched_count))
    table.add_row("未匹配项", str(unmatched_count))
    table.add_row("未匹配项位置", "顶部" if unmatched_position == "top" else "底部")
    
    console.print(table)
    
    # 保存结果
    if output_path:
        sorted_df.to_excel(output_path, index=False, engine='openpyxl')
        console.print(f"[green]✓[/green] 已保存到: {output_path}")
    
    return sorted_df
