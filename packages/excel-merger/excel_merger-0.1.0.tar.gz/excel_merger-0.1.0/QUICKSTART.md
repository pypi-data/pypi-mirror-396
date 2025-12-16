# 快速开始指南 🚀

## 1. 安装依赖

```bash
cd /Users/mac/2025/202512
pip install -r requirements.txt
```

或者单独安装：

```bash
pip install pandas openpyxl typer rich
```

## 2. 运行示例（推荐）

最快的方式是运行示例脚本，它会自动创建测试数据并演示所有功能：

```bash
python example_usage.py
```

这将：
- ✅ 创建测试数据（3个 Excel 文件）
- ✅ 演示 4 种不同的使用方式
- ✅ 生成合并后的 Excel 文件到 `output/` 目录

## 3. 使用 CLI 命令行

### 方式一：Python 模块方式（推荐）

```bash
# 基本用法
python -m excel_merger.cli merge test_data --output merged.xlsx

# 查看帮助
python -m excel_merger.cli --help

# 查看版本
python -m excel_merger.cli version
```

### 方式二：直接运行脚本

```bash
# 基本用法
python excel_merger/cli.py merge test_data --output merged.xlsx
```

### 方式三：安装后使用命令（可选）

```bash
# 安装包
pip install -e .

# 使用命令
excel-merge test_data --output merged.xlsx
```

## 4. CLI 常用命令示例

```bash
# 1. 合并当前目录的所有 .xlsx 文件
python -m excel_merger.cli merge . --output merged.xlsx

# 2. 递归搜索所有子目录
python -m excel_merger.cli merge ./data --recursive --output all.xlsx

# 3. 预览将要处理的文件（不实际合并）
python -m excel_merger.cli merge ./data --dry-run

# 4. 合并指定的 sheet
python -m excel_merger.cli merge ./data --sheet "Sheet1" --output result.xlsx

# 5. 不添加来源文件列
python -m excel_merger.cli merge ./data --no-add-source --output result.xlsx

# 6. 覆盖已存在的输出文件
python -m excel_merger.cli merge ./data --output merged.xlsx --overwrite

# 7. 静默模式
python -m excel_merger.cli merge ./data --quiet --output merged.xlsx
```

## 5. Python API 使用

在你的 Python 脚本中：

```python
from excel_merger import merge_excels

# 基本使用
merge_excels(
    input_dir="data",
    output_file="merged.xlsx"
)

# 返回 DataFrame 进行进一步处理
df = merge_excels(
    input_dir="data",
    output_file="merged.xlsx",
    return_dataframe=True
)

print(f"合并了 {len(df)} 行数据")
```

## 6. 项目结构

```
202512/
├── excel_merger/          # 主包
│   ├── __init__.py       # 包初始化，导出 merge_excels
│   ├── version.py        # 版本信息
│   ├── core.py           # 核心合并逻辑
│   └── cli.py            # CLI 命令行界面
├── excel-merge           # CLI 入口脚本
├── example_usage.py      # 使用示例
├── requirements.txt      # 依赖列表
├── pyproject.toml        # 项目配置
├── README.md             # 完整文档
├── QUICKSTART.md         # 本文件
└── .gitignore           # Git 忽略配置
```

## 7. 验证安装

```bash
# 测试导入
python -c "from excel_merger import merge_excels; print('✓ 安装成功')"

# 查看版本
python -c "from excel_merger import __version__; print(f'版本: {__version__}')"
```

## 8. 常见问题

### Q1: 如何处理 .xls 格式的文件？

默认只支持 `.xlsx` 格式。如需支持 `.xls`：

```bash
pip install xlrd
```

然后使用 `--pattern "*.xls"` 参数。

### Q2: 文件列名不一致怎么办？

工具会自动对齐所有列，缺失的值会填充为 NaN。

### Q3: 如何只合并部分文件？

使用 `--pattern` 参数：

```bash
python -m excel_merger.cli merge ./data --pattern "report_*.xlsx"
```

### Q4: 单个文件读取失败会怎样？

默认会跳过失败的文件并继续处理，同时显示警告信息。

## 9. 下一步

- 📖 阅读完整文档：[README.md](README.md)
- 🔧 查看示例代码：[example_usage.py](example_usage.py)
- 💡 根据需求调整参数和选项

---

🎉 **享受使用 Excel Merger！**
