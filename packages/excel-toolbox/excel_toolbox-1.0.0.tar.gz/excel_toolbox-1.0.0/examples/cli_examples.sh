"""
CLI 命令行使用示例
"""

# ============================================================
# 1. 合并文件夹内所有 Excel 文件
# ============================================================

# 仅合并首表
excel-toolbox merge ./monthly_reports merged.xlsx

# 合并所有工作表
excel-toolbox merge ./monthly_reports merged_all.xlsx --all-sheets


# ============================================================
# 2. 两表关联合并
# ============================================================

# Inner Join（内连接）
excel-toolbox join customers.xlsx orders.xlsx result.xlsx \
  --left-on customer_id \
  --right-on cust_id \
  --how inner

# Left Join（左连接）
excel-toolbox join customers.xlsx orders.xlsx result.xlsx \
  -l customer_id \
  -r cust_id \
  --how left

# 多键关联（在 Python 脚本模式使用）
# CLI 模式暂不支持多键，请使用 Python API


# ============================================================
# 3. 去除重复数据
# ============================================================

# 全行去重
excel-toolbox dedup data.xlsx --output cleaned.xlsx

# 按指定列去重
excel-toolbox dedup data.xlsx \
  --output cleaned.xlsx \
  --subset ID,Name

# 保留最后一次出现
excel-toolbox dedup data.xlsx \
  -o cleaned.xlsx \
  -s ID \
  --keep last

# 覆盖原文件
excel-toolbox dedup data.xlsx --inplace


# ============================================================
# 4. 按模板自定义排序
# ============================================================

# 基本排序
excel-toolbox sort data.xlsx template.xlsx sorted.xlsx \
  --main-col product_id \
  --template-col id

# 未匹配项置于底部
excel-toolbox sort data.xlsx template.xlsx sorted.xlsx \
  -m category \
  -t category_order \
  --unmatched bottom


# ============================================================
# 5. CSV 转 Excel
# ============================================================

# 默认 UTF-8 编码
excel-toolbox csv2excel data.csv

# 指定输出路径和编码
excel-toolbox csv2excel data.csv \
  --output result.xlsx \
  --encoding gbk

# 自定义分隔符（分号分隔）
excel-toolbox csv2excel data.csv \
  -o result.xlsx \
  --delimiter ";"


# ============================================================
# 6. JSON 转 Excel
# ============================================================

# 顶层数组 JSON
excel-toolbox json2excel data.json

# 嵌套对象，指定路径
excel-toolbox json2excel api_response.json \
  --output users.xlsx \
  --pointer data.users

# 复杂路径示例
excel-toolbox json2excel api.json \
  -o items.xlsx \
  -p response.data.items


# ============================================================
# 7. Excel 转 JSON
# ============================================================

# 默认第一个工作表
excel-toolbox excel2json data.xlsx

# 指定工作表名称
excel-toolbox excel2json data.xlsx \
  --output result.json \
  --sheet Sheet2

# 紧凑格式（无缩进）
excel-toolbox excel2json data.xlsx \
  -o compact.json \
  --indent 0

# 美化格式（4 空格缩进）
excel-toolbox excel2json data.xlsx \
  -o pretty.json \
  --indent 4


# ============================================================
# 8. 完整数据处理流水线示例
# ============================================================

# 步骤 1: 导入 CSV
excel-toolbox csv2excel raw_data.csv -o step1.xlsx

# 步骤 2: 去重
excel-toolbox dedup step1.xlsx -o step2.xlsx -s ID

# 步骤 3: 排序
excel-toolbox sort step2.xlsx template.xlsx step3.xlsx -m id -t id

# 步骤 4: 导出 JSON
excel-toolbox excel2json step3.xlsx -o final.json


# ============================================================
# 查看帮助
# ============================================================

# 查看所有命令
excel-toolbox --help

# 查看特定命令帮助
excel-toolbox merge --help
excel-toolbox join --help
excel-toolbox dedup --help
excel-toolbox sort --help
excel-toolbox csv2excel --help
excel-toolbox json2excel --help
excel-toolbox excel2json --help

# 查看版本
excel-toolbox --version
