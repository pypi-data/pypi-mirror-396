# 快速开始指南 🚀

这是一份 5 分钟快速上手指南，让你立即开始使用 Excel Toolbox。

## 📦 第一步：安装

```bash
# 进入项目目录
cd /Users/mac/2025/20251214

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装（推荐）
pip install -e .
```

安装成功后，你应该能运行：
```bash
excel-toolbox --version
```

---

## 🎯 第二步：准备测试数据

创建一些简单的测试文件来体验功能：

### 创建测试 CSV 文件

```bash
mkdir -p test_data
```

创建 `test_data/products.csv`：
```csv
ID,Name,Price,Category
1,Laptop,999.99,Electronics
2,Mouse,29.99,Electronics
3,Desk,299.99,Furniture
4,Chair,199.99,Furniture
5,Monitor,349.99,Electronics
```

---

## 🧪 第三步：尝试基本功能

### 1. CSV 转 Excel

```bash
excel-toolbox csv2excel test_data/products.csv --output test_data/products.xlsx
```

### 2. Excel 转 JSON

```bash
excel-toolbox excel2json test_data/products.xlsx --output test_data/products.json
```

查看生成的 JSON 文件，应该看到格式化的数据。

### 3. Python 脚本调用

创建 `test_script.py`：

```python
from excel_toolbox import csv_to_excel, excel_to_json

# CSV → Excel
df = csv_to_excel("test_data/products.csv", "test_data/output1.xlsx")
print(f"✓ 转换成功: {len(df)} 行数据")

# Excel → JSON
json_str = excel_to_json("test_data/output1.xlsx", "test_data/output1.json")
print("✓ JSON 导出完成")
```

运行：
```bash
python test_script.py
```

---

## 📚 第四步：探索更多功能

### 合并多个 Excel 文件

假设你有多个月度报表：

```bash
# 创建测试文件夹
mkdir -p test_data/reports

# 将几个 Excel 文件放入 reports 文件夹
# 然后合并它们
excel-toolbox merge test_data/reports test_data/merged.xlsx
```

### 去除重复数据

```python
from excel_toolbox import remove_duplicates

stats = remove_duplicates(
    "test_data/products.xlsx",
    subset="Category",  # 按类别去重
    keep="first",
    output_path="test_data/unique_categories.xlsx"
)

print(f"原始: {stats['original_count']} 行")
print(f"去重后: {stats['dedup_count']} 行")
print(f"删除: {stats['dropped_count']} 行")
```

### 两表关联

创建 `test_data/orders.csv`：
```csv
OrderID,ProductID,Quantity
1001,1,2
1002,3,1
1003,5,3
```

```python
from excel_toolbox import join_tables

# 先转换 CSV
csv_to_excel("test_data/orders.csv", "test_data/orders.xlsx")

# 关联产品和订单
df = join_tables(
    "test_data/products.xlsx",
    "test_data/orders.xlsx",
    left_on="ID",
    right_on="ProductID",
    how="inner",
    output_path="test_data/orders_with_details.xlsx"
)

print(f"关联结果: {len(df)} 行")
```

---

## 🎨 第五步：查看 Rich 美化输出

所有命令都使用 Rich 库美化终端输出，你会看到：

- ✅ 彩色进度提示
- 📊 格式化表格
- 🎯 清晰的状态信息

尝试运行任何命令，观察输出效果：

```bash
excel-toolbox dedup test_data/products.xlsx -o test_data/dedup.xlsx -s Category
```

你会看到漂亮的统计表格！

---

## 📖 下一步

- 📚 阅读完整文档：[README.md](README.md)
- 💡 查看更多示例：[examples/](examples/)
- 🚀 发布到 PyPI：[INSTALL.md](INSTALL.md)

---

## 🆘 遇到问题？

### 问题 1: 命令找不到
```bash
# 重新安装
pip uninstall excel-toolbox -y
pip install -e .
```

### 问题 2: 导入错误
```bash
# 检查依赖
pip install -r requirements.txt
```

### 问题 3: 编码问题
```bash
# CSV 使用 GBK 编码
excel-toolbox csv2excel data.csv --encoding gbk
```

---

## ✅ 快速测试清单

- [ ] 安装成功 (`excel-toolbox --version`)
- [ ] CSV 转 Excel 成功
- [ ] Excel 转 JSON 成功
- [ ] Python 脚本调用成功
- [ ] 看到 Rich 美化输出

全部完成？恭喜你已经掌握基本用法！🎉

---

**开始你的数据处理之旅吧！** 🚀

