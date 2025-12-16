"""E2Eテスト - 実際のExcelファイルを使用した統合テスト"""

import json
from pathlib import Path

import pytest

from xlsm2spec.application.analyzer import AnalyzerService
from xlsm2spec.presentation.formatters.json_formatter import JsonFormatter
from xlsm2spec.presentation.formatters.markdown_formatter import MarkdownFormatter


SAMPLE_FILE = Path(__file__).parent.parent / "Samples" / "保健室利用データ_マクロ実行前 1.xlsm"


@pytest.mark.skipif(not SAMPLE_FILE.exists(), reason="Sample file not available")
class TestE2E:
    """E2Eテスト"""

    @pytest.fixture
    def analyzer(self) -> AnalyzerService:
        return AnalyzerService()

    def test_analyze_sample_file(self, analyzer: AnalyzerService) -> None:
        """サンプルファイルの分析が成功すること"""
        workbook = analyzer.analyze(str(SAMPLE_FILE))

        assert workbook.filename == "保健室利用データ_マクロ実行前 1.xlsm"
        assert len(workbook.sheets) == 20
        assert workbook.vba_project is not None
        assert len(workbook.vba_project.modules) == 23

    def test_analyze_extracts_procedures(self, analyzer: AnalyzerService) -> None:
        """プロシージャが正しく抽出されること"""
        workbook = analyzer.analyze(str(SAMPLE_FILE))

        assert workbook.vba_project is not None

        # Calcモジュールのプロシージャを確認
        calc_module = next(
            (m for m in workbook.vba_project.modules if m.name == "Calc"), None
        )
        assert calc_module is not None
        assert len(calc_module.procedures) == 9

        # CalcCount プロシージャを確認
        calc_count = next(
            (p for p in calc_module.procedures if p.name == "CalcCount"), None
        )
        assert calc_count is not None
        assert calc_count.access == "Public"

    def test_markdown_output(self, analyzer: AnalyzerService) -> None:
        """Markdown出力が正しく生成されること"""
        workbook = analyzer.analyze(str(SAMPLE_FILE))
        formatter = MarkdownFormatter()
        result = formatter.format(workbook)

        assert "# 保健室利用データ_マクロ実行前 1.xlsm 仕様書" in result
        assert "## 概要" in result
        assert "## シート一覧" in result
        assert "## VBAモジュール" in result
        assert "CalcCount" in result

    def test_json_output(self, analyzer: AnalyzerService) -> None:
        """JSON出力が正しく生成されること"""
        workbook = analyzer.analyze(str(SAMPLE_FILE))
        formatter = JsonFormatter()
        result = formatter.format(workbook)

        data = json.loads(result)
        assert data["filename"] == "保健室利用データ_マクロ実行前 1.xlsm"
        assert len(data["sheets"]) == 20
        assert data["vba_project"] is not None
        assert len(data["vba_project"]["modules"]) == 23
