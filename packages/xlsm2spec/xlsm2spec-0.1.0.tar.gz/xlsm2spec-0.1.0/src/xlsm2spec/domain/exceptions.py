"""カスタム例外クラス"""


class Xlsm2SpecError(Exception):
    """XLSM2Specの基底例外クラス"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class FileNotFoundError(Xlsm2SpecError):
    """ファイルが見つからない場合の例外"""

    def __init__(self, filepath: str) -> None:
        super().__init__(f"ファイルが見つかりません: {filepath}")
        self.filepath = filepath


class UnsupportedFormatError(Xlsm2SpecError):
    """サポートされていないファイル形式の例外"""

    def __init__(self, filepath: str, extension: str) -> None:
        super().__init__(
            f"サポートされていないファイル形式です: {extension} ({filepath})"
        )
        self.filepath = filepath
        self.extension = extension


class VbaExtractionError(Xlsm2SpecError):
    """VBA抽出に失敗した場合の例外"""

    def __init__(self, filepath: str, reason: str) -> None:
        super().__init__(f"VBA抽出に失敗しました: {reason} ({filepath})")
        self.filepath = filepath
        self.reason = reason


class VbaProtectedError(Xlsm2SpecError):
    """パスワード保護されている場合の例外"""

    def __init__(self, filepath: str) -> None:
        super().__init__(
            f"VBAプロジェクトはパスワードで保護されています: {filepath}"
        )
        self.filepath = filepath


class ParseError(Xlsm2SpecError):
    """構文解析エラー"""

    def __init__(self, message: str, line: int = 0) -> None:
        if line > 0:
            super().__init__(f"構文解析エラー (行 {line}): {message}")
        else:
            super().__init__(f"構文解析エラー: {message}")
        self.line = line
