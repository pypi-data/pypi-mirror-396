# XLSM2Spec

Excel VBAを解析し仕様書を自動生成するCLIツール

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 概要

XLSM2Specは、ExcelファイルのVBAマクロを解析し、構造化された仕様書を自動生成します。
レガシーシステムの保守・移行プロジェクトにおいて、既存のExcelマクロの動作理解を支援します。

## 機能

- ✅ xls/xlsx/xlsm ファイルの読み込み
- ✅ VBAコードの抽出と解析
- ✅ モジュール・プロシージャ構造の解析
- ✅ Markdown/JSON/HTML形式での仕様書出力

## インストール

```bash
pip install xlsm2spec
```

または開発版：

```bash
git clone https://github.com/your-org/xlsm2spec.git
cd xlsm2spec
pip install -e ".[dev]"
```

## 使い方

### 基本的な使い方

```bash
# Excelファイルを解析し、仕様書を標準出力に表示
xlsm2spec analyze sample.xlsm

# 仕様書をファイルに出力
xlsm2spec analyze sample.xlsm -o spec.md

# JSON形式で出力
xlsm2spec analyze sample.xlsm -o spec.json -f json

# HTML形式で出力（スタイル付き）
xlsm2spec analyze sample.xlsm -o spec.html -f html

# 詳細ログを表示
xlsm2spec analyze sample.xlsm --verbose
```

### コマンドオプション

```
Usage: xlsm2spec analyze [OPTIONS] INPUT_FILE

  ExcelファイルのVBAを分析し、仕様書を生成する

Arguments:
  INPUT_FILE  分析するExcelファイル (.xls, .xlsx, .xlsm)  [required]

Options:
  -o, --output PATH     出力ファイルパス（省略時は標準出力）
  -f, --format TEXT     出力形式（markdown, json, html）  [default: markdown]
  --verbose             詳細な出力を表示
  --help                Show this message and exit.
```

## 出力例

```markdown
# sample.xlsm 仕様書

**生成日時**: 2025-12-12 10:00:00

## シート一覧
- Sheet1
- Sheet2

## VBAモジュール一覧

| モジュール名 | 種別 | プロシージャ数 |
|-------------|------|--------------|
| Module1 | standard | 2 |

### Module1

**種別**: standard

#### プロシージャ一覧

##### CalculateTotal

- **種別**: function
- **アクセス**: Public
- **引数**: startRow: Long, endRow: Long
- **戻り値**: Double
```

## 開発

### 環境構築

```bash
# 仮想環境作成
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 開発版インストール
pip install -e ".[dev]"

# テスト実行
pytest

# 型チェック
mypy src/

# リンター
ruff check src/
```

### プロジェクト構造

```
xlsm2spec/
├── src/xlsm2spec/
│   ├── domain/          # ドメインモデル（Workbook, Module, Procedure等）
│   ├── application/     # アプリケーションサービス（AnalyzerService）
│   ├── infrastructure/  # 外部ライブラリ統合（ExcelReader, VbaExtractor, VbaParser）
│   └── presentation/    # 出力フォーマッター（Markdown, JSON, HTML）
├── tests/               # pytest テスト
└── steering/            # MUSUBI SDD ドキュメント
```

### アーキテクチャ

Clean Architecture（4層構造）を採用：

- **Domain層**: ビジネスモデル（Workbook, VbaProject, Module, Procedure）
- **Application層**: ユースケース（AnalyzerService）
- **Infrastructure層**: 外部ライブラリ統合（xlrd, openpyxl, oletools）
- **Presentation層**: 出力フォーマット（Markdown, JSON, HTML）

## ライセンス

MIT License

## 貢献

Issue、Pull Requestを歓迎します。
