"""ドメインモデル - Excel/VBA構造を表現するデータクラス"""

from dataclasses import dataclass, field
from enum import Enum


class ModuleType(Enum):
    """VBAモジュールの種別"""

    STANDARD = "standard"  # 標準モジュール (.bas)
    CLASS = "class"  # クラスモジュール (.cls)
    FORM = "form"  # ユーザーフォーム (.frm)
    SHEET = "sheet"  # シートモジュール
    THISWORKBOOK = "thisworkbook"  # ThisWorkbookモジュール


class ProcedureType(Enum):
    """プロシージャの種別"""

    SUB = "sub"
    FUNCTION = "function"
    PROPERTY_GET = "property_get"
    PROPERTY_LET = "property_let"
    PROPERTY_SET = "property_set"


@dataclass
class Variable:
    """変数・定数を表す値オブジェクト"""

    name: str
    var_type: str | None = None
    is_array: bool = False
    scope: str = "local"  # local, module, global

    def __str__(self) -> str:
        type_str = self.var_type or "Variant"
        array_str = "()" if self.is_array else ""
        return f"{self.name}{array_str} As {type_str}"


@dataclass
class Procedure:
    """Sub/Function/Propertyを表すエンティティ"""

    name: str
    procedure_type: ProcedureType
    access: str = "Public"  # Public or Private
    parameters: list["Variable"] = field(default_factory=list)
    return_type: str | None = None
    source_code: str = ""
    line_start: int = 0
    line_end: int = 0

    @property
    def signature(self) -> str:
        """プロシージャのシグネチャを返す"""
        params_str = ", ".join(str(p) for p in self.parameters)
        base = f"{self.access} {self.procedure_type.value.capitalize()} {self.name}({params_str})"
        if self.return_type:
            return f"{base} As {self.return_type}"
        return base

    @property
    def line_count(self) -> int:
        """プロシージャの行数を返す"""
        if self.line_end >= self.line_start:
            return self.line_end - self.line_start + 1
        return 0


@dataclass
class Module:
    """VBAモジュールを表すエンティティ"""

    name: str
    module_type: ModuleType
    source_code: str = ""
    procedures: list[Procedure] = field(default_factory=list)
    variables: list[Variable] = field(default_factory=list)

    @property
    def line_count(self) -> int:
        """モジュールの総行数を返す"""
        return len(self.source_code.splitlines())

    @property
    def procedure_count(self) -> int:
        """プロシージャ数を返す"""
        return len(self.procedures)


@dataclass
class VbaProject:
    """VBAプロジェクトを表すエンティティ"""

    modules: list[Module] = field(default_factory=list)
    is_protected: bool = False

    @property
    def module_count(self) -> int:
        """モジュール数を返す"""
        return len(self.modules)

    @property
    def total_procedure_count(self) -> int:
        """全プロシージャ数を返す"""
        return sum(m.procedure_count for m in self.modules)

    @property
    def total_line_count(self) -> int:
        """総行数を返す"""
        return sum(m.line_count for m in self.modules)


@dataclass
class Workbook:
    """Excelブックを表すエンティティ"""

    filename: str
    sheets: list[str] = field(default_factory=list)
    vba_project: VbaProject | None = None

    @property
    def has_vba(self) -> bool:
        """VBAプロジェクトが存在するかを返す"""
        return self.vba_project is not None and len(self.vba_project.modules) > 0

    @property
    def sheet_count(self) -> int:
        """シート数を返す"""
        return len(self.sheets)
