"""VbaParserのテスト"""

import pytest

from xlsm2spec.infrastructure.parsers.vba_parser import VbaParser
from xlsm2spec.domain.models import ProcedureType


class TestVbaParser:
    """VbaParser のテスト"""

    @pytest.fixture
    def parser(self):
        return VbaParser()

    def test_parse_simple_sub(self, parser):
        source = """Public Sub HelloWorld()
    MsgBox "Hello World"
End Sub"""
        
        procedures = parser.parse(source)
        assert len(procedures) == 1
        
        proc = procedures[0]
        assert proc.name == "HelloWorld"
        assert proc.procedure_type == ProcedureType.SUB
        assert proc.access == "Public"
        assert len(proc.parameters) == 0

    def test_parse_private_sub(self, parser):
        source = """Private Sub InternalProcess()
    ' Internal code
End Sub"""
        
        procedures = parser.parse(source)
        assert len(procedures) == 1
        assert procedures[0].access == "Private"

    def test_parse_function_with_return_type(self, parser):
        source = """Public Function Add(a As Integer, b As Integer) As Integer
    Add = a + b
End Function"""
        
        procedures = parser.parse(source)
        assert len(procedures) == 1
        
        proc = procedures[0]
        assert proc.name == "Add"
        assert proc.procedure_type == ProcedureType.FUNCTION
        assert proc.return_type == "Integer"
        assert len(proc.parameters) == 2
        assert proc.parameters[0].name == "a"
        assert proc.parameters[0].var_type == "Integer"

    def test_parse_multiple_procedures(self, parser):
        source = """Public Sub Proc1()
End Sub

Private Function Proc2() As String
    Proc2 = "test"
End Function

Public Sub Proc3()
End Sub"""
        
        procedures = parser.parse(source)
        assert len(procedures) == 3
        assert procedures[0].name == "Proc1"
        assert procedures[1].name == "Proc2"
        assert procedures[2].name == "Proc3"

    def test_parse_property_get(self, parser):
        source = """Public Property Get Name() As String
    Name = m_Name
End Property"""
        
        procedures = parser.parse(source)
        assert len(procedures) == 1
        assert procedures[0].procedure_type == ProcedureType.PROPERTY_GET

    def test_parse_property_let(self, parser):
        source = """Public Property Let Name(value As String)
    m_Name = value
End Property"""
        
        procedures = parser.parse(source)
        assert len(procedures) == 1
        assert procedures[0].procedure_type == ProcedureType.PROPERTY_LET

    def test_parse_no_procedures(self, parser):
        source = """Option Explicit
Dim globalVar As Integer
Const MAX_VALUE = 100"""
        
        procedures = parser.parse(source)
        assert len(procedures) == 0

    def test_parse_byval_byref_parameters(self, parser):
        source = """Public Sub Process(ByVal x As Integer, ByRef y As String)
End Sub"""
        
        procedures = parser.parse(source)
        assert len(procedures) == 1
        assert len(procedures[0].parameters) == 2
        assert procedures[0].parameters[0].name == "x"
        assert procedures[0].parameters[1].name == "y"

    def test_parse_optional_parameter(self, parser):
        source = """Public Function GetData(Optional name As String) As Variant
End Function"""
        
        procedures = parser.parse(source)
        assert len(procedures) == 1
        assert len(procedures[0].parameters) == 1
        assert procedures[0].parameters[0].name == "name"
