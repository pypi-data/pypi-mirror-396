"""フォーマッターのテスト"""

import json
import pytest

from xlsm2spec.domain.models import (
    Module,
    ModuleType,
    Procedure,
    ProcedureType,
    Variable,
    VbaProject,
    Workbook,
)
from xlsm2spec.presentation.formatters.markdown_formatter import MarkdownFormatter
from xlsm2spec.presentation.formatters.json_formatter import JsonFormatter


@pytest.fixture
def sample_workbook():
    """テスト用ワークブック"""
    proc = Procedure(
        name="HelloWorld",
        procedure_type=ProcedureType.SUB,
        access="Public",
        parameters=[],
        source_code="Public Sub HelloWorld()\n    MsgBox \"Hello\"\nEnd Sub",
        line_start=1,
        line_end=3,
    )
    module = Module(
        name="Module1",
        module_type=ModuleType.STANDARD,
        source_code="Public Sub HelloWorld()\n    MsgBox \"Hello\"\nEnd Sub",
        procedures=[proc],
        variables=[],
    )
    vba = VbaProject(modules=[module], is_protected=False)
    return Workbook(
        filename="test.xlsm",
        sheets=["Sheet1", "Data"],
        vba_project=vba,
    )


class TestMarkdownFormatter:
    """MarkdownFormatter のテスト"""

    def test_format_basic_structure(self, sample_workbook):
        formatter = MarkdownFormatter()
        result = formatter.format(sample_workbook)
        
        assert "# test.xlsm 仕様書" in result
        assert "## 概要" in result
        assert "## シート一覧" in result
        assert "## VBAモジュール" in result

    def test_format_contains_sheet_names(self, sample_workbook):
        formatter = MarkdownFormatter()
        result = formatter.format(sample_workbook)
        
        assert "Sheet1" in result
        assert "Data" in result

    def test_format_contains_module_info(self, sample_workbook):
        formatter = MarkdownFormatter()
        result = formatter.format(sample_workbook)
        
        assert "Module1" in result
        assert "standard" in result  # ModuleType.STANDARD.value

    def test_format_contains_procedure_table(self, sample_workbook):
        formatter = MarkdownFormatter()
        result = formatter.format(sample_workbook)
        
        assert "| 名前 | 種別 | アクセス | 戻り値 | 行数 |" in result
        assert "HelloWorld" in result

    def test_format_workbook_without_vba(self):
        wb = Workbook(filename="test.xlsx", sheets=["Sheet1"])
        formatter = MarkdownFormatter()
        result = formatter.format(wb)
        
        assert "test.xlsx" in result
        assert "VBAモジュール数**: 0" in result


class TestJsonFormatter:
    """JsonFormatter のテスト"""

    def test_format_valid_json(self, sample_workbook):
        formatter = JsonFormatter()
        result = formatter.format(sample_workbook)
        
        # JSON としてパース可能
        data = json.loads(result)
        assert data is not None

    def test_format_contains_filename(self, sample_workbook):
        formatter = JsonFormatter()
        result = formatter.format(sample_workbook)
        data = json.loads(result)
        
        assert data["filename"] == "test.xlsm"

    def test_format_contains_sheets(self, sample_workbook):
        formatter = JsonFormatter()
        result = formatter.format(sample_workbook)
        data = json.loads(result)
        
        assert data["sheets"] == ["Sheet1", "Data"]

    def test_format_contains_vba_project(self, sample_workbook):
        formatter = JsonFormatter()
        result = formatter.format(sample_workbook)
        data = json.loads(result)
        
        assert data["vba_project"] is not None
        assert data["vba_project"]["is_protected"] is False
        assert len(data["vba_project"]["modules"]) == 1

    def test_format_contains_procedure_info(self, sample_workbook):
        formatter = JsonFormatter()
        result = formatter.format(sample_workbook)
        data = json.loads(result)
        
        module = data["vba_project"]["modules"][0]
        assert len(module["procedures"]) == 1
        
        proc = module["procedures"][0]
        assert proc["name"] == "HelloWorld"
        assert proc["procedure_type"] == "sub"  # ProcedureType.SUB.value (lowercase)
        assert proc["access"] == "Public"

    def test_format_custom_indent(self, sample_workbook):
        formatter = JsonFormatter(indent=4)
        result = formatter.format(sample_workbook)
        
        # 4スペースインデントが使用されていることを確認
        assert "    " in result

    def test_format_workbook_without_vba(self):
        wb = Workbook(filename="test.xlsx", sheets=["Sheet1"])
        formatter = JsonFormatter()
        result = formatter.format(wb)
        data = json.loads(result)
        
        assert data["vba_project"] is None
