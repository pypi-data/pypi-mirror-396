"""分析サービス - VBA解析のオーケストレーション"""

from xlsm2spec.domain.models import Module, Workbook
from xlsm2spec.infrastructure.extractors.vba_extractor import VbaExtractor
from xlsm2spec.infrastructure.parsers.vba_parser import VbaParser
from xlsm2spec.infrastructure.readers.excel_reader import ExcelReader


class AnalyzerService:
    """
    ExcelファイルのVBA分析を行うサービス

    Infrastructure層のコンポーネントをオーケストレーションし、
    Excelファイルの読み込み、VBA抽出、構文解析を一括で実行する
    """

    def __init__(
        self,
        reader: ExcelReader | None = None,
        extractor: VbaExtractor | None = None,
        parser: VbaParser | None = None,
    ):
        """
        Args:
            reader: Excel読み込みアダプター（省略時は自動生成）
            extractor: VBA抽出アダプター（省略時は自動生成）
            parser: VBA解析パーサー（省略時は自動生成）
        """
        self.reader = reader or ExcelReader()
        self.extractor = extractor or VbaExtractor()
        self.parser = parser or VbaParser()

    def analyze(self, filepath: str) -> Workbook:
        """
        Excelファイルを分析し、VBA情報を含むWorkbookを返す

        Args:
            filepath: 分析するExcelファイルのパス

        Returns:
            Workbook: VBA情報を含むワークブック

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            UnsupportedFormatError: サポートされていない形式の場合
            VbaExtractionError: VBA抽出に失敗した場合
        """
        # 1. Excelファイルを読み込み
        workbook = self.reader.read(filepath)

        # 2. VBAプロジェクトを抽出
        vba_project = self.extractor.extract(filepath)

        # 3. 各モジュールのソースコードを解析
        parsed_modules: list[Module] = []
        for module in vba_project.modules:
            procedures = self.parser.parse(module.source_code)
            parsed_module = Module(
                name=module.name,
                module_type=module.module_type,
                source_code=module.source_code,
                procedures=procedures,
                variables=module.variables,
            )
            parsed_modules.append(parsed_module)

        # 4. 解析済みモジュールでVbaProjectを更新
        from xlsm2spec.domain.models import VbaProject

        parsed_vba_project = VbaProject(
            modules=parsed_modules,
            is_protected=vba_project.is_protected,
        )

        # 5. Workbookを更新して返す
        return Workbook(
            filename=workbook.filename,
            sheets=workbook.sheets,
            vba_project=parsed_vba_project,
        )
