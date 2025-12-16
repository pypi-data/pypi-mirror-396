"""エラーハンドリングのテスト"""

import pytest

from xlsm2spec.domain.exceptions import (
    Xlsm2SpecError,
    FileNotFoundError,
    UnsupportedFormatError,
)
from xlsm2spec.infrastructure.readers.excel_reader import ExcelReader


class TestExceptions:
    """例外クラスのテスト"""

    def test_xlsm2spec_error_is_base(self) -> None:
        """Xlsm2SpecErrorが基底クラスであること"""
        assert issubclass(FileNotFoundError, Xlsm2SpecError)
        assert issubclass(UnsupportedFormatError, Xlsm2SpecError)

    def test_file_not_found_error_message(self) -> None:
        """FileNotFoundErrorのメッセージ"""
        e = FileNotFoundError("/path/to/file.xlsx")
        assert "/path/to/file.xlsx" in str(e)

    def test_unsupported_format_error_message(self) -> None:
        """UnsupportedFormatErrorのメッセージ"""
        e = UnsupportedFormatError("/path/to/file.txt", ".txt")
        assert ".txt" in str(e)


class TestExcelReaderErrors:
    """ExcelReaderのエラーハンドリングテスト"""

    @pytest.fixture
    def reader(self) -> ExcelReader:
        return ExcelReader()

    def test_file_not_found(self, reader: ExcelReader) -> None:
        """存在しないファイルでエラー"""
        with pytest.raises(FileNotFoundError):
            reader.read("/nonexistent/file.xlsx")

    def test_unsupported_format(self, reader: ExcelReader, tmp_path) -> None:
        """サポートされていない形式でエラー"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not an excel file")

        with pytest.raises(UnsupportedFormatError):
            reader.read(str(txt_file))

    def test_supported_extensions(self, reader: ExcelReader) -> None:
        """サポートされている拡張子"""
        assert ".xls" in reader.SUPPORTED_EXTENSIONS
        assert ".xlsx" in reader.SUPPORTED_EXTENSIONS
        assert ".xlsm" in reader.SUPPORTED_EXTENSIONS
        assert ".txt" not in reader.SUPPORTED_EXTENSIONS
