from __future__ import annotations

import markdown as md_lib

_HTML_SHELL = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; max-width: 800px;
         margin: 2rem auto; padding: 0 1.25rem; line-height: 1.65; }}
  h1, h2, h3 {{ line-height: 1.25; }}
  h1 {{ border-bottom: 2px solid #8884; padding-bottom: .4rem; }}
  h2 {{ border-bottom: 1px solid #8883; padding-bottom: .25rem; margin-top: 2rem; }}
  code {{ background: #8882; border-radius: 4px; padding: .1em .35em; font-size: .92em; }}
  pre {{ background: #1e1e2e; color: #e6e6ef; border-radius: 8px; padding: 1rem; overflow-x: auto; }}
  pre code {{ background: none; padding: 0; color: inherit; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #8885; padding: .45rem .6rem; text-align: left; }}
  blockquote {{ border-left: 4px solid #8886; margin-left: 0; padding-left: 1rem; opacity: .85; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def markdown_to_html(markdown_text: str, title: str) -> str:
    body = md_lib.markdown(markdown_text, extensions=["tables", "fenced_code", "toc"])
    return _HTML_SHELL.format(title=title, body=body)
