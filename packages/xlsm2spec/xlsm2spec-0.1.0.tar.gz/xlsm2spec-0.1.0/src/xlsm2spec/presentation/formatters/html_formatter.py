"""HTML形式フォーマッター"""

from xlsm2spec.domain.models import Module, Procedure, Workbook


class HtmlFormatter:
    """Workbookを仕様書形式のHTMLに変換する"""

    def format(self, workbook: Workbook) -> str:
        """
        ワークブック情報をHTML形式に変換する

        Args:
            workbook: 変換するワークブック

        Returns:
            str: HTML形式の仕様書
        """
        lines: list[str] = []

        lines.append("<!DOCTYPE html>")
        lines.append('<html lang="ja">')
        lines.append("<head>")
        lines.append('  <meta charset="UTF-8">')
        lines.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        lines.append(f"  <title>{workbook.filename} 仕様書</title>")
        lines.append("  <style>")
        lines.append(self._get_css())
        lines.append("  </style>")
        lines.append("</head>")
        lines.append("<body>")
        lines.append('  <div class="container">')

        # タイトル
        lines.append(f"    <h1>{workbook.filename} 仕様書</h1>")

        # 概要
        lines.append("    <h2>概要</h2>")
        lines.append("    <ul>")
        lines.append(f"      <li><strong>ファイル名</strong>: {workbook.filename}</li>")
        lines.append(f"      <li><strong>シート数</strong>: {len(workbook.sheets)}</li>")

        if workbook.vba_project:
            lines.append(
                f"      <li><strong>VBAモジュール数</strong>: "
                f"{len(workbook.vba_project.modules)}</li>"
            )
            protected = "あり" if workbook.vba_project.is_protected else "なし"
            lines.append(f"      <li><strong>VBA保護</strong>: {protected}</li>")
        else:
            lines.append("      <li><strong>VBAモジュール数</strong>: 0</li>")

        lines.append("    </ul>")

        # シート一覧
        if workbook.sheets:
            lines.append("    <h2>シート一覧</h2>")
            lines.append("    <ol>")
            for sheet in workbook.sheets:
                lines.append(f"      <li>{sheet}</li>")
            lines.append("    </ol>")

        # VBAモジュール
        if workbook.vba_project and workbook.vba_project.modules:
            lines.append("    <h2>VBAモジュール</h2>")

            for module in workbook.vba_project.modules:
                lines.extend(self._format_module(module))

        lines.append("  </div>")
        lines.append("</body>")
        lines.append("</html>")

        return "\n".join(lines)

    def _get_css(self) -> str:
        """CSSスタイルを返す"""
        return """
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      background-color: #f5f5f5;
      margin: 0;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: #fff;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
    h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 8px; margin-top: 30px; }
    h3 { color: #7f8c8d; }
    h4 { color: #95a5a6; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 15px 0;
    }
    th, td {
      border: 1px solid #ddd;
      padding: 10px;
      text-align: left;
    }
    th { background-color: #3498db; color: white; }
    tr:nth-child(even) { background-color: #f9f9f9; }
    tr:hover { background-color: #f5f5f5; }
    pre {
      background-color: #2c3e50;
      color: #ecf0f1;
      padding: 15px;
      border-radius: 5px;
      overflow-x: auto;
    }
    code { font-family: 'Consolas', 'Monaco', monospace; }
    .module-card {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 20px;
      margin: 15px 0;
      background: #fafafa;
    }
    .procedure-details {
      margin: 10px 0;
      padding: 15px;
      background: #fff;
      border-left: 4px solid #3498db;
    }
"""

    def _format_module(self, module: Module) -> list[str]:
        """モジュールをフォーマットする"""
        lines: list[str] = []

        lines.append('    <div class="module-card">')
        lines.append(f"      <h3>{module.name} <small>({module.module_type.value})</small></h3>")
        lines.append("      <ul>")
        lines.append(f"        <li><strong>行数</strong>: {module.line_count}</li>")
        lines.append(f"        <li><strong>プロシージャ数</strong>: {len(module.procedures)}</li>")
        lines.append("      </ul>")

        if module.procedures:
            lines.append("      <h4>プロシージャ一覧</h4>")
            lines.append("      <table>")
            lines.append("        <thead>")
            lines.append("          <tr>")
            lines.append("            <th>名前</th>")
            lines.append("            <th>種別</th>")
            lines.append("            <th>アクセス</th>")
            lines.append("            <th>戻り値</th>")
            lines.append("            <th>行数</th>")
            lines.append("          </tr>")
            lines.append("        </thead>")
            lines.append("        <tbody>")

            for proc in module.procedures:
                return_type = proc.return_type or "-"
                lines.append("          <tr>")
                lines.append(f"            <td>{proc.name}</td>")
                lines.append(f"            <td>{proc.procedure_type.value}</td>")
                lines.append(f"            <td>{proc.access}</td>")
                lines.append(f"            <td>{return_type}</td>")
                lines.append(f"            <td>{proc.line_count}</td>")
                lines.append("          </tr>")

            lines.append("        </tbody>")
            lines.append("      </table>")

            # 各プロシージャの詳細
            for proc in module.procedures:
                lines.extend(self._format_procedure(proc))

        lines.append("    </div>")
        return lines

    def _format_procedure(self, proc: Procedure) -> list[str]:
        """プロシージャの詳細をフォーマットする"""
        lines: list[str] = []

        lines.append('      <div class="procedure-details">')
        lines.append(f"        <h5>{proc.name}</h5>")
        lines.append("        <ul>")
        lines.append(f"          <li><strong>種別</strong>: {proc.procedure_type.value}</li>")
        lines.append(f"          <li><strong>アクセス修飾子</strong>: {proc.access}</li>")
        lines.append(
            f"          <li><strong>位置</strong>: 行 {proc.line_start} - {proc.line_end}</li>"
        )

        if proc.return_type:
            lines.append(f"          <li><strong>戻り値型</strong>: {proc.return_type}</li>")

        lines.append("        </ul>")

        if proc.parameters:
            lines.append("        <p><strong>パラメータ:</strong></p>")
            lines.append("        <ul>")
            for param in proc.parameters:
                param_type = param.var_type or "Variant"
                array_mark = "[]" if param.is_array else ""
                lines.append(f"          <li><code>{param.name}</code>: {param_type}{array_mark}</li>")
            lines.append("        </ul>")

        lines.append("        <p><strong>シグネチャ:</strong></p>")
        lines.append(f"        <pre><code>{proc.signature}</code></pre>")
        lines.append("      </div>")

        return lines
