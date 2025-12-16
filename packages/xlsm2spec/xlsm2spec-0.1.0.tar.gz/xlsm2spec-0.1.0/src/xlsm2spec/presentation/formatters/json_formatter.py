"""JSON形式フォーマッター"""

import json
from typing import Any

from xlsm2spec.domain.models import Module, Procedure, Variable, Workbook


class JsonFormatter:
    """Workbookを構造化されたJSONに変換する"""

    def __init__(self, indent: int = 2):
        """
        Args:
            indent: JSONインデント幅（デフォルト: 2）
        """
        self.indent = indent

    def format(self, workbook: Workbook) -> str:
        """
        ワークブック情報をJSON形式に変換する

        Args:
            workbook: 変換するワークブック

        Returns:
            str: JSON形式の仕様書
        """
        data = self._workbook_to_dict(workbook)
        return json.dumps(data, indent=self.indent, ensure_ascii=False)

    def _workbook_to_dict(self, workbook: Workbook) -> dict[str, Any]:
        """WorkbookをdictにVariabless変換する"""
        result: dict[str, Any] = {
            "filename": workbook.filename,
            "sheets": workbook.sheets,
            "vba_project": None,
        }

        if workbook.vba_project:
            result["vba_project"] = {
                "is_protected": workbook.vba_project.is_protected,
                "modules": [
                    self._module_to_dict(m) for m in workbook.vba_project.modules
                ],
            }

        return result

    def _module_to_dict(self, module: Module) -> dict[str, Any]:
        """Moduleをdictに変換する"""
        return {
            "name": module.name,
            "module_type": module.module_type.value,
            "line_count": module.line_count,
            "procedures": [self._procedure_to_dict(p) for p in module.procedures],
            "variables": [self._variable_to_dict(v) for v in module.variables],
        }

    def _procedure_to_dict(self, proc: Procedure) -> dict[str, Any]:
        """Procedureをdictに変換する"""
        return {
            "name": proc.name,
            "procedure_type": proc.procedure_type.value,
            "access": proc.access,
            "parameters": [self._variable_to_dict(p) for p in proc.parameters],
            "return_type": proc.return_type,
            "signature": proc.signature,
            "line_start": proc.line_start,
            "line_end": proc.line_end,
            "line_count": proc.line_count,
        }

    def _variable_to_dict(self, var: Variable) -> dict[str, Any]:
        """Variableをdictに変換する"""
        return {
            "name": var.name,
            "var_type": var.var_type,
            "is_array": var.is_array,
        }
