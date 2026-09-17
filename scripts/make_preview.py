"""Produce a single-file, offline, READ-ONLY snapshot of the working application."""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.service import bootstrap
ROOT=Path(__file__).resolve().parents[1]

def main():
    data = json.dumps(bootstrap(include_results=True), separators=(',', ':'), ensure_ascii=True).replace('<', r'\u003c')
    css = (ROOT/'frontend/src/style.css').read_text()
    js = (ROOT/'frontend/src/app.js').read_text().replace('</script', '<\\/script')
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Signal Atlas · Offline Teaching Preview</title><style>' + css + '</style></head>'
            '<body><div id="app"></div><script>window.__PREVIEW__=' + data + ';</script><script>' + js + '</script></body></html>')
    out=ROOT/'preview/Signal_Atlas_Preview.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    print(f'Created {out} ({out.stat().st_size:,} bytes). Saved results only; use FastAPI for editable SPARQL.')
if __name__=='__main__': main()
