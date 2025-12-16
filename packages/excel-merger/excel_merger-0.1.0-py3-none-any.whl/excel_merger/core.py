"""
核心合并逻辑模块
"""

from pathlib import Path
from typing import List, Optional, Union
import pandas as pd


def list_excel_files(
    input_dir: Path, pattern: str = "*.xlsx", recursive: bool = False
) -> List[Path]:
    """
    列出目录中所有符合条件的 Excel 文件。
    
    :param input_dir: 输入文件夹路径
    :param pattern: 匹配 Excel 文件的通配符
    :param recursive: 是否递归搜索子目录
    :return: Excel 文件路径列表
    """
    if recursive:
        files = list(input_dir.rglob(pattern))
    else:
        files = list(input_dir.glob(pattern))
    
    return sorted(files)


def read_single_excel(
    path: Path,
    sheet_name: Optional[Union[str, int]] = None,
    header: int = 0,
) -> pd.DataFrame:
    """
    读取单个 Excel 文件。
    
    :param path: Excel 文件路径
    :param sheet_name: 要读取的 sheet 名称或索引；为 None 时使用第一个 sheet
    :param header: 表头所在行号
    :return: DataFrame
    :raises Exception: 读取失败时抛出异常
    """
    if sheet_name is None:
        sheet_name = 0  # 默认读取第一个 sheet
    
    df = pd.read_excel(path, sheet_name=sheet_name, header=header)
    return df


def merge_excels(
    input_dir: Union[str, Path],
    output_file: Union[str, Path],
    pattern: str = "*.xlsx",
    recursive: bool = False,
    sheet_name: Optional[str] = None,
    header: int = 0,
    add_source_column: bool = True,
    source_column_name: str = "source_file",
    overwrite: bool = False,
    return_dataframe: bool = False,
    quiet: bool = False,
) -> Optional[pd.DataFrame]:
    """
    从指定目录中读取符合条件的 Excel 文件并合并。

    :param input_dir: 输入文件夹路径
    :param output_file: 输出 Excel 文件路径
    :param pattern: 匹配 Excel 文件的通配符，默认 '*.xlsx'
    :param recursive: 是否递归搜索子目录
    :param sheet_name: 要读取的 sheet 名称；为 None 时默认使用第一个 sheet
    :param header: 表头所在行号（pandas 的 header 参数）
    :param add_source_column: 是否在结果中新增来源文件列
    :param source_column_name: 来源文件列名
    :param overwrite: 若输出文件已存在，是否允许覆盖
    :param return_dataframe: 若为 True，则返回合并后的 DataFrame；否则返回 None
    :param quiet: 若为 True，则尽量减少日志输出
    :return: 若 return_dataframe=True，则返回合并后的 DataFrame，否则返回 None
    :raises FileNotFoundError: input_dir 不存在或非目录
    :raises ValueError: 找不到任何匹配文件，或全部文件读取失败
    :raises FileExistsError: 输出文件存在且 overwrite=False
    """
    # 转换路径
    input_dir = Path(input_dir)
    output_file = Path(output_file)
    
    # 检查输入目录
    if not input_dir.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")
    if not input_dir.is_dir():
        raise FileNotFoundError(f"输入路径不是目录: {input_dir}")
    
    # 检查输出文件
    if output_file.exists() and not overwrite:
        raise FileExistsError(f"输出文件已存在，使用 overwrite=True 来覆盖: {output_file}")
    
    # 获取文件列表
    files = list_excel_files(input_dir, pattern, recursive)
    
    if not files:
        raise ValueError(f"未找到任何匹配 '{pattern}' 的文件")
    
    # 读取并合并所有文件
    dataframes = []
    success_count = 0
    failed_files = []
    
    for file_path in files:
        try:
            df = read_single_excel(file_path, sheet_name, header)
            
            # 添加来源文件列
            if add_source_column:
                df[source_column_name] = file_path.name
            
            dataframes.append(df)
            success_count += 1
            
        except Exception as e:
            failed_files.append((file_path, str(e)))
            if not quiet:
                print(f"警告: 读取文件失败 {file_path.name}: {e}")
    
    # 检查是否至少成功读取了一个文件
    if not dataframes:
        raise ValueError(f"所有文件读取失败，共 {len(files)} 个文件")
    
    # 合并所有 DataFrame
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    # 写出结果
    output_file.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_excel(output_file, index=False, sheet_name="merged")
    
    if not quiet:
        print(f"成功合并 {success_count}/{len(files)} 个文件")
        print(f"合并后总行数: {len(merged_df)}")
        print(f"输出文件: {output_file}")
    
    # 返回结果
    if return_dataframe:
        return merged_df
    return None
