"""VBA抽出アダプター - oletoolsを使用"""

from oletools.olevba import VBA_Parser

from xlsm2spec.domain.exceptions import VbaExtractionError, VbaProtectedError
from xlsm2spec.domain.models import Module, ModuleType, VbaProject


class VbaExtractor:
    """ExcelファイルからVBAコードを抽出する"""

    def extract(self, filepath: str) -> VbaProject:
        """
        ExcelファイルからVBAプロジェクトを抽出する

        Args:
            filepath: Excelファイルのパス

        Returns:
            VbaProject: 抽出したVBAプロジェクト

        Raises:
            VbaExtractionError: VBA抽出に失敗した場合
            VbaProtectedError: VBAプロジェクトがパスワード保護されている場合
        """
        try:
            vba_parser = VBA_Parser(filepath)

            # VBAが含まれているかチェック
            if not vba_parser.detect_vba_macros():
                vba_parser.close()
                return VbaProject(modules=[], is_protected=False)

            modules: list[Module] = []

            for (
                _filename,
                _stream_path,
                vba_filename,
                vba_code,
            ) in vba_parser.extract_macros():
                if vba_code:
                    module_type = self._detect_module_type(vba_filename)
                    module = Module(
                        name=self._clean_module_name(vba_filename),
                        module_type=module_type,
                        source_code=vba_code,
                        procedures=[],
                        variables=[],
                    )
                    modules.append(module)

            vba_parser.close()
            return VbaProject(modules=modules, is_protected=False)

        except Exception as e:
            error_msg = str(e).lower()
            if "password" in error_msg or "protected" in error_msg:
                raise VbaProtectedError(filepath) from e
            raise VbaExtractionError(filepath, str(e)) from e

    def _detect_module_type(self, name: str) -> ModuleType:
        """モジュール名から種別を判定する"""
        name_lower = name.lower()

        if name_lower == "thisworkbook":
            return ModuleType.THISWORKBOOK
        elif name_lower.startswith("sheet"):
            return ModuleType.SHEET
        elif name.endswith(".cls"):
            return ModuleType.CLASS
        elif name.endswith(".frm"):
            return ModuleType.FORM
        else:
            return ModuleType.STANDARD

    def _clean_module_name(self, name: str) -> str:
        """モジュール名をクリーンアップする"""
        # 拡張子を除去
        for ext in [".bas", ".cls", ".frm"]:
            if name.endswith(ext):
                return name[: -len(ext)]
        return name
