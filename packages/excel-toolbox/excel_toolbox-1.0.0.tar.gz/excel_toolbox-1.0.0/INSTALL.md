# 安装和发布指南

## 📦 安装方式

### 方式一：开发模式安装（推荐用于开发）

```bash
# 1. 克隆或下载项目
cd /path/to/excel-toolbox

# 2. 安装依赖
pip install -r requirements.txt

# 3. 以开发模式安装（可编辑模式）
pip install -e .
```

**优点**：代码修改后立即生效，无需重新安装

### 方式二：正式安装

```bash
# 1. 进入项目目录
cd /path/to/excel-toolbox

# 2. 构建并安装
pip install .
```

### 方式三：从 PyPI 安装（发布后）

```bash
pip install excel-toolbox
```

---

## 🚀 发布到 PyPI

### 准备工作

1. **注册 PyPI 账号**
   - 访问 https://pypi.org/account/register/
   - 注册并验证邮箱

2. **安装构建工具**
   ```bash
   pip install build twine
   ```

### 发布步骤

#### 1. 更新版本号

编辑 `pyproject.toml`：
```toml
[project]
version = "1.0.0"  # 修改版本号
```

编辑 `excel_toolbox/__init__.py`：
```python
__version__ = "1.0.0"  # 保持一致
```

#### 2. 构建分发包

```bash
# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info

# 构建源码包和 wheel 包
python -m build
```

成功后会在 `dist/` 目录下生成：
- `excel-toolbox-1.0.0.tar.gz` （源码包）
- `excel_toolbox-1.0.0-py3-none-any.whl` （wheel 包）

#### 3. 检查包

```bash
# 检查包的完整性
twine check dist/*
```

#### 4. 上传到 TestPyPI（可选，用于测试）

```bash
# 上传到测试环境
twine upload --repository testpypi dist/*

# 从测试环境安装验证
pip install --index-url https://test.pypi.org/simple/ excel-toolbox
```

#### 5. 上传到正式 PyPI

```bash
# 上传到正式环境
twine upload dist/*

# 输入 PyPI 用户名和密码
# 或使用 API Token（推荐）
```

**使用 API Token（推荐）**：
```bash
# 在 PyPI 生成 API Token
# 账户设置 -> API tokens -> Add API token

# 创建 ~/.pypirc 文件
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # 你的 token
```

#### 6. 验证安装

```bash
# 卸载旧版本
pip uninstall excel-toolbox -y

# 从 PyPI 安装
pip install excel-toolbox

# 测试命令
excel-toolbox --version
```

---

## 📝 版本管理

### 语义化版本号（Semantic Versioning）

格式：`主版本.次版本.修订号`

- **主版本**：不兼容的 API 修改
- **次版本**：向下兼容的功能新增
- **修订号**：向下兼容的问题修正

示例：
- `1.0.0` - 首次正式发布
- `1.1.0` - 新增功能（兼容 1.0.0）
- `1.1.1` - 修复 bug
- `2.0.0` - 重大变更（不兼容 1.x）

### 更新发布流程

```bash
# 1. 修改代码并测试
# ...

# 2. 更新版本号
# 编辑 pyproject.toml 和 __init__.py

# 3. 提交 Git
git add .
git commit -m "Release v1.1.0: Add new feature"
git tag v1.1.0
git push origin main --tags

# 4. 重新构建和发布
rm -rf dist/
python -m build
twine upload dist/*
```

---

## 🔧 配置文件说明

### `pyproject.toml` - 项目元数据

```toml
[project]
name = "excel-toolbox"           # PyPI 包名
version = "1.0.0"                # 版本号
description = "..."              # 简短描述
authors = [...]                  # 作者信息
requires-python = ">=3.9"        # Python 版本要求
dependencies = [...]             # 依赖列表

[project.scripts]
excel-toolbox = "excel_toolbox.cli:app"  # CLI 入口点
```

### `setup.py` - 安装脚本

简化配置，主要功能由 `pyproject.toml` 定义：
```python
from setuptools import setup, find_packages
setup(
    packages=find_packages(),
    include_package_data=True,
)
```

### `requirements.txt` - 开发依赖

```
pandas>=2.0.0
openpyxl>=3.1.0
xlrd>=2.0.0
typer>=0.9.0
rich>=13.0.0
```

---

## 🧪 本地测试

### 1. 功能测试

```python
# 创建测试脚本 test_local.py
from excel_toolbox import merge_excel_files

df = merge_excel_files("./test_data")
print(f"✓ 合并成功: {len(df)} 行")
```

### 2. CLI 测试

```bash
# 测试命令是否可用
excel-toolbox --help
excel-toolbox --version

# 测试具体功能
excel-toolbox merge ./test_data output.xlsx
```

### 3. 安装测试

```bash
# 开发模式
pip install -e .
python -c "from excel_toolbox import merge_excel_files; print('✓ 导入成功')"

# 正式安装
pip uninstall excel-toolbox -y
pip install .
excel-toolbox --version
```

---

## 📂 项目文件清单

发布前确保包含以下文件：

```
excel-toolbox/
├── excel_toolbox/          # 源代码包
│   ├── __init__.py
│   ├── merger.py
│   ├── cleaner.py
│   ├── converter.py
│   └── cli.py
├── examples/               # 示例代码
├── README.md              # 说明文档
├── LICENSE                # 许可证（建议添加）
├── pyproject.toml         # 项目配置
├── setup.py               # 安装脚本
└── requirements.txt       # 依赖清单
```

---

## ⚠️ 常见问题

### Q1: `twine upload` 提示认证失败？
**A**: 使用 API Token 而非密码，在 `~/.pypirc` 配置

### Q2: 包名已被占用？
**A**: 在 `pyproject.toml` 中修改 `name` 为其他名称

### Q3: 构建失败提示缺少文件？
**A**: 检查 `MANIFEST.in` 或确保 `pyproject.toml` 正确配置

### Q4: CLI 命令找不到？
**A**: 检查 `[project.scripts]` 配置，重新安装包

---

## 📚 参考资源

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI 官方文档](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)
- [Twine 文档](https://twine.readthedocs.io/)

---

## 🎉 发布检查清单

- [ ] 代码测试通过
- [ ] 更新版本号
- [ ] 更新 README.md
- [ ] 添加 LICENSE 文件
- [ ] 构建分发包 (`python -m build`)
- [ ] 检查包完整性 (`twine check dist/*`)
- [ ] 上传到 TestPyPI 测试
- [ ] 上传到正式 PyPI
- [ ] Git 提交并打标签
- [ ] 验证安装和功能

---

**祝发布顺利！** 🚀
