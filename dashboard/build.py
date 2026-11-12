"""Build dashboard/index.html by joining the files in dashboard/sections in name order.

Run:  python dashboard/build.py

The page is one self-contained file (styles and scripts are inlined), so it
opens by double-clicking, with no server and no internet.

A section is an HTML file holding one or more panels:

    <section class="panel">
      <h2>Short plain title</h2>
      <p class="sub">At most one line under it.</p>
      ... one big chart or one table ...
    </section>

A chart is a div with its data as JSON; the page draws it and shows the values
on hover:

    <div class="chart"><script type="application/json">
    {"type": "line", "x": ["2022-01-03", "..."],
     "series": [{"name": "System", "values": [1000, 1012.5]}],
     "format": "dollar"}
    </script></div>

    type: "line" or "bar".  format: "percent", "dollar" or "number".
    decimals: optional.  A series can set its own "color".

Placeholders a section can use:

    {{PROJECT_NAME}}    the project name
    {{SETTINGS_TABLE}}  the "My settings" list from CLAUDE.md, as a table
    <span data-today></span>   today's date, filled in when the page opens
"""

from __future__ import annotations

import html
import re
from pathlib import Path

DASHBOARD = Path(__file__).resolve().parent
ROOT = DASHBOARD.parent
SECTIONS = DASHBOARD / "sections"
ASSETS = DASHBOARD / "assets"
OUTPUT = DASHBOARD / "index.html"
PROJECT_NAME = "Trading Bot"


def read_settings() -> list[tuple[str, str]]:
    """Return the bullets under '## My settings' in CLAUDE.md as (name, value) pairs."""
    lines = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## My settings")
    except StopIteration:
        raise SystemExit("CLAUDE.md has no '## My settings' section.")
    settings: list[tuple[str, str]] = []
    for line in lines[start + 1:]:
        text = line.strip()
        if text.startswith("* "):
            name, sep, value = text[2:].partition(": ")
            settings.append((name, value) if sep else ("", name))
        elif text and settings:
            break  # first non-bullet line after the list ends the settings
    return settings


def settings_table() -> str:
    rows = []
    for name, value in read_settings():
        if name:
            rows.append(f"<tr><th>{html.escape(name)}</th><td>{html.escape(value)}</td></tr>")
        else:
            rows.append(f'<tr><td colspan="2">{html.escape(value)}</td></tr>')
    return "<table>\n<tbody>\n" + "\n".join(rows) + "\n</tbody>\n</table>"


def build() -> Path:
    files = sorted(SECTIONS.glob("*.html"), key=lambda p: p.name)
    if not files:
        raise SystemExit(f"No sections found in {SECTIONS}")

    body = "\n\n".join(
        f"<!-- {f.name} -->\n{f.read_text(encoding='utf-8').strip()}" for f in files
    )
    replacements = {"{{PROJECT_NAME}}": html.escape(PROJECT_NAME)}
    if "{{SETTINGS_TABLE}}" in body:
        replacements["{{SETTINGS_TABLE}}"] = settings_table()
    for token, value in replacements.items():
        body = body.replace(token, value)
    leftover = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", body)))
    if leftover:
        raise SystemExit(f"Unknown placeholders in sections: {', '.join(leftover)}")

    css = (ASSETS / "style.css").read_text(encoding="utf-8")
    js = (ASSETS / "app.js").read_text(encoding="utf-8")
    js = js.replace("</script", "<\\/script")  # a closing tag would end the inline script early
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(PROJECT_NAME)}</title>
<style>
{css}</style>
</head>
<body>
<main>
{body}
</main>
<script>
{js}</script>
</body>
</html>
"""
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Built {OUTPUT.relative_to(ROOT)} from {len(files)} section(s): "
          + ", ".join(f.stem for f in files))
    return OUTPUT


if __name__ == "__main__":
    build()
