# Excel Toolbox 📊

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**一体化 Excel 数据处理工具集** - 数据整合、清洗、转换全流程解决方案

> 📖 **原始需求文档**: [readme.md](readme.md)  
> 🚀 **快速开始**: [QUICKSTART.md](QUICKSTART.md)  
> 📦 **安装说明**: [INSTALL.md](INSTALL.md)  
> 🎯 **发布指南**: [PUBLISH_GUIDE.md](PUBLISH_GUIDE.md)  
> 📋 **发布快速参考**: [PUBLISH_QUICKREF.md](PUBLISH_QUICKREF.md)  
> 📊 **项目总览**: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

## ✨ 核心特性

- 🔗 **数据聚合** - 批量合并文件 / 关联合并表
- 🧹 **数据清洗** - 去重清理 / 自定义排序
- 🔄 **格式转换** - CSV/JSON/Excel 跨格式互转
- 📋 **元数据管理** - 自动附加来源信息
- 🎨 **美化输出** - Rich 终端显示
- 🚀 **双模式支持** - CLI 命令行 + Python 脚本调用

## 🎯 设计原则

✅ **高内聚低耦合** - 每个功能模块独立封装  
✅ **强类型契约** - 完整类型提示与参数校验  
✅ **防御式编程** - 精细化异常处理  
✅ **零数据丢失** - 所有转换保留原始数据语义

## 📦 安装

### 方式一：使用 pip 安装（推荐）

```bash
pip install -e .
```

### 方式二：安装依赖后直接使用

```bash
pip install -r requirements.txt
```

## 🚀 快速开始

### CLI 命令行模式

```bash
# 查看帮助
excel-toolbox --help

# 合并文件夹内所有 Excel
excel-toolbox merge ./data merged.xlsx

# 两表关联合并
excel-toolbox join left.xlsx right.xlsx output.xlsx --left-on id --right-on user_id

# 去除重复数据
excel-toolbox dedup data.xlsx --output cleaned.xlsx --subset ID

# 自定义排序
excel-toolbox sort data.xlsx template.xlsx sorted.xlsx --main-col id --template-col id

# CSV 转 Excel
excel-toolbox csv2excel data.csv --output result.xlsx

# JSON 转 Excel
excel-toolbox json2excel api.json --pointer data.items

# Excel 转 JSON
excel-toolbox excel2json data.xlsx --sheet Sheet1
```

### Python 脚本模式

```python
from excel_toolbox import (
    merge_excel_files,
    join_tables,
    remove_duplicates,
    sort_by_template,
    csv_to_excel,
    json_to_excel,
    excel_to_json
)

# 合并文件夹内所有 Excel 文件
df = merge_excel_files(
    folder_path="./data",
    output_path="merged.xlsx",
    include_all_sheets=True
)

# 两表关联合并
df = join_tables(
    left_file="customers.xlsx",
    right_file="orders.xlsx",
    left_on="customer_id",
    right_on="cust_id",
    how="left",
    output_path="result.xlsx"
)

# 去除重复数据
stats = remove_duplicates(
    input_file="data.xlsx",
    subset=["ID", "Name"],
    keep="first",
    output_path="cleaned.xlsx"
)
print(f"删除了 {stats['dropped_count']} 行重复数据")

# 按模板排序
df = sort_by_template(
    main_file="products.xlsx",
    template_file="order_template.xlsx",
    main_col="product_id",
    template_col="id",
    unmatched_position="bottom",
    output_path="sorted.xlsx"
)

# CSV 转 Excel
df = csv_to_excel(
    csv_path="data.csv",
    encoding="utf-8",
    delimiter=","
)

# JSON 转 Excel
df = json_to_excel(
    json_path="api_response.json",
    json_pointer="data.items"
)

# Excel 转 JSON
json_str = excel_to_json(
    excel_path="data.xlsx",
    sheet_name="Sheet1",
    indent=2
)
```

## 📚 功能详解

### 1️⃣ 数据合并模块

#### `merge_excel_files` - 合并文件夹内所有 Excel

**功能**：遍历文件夹，智能合并所有 Excel 工作簿，自动注入元数据

**参数**：
- `folder_path` (str): 文件夹路径
- `output_path` (Optional[str]): 输出文件路径
- `include_all_sheets` (bool): 是否合并所有工作表（默认 False）

**返回**：`pd.DataFrame`

**元数据列**：
- `source_file`: 来源文件名
- `source_sheet`: 来源工作表名

**示例**：
```python
# 仅合并首表
df = merge_excel_files("./reports")

# 合并所有工作表
df = merge_excel_files("./reports", "all_data.xlsx", include_all_sheets=True)
```

---

#### `join_tables` - 两表关联合并

**功能**：实现类 SQL 的 `inner/left/right/outer` 四种连接模式

**参数**：
- `left_file` (str): 左表文件路径
- `right_file` (str): 右表文件路径
- `left_on` (str | List[str]): 左表关联键
- `right_on` (str | List[str]): 右表关联键
- `how` (Literal["inner", "left", "right", "outer"]): 连接类型
- `suffixes` (Tuple[str, str]): 重名列后缀（默认 `_left`, `_right`）
- `output_path` (Optional[str]): 输出路径

**返回**：`pd.DataFrame`

**示例**：
```python
# 内连接
df = join_tables("users.xlsx", "orders.xlsx", "id", "user_id")

# 左连接，多键关联
df = join_tables(
    "table_a.xlsx", "table_b.xlsx",
    left_on=["key1", "key2"],
    right_on=["k1", "k2"],
    how="left"
)
```

---

### 2️⃣ 数据清洗模块

#### `remove_duplicates` - 去除重复数据

**功能**：支持全行去重或指定列组合去重

**参数**：
- `input_file` (str): 输入文件路径
- `subset` (Optional[str | List[str]]): 去重依据列（None=全行）
- `keep` (Literal["first", "last", False]): 保留策略
- `inplace` (bool): 是否覆盖原文件
- `output_path` (Optional[str]): 输出路径

**返回**：字典 `{original_count, dedup_count, dropped_count}`

**示例**：
```python
# 全行去重
stats = remove_duplicates("data.xlsx", output_path="cleaned.xlsx")

# 按 ID 列去重，保留最后一次出现
stats = remove_duplicates(
    "data.xlsx",
    subset="ID",
    keep="last",
    output_path="result.xlsx"
)

# 删除所有重复项（包括首次出现）
stats = remove_duplicates("data.xlsx", keep=False, output_path="unique.xlsx")
```

---

#### `sort_by_template` - 按模板自定义排序

**功能**：依据模板文件列值顺序重排主数据

**参数**：
- `main_file` (str): 主数据文件
- `template_file` (str): 模板文件
- `main_col` (str): 主数据匹配列
- `template_col` (str): 模板匹配列
- `unmatched_position` (Literal["top", "bottom"]): 未匹配项位置
- `output_path` (Optional[str]): 输出路径

**返回**：`pd.DataFrame`

**示例**：
```python
# 按模板顺序排序，未匹配项置于顶部
df = sort_by_template(
    main_file="products.xlsx",
    template_file="priority_list.xlsx",
    main_col="product_id",
    template_col="id"
)

# 未匹配项置于底部
df = sort_by_template(
    "data.xlsx", "template.xlsx",
    "name", "name",
    unmatched_position="bottom",
    output_path="sorted.xlsx"
)
```

---

### 3️⃣ 格式转换模块

#### `csv_to_excel` - CSV 转 Excel

**功能**：智能编码识别，保留原始数据类型

**参数**：
- `csv_path` (str): CSV 文件路径
- `output_path` (Optional[str]): 输出路径（默认同目录 .xlsx）
- `encoding` (str): 文件编码（默认 utf-8）
- `delimiter` (str): 分隔符（默认逗号）
- `include_index` (bool): 是否包含索引

**返回**：`pd.DataFrame`

**示例**：
```python
# 默认 UTF-8 编码
df = csv_to_excel("data.csv")

# GBK 编码，分号分隔
df = csv_to_excel("data.csv", encoding="gbk", delimiter=";")
```

---

#### `json_to_excel` - JSON 转 Excel

**功能**：支持平铺/嵌套 JSON，通过路径表达式提取数据

**参数**：
- `json_path` (str): JSON 文件路径
- `output_path` (Optional[str]): 输出路径
- `json_pointer` (Optional[str]): JSON 路径（点分隔，如 `data.items`）
- `include_index` (bool): 是否包含索引

**返回**：`pd.DataFrame`

**支持结构**：
| JSON 顶层 | 处理方式 |
|----------|---------|
| `[{...}]` | 直接转换 |
| `{"key": [...]}` | 需指定 `json_pointer` |
| 混合嵌套 | 自动扁平化 |

**示例**：
```python
# 顶层数组
df = json_to_excel("data.json")

# 嵌套对象
df = json_to_excel("api.json", json_pointer="response.data.items")
```

---

#### `excel_to_json` - Excel 转 JSON

**功能**：输出标准 JSON 数组，NaN→null，支持美化

**参数**：
- `excel_path` (str): Excel 文件路径
- `output_path` (Optional[str]): 输出路径
- `sheet_name` (str | int): 工作表名称或索引
- `indent` (Optional[int]): 缩进（2=美化，None=紧凑）
- `date_format` (str): 日期格式（iso/epoch）

**返回**：`str` (JSON 字符串)

**示例**：
```python
# 紧凑格式
json_str = excel_to_json("data.xlsx", indent=None)

# 指定工作表
json_str = excel_to_json("data.xlsx", sheet_name="Summary")
```

---

## 🛡️ 异常处理

| 异常类型 | 触发场景 | 处理策略 |
|---------|---------|---------|
| `FileNotFoundError` | 文件不存在 | 中断执行 |
| `ValueError` | 参数冲突 | 中断执行 |
| `KeyError` | 列名/路径不存在 | 中断执行 |
| `UnicodeDecodeError` | 编码错误 | 提示尝试其他编码 |
| `RuntimeError` | 无有效数据 | 中断执行 |
| `Warning` | 单文件失败 | 跳过并记录警告 |

---

## 📋 CLI 命令速查

| 命令 | 功能 | 示例 |
|------|------|------|
| `merge` | 合并文件夹 Excel | `excel-toolbox merge ./data out.xlsx` |
| `join` | 两表关联 | `excel-toolbox join a.xlsx b.xlsx out.xlsx -l id -r id` |
| `dedup` | 去重 | `excel-toolbox dedup data.xlsx -o clean.xlsx -s ID` |
| `sort` | 自定义排序 | `excel-toolbox sort data.xlsx tpl.xlsx out.xlsx -m id -t id` |
| `csv2excel` | CSV→Excel | `excel-toolbox csv2excel data.csv` |
| `json2excel` | JSON→Excel | `excel-toolbox json2excel api.json -p data.items` |
| `excel2json` | Excel→JSON | `excel-toolbox excel2json data.xlsx -s Sheet1` |

---

## 🔧 依赖环境

- **Python**: 3.9+
- **核心依赖**:
  ```
  pandas>=2.0.0
  openpyxl>=3.1.0
  xlrd>=2.0.0
  typer>=0.9.0
  rich>=13.0.0
  ```

---

## 📝 项目结构

```
excel-toolbox/
├── excel_toolbox/
│   ├── __init__.py       # 包初始化
│   ├── merger.py         # 数据合并模块
│   ├── cleaner.py        # 数据清洗模块
│   ├── converter.py      # 格式转换模块
│   └── cli.py            # CLI 命令行接口
├── examples/             # 使用示例
├── requirements.txt      # 依赖清单
├── pyproject.toml        # 项目配置
├── setup.py              # 安装脚本
└── README.md             # 说明文档
```

---

## 🎓 使用示例场景

### 场景 1：合并月度报表
```python
# 将 ./monthly_reports 下所有 Excel 合并为一个文件
df = merge_excel_files("./monthly_reports", "yearly_report.xlsx")
# 自动添加 source_file 和 source_sheet 列标识来源
```

### 场景 2：客户订单关联分析
```python
# 左连接：保留所有客户，关联订单信息
df = join_tables(
    "customers.xlsx", "orders.xlsx",
    left_on="customer_id",
    right_on="cust_id",
    how="left",
    output_path="customer_orders.xlsx"
)
```

### 场景 3：数据清洗流水线
```python
# 1. 去除重复客户
stats = remove_duplicates("raw_customers.xlsx", subset="phone", output_path="step1.xlsx")

# 2. 按优先级排序
df = sort_by_template("step1.xlsx", "priority.xlsx", "level", "priority_level", output_path="final.xlsx")
```

### 场景 4：多格式数据汇总
```python
# 1. CSV 转 Excel
csv_to_excel("sales.csv", "sales.xlsx")

# 2. JSON API 响应转 Excel
json_to_excel("api_response.json", "users.xlsx", json_pointer="data.users")

# 3. 合并所有 Excel
merge_excel_files(".", "all_data.xlsx")
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 📮 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/yourusername/excel-toolbox/issues)
- **功能建议**: [GitHub Discussions](https://github.com/yourusername/excel-toolbox/discussions)

---

**Excel Toolbox** - 让数据处理更简单 🚀
