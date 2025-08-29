import os, datetime
from pathlib import Path
from pypdf import PdfMerger

ROOT = Path(__file__).resolve().parents[1]
INCOMING = ROOT / "incoming"
DOCS = ROOT / "docs"
MANIFEST = ROOT / "manifest.txt"

DOCS.mkdir(exist_ok=True, parents=True)
INCOMING.mkdir(exist_ok=True, parents=True)

def read_manifest():
    if MANIFEST.exists():
        order = [l.strip() for l in MANIFEST.read_text(encoding="utf-8").splitlines() if l.strip()]
        files = []
        for name in order:
            p = INCOMING / name
            if p.is_file():
                files.append(p)
        if files:
            return files
    # fallback: todos los PDFs por orden alfabético
    return sorted(INCOMING.glob("*.pdf"))

def merge(files):
    if not files:
        print("⚠️  No hay PDFs en incoming/. Nada que fusionar.")
        return None
    m = PdfMerger()
    for f in files:
        m.append(str(f))
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    out = DOCS / f"merged_{stamp}.pdf"
    with open(out, "wb") as fh:
        m.write(fh)
    m.close()
    return out

def build_index():
    items = sorted(DOCS.glob("*.pdf"), reverse=True)
    rows = []
    for p in items:
        size_mb = p.stat().st_size / (1024*1024)
        rows.append(f'<tr><td><a href="{p.name}">{p.name}</a></td><td>{size_mb:.2f} MB</td></tr>')
    html = f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PDFs fusionados</title>
<style>body{{font-family:system-ui,Arial,sans-serif;margin:2rem;}} table{{border-collapse:collapse;width:100%;}} td,th{{border:1px solid #ddd;padding:.6rem;}} th{{background:#f5f5f5;text-align:left;}}</style>
</head><body>
<h1>PDFs fusionados</h1>
<p>Generados automáticamente por GitHub Actions.</p>
<table>
<thead><tr><th>Archivo</th><th>Tamaño</th></tr></thead>
<tbody>
{''.join(rows) if rows else '<tr><td colspan="2">Aún no hay archivos.</td></tr>'}
</tbody>
</table>
</body></html>"""
    (DOCS / "index.html").write_text(html, encoding="utf-8")

def main():
    files = read_manifest()
    print("Archivos a fusionar:", [f.name for f in files])
    out = merge(files)
    if out:
        print(f"✅ Generado: {out.relative_to(ROOT)}")
    build_index()
    print("🟢 docs/index.html actualizado.")

if __name__ == "__main__":
    main()
