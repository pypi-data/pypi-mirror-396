"""Markdown形式フォーマッター"""

from xlsm2spec.domain.models import Module, Procedure, Workbook


class MarkdownFormatter:
    """Workbookを仕様書形式のMarkdownに変換する"""

    def format(self, workbook: Workbook) -> str:
        """
        ワークブック情報をMarkdown形式に変換する

        Args:
            workbook: 変換するワークブック

        Returns:
            str: Markdown形式の仕様書
        """
        lines: list[str] = []

        # タイトル
        lines.append(f"# {workbook.filename} 仕様書")
        lines.append("")
        lines.append("## 概要")
        lines.append("")
        lines.append(f"- **ファイル名**: {workbook.filename}")
        lines.append(f"- **シート数**: {len(workbook.sheets)}")

        if workbook.vba_project:
            lines.append(f"- **VBAモジュール数**: {len(workbook.vba_project.modules)}")
            lines.append(f"- **VBA保護**: {'あり' if workbook.vba_project.is_protected else 'なし'}")
        else:
            lines.append("- **VBAモジュール数**: 0")
        lines.append("")

        # シート一覧
        if workbook.sheets:
            lines.append("## シート一覧")
            lines.append("")
            for i, sheet in enumerate(workbook.sheets, 1):
                lines.append(f"{i}. {sheet}")
            lines.append("")

        # VBAモジュール
        if workbook.vba_project and workbook.vba_project.modules:
            lines.append("## VBAモジュール")
            lines.append("")

            for module in workbook.vba_project.modules:
                lines.extend(self._format_module(module))

        return "\n".join(lines)

    def _format_module(self, module: Module) -> list[str]:
        """モジュールをフォーマットする"""
        lines: list[str] = []

        lines.append(f"### {module.name} ({module.module_type.value})")
        lines.append("")
        lines.append(f"- **行数**: {module.line_count}")
        lines.append(f"- **プロシージャ数**: {len(module.procedures)}")
        lines.append("")

        if module.procedures:
            lines.append("#### プロシージャ一覧")
            lines.append("")
            lines.append("| 名前 | 種別 | アクセス | 戻り値 | 行数 |")
            lines.append("|------|------|----------|--------|------|")

            for proc in module.procedures:
                return_type = proc.return_type or "-"
                lines.append(
                    f"| {proc.name} | {proc.procedure_type.value} | "
                    f"{proc.access} | {return_type} | {proc.line_count} |"
                )
            lines.append("")

            # 各プロシージャの詳細
            for proc in module.procedures:
                lines.extend(self._format_procedure(proc))

        return lines

    def _format_procedure(self, proc: Procedure) -> list[str]:
        """プロシージャの詳細をフォーマットする"""
        lines: list[str] = []

        lines.append(f"##### {proc.name}")
        lines.append("")
        lines.append(f"- **種別**: {proc.procedure_type.value}")
        lines.append(f"- **アクセス修飾子**: {proc.access}")
        lines.append(f"- **位置**: 行 {proc.line_start} - {proc.line_end}")

        if proc.return_type:
            lines.append(f"- **戻り値型**: {proc.return_type}")
        lines.append("")

        # パラメータ
        if proc.parameters:
            lines.append("**パラメータ:**")
            lines.append("")
            for param in proc.parameters:
                param_type = param.var_type or "Variant"
                array_mark = "[]" if param.is_array else ""
                lines.append(f"- `{param.name}`: {param_type}{array_mark}")
            lines.append("")

        # シグネチャ
        lines.append("**シグネチャ:**")
        lines.append("")
        lines.append("```vba")
        lines.append(proc.signature)
        lines.append("```")
        lines.append("")

        return lines
