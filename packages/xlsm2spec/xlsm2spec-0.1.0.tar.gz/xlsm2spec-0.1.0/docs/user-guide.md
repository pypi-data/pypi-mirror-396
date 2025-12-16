# XLSM2Spec 利用者ガイド

Excel VBAマクロを解析し、仕様書を自動生成するツールの利用ガイドです。

---

## 目次

1. [はじめに](#はじめに)
2. [インストール](#インストール)
3. [基本的な使い方](#基本的な使い方)
4. [出力形式](#出力形式)
5. [コマンドリファレンス](#コマンドリファレンス)
6. [出力内容の解説](#出力内容の解説)
7. [トラブルシューティング](#トラブルシューティング)
8. [FAQ](#faq)

---

## はじめに

### XLSM2Specとは

XLSM2Specは、ExcelファイルのVBAマクロを自動解析し、構造化された仕様書を生成するコマンドラインツールです。

### こんな方におすすめ

- 📋 レガシーExcelマクロの保守・移行を担当している方
- 📖 既存VBAコードのドキュメントを作成したい方
- 🔍 VBAマクロの構造を素早く把握したい方
- 📊 Excelマクロの棚卸しを行いたい方

### 対応ファイル形式

| 拡張子 | 形式名 | VBA対応 |
|--------|--------|---------|
| `.xls` | Excel 97-2003 | ✅ |
| `.xlsx` | Excel 2007+ (マクロなし) | ❌ |
| `.xlsm` | Excel 2007+ (マクロ有効) | ✅ |

---

## インストール

### 前提条件

- Python 3.11 以上
- pip（Pythonパッケージマネージャー）

### インストール手順

```bash
# pipでインストール
pip install xlsm2spec

# または、ソースからインストール
git clone https://github.com/your-org/xlsm2spec.git
cd xlsm2spec
pip install -e .
```

### インストール確認

```bash
xlsm2spec --version
# 出力: xlsm2spec version 0.1.0
```

---

## 基本的な使い方

### 最もシンプルな使い方

```bash
xlsm2spec analyze ファイル名.xlsm
```

これだけで、ターミナルにMarkdown形式の仕様書が出力されます。

### ファイルに保存する

```bash
xlsm2spec analyze ファイル名.xlsm -o 仕様書.md
```

`-o` オプションで出力先ファイルを指定します。

### 使用例

```bash
# 1. 基本的な解析（標準出力）
xlsm2spec analyze 売上管理.xlsm

# 2. Markdown形式でファイル保存
xlsm2spec analyze 売上管理.xlsm -o 売上管理_仕様書.md

# 3. JSON形式で出力
xlsm2spec analyze 売上管理.xlsm -f json -o 売上管理_仕様書.json

# 4. HTML形式で出力（スタイル付き）
xlsm2spec analyze 売上管理.xlsm -f html -o 売上管理_仕様書.html

# 5. 詳細モード（解析状況を表示）
xlsm2spec analyze 売上管理.xlsm --verbose -o 仕様書.md
```

---

## 出力形式

### Markdown形式（デフォルト）

テキストエディタやGitHub/GitLabで閲覧しやすい形式です。

```bash
xlsm2spec analyze ファイル.xlsm -f markdown -o spec.md
```

**特徴:**
- シンプルで軽量
- バージョン管理との相性が良い
- 様々なツールで閲覧可能

### JSON形式

プログラムからの二次利用に適した構造化データ形式です。

```bash
xlsm2spec analyze ファイル.xlsm -f json -o spec.json
```

**特徴:**
- 機械可読
- 他のツールとの連携が容易
- データ分析に活用可能

### HTML形式

ブラウザで見やすいスタイル付きドキュメントです。

```bash
xlsm2spec analyze ファイル.xlsm -f html -o spec.html
```

**特徴:**
- 見やすいデザイン
- 目次・テーブル付き
- 印刷にも適している

---

## コマンドリファレンス

### analyze コマンド

ExcelファイルのVBAを解析し、仕様書を生成します。

```
xlsm2spec analyze [OPTIONS] INPUT_FILE
```

#### 引数

| 引数 | 必須 | 説明 |
|------|------|------|
| `INPUT_FILE` | ✅ | 解析するExcelファイルのパス |

#### オプション

| オプション | 短縮形 | 説明 | デフォルト |
|------------|--------|------|------------|
| `--output` | `-o` | 出力ファイルパス | 標準出力 |
| `--format` | `-f` | 出力形式 (markdown/json/html) | markdown |
| `--verbose` | なし | 詳細な解析情報を表示 | なし |
| `--help` | なし | ヘルプを表示 | - |

### その他のコマンド

```bash
# バージョン表示
xlsm2spec --version

# ヘルプ表示
xlsm2spec --help
xlsm2spec analyze --help
```

---

## 出力内容の解説

### 仕様書の構成

生成される仕様書は以下の構成になっています：

```
仕様書
├── 概要
│   ├── ファイル名
│   ├── シート数
│   ├── VBAモジュール数
│   └── VBA保護状態
├── シート一覧
└── VBAモジュール
    ├── モジュール情報
    │   ├── モジュール名
    │   ├── 種別
    │   └── 行数
    └── プロシージャ一覧
        ├── 名前
        ├── 種別（Sub/Function/Property）
        ├── アクセス修飾子
        ├── パラメータ
        ├── 戻り値型
        └── シグネチャ
```

### モジュール種別

| 種別 | 説明 |
|------|------|
| `standard` | 標準モジュール（.bas） |
| `class` | クラスモジュール（.cls） |
| `sheet` | シートモジュール |
| `thisworkbook` | ThisWorkbookモジュール |
| `form` | ユーザーフォーム（.frm） |

### プロシージャ種別

| 種別 | 説明 |
|------|------|
| `sub` | Subプロシージャ（戻り値なし） |
| `function` | Functionプロシージャ（戻り値あり） |
| `property_get` | プロパティ取得 |
| `property_let` | プロパティ設定（値型） |
| `property_set` | プロパティ設定（オブジェクト型） |

---

## トラブルシューティング

### よくあるエラーと対処法

#### ファイルが見つからない

```
エラー: ファイルが見つかりません: sample.xlsm
```

**対処法:**
- ファイルパスが正しいか確認してください
- ファイル名に日本語が含まれる場合は、パスを引用符で囲んでください

```bash
xlsm2spec analyze "日本語ファイル名.xlsm"
```

#### サポートされていない形式

```
エラー: サポートされていないファイル形式です: .txt
```

**対処法:**
- 対応形式（.xls, .xlsx, .xlsm）を確認してください
- xlsxファイルにはVBAが含まれません

#### VBAプロジェクトが保護されている

```
警告: VBAプロジェクトがパスワード保護されています
```

**対処法:**
- VBAプロジェクトのパスワード保護を解除してください
- Excelで「開発」タブ → VBAプロジェクトのプロパティ → 保護タブ

### パフォーマンスに関する注意

- 大きなファイル（10MB以上）は解析に時間がかかる場合があります
- `--verbose` オプションで進捗を確認できます

---

## FAQ

### Q: VBAがないExcelファイルも解析できますか？

**A:** はい、解析できます。ただし、VBAモジュール情報は空になります。シート一覧は取得できます。

### Q: マクロが含まれていない.xlsxファイルを解析するとどうなりますか？

**A:** シート一覧のみが出力されます。VBAモジュール数は0と表示されます。

### Q: 複数のファイルを一度に解析できますか？

**A:** 現在のバージョンでは1ファイルずつの解析になります。シェルスクリプトで複数ファイルを処理できます：

```bash
# Linux/macOS
for f in *.xlsm; do
  xlsm2spec analyze "$f" -o "${f%.xlsm}_spec.md"
done

# Windows PowerShell
Get-ChildItem *.xlsm | ForEach-Object {
  xlsm2spec analyze $_.Name -o ($_.BaseName + "_spec.md")
}
```

### Q: 日本語のVBAコメントは正しく処理されますか？

**A:** はい、UTF-8およびShift_JISエンコーディングに対応しています。

### Q: 生成された仕様書を編集してもいいですか？

**A:** もちろんです。生成された仕様書は自由に編集・カスタマイズしてください。

### Q: CI/CDパイプラインで使用できますか？

**A:** はい、コマンドラインツールなのでCI/CDに組み込めます。終了コードで成功/失敗を判定できます：

- `0`: 成功
- `1`: エラー
- `2`: 警告（VBA保護など）

---

## お問い合わせ・フィードバック

- GitHub Issues: [https://github.com/your-org/xlsm2spec/issues](https://github.com/your-org/xlsm2spec/issues)
- 機能リクエストや不具合報告をお待ちしています

---

**XLSM2Spec** - Excel VBAを見える化するツール

バージョン: 0.1.0
