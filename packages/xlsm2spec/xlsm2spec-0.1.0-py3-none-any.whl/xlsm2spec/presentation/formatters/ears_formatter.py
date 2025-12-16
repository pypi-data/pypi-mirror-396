"""EARS形式フォーマッター - VBAプロシージャを要件形式に変換"""

from xlsm2spec.domain.models import Module, ModuleType, Procedure, ProcedureType, Workbook


class EarsFormatter:
    """WorkbookをEARS（Easy Approach to Requirements Syntax）形式に変換する"""

    def format(self, workbook: Workbook) -> str:
        """
        ワークブック情報をEARS形式に変換する

        Args:
            workbook: 変換するワークブック

        Returns:
            str: EARS形式の要件仕様書
        """
        lines: list[str] = []

        # ヘッダー
        lines.append(f"# {workbook.filename} 要件仕様書（EARS形式）")
        lines.append("")
        lines.append("本ドキュメントは、VBAマクロから自動生成されたEARS形式の要件仕様書です。")
        lines.append("")

        # 概要
        lines.append("## 1. 概要")
        lines.append("")
        lines.append(f"- **対象ファイル**: {workbook.filename}")
        lines.append(f"- **シート数**: {len(workbook.sheets)}")

        if workbook.vba_project:
            lines.append(f"- **VBAモジュール数**: {len(workbook.vba_project.modules)}")
            total_procs = sum(len(m.procedures) for m in workbook.vba_project.modules)
            lines.append(f"- **プロシージャ数**: {total_procs}")
        lines.append("")

        # 要件ID採番用カウンター
        req_counter = 1

        # VBAモジュールごとの要件
        if workbook.vba_project and workbook.vba_project.modules:
            lines.append("## 2. 機能要件")
            lines.append("")

            for module in workbook.vba_project.modules:
                if module.procedures:
                    lines.append(f"### 2.{req_counter}. {module.name} モジュール")
                    lines.append("")
                    lines.append(f"**モジュール種別**: {self._get_module_type_ja(module.module_type)}")
                    lines.append("")

                    for proc in module.procedures:
                        req_id = f"REQ-{req_counter:03d}"
                        lines.extend(self._format_procedure_as_ears(proc, req_id, module))
                        req_counter += 1

        # 凡例
        lines.append("---")
        lines.append("")
        lines.append("## 付録: EARS形式パターン凡例")
        lines.append("")
        lines.append("| パターン | 構文 | 用途 |")
        lines.append("|----------|------|------|")
        lines.append("| ユビキタス | システムは〈動作〉する | 常に成り立つ要件 |")
        lines.append("| イベント駆動 | 〈トリガー〉のとき、システムは〈動作〉する | イベントに応じた要件 |")
        lines.append("| オプション | 〈条件〉の場合、システムは〈動作〉する | 条件付き要件 |")
        lines.append("| 状態駆動 | 〈状態〉の間、システムは〈動作〉する | 状態に基づく要件 |")
        lines.append("| 複合 | 〈トリガー〉のとき、〈条件〉の場合、システムは〈動作〉する | 複合条件 |")
        lines.append("")

        return "\n".join(lines)

    def _get_module_type_ja(self, module_type: ModuleType) -> str:
        """モジュール種別の日本語名を返す"""
        mapping = {
            ModuleType.STANDARD: "標準モジュール",
            ModuleType.CLASS: "クラスモジュール",
            ModuleType.SHEET: "シートモジュール",
            ModuleType.THISWORKBOOK: "ThisWorkbookモジュール",
            ModuleType.FORM: "ユーザーフォーム",
        }
        return mapping.get(module_type, module_type.value)

    def _format_procedure_as_ears(
        self, proc: Procedure, req_id: str, module: Module
    ) -> list[str]:
        """プロシージャをEARS形式の要件に変換する"""
        lines: list[str] = []

        # EARSパターンを判定
        ears_pattern = self._detect_ears_pattern(proc, module)

        lines.append(f"#### {req_id}: {proc.name}")
        lines.append("")
        lines.append(f"**パターン**: {ears_pattern}")
        lines.append("")

        # EARS形式の要件文を生成
        requirement = self._generate_ears_statement(proc, ears_pattern, module)
        lines.append(f"> {requirement}")
        lines.append("")

        # 詳細情報
        lines.append("**詳細:**")
        lines.append("")
        lines.append(f"- **種別**: {self._get_procedure_type_ja(proc.procedure_type)}")
        lines.append(f"- **アクセス**: {proc.access}")
        lines.append(f"- **位置**: 行 {proc.line_start} - {proc.line_end}")

        if proc.parameters:
            params_str = ", ".join(
                f"`{p.name}: {p.var_type or 'Variant'}`" for p in proc.parameters
            )
            lines.append(f"- **入力パラメータ**: {params_str}")

        if proc.return_type:
            lines.append(f"- **戻り値**: `{proc.return_type}`")

        lines.append("")
        lines.append("**シグネチャ:**")
        lines.append("")
        lines.append("```vba")
        lines.append(proc.signature)
        lines.append("```")
        lines.append("")

        return lines

    def _detect_ears_pattern(self, proc: Procedure, module: Module) -> str:
        """プロシージャからEARSパターンを推定する"""
        name_lower = proc.name.lower()

        # イベント駆動パターン（イベントハンドラー）
        event_keywords = [
            "click", "change", "open", "close", "activate", "deactivate",
            "beforeprint", "beforesave", "beforeclose", "selectionchange",
            "calculate", "doubleclick", "initialize", "terminate",
        ]
        for keyword in event_keywords:
            if keyword in name_lower:
                return "イベント駆動"

        # ThisWorkbookやSheetモジュールのプロシージャはイベント駆動の可能性
        if module.module_type in [ModuleType.THISWORKBOOK, ModuleType.SHEET]:
            if proc.access == "Private" and "_" in proc.name:
                return "イベント駆動"

        # オプションパターン（条件分岐を示唆する名前）
        optional_keywords = ["if", "check", "validate", "when", "optional"]
        for keyword in optional_keywords:
            if keyword in name_lower:
                return "オプション"

        # パラメータがある場合はオプションパターンの可能性
        if proc.parameters:
            return "オプション"

        # 状態駆動パターン（状態を示唆する名前）
        state_keywords = ["while", "during", "status", "state", "mode"]
        for keyword in state_keywords:
            if keyword in name_lower:
                return "状態駆動"

        # デフォルトはユビキタス
        return "ユビキタス"

    def _generate_ears_statement(
        self, proc: Procedure, pattern: str, module: Module
    ) -> str:
        """EARSパターンに基づいて要件文を生成する"""
        action = self._infer_action(proc)

        if pattern == "イベント駆動":
            trigger = self._infer_trigger(proc, module)
            return f"{trigger}とき、システムは{action}。"

        elif pattern == "オプション":
            condition = self._infer_condition(proc)
            return f"{condition}場合、システムは{action}。"

        elif pattern == "状態駆動":
            state = self._infer_state(proc)
            return f"{state}間、システムは{action}。"

        else:  # ユビキタス
            return f"システムは{action}機能を提供する。"

    def _infer_action(self, proc: Procedure) -> str:
        """プロシージャ名から動作を推定する"""
        name = proc.name

        # 一般的なプレフィックスから動作を推定
        action_mapping = {
            "Get": "データを取得する",
            "Set": "データを設定する",
            "Calc": "計算を実行する",
            "Calculate": "計算を実行する",
            "Make": "作成する",
            "Create": "作成する",
            "Delete": "削除する",
            "Del": "削除する",
            "Update": "更新する",
            "Init": "初期化する",
            "Initialize": "初期化する",
            "Save": "保存する",
            "Load": "読み込む",
            "Print": "印刷する",
            "Export": "エクスポートする",
            "Import": "インポートする",
            "Find": "検索する",
            "Search": "検索する",
            "Sort": "並び替える",
            "Filter": "フィルタリングする",
            "Validate": "検証する",
            "Check": "チェックする",
            "Convert": "変換する",
            "Conv": "変換する",
            "Format": "書式設定する",
            "Clear": "クリアする",
            "Reset": "リセットする",
            "Show": "表示する",
            "Hide": "非表示にする",
            "Open": "開く",
            "Close": "閉じる",
        }

        for prefix, action in action_mapping.items():
            if name.startswith(prefix):
                return action

        # Functionの場合は値を返す動作
        if proc.procedure_type == ProcedureType.FUNCTION:
            if proc.return_type:
                return f"{proc.return_type}型の値を算出する"
            return "値を算出する"

        # デフォルト
        return f"{name}処理を実行する"

    def _infer_trigger(self, proc: Procedure, module: Module) -> str:
        """イベントトリガーを推定する"""
        name_lower = proc.name.lower()

        trigger_mapping = {
            "workbook_open": "ワークブックが開かれた",
            "workbook_close": "ワークブックが閉じられた",
            "workbook_activate": "ワークブックがアクティブになった",
            "workbook_beforesave": "ワークブックが保存される前の",
            "workbook_beforeclose": "ワークブックが閉じられる前の",
            "worksheet_change": "セルの値が変更された",
            "worksheet_activate": "シートがアクティブになった",
            "worksheet_selectionchange": "セルの選択が変更された",
            "worksheet_calculate": "シートが再計算された",
            "click": "ボタンがクリックされた",
            "dblclick": "ダブルクリックされた",
            "initialize": "オブジェクトが初期化された",
            "terminate": "オブジェクトが終了した",
        }

        for pattern, trigger in trigger_mapping.items():
            if pattern in name_lower:
                return trigger

        return "イベントが発生した"

    def _infer_condition(self, proc: Procedure) -> str:
        """条件を推定する"""
        if proc.parameters:
            param_desc = ", ".join(p.name for p in proc.parameters)
            return f"ユーザーが{param_desc}を指定した"

        return "特定の条件を満たした"

    def _infer_state(self, proc: Procedure) -> str:
        """状態を推定する"""
        name_lower = proc.name.lower()

        if "while" in name_lower:
            return "処理が継続している"
        if "during" in name_lower:
            return "処理中の"

        return "特定の状態にある"

    def _get_procedure_type_ja(self, proc_type: ProcedureType) -> str:
        """プロシージャ種別の日本語名を返す"""
        mapping = {
            ProcedureType.SUB: "Subプロシージャ",
            ProcedureType.FUNCTION: "Functionプロシージャ",
            ProcedureType.PROPERTY_GET: "Property Get",
            ProcedureType.PROPERTY_LET: "Property Let",
            ProcedureType.PROPERTY_SET: "Property Set",
        }
        return mapping.get(proc_type, proc_type.value)
