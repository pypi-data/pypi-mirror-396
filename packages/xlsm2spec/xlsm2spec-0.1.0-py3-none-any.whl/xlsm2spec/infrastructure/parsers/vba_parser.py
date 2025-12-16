"""VBA構文解析パーサー - 正規表現ベース"""

import re

from xlsm2spec.domain.models import Procedure, ProcedureType, Variable


class VbaParser:
    """VBAソースコードを解析し、プロシージャ情報を抽出する"""

    # プロシージャ宣言のパターン
    PROCEDURE_PATTERN = re.compile(
        r"^\s*(?P<access>Public|Private)?\s*"
        r"(?P<type>Sub|Function|Property\s+Get|Property\s+Let|Property\s+Set)\s+"
        r"(?P<name>\w+)\s*"
        r"\((?P<params>[^)]*)\)"
        r"(?:\s+As\s+(?P<return>\w+))?",
        re.IGNORECASE | re.MULTILINE,
    )

    # プロシージャ終了のパターン
    END_PATTERNS = {
        "sub": re.compile(r"^\s*End\s+Sub\s*$", re.IGNORECASE),
        "function": re.compile(r"^\s*End\s+Function\s*$", re.IGNORECASE),
        "property": re.compile(r"^\s*End\s+Property\s*$", re.IGNORECASE),
    }

    def parse(self, source_code: str) -> list[Procedure]:
        """
        VBAソースコードを解析し、プロシージャ一覧を返す

        Args:
            source_code: VBAソースコード

        Returns:
            list[Procedure]: プロシージャ一覧
        """
        procedures: list[Procedure] = []
        lines = source_code.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]
            match = self.PROCEDURE_PATTERN.match(line)

            if match:
                procedure = self._parse_procedure(match, lines, i)
                if procedure:
                    procedures.append(procedure)
                    # プロシージャの終了行までスキップ
                    i = procedure.line_end
            i += 1

        return procedures

    def _parse_procedure(
        self, match: re.Match[str], lines: list[str], start_line: int
    ) -> Procedure | None:
        """プロシージャ情報を解析する"""
        proc_type_str = match.group("type").lower()
        proc_type = self._get_procedure_type(proc_type_str)

        if proc_type is None:
            return None

        access = match.group("access") or "Public"
        name = match.group("name")
        params_str = match.group("params") or ""
        return_type = match.group("return")

        # 終了位置を検索
        end_line = self._find_end_line(lines, start_line, proc_type_str)

        # ソースコードを抽出
        source_lines = lines[start_line : end_line + 1]
        source_code = "\n".join(source_lines)

        return Procedure(
            name=name,
            procedure_type=proc_type,
            access=access,
            parameters=self._parse_parameters(params_str),
            return_type=return_type,
            source_code=source_code,
            line_start=start_line + 1,  # 1-indexed
            line_end=end_line + 1,  # 1-indexed
        )

    def _get_procedure_type(self, type_str: str) -> ProcedureType | None:
        """プロシージャ種別を取得する"""
        type_lower = type_str.lower().strip()

        if type_lower == "sub":
            return ProcedureType.SUB
        elif type_lower == "function":
            return ProcedureType.FUNCTION
        elif "property" in type_lower and "get" in type_lower:
            return ProcedureType.PROPERTY_GET
        elif "property" in type_lower and "let" in type_lower:
            return ProcedureType.PROPERTY_LET
        elif "property" in type_lower and "set" in type_lower:
            return ProcedureType.PROPERTY_SET
        return None

    def _find_end_line(
        self, lines: list[str], start_line: int, proc_type: str
    ) -> int:
        """プロシージャの終了行を検索する"""
        # プロシージャ種別に応じた終了パターン
        if "property" in proc_type:
            end_pattern = self.END_PATTERNS["property"]
        elif proc_type == "function":
            end_pattern = self.END_PATTERNS["function"]
        else:
            end_pattern = self.END_PATTERNS["sub"]

        for i in range(start_line + 1, len(lines)):
            if end_pattern.match(lines[i]):
                return i

        # 終了が見つからない場合は開始行を返す
        return start_line

    def _parse_parameters(self, params_str: str) -> list[Variable]:
        """パラメータ文字列を解析する"""
        if not params_str.strip():
            return []

        params: list[Variable] = []

        # カンマで分割（ただし括弧内のカンマは無視）
        param_parts = self._split_parameters(params_str)

        for param in param_parts:
            param = param.strip()
            if not param:
                continue

            variable = self._parse_single_parameter(param)
            if variable:
                params.append(variable)

        return params

    def _split_parameters(self, params_str: str) -> list[str]:
        """パラメータをカンマで分割する（括弧を考慮）"""
        result: list[str] = []
        current = ""
        paren_depth = 0

        for char in params_str:
            if char == "(":
                paren_depth += 1
                current += char
            elif char == ")":
                paren_depth -= 1
                current += char
            elif char == "," and paren_depth == 0:
                result.append(current)
                current = ""
            else:
                current += char

        if current:
            result.append(current)

        return result

    def _parse_single_parameter(self, param: str) -> Variable | None:
        """単一のパラメータを解析する"""
        # ByVal/ByRef, Optional, ParamArray を除去
        param = re.sub(
            r"\b(ByVal|ByRef|Optional|ParamArray)\b", "", param, flags=re.IGNORECASE
        ).strip()

        # "name As Type" または "name() As Type" をパース
        is_array = "()" in param
        param = param.replace("()", "")

        parts = re.split(r"\s+As\s+", param, maxsplit=1, flags=re.IGNORECASE)

        name = parts[0].strip()
        var_type = parts[1].strip() if len(parts) > 1 else None

        if not name:
            return None

        return Variable(name=name, var_type=var_type, is_array=is_array)
