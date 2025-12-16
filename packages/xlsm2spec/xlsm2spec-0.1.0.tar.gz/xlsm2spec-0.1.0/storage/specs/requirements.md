# Excel2Spec 要件定義書

**Version**: 1.0
**Last Updated**: 2025-12-12
**Status**: Draft
**Format**: EARS (Easy Approach to Requirements Syntax)

---

## 概要

本ドキュメントは、Excel2Specの機能要件をEARS形式で定義します。
すべての要件は以下の5パターンのいずれかを使用します：

1. **Event-driven**: `WHEN [event], the [system] SHALL [response]`
2. **State-driven**: `WHILE [state], the [system] SHALL [response]`
3. **Unwanted behavior**: `IF [error], THEN the [system] SHALL [response]`
4. **Optional features**: `WHERE [feature enabled], the [system] SHALL [response]`
5. **Ubiquitous**: `The [system] SHALL [requirement]`

---

## FR: 機能要件 (Functional Requirements)

### FR-100: Excelファイル読み込み

#### FR-101: xlsファイル読み込み
**Type**: Event-driven

**Requirement**:
> WHEN ユーザーがxls形式（BIFF8）のExcelファイルを指定した時、
> システムはファイルを読み込み、ワークブック構造を解析するものとする。

**Acceptance Criteria**:
- [ ] xls形式（Excel 97-2003）のファイルを読み込める
- [ ] シート名一覧を取得できる
- [ ] 各シートのセルデータにアクセスできる
- [ ] 読み込み完了時にワークブックオブジェクトを返す

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-ExcelReader, Test: test_xls_reader.py

---

#### FR-102: xlsmファイル読み込み
**Type**: Event-driven

**Requirement**:
> WHEN ユーザーがxlsm形式（マクロ有効ブック）のExcelファイルを指定した時、
> システムはファイルを読み込み、ワークブック構造とVBAプロジェクトを解析するものとする。

**Acceptance Criteria**:
- [ ] xlsm形式（Excel 2007+マクロ有効）のファイルを読み込める
- [ ] シート名一覧を取得できる
- [ ] VBAプロジェクトの存在を検出できる
- [ ] vbaProject.binを抽出できる

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-ExcelReader, Test: test_xlsm_reader.py

---

#### FR-103: xlsxファイル読み込み
**Type**: Event-driven

**Requirement**:
> WHEN ユーザーがxlsx形式のExcelファイルを指定した時、
> システムはファイルを読み込み、ワークブック構造を解析するものとする（VBAなし）。

**Acceptance Criteria**:
- [ ] xlsx形式のファイルを読み込める
- [ ] シート名一覧を取得できる
- [ ] VBAが存在しないことを正しく報告する

**Priority**: P1
**Trace**: → Design: C4-Component-ExcelReader, Test: test_xlsx_reader.py

---

### FR-200: VBAコード抽出

#### FR-201: VBAプロジェクト抽出
**Type**: Event-driven

**Requirement**:
> WHEN Excelファイルの読み込みが完了した時、
> システムはVBAプロジェクトを検出し、すべてのVBAモジュールのソースコードを抽出するものとする。

**Acceptance Criteria**:
- [ ] 標準モジュール（.bas）を抽出できる
- [ ] クラスモジュール（.cls）を抽出できる
- [ ] フォームモジュール（.frm）を抽出できる
- [ ] ThisWorkbook、Sheetモジュールを抽出できる
- [ ] 各モジュールのソースコードを文字列として取得できる

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-VbaExtractor, Test: test_vba_extractor.py

---

#### FR-202: パスワード保護VBAの検出
**Type**: Unwanted behavior

**Requirement**:
> IF VBAプロジェクトがパスワードで保護されている場合、
> THEN システムは警告メッセージを出力し、VBA抽出をスキップするものとする。

**Acceptance Criteria**:
- [ ] パスワード保護を検出できる
- [ ] 警告メッセージを出力する
- [ ] 処理を中断せず、利用可能な情報で続行する
- [ ] 最終レポートに「VBA保護あり」を記載する

**Priority**: P0 (MVP)
**Trace**: → Design: ADR-002-PasswordProtection, Test: test_vba_protected.py

---

### FR-300: 静的コード解析

#### FR-301: モジュール構造解析
**Type**: Event-driven

**Requirement**:
> WHEN VBAソースコードが抽出された時、
> システムはすべてのモジュール、プロシージャ（Sub/Function）、プロパティを識別するものとする。

**Acceptance Criteria**:
- [ ] モジュール名を識別できる
- [ ] Sub プロシージャを識別できる
- [ ] Function プロシージャを識別できる
- [ ] Property Get/Let/Set を識別できる
- [ ] 各プロシージャの引数と戻り値の型を取得できる
- [ ] Public/Private のアクセス修飾子を識別できる

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-VbaParser, Test: test_vba_parser_structure.py

---

#### FR-302: 変数・定数解析
**Type**: Event-driven

**Requirement**:
> WHEN プロシージャの解析が行われた時、
> システムはすべてのローカル変数、モジュールレベル変数、定数を識別するものとする。

**Acceptance Criteria**:
- [ ] Dim/Private/Public で宣言された変数を識別できる
- [ ] Const で宣言された定数を識別できる
- [ ] 変数の型（As 句）を取得できる
- [ ] 配列変数を識別できる
- [ ] グローバル変数とローカル変数を区別できる

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-VbaParser, Test: test_vba_parser_variables.py

---

#### FR-303: セル参照解析
**Type**: Event-driven

**Requirement**:
> WHEN VBAコードの解析が行われた時、
> システムはすべてのセル参照（Range, Cells, ActiveCell等）を識別するものとする。

**Acceptance Criteria**:
- [ ] Range("A1") 形式の参照を識別できる
- [ ] Cells(1, 1) 形式の参照を識別できる
- [ ] ActiveCell 参照を識別できる
- [ ] Worksheets("Sheet1").Range(...) 形式を識別できる
- [ ] 名前付き範囲参照を識別できる
- [ ] 参照がRead/Writeどちらかを判定できる

**Priority**: P1
**Trace**: → Design: C4-Component-CellReferenceTracker, Test: test_cell_references.py

---

#### FR-304: 制御フロー解析
**Type**: Event-driven

**Requirement**:
> WHEN プロシージャの解析が行われた時、
> システムは制御フロー構造（If/For/Do/Select Case/While）を識別し、ネスト構造を把握するものとする。

**Acceptance Criteria**:
- [ ] If...Then...Else...End If を識別できる
- [ ] For...Next ループを識別できる
- [ ] For Each...Next ループを識別できる
- [ ] Do...Loop を識別できる
- [ ] While...Wend を識別できる
- [ ] Select Case を識別できる
- [ ] ネストレベルを追跡できる
- [ ] Exit Sub/Function/For/Do を識別できる

**Priority**: P1
**Trace**: → Design: C4-Component-ControlFlowAnalyzer, Test: test_control_flow.py

---

#### FR-305: 関数呼び出し解析
**Type**: Event-driven

**Requirement**:
> WHEN プロシージャの解析が行われた時、
> システムはすべての関数・サブプロシージャ呼び出しを識別し、呼び出しグラフを構築するものとする。

**Acceptance Criteria**:
- [ ] 同一モジュール内の呼び出しを識別できる
- [ ] 他モジュールへの呼び出しを識別できる
- [ ] VBA組み込み関数の呼び出しを識別できる
- [ ] 外部ライブラリ（参照設定）の呼び出しを識別できる
- [ ] 呼び出しグラフをデータ構造として出力できる

**Priority**: P1
**Trace**: → Design: C4-Component-CallGraphBuilder, Test: test_call_graph.py

---

### FR-400: 仕様書生成

#### FR-401: Markdown仕様書出力
**Type**: Event-driven

**Requirement**:
> WHEN 静的解析が完了した時、
> システムは解析結果をMarkdown形式の仕様書として出力するものとする。

**Acceptance Criteria**:
- [ ] 有効なMarkdown形式で出力される
- [ ] ファイル概要セクションを含む
- [ ] モジュール一覧セクションを含む
- [ ] 各プロシージャの詳細セクションを含む
- [ ] 出力ファイルパスを指定できる
- [ ] UTF-8エンコーディングで出力される

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-MarkdownGenerator, Test: test_markdown_output.py

---

#### FR-402: モジュール一覧出力
**Type**: State-driven

**Requirement**:
> WHILE 仕様書を生成している間、
> システムはすべてのVBAモジュールを一覧表形式で出力するものとする。

**Acceptance Criteria**:
- [ ] モジュール名を含む
- [ ] モジュール種別（標準/クラス/フォーム/シート）を含む
- [ ] プロシージャ数を含む
- [ ] 行数を含む

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-MarkdownGenerator, Test: test_module_list.py

---

#### FR-403: プロシージャ詳細出力
**Type**: State-driven

**Requirement**:
> WHILE 仕様書を生成している間、
> システムは各プロシージャの詳細情報（名前、引数、戻り値、処理概要）を出力するものとする。

**Acceptance Criteria**:
- [ ] プロシージャ名を含む
- [ ] 引数一覧（名前、型）を含む
- [ ] 戻り値の型を含む（Functionの場合）
- [ ] アクセス修飾子（Public/Private）を含む
- [ ] コード行数を含む
- [ ] 呼び出している他のプロシージャを含む

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-MarkdownGenerator, Test: test_procedure_details.py

---

#### FR-404: 処理フロー図出力
**Type**: Optional feature

**Requirement**:
> WHERE フロー図生成オプションが有効な場合、
> システムは各プロシージャの処理フローをMermaid形式のフローチャートとして出力するものとする。

**Acceptance Criteria**:
- [ ] 有効なMermaid構文で出力される
- [ ] 条件分岐を表現できる
- [ ] ループを表現できる
- [ ] 関数呼び出しを表現できる

**Priority**: P2
**Trace**: → Design: C4-Component-FlowchartGenerator, Test: test_flowchart.py

---

### FR-500: CLIインターフェース

#### FR-501: 基本コマンド
**Type**: Ubiquitous

**Requirement**:
> システムは `excel2spec` コマンドでCLIとして実行可能であるものとする。

**Acceptance Criteria**:
- [ ] `excel2spec <input_file>` で実行できる
- [ ] `excel2spec --help` でヘルプを表示できる
- [ ] `excel2spec --version` でバージョンを表示できる
- [ ] 成功時は終了コード0を返す
- [ ] エラー時は非ゼロの終了コードを返す

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-CLI, Test: test_cli_basic.py

---

#### FR-502: 出力オプション
**Type**: Event-driven

**Requirement**:
> WHEN ユーザーが `--output` オプションを指定した時、
> システムは指定されたパスに仕様書を出力するものとする。

**Acceptance Criteria**:
- [ ] `--output <path>` で出力先を指定できる
- [ ] `-o <path>` 短縮形が使用できる
- [ ] 指定なし時はデフォルトの出力先に出力する
- [ ] 出力先ディレクトリが存在しない場合は作成する

**Priority**: P0 (MVP)
**Trace**: → Design: C4-Component-CLI, Test: test_cli_output.py

---

#### FR-503: 詳細度オプション
**Type**: Optional feature

**Requirement**:
> WHERE ユーザーが `--verbose` オプションを指定した場合、
> システムは処理の詳細なログを出力するものとする。

**Acceptance Criteria**:
- [ ] `--verbose` または `-v` で詳細ログを有効化できる
- [ ] 読み込み進捗を表示する
- [ ] 解析進捗を表示する
- [ ] 出力進捗を表示する

**Priority**: P1
**Trace**: → Design: C4-Component-CLI, Test: test_cli_verbose.py

---

#### FR-504: フォーマット選択
**Type**: Event-driven

**Requirement**:
> WHEN ユーザーが `--format` オプションを指定した時、
> システムは指定された形式で仕様書を出力するものとする。

**Acceptance Criteria**:
- [ ] `--format markdown` （デフォルト）をサポートする
- [ ] `--format json` をサポートする
- [ ] `--format html` をサポートする（P2）
- [ ] 不正なフォーマット指定時はエラーメッセージを出力する

**Priority**: P1
**Trace**: → Design: C4-Component-OutputFormatter, Test: test_output_formats.py

---

### FR-600: バッチ処理

#### FR-601: 複数ファイル処理
**Type**: Event-driven

**Requirement**:
> WHEN ユーザーがディレクトリパスを指定した時、
> システムはディレクトリ内のすべてのExcelファイルを処理するものとする。

**Acceptance Criteria**:
- [ ] ディレクトリを入力として受け付ける
- [ ] xls, xlsx, xlsm ファイルを自動検出する
- [ ] 各ファイルを順次処理する
- [ ] 処理進捗を表示する
- [ ] 個別のエラーで処理全体が中断しない

**Priority**: P1
**Trace**: → Design: C4-Component-BatchProcessor, Test: test_batch_processing.py

---

#### FR-602: 統合レポート
**Type**: Optional feature

**Requirement**:
> WHERE バッチ処理が実行された場合、
> システムは処理したすべてのファイルの統合レポートを生成するものとする。

**Acceptance Criteria**:
- [ ] 処理ファイル一覧を含む
- [ ] 各ファイルのモジュール数・プロシージャ数を含む
- [ ] 総合統計（合計行数等）を含む
- [ ] 個別仕様書へのリンクを含む

**Priority**: P2
**Trace**: → Design: C4-Component-ReportAggregator, Test: test_aggregate_report.py

---

## NFR: 非機能要件 (Non-Functional Requirements)

### NFR-001: パフォーマンス
**Type**: Ubiquitous

**Requirement**:
> システムは、1000行のVBAコードを含むExcelファイルを5分以内に処理できるものとする。

**Acceptance Criteria**:
- [ ] 処理時間 < 5分（1000行VBA）
- [ ] メモリ使用量 < 500MB
- [ ] 10,000行VBAでも処理可能

**Priority**: P1
**Trace**: → Test: test_performance.py

---

### NFR-002: クロスプラットフォーム
**Type**: Ubiquitous

**Requirement**:
> システムは、Windows、macOS、Linuxで動作するものとする。

**Acceptance Criteria**:
- [ ] Windows 10/11 で動作する
- [ ] macOS 12+ で動作する
- [ ] Ubuntu 20.04+ で動作する
- [ ] 同一の実行可能ファイル/スクリプトで動作する

**Priority**: P0 (MVP)
**Trace**: → Test: CI matrix tests

---

### NFR-003: エラーハンドリング
**Type**: Ubiquitous

**Requirement**:
> システムは、すべてのエラーに対して明確なエラーメッセージを表示するものとする。

**Acceptance Criteria**:
- [ ] ファイルが見つからない場合のエラーメッセージ
- [ ] ファイル形式が不正な場合のエラーメッセージ
- [ ] VBA抽出失敗時のエラーメッセージ
- [ ] 出力先書き込み不可時のエラーメッセージ
- [ ] エラーメッセージは日本語で表示される

**Priority**: P0 (MVP)
**Trace**: → Test: test_error_handling.py

---

### NFR-004: 文字エンコーディング
**Type**: Ubiquitous

**Requirement**:
> システムは、日本語を含むVBAコードとExcelファイルを正しく処理するものとする。

**Acceptance Criteria**:
- [ ] Shift_JIS エンコードの xls ファイルを処理できる
- [ ] UTF-8 エンコードの xlsm ファイルを処理できる
- [ ] 日本語変数名を正しく解析できる
- [ ] 日本語コメントを正しく抽出できる
- [ ] 出力は UTF-8 で行う

**Priority**: P0 (MVP)
**Trace**: → Test: test_japanese_encoding.py

---

## トレーサビリティマトリクス

| Requirement ID | Design Component | Test File | Status |
|---------------|------------------|-----------|--------|
| FR-101 | ExcelReader | test_xls_reader.py | 未実装 |
| FR-102 | ExcelReader | test_xlsm_reader.py | 未実装 |
| FR-103 | ExcelReader | test_xlsx_reader.py | 未実装 |
| FR-201 | VbaExtractor | test_vba_extractor.py | 未実装 |
| FR-202 | VbaExtractor | test_vba_protected.py | 未実装 |
| FR-301 | VbaParser | test_vba_parser_structure.py | 未実装 |
| FR-302 | VbaParser | test_vba_parser_variables.py | 未実装 |
| FR-303 | CellReferenceTracker | test_cell_references.py | 未実装 |
| FR-304 | ControlFlowAnalyzer | test_control_flow.py | 未実装 |
| FR-305 | CallGraphBuilder | test_call_graph.py | 未実装 |
| FR-401 | MarkdownGenerator | test_markdown_output.py | 未実装 |
| FR-402 | MarkdownGenerator | test_module_list.py | 未実装 |
| FR-403 | MarkdownGenerator | test_procedure_details.py | 未実装 |
| FR-404 | FlowchartGenerator | test_flowchart.py | 未実装 |
| FR-501 | CLI | test_cli_basic.py | 未実装 |
| FR-502 | CLI | test_cli_output.py | 未実装 |
| FR-503 | CLI | test_cli_verbose.py | 未実装 |
| FR-504 | OutputFormatter | test_output_formats.py | 未実装 |
| FR-601 | BatchProcessor | test_batch_processing.py | 未実装 |
| FR-602 | ReportAggregator | test_aggregate_report.py | 未実装 |

---

**Last Updated**: 2025-12-12
**Author**: MUSUBI SDD Workflow
