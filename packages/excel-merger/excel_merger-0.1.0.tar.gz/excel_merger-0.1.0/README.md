# Excel Merger 📊

一个强大的 Excel 文件合并工具，支持命令行（CLI）和 Python API 两种使用方式。

使用 `Typer` 提供现代化 CLI 体验，使用 `rich` 实现精美的命令行输出。

## ✨ 特性

- 🚀 **易于使用** - 简单的命令行界面和 Python API
- 📁 **批量合并** - 自动合并文件夹中的所有 Excel 文件
- 🔍 **灵活匹配** - 支持通配符模式和递归搜索
- 🎨 **精美输出** - 使用 Rich 库实现彩色、表格化的命令行输出
- 📊 **智能处理** - 自动对齐列结构，可选添加来源文件列
- ⚡ **进度显示** - 实时显示处理进度
- 🛡️ **错误处理** - 单个文件失败不影响整体合并

## 📦 安装

### 方式一：从源码安装

```bash
# 克隆或下载项目
cd /path/to/202512

# 安装依赖
pip install -r requirements.txt

# 安装项目（开发模式）
pip install -e .
```

### 方式二：仅安装依赖（无需安装项目）

```bash
pip install pandas openpyxl typer rich
```

## 🚀 使用方法

### 命令行（CLI）使用

#### 基本用法

```bash
# 合并当前目录下的所有 .xlsx 文件
excel-merge . --output merged.xlsx

# 或者使用 Python 模块方式运行
python -m excel_merger.cli merge . --output merged.xlsx
```

#### 高级用法

```bash
# 递归搜索所有子目录中的 Excel 文件
excel-merge ./data --recursive --output all_merged.xlsx

# 合并指定 sheet
excel-merge ./reports --sheet "Data" --output data_merged.xlsx

# 使用自定义文件匹配模式
excel-merge ./data --pattern "report_*.xlsx" --output reports.xlsx

# 仅预览将要处理的文件（不实际合并）
excel-merge ./data --dry-run

# 不添加来源文件列
excel-merge ./data --no-add-source --output merged_no_source.xlsx

# 覆盖已存在的输出文件
excel-merge ./data --output merged.xlsx --overwrite

# 静默模式（减少输出）
excel-merge ./data --quiet --output merged.xlsx
```

#### 查看帮助

```bash
# 查看完整帮助
excel-merge --help

# 查看版本
excel-merge version
```

### Python API 使用

```python
from excel_merger import merge_excels

# 基本使用
merge_excels(
    input_dir="data/excels",
    output_file="output/merged.xlsx"
)

# 高级使用
df = merge_excels(
    input_dir="data/monthly",
    output_file="output/monthly_merged.xlsx",
    pattern="*.xlsx",              # 文件匹配模式
    recursive=True,                # 递归搜索子目录
    sheet_name="Sheet1",           # 指定要合并的 sheet
    header=0,                      # 表头行号
    add_source_column=True,        # 添加来源文件列
    source_column_name="来源文件",  # 来源列名称
    overwrite=True,                # 覆盖已存在文件
    return_dataframe=True,         # 返回 DataFrame
    quiet=False,                   # 显示处理信息
)

print(f"合并后的行数: {len(df)}")
print(f"列名: {df.columns.tolist()}")
```

## 📋 参数说明

### CLI 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_dir` | Path | 必填 | 待合并的 Excel 文件所在文件夹 |
| `--output, -o` | Path | `merged.xlsx` | 输出文件路径 |
| `--pattern, -p` | str | `*.xlsx` | 文件匹配通配符 |
| `--recursive, -r` | bool | `False` | 是否递归遍历子文件夹 |
| `--sheet, -s` | str | `None` | 指定要合并的 sheet 名称 |
| `--header` | int | `0` | 表头所在行号 |
| `--add-source/--no-add-source` | bool | `True` | 是否添加来源文件列 |
| `--source-col` | str | `source_file` | 来源文件列名称 |
| `--dry-run` | bool | `False` | 仅显示将要处理的文件 |
| `--overwrite` | bool | `False` | 是否覆盖已存在的输出文件 |
| `--quiet, -q` | bool | `False` | 减少输出信息 |

### Python API 参数

参数与 CLI 基本一致，额外包括：

- `return_dataframe` (bool): 是否返回合并后的 DataFrame，默认 `False`

## 📸 效果展示

CLI 运行效果包括：

- 🎨 彩色标题面板
- 📋 格式化的文件列表表格
- ⏳ 实时进度条
- 📊 合并结果统计面板
- ⚠️ 清晰的错误和警告提示

## 🔧 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black excel_merger/

# 代码检查
flake8 excel_merger/
```

## 📝 示例场景

### 场景 1：合并月度报表

```bash
excel-merge ./reports/2024 --pattern "report_*.xlsx" --output yearly_report.xlsx
```

### 场景 2：合并多个部门数据

```python
from excel_merger import merge_excels

result = merge_excels(
    input_dir="data/departments",
    output_file="all_departments.xlsx",
    recursive=True,
    add_source_column=True,
    source_column_name="部门",
    return_dataframe=True
)

# 进一步处理合并后的数据
print(result.groupby("部门").size())
```

### 场景 3：批量处理多个文件夹

```python
from pathlib import Path
from excel_merger import merge_excels

folders = ["2023Q1", "2023Q2", "2023Q3", "2023Q4"]

for folder in folders:
    merge_excels(
        input_dir=f"data/{folder}",
        output_file=f"output/{folder}_merged.xlsx",
        quiet=True
    )
```

## ⚠️ 注意事项

1. **文件格式**：默认支持 `.xlsx` 格式，如需支持 `.xls` 请安装 `xlrd`
2. **列名对齐**：合并时会自动对齐所有列，缺失值填充为 NaN
3. **大文件**：处理大量文件时建议使用进度条模式查看进度
4. **错误处理**：单个文件读取失败会跳过并继续处理其他文件

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

如有问题或建议，请提交 Issue。
