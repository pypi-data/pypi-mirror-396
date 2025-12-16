# Technology Stack

**Project**: XLSM2Spec
**Last Updated**: 2025-12-12
**Status**: 決定済み

---

## 概要

XLSM2Specは、Pythonベースのクロスプラットフォームな CLI ツールとして開発します。
VBA解析にはPythonの豊富なライブラリエコシステムを活用します。

## 技術スタック決定

| 項目 | 選定技術 | 理由 |
|------|---------|------|
| **言語** | Python 3.11+ | 豊富なExcelライブラリ、クロスプラットフォーム |
| **パッケージ管理** | uv / pip | 高速なパッケージ管理 |
| **CLI フレームワーク** | Typer | 型ヒント対応、自動ヘルプ生成 |
| **Excel読み込み(xls)** | xlrd | BIFF8形式のサポート |
| **Excel読み込み(xlsx/xlsm)** | openpyxl | OOXML形式のサポート |
| **VBA抽出** | oletools | OLE構造からのVBA抽出 |
| **VBA解析** | カスタムパーサー | 正規表現 + AST構築 |
| **テスト** | pytest | Python標準テストフレームワーク |
| **型チェック** | mypy | 静的型チェック |
| **リンター** | ruff | 高速なPythonリンター |
| **フォーマッター** | ruff format | 統一されたコードスタイル |
| **ドキュメント** | MkDocs | Markdown ベースのドキュメント生成 |

---

## 詳細技術選定

### プログラミング言語

**Python 3.11+**

選定理由：
- Excelファイル処理ライブラリが豊富（xlrd, openpyxl, oletools）
- VBA解析のための文字列処理が容易
- クロスプラットフォーム対応
- AI連携（将来）が容易（OpenAI SDK等）
- チームの習熟度が高い

代替案と却下理由：
- **Node.js**: VBA解析ライブラリが限定的
- **Rust**: 開発速度優先、バイナリ配布は後で検討
- **C#**: Linux/macOS対応が複雑

---

### Excel読み込み

#### xls形式（BIFF8）

**xlrd 2.0+**

```python
import xlrd

workbook = xlrd.open_workbook("file.xls")
for sheet in workbook.sheets():
    print(sheet.name)
```

選定理由：
- xls形式（Excel 97-2003）の読み込みに特化
- 安定した実績

注意点：
- xlrd 2.0以降はxls形式のみサポート（xlsxは非対応）

#### xlsx/xlsm形式（OOXML）

**openpyxl 3.1+**

```python
from openpyxl import load_workbook

workbook = load_workbook("file.xlsm", keep_vba=True)
for sheet in workbook.sheetnames:
    print(sheet)
```

選定理由：
- OOXML形式の標準ライブラリ
- VBAプロジェクト（vbaProject.bin）へのアクセスが可能
- 活発なメンテナンス

---

### VBA抽出

**oletools 0.60+**

```python
from oletools.olevba import VBA_Parser

vba_parser = VBA_Parser("file.xlsm")
for filename, stream_path, vba_filename, vba_code in vba_parser.extract_macros():
    print(f"Module: {vba_filename}")
    print(vba_code)
```

選定理由：
- OLE構造からVBAマクロを抽出するデファクトスタンダード
- xls、xlsm両方に対応
- セキュリティ分析向けに設計されているため堅牢

---

### VBA解析

**カスタムパーサー（正規表現 + AST）**

VBA構文解析専用のPythonライブラリは限定的なため、
正規表現ベースのカスタムパーサーを構築します。

```python
# 例：プロシージャ抽出の正規表現
PROCEDURE_PATTERN = r"""
    (?P<access>Public|Private)?\s*
    (?P<type>Sub|Function)\s+
    (?P<name>\w+)\s*
    \((?P<params>[^)]*)\)
    (?:\s+As\s+(?P<return>\w+))?
"""
```

将来的には `antlr4` でVBA文法を定義し、
完全なASTパーサーに移行することも検討。

---

### CLIフレームワーク

**Typer 0.9+**

```python
import typer

app = typer.Typer()

@app.command()
def analyze(
    input_file: str,
    output: str = typer.Option(None, "--output", "-o"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Excelファイルを解析し仕様書を生成します"""
    pass

if __name__ == "__main__":
    app()
```

選定理由：
- 型ヒントベースでCLI引数を定義
- 自動的にヘルプテキストを生成
- Rich との統合でカラフルな出力
- Click の上位互換

---

### テストフレームワーク

**pytest 7.4+**

```python
# tests/test_excel_reader.py
import pytest
from xlsm2spec.readers import ExcelReader

def test_read_xls_file():
    reader = ExcelReader("tests/fixtures/sample.xls")
    workbook = reader.read()
    assert len(workbook.sheets) == 2

def test_read_xlsm_file():
    reader = ExcelReader("tests/fixtures/sample.xlsm")
    workbook = reader.read()
    assert workbook.has_vba == True
```

選定理由：
- Pythonの標準的なテストフレームワーク
- フィクスチャ、パラメータ化テストが強力
- pytest-cov でカバレッジ計測

---

### 品質管理ツール

| ツール | 用途 |
|--------|------|
| **ruff** | リンター（flake8, isort, pyupgrade統合） |
| **ruff format** | フォーマッター（black互換） |
| **mypy** | 静的型チェック |
| **pre-commit** | Git フック管理 |

---

## プロジェクト構成

```
xlsm2spec/
├── pyproject.toml          # プロジェクト設定
├── src/
│   └── xlsm2spec/
│       ├── __init__.py
│       ├── cli.py          # CLI エントリーポイント
│       ├── domain/         # ドメイン層
│       │   ├── models.py   # Workbook, Module, Procedure
│       │   └── services.py # ドメインサービス
│       ├── application/    # アプリケーション層
│       │   └── analyzer.py # メイン解析サービス
│       ├── infrastructure/ # インフラ層
│       │   ├── readers/    # Excel読み込み
│       │   ├── extractors/ # VBA抽出
│       │   └── parsers/    # VBA解析
│       └── presentation/   # プレゼンテーション層
│           └── formatters/ # 出力フォーマット
├── tests/
│   ├── fixtures/           # テスト用Excelファイル
│   ├── unit/
│   └── integration/
└── docs/
```

---

## 依存関係

### 本番依存（requirements）

```toml
[project]
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "xlrd>=2.0.0",
    "openpyxl>=3.1.0",
    "oletools>=0.60.0",
]
```

### 開発依存（dev-requirements）

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.6.0",
    "ruff>=0.1.0",
    "pre-commit>=3.5.0",
]
```

---

## ビルド・配布

### パッケージング

**PyPI への公開**

```bash
# ビルド
python -m build

# PyPI にアップロード
twine upload dist/*
```

### 実行可能バイナリ（将来）

**PyInstaller** または **Nuitka** で単一実行可能ファイルを生成

```bash
pyinstaller --onefile src/xlsm2spec/cli.py
```

---

## 開発環境セットアップ

```bash
# リポジトリクローン
git clone https://github.com/your-org/xlsm2spec.git
cd xlsm2spec

# 仮想環境作成（uv推奨）
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 依存関係インストール
uv pip install -e ".[dev]"

# pre-commit フック設定
pre-commit install

# テスト実行
pytest

# 型チェック
mypy src/

# リンター
ruff check src/
```

---

## AI統合（Phase 3）

将来的なAI統合のための技術選定：

| 用途 | 選定技術 |
|------|---------|
| **LLM API** | OpenAI API / Azure OpenAI |
| **ローカルLLM** | Ollama + LlamaIndex |
| **プロンプト管理** | LangChain / 独自実装 |

---

**Last Updated**: 2025-12-12
**Maintained By**: MUSUBI SDD Workflow
