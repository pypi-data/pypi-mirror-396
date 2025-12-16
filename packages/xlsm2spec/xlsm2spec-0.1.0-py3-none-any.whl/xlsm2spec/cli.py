"""XLSM2Spec CLI - ExcelファイルからVBA仕様書を生成"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from xlsm2spec import __version__
from xlsm2spec.application.analyzer import AnalyzerService
from xlsm2spec.domain.exceptions import (
    Xlsm2SpecError,
    FileNotFoundError,
    UnsupportedFormatError,
    VbaExtractionError,
    VbaProtectedError,
)
from xlsm2spec.domain.models import Workbook
from xlsm2spec.presentation.formatters.ears_formatter import EarsFormatter
from xlsm2spec.presentation.formatters.html_formatter import HtmlFormatter
from xlsm2spec.presentation.formatters.json_formatter import JsonFormatter
from xlsm2spec.presentation.formatters.markdown_formatter import MarkdownFormatter

app = typer.Typer(
    name="xlsm2spec",
    help="ExcelファイルからVBA仕様書を生成するツール",
    add_completion=False,
)
console = Console()
error_console = Console(stderr=True)


def version_callback(value: bool) -> None:
    """バージョン表示"""
    if value:
        console.print(f"xlsm2spec version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="バージョンを表示",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """XLSM2Spec - ExcelファイルからVBA仕様書を生成"""
    pass


@app.command()
def analyze(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="分析するExcelファイル (.xls, .xlsx, .xlsm)",
            exists=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="出力ファイルパス（省略時は標準出力）",
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="出力形式（markdown, json, html, ears）",
        ),
    ] = "markdown",
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            help="詳細な出力を表示",
        ),
    ] = False,
) -> None:
    """ExcelファイルのVBAを分析し、仕様書を生成する"""
    try:
        # 分析実行
        if verbose:
            console.print(f"[blue]分析中:[/blue] {input_file}")

        analyzer = AnalyzerService()
        workbook = analyzer.analyze(str(input_file))

        if verbose:
            _print_summary(workbook)

        # フォーマット
        format_lower = format.lower()
        formatter: EarsFormatter | JsonFormatter | HtmlFormatter | MarkdownFormatter
        if format_lower == "json":
            formatter = JsonFormatter()
        elif format_lower == "html":
            formatter = HtmlFormatter()
        elif format_lower == "ears":
            formatter = EarsFormatter()
        else:
            formatter = MarkdownFormatter()

        result = formatter.format(workbook)

        # 出力
        if output:
            output.write_text(result, encoding="utf-8")
            console.print(f"[green]✓[/green] 仕様書を生成しました: {output}")
        else:
            console.print(result)

    except FileNotFoundError as e:
        error_console.print(f"[red]エラー:[/red] {e}")
        raise typer.Exit(1) from None
    except UnsupportedFormatError as e:
        error_console.print(f"[red]エラー:[/red] {e}")
        raise typer.Exit(1) from None
    except VbaProtectedError as e:
        error_console.print(f"[yellow]警告:[/yellow] {e}")
        error_console.print("VBAプロジェクトが保護されているため、完全な分析ができません。")
        raise typer.Exit(2) from None
    except VbaExtractionError as e:
        error_console.print(f"[red]エラー:[/red] {e}")
        raise typer.Exit(1) from None
    except Xlsm2SpecError as e:
        error_console.print(f"[red]エラー:[/red] {e}")
        raise typer.Exit(1) from None


def _print_summary(workbook: Workbook) -> None:
    """分析結果のサマリーを表示"""
    lines = [
        f"ファイル: {workbook.filename}",
        f"シート数: {len(workbook.sheets)}",
    ]

    if workbook.vba_project:
        lines.append(f"VBAモジュール数: {len(workbook.vba_project.modules)}")
        total_procs = sum(
            len(m.procedures) for m in workbook.vba_project.modules
        )
        lines.append(f"プロシージャ数: {total_procs}")

    console.print(Panel("\n".join(lines), title="分析結果", border_style="blue"))


if __name__ == "__main__":
    app()
