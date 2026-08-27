#!/usr/bin/env python3
"""Compose index.html from template + inlined base64 logos.
Run: python3 build.py
Triggered automatically by .github/workflows/build.yml on every push to main.
"""
import pathlib, sys

root = pathlib.Path(__file__).parent
with open(root / "src" / "logo-light-sm.b64") as f: light = f.read().strip()
with open(root / "src" / "logo-dark-sm.b64") as f: dark = f.read().strip()
with open(root / "src" / "index.template.html") as f: tpl = f.read()

html = '<!doctype html><html><head><meta charset="utf-8">' + tpl
html = html.replace("__LIGHT__", light).replace("__DARK__", dark)
html = html.replace("<!-- LANDING -->", "</head><body><!-- LANDING -->")
html += "</body></html>"

out = root / "index.html"
out.write_text(html)
print(f"wrote {out} ({len(html)} bytes)")
