"""
CLI 命令行界面模块
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import box

from .core import list_excel_files, merge_excels
from .version import __version__

app = typer.Typer(help="Excel Merger - 合并多个 Excel 文件的强大工具")
console = Console()


def show_welcome():
    """显示欢迎信息"""
    welcome_text = f"""
[bold cyan]Excel Merger[/bold cyan]
[dim]版本: {__version__}[/dim]

一个强大的 Excel 文件合并工具
支持命令行和 Python API 两种使用方式
    """
    console.print(Panel(welcome_text, border_style="cyan", box=box.ROUNDED))


def show_file_table(files: list, input_dir: Path):
    """显示文件列表"""
    table = Table(title="📋 待处理的 Excel 文件", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=6, justify="right")
    table.add_column("文件名", style="cyan")
    table.add_column("大小", justify="right", style="green")
    table.add_column("路径", style="dim")
    
    for idx, file_path in enumerate(files, 1):
        size = file_path.stat().st_size
        size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
        rel_path = file_path.relative_to(input_dir) if file_path.is_relative_to(input_dir) else file_path
        table.add_row(
            str(idx),
            file_path.name,
            size_str,
            str(rel_path.parent) if rel_path.parent != Path('.') else "."
        )
    
    console.print(table)


def show_summary(success_count: int, total_count: int, total_rows: int, output_file: Path):
    """显示合并结果摘要"""
    if success_count == total_count:
        status_icon = "✅"
        status_text = "[bold green]全部成功[/bold green]"
    else:
        status_icon = "⚠️"
        status_text = f"[bold yellow]部分成功[/bold yellow]"
    
    summary = f"""
{status_icon} {status_text}

[cyan]处理文件数:[/cyan] {total_count}
[cyan]成功读取:[/cyan] {success_count}
[cyan]合并后总行数:[/cyan] {total_rows}
[cyan]输出文件:[/cyan] {output_file}
    """
    console.print(Panel(summary, title="📊 合并结果", border_style="green", box=box.ROUNDED))


@app.command()
def merge(
    input_dir: Path = typer.Argument(
        ...,
        help="待合并的 Excel 文件所在文件夹",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    output_file: Path = typer.Option(
        "merged.xlsx",
        "--output",
        "-o",
        help="输出合并后的 Excel 文件路径",
    ),
    pattern: str = typer.Option(
        "*.xlsx",
        "--pattern",
        "-p",
        help="匹配 Excel 文件的通配符（glob）",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="是否递归遍历子文件夹",
    ),
    sheet_name: Optional[str] = typer.Option(
        None,
        "--sheet",
        "-s",
        help="指定要合并的 sheet 名称；默认取第一个 sheet",
    ),
    header: int = typer.Option(
        0,
        "--header",
        help="表头所在的行号（0 表示第一行）",
    ),
    add_source_column: bool = typer.Option(
        True,
        "--add-source/--no-add-source",
        help="是否添加来源文件列",
    ),
    source_column_name: str = typer.Option(
        "source_file",
        "--source-col",
        help="来源文件列名称",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="仅显示将要处理的文件，不实际写出结果",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="如输出文件已存在，是否允许覆盖",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="减少输出，只显示关键错误",
    ),
):
    """
    合并指定文件夹中的 Excel 文件
    """
    # 显示欢迎信息
    if not quiet:
        show_welcome()
    
    try:
        # 获取文件列表
        files = list_excel_files(input_dir, pattern, recursive)
        
        if not files:
            console.print(f"[bold red]❌ 错误:[/bold red] 未找到任何匹配 '{pattern}' 的文件", style="red")
            raise typer.Exit(code=3)
        
        # 显示文件列表
        if not quiet:
            show_file_table(files, input_dir)
            console.print(f"\n[cyan]找到 {len(files)} 个文件[/cyan]\n")
        
        # 如果是 dry-run 模式，直接退出
        if dry_run:
            console.print(f"[yellow]🔍 Dry-run 模式: 将输出到[/yellow] [bold]{output_file}[/bold]")
            console.print("[green]✓ Dry-run 完成，未实际处理文件[/green]")
            raise typer.Exit(code=0)
        
        # 检查输出文件是否存在
        if output_file.exists() and not overwrite:
            console.print(
                f"[bold red]❌ 错误:[/bold red] 输出文件已存在: {output_file}\n"
                f"使用 --overwrite 选项来覆盖",
                style="red"
            )
            raise typer.Exit(code=2)
        
        # 执行合并（带进度条）
        if not quiet:
            console.print("[bold cyan]🚀 开始合并 Excel 文件...[/bold cyan]\n")
        
        import pandas as pd
        from .core import read_single_excel
        
        dataframes = []
        success_count = 0
        failed_files = []
        
        if quiet:
            # 静默模式，直接处理
            for file_path in files:
                try:
                    df = read_single_excel(file_path, sheet_name, header)
                    if add_source_column:
                        df[source_column_name] = file_path.name
                    dataframes.append(df)
                    success_count += 1
                except Exception as e:
                    failed_files.append((file_path, str(e)))
        else:
            # 带进度条的处理
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]处理文件...", total=len(files))
                
                for file_path in files:
                    progress.update(task, description=f"[cyan]处理: {file_path.name}")
                    try:
                        df = read_single_excel(file_path, sheet_name, header)
                        if add_source_column:
                            df[source_column_name] = file_path.name
                        dataframes.append(df)
                        success_count += 1
                    except Exception as e:
                        failed_files.append((file_path, str(e)))
                        console.print(f"[yellow]⚠️  跳过文件 {file_path.name}: {e}[/yellow]")
                    
                    progress.advance(task)
        
        # 检查是否至少成功读取了一个文件
        if not dataframes:
            console.print(f"[bold red]❌ 错误:[/bold red] 所有文件读取失败，共 {len(files)} 个文件", style="red")
            raise typer.Exit(code=4)
        
        # 合并所有 DataFrame
        if not quiet:
            console.print("\n[cyan]📦 合并数据...[/cyan]")
        merged_df = pd.concat(dataframes, ignore_index=True)
        
        # 写出结果
        if not quiet:
            console.print(f"[cyan]💾 写入文件: {output_file}[/cyan]")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        merged_df.to_excel(output_file, index=False, sheet_name="merged")
        
        # 显示摘要
        if not quiet:
            console.print()
            show_summary(success_count, len(files), len(merged_df), output_file)
        else:
            console.print(f"成功合并 {success_count}/{len(files)} 个文件到 {output_file}")
        
        # 显示失败的文件
        if failed_files and not quiet:
            console.print("\n[yellow]⚠️  以下文件读取失败:[/yellow]")
            for file_path, error in failed_files:
                console.print(f"  • {file_path.name}: {error}")
        
    except typer.Exit:
        raise
    except FileNotFoundError as e:
        console.print(f"[bold red]❌ 错误:[/bold red] {e}", style="red")
        raise typer.Exit(code=2)
    except ValueError as e:
        console.print(f"[bold red]❌ 错误:[/bold red] {e}", style="red")
        raise typer.Exit(code=3)
    except Exception as e:
        console.print(f"[bold red]❌ 未预期的错误:[/bold red] {e}", style="red")
        import traceback
        if not quiet:
            console.print(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command()
def version():
    """显示版本信息"""
    console.print(f"[bold cyan]Excel Merger[/bold cyan] version [green]{__version__}[/green]")


def main():
    """主入口函数"""
    app()


if __name__ == "__main__":
    main()
