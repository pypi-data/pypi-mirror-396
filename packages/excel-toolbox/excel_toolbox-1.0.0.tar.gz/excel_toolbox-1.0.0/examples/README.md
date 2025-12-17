# 使用示例说明

本目录包含 Excel Toolbox 的完整使用示例。

## 📁 文件说明

### `usage_examples.py`
**Python 脚本调用示例**

包含所有功能模块的完整 Python 代码示例：
- 合并文件夹内所有 Excel 文件
- 两表关联合并
- 去除重复数据
- 按模板自定义排序
- CSV 转 Excel
- JSON 转 Excel
- Excel 转 JSON
- 完整数据处理流水线

**使用方法**：
```bash
# 根据实际情况修改文件路径后运行
python examples/usage_examples.py
```

---

### `cli_examples.sh`
**CLI 命令行示例**

包含所有 CLI 命令的使用示例，覆盖：
- 所有基本命令的标准用法
- 常用参数组合
- 完整的数据处理流水线
- 帮助命令

**使用方法**：
```bash
# 查看示例
cat examples/cli_examples.sh

# 复制命令直接在终端运行
excel-toolbox merge ./data merged.xlsx
```

---

## 🎓 学习路径

### 新手入门
1. 先阅读 [QUICKSTART.md](../QUICKSTART.md)
2. 运行几个简单的 CLI 命令
3. 查看 `cli_examples.sh` 中的示例

### 进阶使用
1. 阅读 `usage_examples.py` 了解 Python API
2. 修改示例代码适配自己的数据
3. 编写自己的数据处理脚本

### 高级应用
1. 阅读源代码了解实现细节
2. 组合多个功能构建复杂流水线
3. 扩展自定义功能

---

## 💡 实用技巧

### 技巧 1: 链式处理
```bash
# CSV → Excel → 去重 → 排序 → JSON
excel-toolbox csv2excel data.csv -o step1.xlsx
excel-toolbox dedup step1.xlsx -o step2.xlsx -s ID
excel-toolbox sort step2.xlsx template.xlsx step3.xlsx -m id -t id
excel-toolbox excel2json step3.xlsx -o final.json
```

### 技巧 2: Python 流水线
```python
from excel_toolbox import csv_to_excel, remove_duplicates, sort_by_template

# 链式调用
df1 = csv_to_excel("data.csv", "step1.xlsx")
stats = remove_duplicates("step1.xlsx", subset="ID", output_path="step2.xlsx")
df3 = sort_by_template("step2.xlsx", "template.xlsx", "id", "id", output_path="final.xlsx")
```

### 技巧 3: 批处理
```bash
# 批量转换多个 CSV 文件
for file in *.csv; do
    excel-toolbox csv2excel "$file" --output "${file%.csv}.xlsx"
done
```

---

## 🔍 常见场景示例

### 场景 1: 月度报表汇总
```python
# 合并所有月度报表
df = merge_excel_files("./monthly_reports", "yearly.xlsx", include_all_sheets=True)
```

### 场景 2: 数据清洗
```python
# 去重 + 排序
remove_duplicates("raw.xlsx", subset="ID", output_path="clean.xlsx")
sort_by_template("clean.xlsx", "priority.xlsx", "category", "order", output_path="final.xlsx")
```

### 场景 3: 格式转换
```bash
# CSV 导入，处理后导出 JSON
excel-toolbox csv2excel data.csv -o temp.xlsx
excel-toolbox dedup temp.xlsx -o clean.xlsx -s ID
excel-toolbox excel2json clean.xlsx -o output.json
```

---

## 🆘 遇到问题？

1. **查看帮助**: `excel-toolbox <command> --help`
2. **阅读文档**: [README.md](../README.md)
3. **检查示例**: 对比你的代码与示例的差异
4. **测试安装**: `python test_installation.py`

---

**开始探索示例代码吧！** 🚀
