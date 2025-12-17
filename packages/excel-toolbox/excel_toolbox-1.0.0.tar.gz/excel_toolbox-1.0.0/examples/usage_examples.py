"""
使用示例 - Python 脚本模式

演示所有功能的完整使用方法
"""

from excel_toolbox import (
    merge_excel_files,
    join_tables,
    remove_duplicates,
    sort_by_template,
    csv_to_excel,
    json_to_excel,
    excel_to_json
)


def example_merge_files():
    """示例 1: 合并文件夹内所有 Excel 文件"""
    print("\n" + "="*60)
    print("示例 1: 合并文件夹内所有 Excel 文件")
    print("="*60)
    
    # 仅合并首表
    df = merge_excel_files(
        folder_path="./sample_data/monthly_reports",
        output_path="./output/merged_first_sheet.xlsx",
        include_all_sheets=False
    )
    print(f"\n✓ 首表合并完成，共 {len(df)} 行数据")
    
    # 合并所有工作表
    df_all = merge_excel_files(
        folder_path="./sample_data/monthly_reports",
        output_path="./output/merged_all_sheets.xlsx",
        include_all_sheets=True
    )
    print(f"✓ 全部工作表合并完成，共 {len(df_all)} 行数据")


def example_join_tables():
    """示例 2: 两表关联合并"""
    print("\n" + "="*60)
    print("示例 2: 两表关联合并（SQL JOIN）")
    print("="*60)
    
    # Inner Join
    df_inner = join_tables(
        left_file="./sample_data/customers.xlsx",
        right_file="./sample_data/orders.xlsx",
        left_on="customer_id",
        right_on="cust_id",
        how="inner",
        output_path="./output/inner_join.xlsx"
    )
    print(f"\n✓ Inner Join 完成，共 {len(df_inner)} 行")
    
    # Left Join
    df_left = join_tables(
        left_file="./sample_data/customers.xlsx",
        right_file="./sample_data/orders.xlsx",
        left_on="customer_id",
        right_on="cust_id",
        how="left",
        output_path="./output/left_join.xlsx"
    )
    print(f"✓ Left Join 完成，共 {len(df_left)} 行")


def example_remove_duplicates():
    """示例 3: 去除重复数据"""
    print("\n" + "="*60)
    print("示例 3: 去除重复数据")
    print("="*60)
    
    # 全行去重
    stats1 = remove_duplicates(
        input_file="./sample_data/duplicates.xlsx",
        output_path="./output/dedup_all.xlsx"
    )
    print(f"\n✓ 全行去重: 删除 {stats1['dropped_count']} 行")
    
    # 按指定列去重
    stats2 = remove_duplicates(
        input_file="./sample_data/duplicates.xlsx",
        subset=["ID", "Name"],
        keep="last",
        output_path="./output/dedup_subset.xlsx"
    )
    print(f"✓ 按列去重: 删除 {stats2['dropped_count']} 行")


def example_sort_by_template():
    """示例 4: 按模板自定义排序"""
    print("\n" + "="*60)
    print("示例 4: 按模板自定义排序")
    print("="*60)
    
    df = sort_by_template(
        main_file="./sample_data/products.xlsx",
        template_file="./sample_data/priority_template.xlsx",
        main_col="product_id",
        template_col="id",
        unmatched_position="bottom",
        output_path="./output/sorted_products.xlsx"
    )
    print(f"\n✓ 排序完成，共 {len(df)} 行数据")


def example_csv_to_excel():
    """示例 5: CSV 转 Excel"""
    print("\n" + "="*60)
    print("示例 5: CSV 转 Excel")
    print("="*60)
    
    # UTF-8 编码
    df1 = csv_to_excel(
        csv_path="./sample_data/sales.csv",
        output_path="./output/sales.xlsx",
        encoding="utf-8"
    )
    print(f"\n✓ UTF-8 CSV 转换完成，{len(df1)} 行")
    
    # GBK 编码
    df2 = csv_to_excel(
        csv_path="./sample_data/sales_gbk.csv",
        output_path="./output/sales_gbk.xlsx",
        encoding="gbk"
    )
    print(f"✓ GBK CSV 转换完成，{len(df2)} 行")


def example_json_to_excel():
    """示例 6: JSON 转 Excel"""
    print("\n" + "="*60)
    print("示例 6: JSON 转 Excel")
    print("="*60)
    
    # 顶层数组
    df1 = json_to_excel(
        json_path="./sample_data/simple_array.json",
        output_path="./output/from_simple_json.xlsx"
    )
    print(f"\n✓ 简单数组转换完成，{len(df1)} 行")
    
    # 嵌套对象
    df2 = json_to_excel(
        json_path="./sample_data/nested_object.json",
        output_path="./output/from_nested_json.xlsx",
        json_pointer="data.items"
    )
    print(f"✓ 嵌套对象转换完成，{len(df2)} 行")


def example_excel_to_json():
    """示例 7: Excel 转 JSON"""
    print("\n" + "="*60)
    print("示例 7: Excel 转 JSON")
    print("="*60)
    
    # 美化格式
    json_str1 = excel_to_json(
        excel_path="./sample_data/products.xlsx",
        output_path="./output/products_pretty.json",
        sheet_name=0,
        indent=2
    )
    print(f"\n✓ 美化格式 JSON 生成完成")
    
    # 紧凑格式
    json_str2 = excel_to_json(
        excel_path="./sample_data/products.xlsx",
        output_path="./output/products_compact.json",
        sheet_name=0,
        indent=None
    )
    print(f"✓ 紧凑格式 JSON 生成完成")


def example_pipeline():
    """示例 8: 完整数据处理流水线"""
    print("\n" + "="*60)
    print("示例 8: 完整数据处理流水线")
    print("="*60)
    
    # 步骤 1: CSV 转 Excel
    print("\n步骤 1: 导入 CSV 数据")
    df1 = csv_to_excel("./sample_data/raw_data.csv", "./output/step1_imported.xlsx")
    
    # 步骤 2: 去重
    print("\n步骤 2: 去除重复数据")
    stats = remove_duplicates(
        "./output/step1_imported.xlsx",
        subset="ID",
        output_path="./output/step2_deduped.xlsx"
    )
    
    # 步骤 3: 按模板排序
    print("\n步骤 3: 自定义排序")
    df3 = sort_by_template(
        "./output/step2_deduped.xlsx",
        "./sample_data/sort_template.xlsx",
        "category",
        "category_order",
        output_path="./output/step3_sorted.xlsx"
    )
    
    # 步骤 4: 导出 JSON
    print("\n步骤 4: 导出为 JSON")
    json_str = excel_to_json("./output/step3_sorted.xlsx", "./output/final_result.json")
    
    print("\n" + "="*60)
    print("✓ 完整流水线处理完成！")
    print("="*60)


if __name__ == "__main__":
    import os
    
    # 创建输出目录
    os.makedirs("./output", exist_ok=True)
    
    print("\n" + "🚀 Excel Toolbox 使用示例演示".center(60, "="))
    
    # 运行所有示例（需要相应的示例数据文件）
    # 注释掉暂时没有数据的示例，避免报错
    
    print("\n提示：请确保 ./sample_data 目录下有对应的示例文件")
    print("或根据实际情况修改文件路径")
    
    # 取消下面的注释来运行示例
    # example_merge_files()
    # example_join_tables()
    # example_remove_duplicates()
    # example_sort_by_template()
    # example_csv_to_excel()
    # example_json_to_excel()
    # example_excel_to_json()
    # example_pipeline()
    
    print("\n" + "="*60)
    print("所有示例代码位于 examples/usage_examples.py")
    print("根据需要修改文件路径后运行")
    print("="*60)
