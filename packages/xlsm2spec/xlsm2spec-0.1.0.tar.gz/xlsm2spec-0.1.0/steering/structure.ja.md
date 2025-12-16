# Project Structure

**Project**: XLSM2Spec
**Last Updated**: 2025-12-12
**Version**: 1.0

---

## Architecture Pattern

**Primary Pattern**: Clean Architecture（クリーンアーキテクチャ）

XLSM2Specは、ドメイン駆動設計（DDD）とクリーンアーキテクチャの原則に基づき、
4層のレイヤー構造を採用します。これにより、テスタビリティと保守性を確保します。

---

## アーキテクチャ概要（C4モデル）

### レベル1: システムコンテキスト

```
┌─────────────────────────────────────────────────────────────┐
│                        ユーザー                              │
│                   （SE、コンサルタント）                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     XLSM2Spec                              │
│    Excel/VBAファイルを解析し仕様書を生成するCLIツール         │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
      ┌──────────┐     ┌──────────┐     ┌──────────┐
      │  Excel   │     │ ファイル  │     │   AI    │
      │ ファイル  │     │ システム  │     │  API    │
      │ (入力)   │     │ (出力)   │     │ (将来)  │
      └──────────┘     └──────────┘     └──────────┘
```

### レベル2: コンテナ図

```
┌─────────────────────────────────────────────────────────────┐
│                     XLSM2Spec CLI                          │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                 Presentation Layer                      │ │
│ │    CLI Interface, Output Formatters                    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                              │                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                 Application Layer                       │ │
│ │    Analyzer Service, Workflow Orchestration            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                              │                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                   Domain Layer                          │ │
│ │    Workbook, Module, Procedure, CellReference          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                              │                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                Infrastructure Layer                     │ │
│ │    ExcelReader, VbaExtractor, VbaParser                │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Layers

### Layer 1: Domain（ドメイン層）

**Purpose**: ビジネスロジックとドメインモデル

**Rules**:
- 他のどの層にも依存しない
- 純粋なPythonのみ（外部ライブラリ不可）
- I/O操作なし

**Contents**:
- `Workbook`: Excelブックを表すエンティティ
- `VbaProject`: VBAプロジェクトを表すエンティティ
- `Module`: VBAモジュールを表すエンティティ
- `Procedure`: Sub/Functionを表すエンティティ
- `Variable`: 変数・定数を表す値オブジェクト
- `CellReference`: セル参照を表す値オブジェクト

**Location**: `src/xlsm2spec/domain/`

```python
# domain/models.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class ModuleType(Enum):
    STANDARD = "standard"
    CLASS = "class"
    FORM = "form"
    SHEET = "sheet"
    THISWORKBOOK = "thisworkbook"

class ProcedureType(Enum):
    SUB = "sub"
    FUNCTION = "function"
    PROPERTY_GET = "property_get"
    PROPERTY_LET = "property_let"
    PROPERTY_SET = "property_set"

@dataclass
class Variable:
    name: str
    var_type: Optional[str]
    is_array: bool = False
    scope: str = "local"

@dataclass
class Procedure:
    name: str
    procedure_type: ProcedureType
    access: str  # "Public" or "Private"
    parameters: List[Variable]
    return_type: Optional[str]
    source_code: str
    line_start: int
    line_end: int

@dataclass
class Module:
    name: str
    module_type: ModuleType
    source_code: str
    procedures: List[Procedure]
    variables: List[Variable]

@dataclass
class VbaProject:
    modules: List[Module]
    is_protected: bool = False

@dataclass
class Workbook:
    filename: str
    sheets: List[str]
    vba_project: Optional[VbaProject]
```

---

### Layer 2: Application（アプリケーション層）

**Purpose**: ユースケースの実装、ワークフローのオーケストレーション

**Rules**:
- Domain層のみに依存
- Infrastructure層はインターフェース経由で使用
- 入出力の変換を担当

**Contents**:
- `AnalyzerService`: メインの解析ワークフロー
- `SpecificationGenerator`: 仕様書生成ロジック

**Location**: `src/xlsm2spec/application/`

```python
# application/analyzer.py
from typing import Protocol
from xlsm2spec.domain.models import Workbook, VbaProject

class ExcelReaderPort(Protocol):
    """Excel読み込みのインターフェース"""
    def read(self, filepath: str) -> Workbook: ...

class VbaExtractorPort(Protocol):
    """VBA抽出のインターフェース"""
    def extract(self, filepath: str) -> VbaProject: ...

class VbaParserPort(Protocol):
    """VBA解析のインターフェース"""
    def parse(self, source_code: str) -> list: ...

class AnalyzerService:
    def __init__(
        self,
        excel_reader: ExcelReaderPort,
        vba_extractor: VbaExtractorPort,
        vba_parser: VbaParserPort,
    ):
        self._excel_reader = excel_reader
        self._vba_extractor = vba_extractor
        self._vba_parser = vba_parser
    
    def analyze(self, filepath: str) -> Workbook:
        """Excelファイルを解析し、仕様情報を抽出する"""
        workbook = self._excel_reader.read(filepath)
        
        if workbook.vba_project:
            for module in workbook.vba_project.modules:
                procedures = self._vba_parser.parse(module.source_code)
                module.procedures = procedures
        
        return workbook
```

---

### Layer 3: Infrastructure（インフラストラクチャ層）

**Purpose**: 外部システムとの統合（ファイルI/O、ライブラリ）

**Rules**:
- Application層のインターフェース（Port）を実装
- 外部ライブラリの使用はこの層に限定
- すべてのI/O操作はこの層で行う

**Contents**:
- `readers/`: Excel読み込みアダプター（xlrd, openpyxl）
- `extractors/`: VBA抽出アダプター（oletools）
- `parsers/`: VBA解析（カスタムパーサー）

**Location**: `src/xlsm2spec/infrastructure/`

```python
# infrastructure/readers/excel_reader.py
import xlrd
from openpyxl import load_workbook
from xlsm2spec.domain.models import Workbook

class ExcelReader:
    def read(self, filepath: str) -> Workbook:
        if filepath.endswith('.xls'):
            return self._read_xls(filepath)
        elif filepath.endswith(('.xlsx', '.xlsm')):
            return self._read_xlsx(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")
    
    def _read_xls(self, filepath: str) -> Workbook:
        wb = xlrd.open_workbook(filepath)
        sheets = [sheet.name for sheet in wb.sheets()]
        return Workbook(filename=filepath, sheets=sheets, vba_project=None)
    
    def _read_xlsx(self, filepath: str) -> Workbook:
        wb = load_workbook(filepath, keep_vba=True)
        sheets = wb.sheetnames
        has_vba = wb.vba_archive is not None
        return Workbook(filename=filepath, sheets=sheets, vba_project=None)
```

```python
# infrastructure/extractors/vba_extractor.py
from oletools.olevba import VBA_Parser
from xlsm2spec.domain.models import VbaProject, Module, ModuleType

class VbaExtractor:
    def extract(self, filepath: str) -> VbaProject:
        vba_parser = VBA_Parser(filepath)
        modules = []
        
        for filename, stream_path, vba_filename, vba_code in vba_parser.extract_macros():
            module_type = self._detect_module_type(vba_filename)
            module = Module(
                name=vba_filename,
                module_type=module_type,
                source_code=vba_code,
                procedures=[],
                variables=[],
            )
            modules.append(module)
        
        vba_parser.close()
        return VbaProject(modules=modules, is_protected=False)
    
    def _detect_module_type(self, name: str) -> ModuleType:
        if name.startswith("Sheet"):
            return ModuleType.SHEET
        elif name == "ThisWorkbook":
            return ModuleType.THISWORKBOOK
        elif name.endswith(".cls"):
            return ModuleType.CLASS
        elif name.endswith(".frm"):
            return ModuleType.FORM
        else:
            return ModuleType.STANDARD
```

```python
# infrastructure/parsers/vba_parser.py
import re
from typing import List
from xlsm2spec.domain.models import Procedure, ProcedureType, Variable

class VbaParser:
    PROCEDURE_PATTERN = re.compile(
        r"(?P<access>Public|Private)?\s*"
        r"(?P<type>Sub|Function)\s+"
        r"(?P<name>\w+)\s*"
        r"\((?P<params>[^)]*)\)"
        r"(?:\s+As\s+(?P<return>\w+))?",
        re.IGNORECASE
    )
    
    def parse(self, source_code: str) -> List[Procedure]:
        procedures = []
        lines = source_code.split('\n')
        
        for i, line in enumerate(lines):
            match = self.PROCEDURE_PATTERN.match(line.strip())
            if match:
                procedure = Procedure(
                    name=match.group('name'),
                    procedure_type=ProcedureType[match.group('type').upper()],
                    access=match.group('access') or 'Public',
                    parameters=self._parse_parameters(match.group('params')),
                    return_type=match.group('return'),
                    source_code="",  # Will be filled later
                    line_start=i + 1,
                    line_end=i + 1,  # Will be updated
                )
                procedures.append(procedure)
        
        return procedures
    
    def _parse_parameters(self, params_str: str) -> List[Variable]:
        if not params_str.strip():
            return []
        
        params = []
        for param in params_str.split(','):
            param = param.strip()
            # Parse "ByVal name As Type" or "name As Type" or "name"
            parts = param.split(' As ')
            name = parts[0].replace('ByVal', '').replace('ByRef', '').strip()
            var_type = parts[1].strip() if len(parts) > 1 else None
            params.append(Variable(name=name, var_type=var_type))
        
        return params
```

---

### Layer 4: Presentation（プレゼンテーション層）

**Purpose**: ユーザーインターフェース（CLI）、出力フォーマット

**Rules**:
- Application層に依存
- ユーザー入力の検証
- 出力の整形

**Contents**:
- `cli.py`: Typerベースのコマンドラインインターフェース
- `formatters/`: 出力フォーマッター（Markdown, JSON, HTML）

**Location**: `src/xlsm2spec/presentation/` および `src/xlsm2spec/cli.py`

```python
# cli.py
import typer
from pathlib import Path
from rich.console import Console
from xlsm2spec.application.analyzer import AnalyzerService
from xlsm2spec.infrastructure.readers.excel_reader import ExcelReader
from xlsm2spec.infrastructure.extractors.vba_extractor import VbaExtractor
from xlsm2spec.infrastructure.parsers.vba_parser import VbaParser
from xlsm2spec.presentation.formatters.markdown import MarkdownFormatter

app = typer.Typer(help="Excel VBAファイルを解析し仕様書を生成します")
console = Console()

@app.command()
def analyze(
    input_file: Path = typer.Argument(..., help="解析するExcelファイルのパス"),
    output: Path = typer.Option(None, "--output", "-o", help="出力ファイルのパス"),
    format: str = typer.Option("markdown", "--format", "-f", help="出力形式 (markdown/json)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="詳細ログを出力"),
):
    """Excelファイルを解析し仕様書を生成します"""
    
    if not input_file.exists():
        console.print(f"[red]エラー: ファイルが見つかりません: {input_file}[/red]")
        raise typer.Exit(code=1)
    
    # 依存性の注入
    analyzer = AnalyzerService(
        excel_reader=ExcelReader(),
        vba_extractor=VbaExtractor(),
        vba_parser=VbaParser(),
    )
    
    if verbose:
        console.print(f"[blue]解析中: {input_file}[/blue]")
    
    # 解析実行
    workbook = analyzer.analyze(str(input_file))
    
    # 出力
    formatter = MarkdownFormatter()
    spec = formatter.format(workbook)
    
    if output:
        output.write_text(spec, encoding='utf-8')
        console.print(f"[green]仕様書を出力しました: {output}[/green]")
    else:
        console.print(spec)

@app.command()
def version():
    """バージョン情報を表示します"""
    console.print("XLSM2Spec v0.1.0")

if __name__ == "__main__":
    app()
```

```python
# presentation/formatters/markdown.py
from xlsm2spec.domain.models import Workbook, Module, Procedure

class MarkdownFormatter:
    def format(self, workbook: Workbook) -> str:
        lines = []
        lines.append(f"# {workbook.filename} 仕様書\n")
        lines.append(f"**生成日時**: {self._now()}\n")
        
        # シート一覧
        lines.append("## シート一覧\n")
        for sheet in workbook.sheets:
            lines.append(f"- {sheet}")
        lines.append("")
        
        # VBAプロジェクト
        if workbook.vba_project:
            lines.append("## VBAモジュール一覧\n")
            lines.append("| モジュール名 | 種別 | プロシージャ数 |")
            lines.append("|-------------|------|--------------|")
            for module in workbook.vba_project.modules:
                lines.append(
                    f"| {module.name} | {module.module_type.value} | "
                    f"{len(module.procedures)} |"
                )
            lines.append("")
            
            # 各モジュールの詳細
            for module in workbook.vba_project.modules:
                lines.extend(self._format_module(module))
        else:
            lines.append("## VBAプロジェクト\n")
            lines.append("VBAマクロは含まれていません。\n")
        
        return "\n".join(lines)
    
    def _format_module(self, module: Module) -> list:
        lines = []
        lines.append(f"### {module.name}\n")
        lines.append(f"**種別**: {module.module_type.value}\n")
        
        if module.procedures:
            lines.append("#### プロシージャ一覧\n")
            for proc in module.procedures:
                lines.extend(self._format_procedure(proc))
        
        return lines
    
    def _format_procedure(self, proc: Procedure) -> list:
        lines = []
        lines.append(f"##### {proc.name}\n")
        lines.append(f"- **種別**: {proc.procedure_type.value}")
        lines.append(f"- **アクセス**: {proc.access}")
        
        if proc.parameters:
            params = ", ".join(
                f"{p.name}: {p.var_type or 'Variant'}" 
                for p in proc.parameters
            )
            lines.append(f"- **引数**: {params}")
        
        if proc.return_type:
            lines.append(f"- **戻り値**: {proc.return_type}")
        
        lines.append("")
        return lines
    
    def _now(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

---

## Layer Dependency Rules

```
┌─────────────────────────────────────────┐
│        Presentation Layer               │ ← CLIエントリーポイント
│        (cli.py, formatters/)            │
├─────────────────────────────────────────┤
          │ depends on
          ▼
┌─────────────────────────────────────────┐
│        Application Layer                │ ← ユースケース
│        (analyzer.py)                    │
├─────────────────────────────────────────┤
          │ depends on (interface)
          ▼
┌─────────────────────────────────────────┐
│        Domain Layer                     │ ← ビジネスモデル
│        (models.py)                      │
└─────────────────────────────────────────┘
          ▲
          │ implements
┌─────────────────────────────────────────┐
│        Infrastructure Layer             │ ← 外部ライブラリ
│        (readers/, extractors/, parsers/)│
└─────────────────────────────────────────┘
```

**依存関係のルール**:
1. 上位層は下位層に依存できる
2. 下位層は上位層に依存してはならない
3. Domain層は他のどの層にも依存しない
4. Infrastructure層はDomain層のモデルを使用するが、Application層のインターフェースを実装する

---

## ディレクトリ構成

```
xlsm2spec/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
├── docs/
│   └── ...                     # ドキュメント
├── src/
│   └── xlsm2spec/
│       ├── __init__.py
│       ├── cli.py              # CLIエントリーポイント
│       ├── domain/
│       │   ├── __init__.py
│       │   └── models.py       # ドメインモデル
│       ├── application/
│       │   ├── __init__.py
│       │   └── analyzer.py     # アプリケーションサービス
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── readers/
│       │   │   ├── __init__.py
│       │   │   └── excel_reader.py
│       │   ├── extractors/
│       │   │   ├── __init__.py
│       │   │   └── vba_extractor.py
│       │   └── parsers/
│       │       ├── __init__.py
│       │       └── vba_parser.py
│       └── presentation/
│           ├── __init__.py
│           └── formatters/
│               ├── __init__.py
│               ├── markdown.py
│               └── json_formatter.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytestフィクスチャ
│   ├── fixtures/               # テスト用Excelファイル
│   │   ├── sample.xls
│   │   └── sample.xlsm
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── presentation/
│   └── integration/
│       └── test_analyze_workflow.py
├── steering/                    # MUSUBI SDD ドキュメント
│   ├── product.ja.md
│   ├── structure.ja.md
│   ├── tech.ja.md
│   └── rules/
├── storage/                     # MUSUBI ストレージ
│   ├── specs/
│   ├── features/
│   └── changes/
├── templates/                   # 出力テンプレート
├── pyproject.toml
├── README.md
├── AGENTS.md
└── .gitignore
```

---

## コンポーネント一覧

| コンポーネント | 層 | 責務 | 依存 |
|--------------|-----|------|------|
| `cli.py` | Presentation | CLIコマンド処理 | AnalyzerService |
| `MarkdownFormatter` | Presentation | Markdown出力生成 | Domain models |
| `AnalyzerService` | Application | 解析ワークフロー | Ports (interfaces) |
| `Workbook` | Domain | Excelブックモデル | なし |
| `Module` | Domain | VBAモジュールモデル | なし |
| `Procedure` | Domain | プロシージャモデル | なし |
| `ExcelReader` | Infrastructure | Excel読み込み | xlrd, openpyxl |
| `VbaExtractor` | Infrastructure | VBA抽出 | oletools |
| `VbaParser` | Infrastructure | VBA構文解析 | 正規表現 |

---

**Last Updated**: 2025-12-12
**Maintained By**: MUSUBI SDD Workflow
