"""Domainモデルのテスト"""

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


class TestVariable:
    """Variableモデルのテスト"""

    def test_create_simple_variable(self):
        var = Variable(name="counter", var_type="Integer")
        assert var.name == "counter"
        assert var.var_type == "Integer"
        assert var.is_array is False

    def test_create_array_variable(self):
        var = Variable(name="items", var_type="String", is_array=True)
        assert var.is_array is True


class TestProcedure:
    """Procedureモデルのテスト"""

    def test_create_sub(self):
        proc = Procedure(
            name="TestSub",
            procedure_type=ProcedureType.SUB,
            access="Public",
            parameters=[],
            source_code="Public Sub TestSub()\nEnd Sub",
            line_start=1,
            line_end=2,
        )
        assert proc.name == "TestSub"
        assert proc.procedure_type == ProcedureType.SUB
        assert proc.line_count == 2

    def test_create_function_with_params(self):
        params = [
            Variable(name="x", var_type="Integer"),
            Variable(name="y", var_type="Integer"),
        ]
        proc = Procedure(
            name="Add",
            procedure_type=ProcedureType.FUNCTION,
            access="Public",
            parameters=params,
            return_type="Integer",
            source_code="Public Function Add(x As Integer, y As Integer) As Integer\n    Add = x + y\nEnd Function",
            line_start=1,
            line_end=3,
        )
        assert len(proc.parameters) == 2
        assert proc.return_type == "Integer"

    def test_signature_sub(self):
        proc = Procedure(
            name="MySub",
            procedure_type=ProcedureType.SUB,
            access="Private",
            parameters=[],
            source_code="",
            line_start=1,
            line_end=1,
        )
        assert proc.signature == "Private Sub MySub()"

    def test_signature_function_with_return(self):
        proc = Procedure(
            name="GetValue",
            procedure_type=ProcedureType.FUNCTION,
            access="Public",
            parameters=[Variable(name="id", var_type="Long")],
            return_type="String",
            source_code="",
            line_start=1,
            line_end=1,
        )
        assert proc.signature == "Public Function GetValue(id As Long) As String"


class TestModule:
    """Moduleモデルのテスト"""

    def test_create_module(self):
        module = Module(
            name="Utils",
            module_type=ModuleType.STANDARD,
            source_code="Option Explicit\n\nPublic Sub Test()\nEnd Sub",
            procedures=[],
            variables=[],
        )
        assert module.name == "Utils"
        assert module.module_type == ModuleType.STANDARD
        assert module.line_count == 4


class TestVbaProject:
    """VbaProjectモデルのテスト"""

    def test_empty_project(self):
        project = VbaProject(modules=[], is_protected=False)
        assert len(project.modules) == 0
        assert project.is_protected is False

    def test_protected_project(self):
        project = VbaProject(modules=[], is_protected=True)
        assert project.is_protected is True


class TestWorkbook:
    """Workbookモデルのテスト"""

    def test_create_workbook_without_vba(self):
        wb = Workbook(filename="test.xlsx", sheets=["Sheet1", "Sheet2"])
        assert wb.filename == "test.xlsx"
        assert len(wb.sheets) == 2
        assert wb.vba_project is None

    def test_create_workbook_with_vba(self):
        vba = VbaProject(modules=[], is_protected=False)
        wb = Workbook(filename="test.xlsm", sheets=["Sheet1"], vba_project=vba)
        assert wb.vba_project is not None
