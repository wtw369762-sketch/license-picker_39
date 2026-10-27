"""把许可证数据集渲染成一张可离线打开的静态对比页。

运行：python tools/build_web.py
输出：web/index.html（由脚本生成，请勿手工编辑）
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from license_picker.rules import load_licenses  # noqa: E402

OUTPUT = ROOT / "web" / "index.html"

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>开源许可证对比 · license-picker</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 40px 24px 64px;
    font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
    color: #1c2230; background: #f6f7fb; line-height: 1.65;
  }}
  main {{ max-width: 980px; margin: 0 auto; }}
  h1 {{ font-size: 28px; margin: 0 0 8px; letter-spacing: 0.5px; }}
  .lede {{ color: #55607a; margin: 0 0 28px; }}
  input {{
    width: 100%; padding: 11px 14px; border: 1px solid #d6dbe8; border-radius: 10px;
    font-size: 15px; background: #fff; outline: none;
  }}
  input:focus {{ border-color: #5b7cfa; box-shadow: 0 0 0 3px rgba(91,124,250,.15); }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 18px; background: #fff;
    border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(20,30,60,.08); }}
  th, td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid #eef1f7; font-size: 14px; }}
  th {{ background: #eef2ff; font-weight: 600; color: #2b3550; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #fafbff; }}
  code {{ background: #f0f3fa; padding: 2px 6px; border-radius: 5px; font-size: 13px; }}
  .tag {{ display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 12px; }}
  .permissive {{ background: #e6f6ec; color: #1d7a3f; }}
  .weak-copyleft {{ background: #fff4e0; color: #8a5a00; }}
  .strong-copyleft {{ background: #fdeaea; color: #a72020; }}
  .network-copyleft {{ background: #f2e9fd; color: #5b21a8; }}
  .public-domain {{ background: #e9eef5; color: #445; }}
  .hint {{ margin-top: 26px; padding: 16px 18px; background: #fff; border-radius: 12px;
    border-left: 4px solid #5b7cfa; box-shadow: 0 1px 3px rgba(20,30,60,.06); }}
  .hint h2 {{ font-size: 16px; margin: 0 0 8px; }}
  .hint ol {{ margin: 0; padding-left: 20px; }}
  footer {{ margin-top: 34px; color: #78829b; font-size: 13px; }}
  a {{ color: #3f5bd0; }}
  @media (max-width: 720px) {{
    th:nth-child(5), td:nth-child(5) {{ display: none; }}
  }}
</style>
</head>
<body>
<main>
  <h1>开源许可证对比</h1>
  <p class="lede">共 {count} 种许可证 · 由 <code>tools/build_web.py</code> 从数据集自动生成，请勿手工编辑。</p>
  <input id="q" type="search" placeholder="搜索许可证名称、SPDX 标识或义务…" aria-label="搜索许可证">
  <table id="t">
    <thead>
      <tr><th>SPDX</th><th>名称</th><th>类型</th><th>专利授权</th><th>主要义务</th></tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
  <div class="hint">
    <h2>三步选定</h2>
    <ol>
      <li>先回答“能不能接受下游闭源”，这一条几乎决定了宽松 / copyleft 的大方向。</li>
      <li>再确认是否涉及专利：涉及就优先挑带明确专利授权的许可证。</li>
      <li>最后看使用形态：库看弱 copyleft，网络服务看 AGPL，桌面应用看 GPL。</li>
    </ol>
  </div>
  <footer>
    数据来源：各许可证官方文本与 SPDX 许可证列表。
    命令行版本见 <a href="https://github.com/wtw369762-sketch/license-picker_39">license-picker_39</a>。
  </footer>
</main>
<script>
  const input = document.getElementById('q');
  const rows = Array.from(document.querySelectorAll('#t tbody tr'));
  input.addEventListener('input', () => {{
    const key = input.value.trim().toLowerCase();
    rows.forEach((row) => {{
      row.style.display = row.textContent.toLowerCase().includes(key) ? '' : 'none';
    }});
  }});
</script>
</body>
</html>
"""


def render_rows() -> str:
    rows = []
    for lic in load_licenses():
        rows.append(
            "      <tr>"
            "<td><code>%s</code></td>"
            "<td>%s</td>"
            '<td><span class="tag %s">%s</span></td>'
            "<td>%s</td>"
            "<td>%s</td>"
            "</tr>"
            % (
                html.escape(lic.spdx),
                html.escape(lic.name_zh),
                html.escape(lic.category),
                html.escape(lic.category_label),
                "有" if lic.patent_grant else "无",
                html.escape("；".join(lic.obligations)),
            )
        )
    return "\n".join(rows)


def render_page() -> str:
    licenses = load_licenses()
    return PAGE.format(count=len(licenses), rows=render_rows())


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_page(), encoding="utf-8")
    print("已生成 %s（%d 字节）" % (OUTPUT, OUTPUT.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
