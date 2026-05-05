from __future__ import annotations

import base64
import datetime as dt
import os
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
ENCODINGS_DIR = PUBLIC_DIR / "encodings"


ENCODING_PAGES = [
    # name, python codec, label, html meta charset
    ("utf-8", "utf-8", "UTF-8", "utf-8"),
    ("shift_jis", "shift_jis", "Shift_JIS", "shift_jis"),
    ("euc-jp", "euc_jp", "EUC-JP", "euc-jp"),
    ("iso-2022-jp", "iso2022_jp", "ISO-2022-JP", "iso-2022-jp"),
    ("utf-16", "utf-16", "UTF-16 (BOM付き)", "utf-16"),
    ("utf-16le", "utf-16le", "UTF-16LE", "utf-16le"),
    ("utf-16be", "utf-16be", "UTF-16BE", "utf-16be"),
]


SAMPLE_LINES = [
    ("日本語", "こんにちは、世界"),
    ("漢字", "𠮟（サロゲートペアを含む例）"),
    ("ひらがな", "あいうえお"),
    ("カタカナ", "アイウエオ"),
    ("絵文字", "🍣🍺（環境によっては豆腐になります）"),
    ("記号", "①Ⅳ㎏€™✓"),
    ("アクセント", "café naïve résumé"),
    ("ギリシャ文字", "αβγδε"),
]


def build_html(*, title: str, charset: str, description: str, canonical_path: str) -> str:
    # GitHub Pages では絶対URLが確定しないため、OGPは相対URL中心にして
    # og:url は canonical のパスのみを埋め、実運用では公開URLに合わせて上書きしてもらう。
    og_title = title
    og_desc = description
    og_image = "/ogp.png"
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    rows = "\n".join(
        f"<tr><th>{label}</th><td><code>{value}</code></td></tr>" for label, value in SAMPLE_LINES
    )

    return f"""<!doctype html>
<html>
  <head>
    <meta charset="{charset}">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{description}">

    <!-- OGP -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{og_desc}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:url" content="{canonical_path}">
    <meta name="twitter:card" content="summary_large_image">

    <style>
      :root {{
        color-scheme: light dark;
        --bg: #0b1020;
        --panel: rgba(255,255,255,0.06);
        --text: rgba(255,255,255,0.92);
        --muted: rgba(255,255,255,0.7);
        --accent: #7dd3fc;
        --border: rgba(255,255,255,0.12);
      }}
      @media (prefers-color-scheme: light) {{
        :root {{
          --bg: #f6f7fb;
          --panel: #ffffff;
          --text: #0b1020;
          --muted: rgba(11,16,32,0.74);
          --accent: #0369a1;
          --border: rgba(11,16,32,0.12);
        }}
      }}
      body {{
        margin: 0;
        font-family: ui-sans-serif, system-ui, -apple-system, "Hiragino Sans", "Noto Sans JP", "Segoe UI", sans-serif;
        background: radial-gradient(1200px 600px at 20% 0%, rgba(125,211,252,0.18), transparent 55%),
                    radial-gradient(900px 450px at 90% 20%, rgba(167,139,250,0.14), transparent 60%),
                    var(--bg);
        color: var(--text);
      }}
      a {{ color: var(--accent); text-decoration: none; }}
      a:hover {{ text-decoration: underline; }}
      .wrap {{
        max-width: 980px;
        margin: 0 auto;
        padding: 28px 20px 56px;
      }}
      header {{
        display: flex;
        align-items: baseline;
        gap: 14px;
        flex-wrap: wrap;
        margin-bottom: 18px;
      }}
      header h1 {{
        font-size: 22px;
        margin: 0;
        letter-spacing: 0.2px;
      }}
      header .meta {{
        color: var(--muted);
        font-size: 13px;
      }}
      nav {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px 14px;
        padding: 12px 14px;
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 14px;
        margin: 14px 0 20px;
      }}
      nav .pill {{
        display: inline-flex;
        gap: 6px;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(125,211,252,0.12);
        border: 1px solid rgba(125,211,252,0.22);
        color: var(--text);
        font-size: 13px;
      }}
      main {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        overflow: hidden;
      }}
      .section {{
        padding: 18px 16px;
      }}
      .section + .section {{
        border-top: 1px solid var(--border);
      }}
      .note {{
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
      }}
      th, td {{
        text-align: left;
        padding: 10px 8px;
        border-bottom: 1px solid var(--border);
        vertical-align: top;
      }}
      th {{
        width: 180px;
        color: var(--muted);
        font-weight: 600;
        font-size: 13px;
      }}
      code {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        font-size: 13px;
        word-break: break-word;
      }}
      footer {{
        margin-top: 16px;
        color: var(--muted);
        font-size: 12px;
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <header>
        <h1>{title}</h1>
        <div class="meta">generated: <code>{generated}</code></div>
      </header>

      <nav>
        <a class="pill" href="/index.html">Home</a>
        <a class="pill" href="/encodings/utf-8.html">UTF-8</a>
        <a class="pill" href="/encodings/shift_jis.html">Shift_JIS</a>
        <a class="pill" href="/encodings/euc-jp.html">EUC-JP</a>
        <a class="pill" href="/encodings/iso-2022-jp.html">ISO-2022-JP</a>
        <a class="pill" href="/encodings/utf-16.html">UTF-16</a>
        <a class="pill" href="/encodings/utf-16le.html">UTF-16LE</a>
        <a class="pill" href="/encodings/utf-16be.html">UTF-16BE</a>
      </nav>

      <main>
        <div class="section">
          <div class="note">
            このページは <b>{charset}</b> を指定し、<b>実ファイルもその文字コード</b>で生成しています。<br>
            文字コードによっては表現できない文字（絵文字や一部記号、サロゲートペア等）が <code>?</code> になったり、
            化けたりすることがあります（それを観察するためのページです）。
          </div>
        </div>
        <div class="section">
          <table>
            <tbody>
              {rows}
            </tbody>
          </table>
        </div>
      </main>

      <footer>
        <div>repo: <code>encoding-test</code></div>
      </footer>
    </div>
  </body>
</html>
"""


def png_bytes_rgba_solid(*, width: int, height: int, rgba: tuple[int, int, int, int]) -> bytes:
    r, g, b, a = rgba
    # PNG: each scanline starts with filter byte 0
    raw = bytearray()
    row = bytes([r, g, b, a]) * width
    for _ in range(height):
        raw.append(0)
        raw.extend(row)
    compressed = zlib.compress(bytes(raw), level=9)

    def chunk(typ: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit, RGBA
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", ihdr),
            chunk(b"IDAT", compressed),
            chunk(b"IEND", b""),
        ]
    )


def write_file_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def write_text_encoded(
    *,
    path: Path,
    text: str,
    codec: str,
    add_bom: bool = False,
    bom_bytes: bytes | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode(codec, errors="replace")
    if bom_bytes is not None:
        data = bom_bytes + data
    elif add_bom:
        # python's utf-16 includes BOM; other codecs do not.
        if codec.lower() in {"utf-16le"}:
            data = b"\xff\xfe" + data
        elif codec.lower() in {"utf-16be"}:
            data = b"\xfe\xff" + data
    path.write_bytes(data)


def main() -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    ENCODINGS_DIR.mkdir(parents=True, exist_ok=True)

    # OGP image (simple solid background)
    ogp_path = PUBLIC_DIR / "ogp.png"
    ogp_png = png_bytes_rgba_solid(width=1200, height=630, rgba=(11, 16, 32, 255))
    write_file_bytes(ogp_path, ogp_png)

    # Home page is always UTF-8
    home = build_html(
        title="encoding-test (GitHub Pages)",
        charset="utf-8",
        description="一般的な文字コードごとのHTML表示テスト（GitHub Pages）",
        canonical_path="/index.html",
    )
    write_text_encoded(path=PUBLIC_DIR / "index.html", text=home, codec="utf-8")

    # Encoding pages
    for slug, codec, label, meta_charset in ENCODING_PAGES:
        html = build_html(
            title=f"Encoding: {label}",
            charset=meta_charset,
            description=f"{label} で生成したHTMLページ",
            canonical_path=f"/encodings/{slug}.html",
        )

        # For UTF-16LE/BE, most browsers expect BOM to reliably detect UTF-16.
        add_bom = slug in {"utf-16le", "utf-16be"}
        # For utf-16 codec, Python includes BOM; keep it as-is.
        write_text_encoded(path=ENCODINGS_DIR / f"{slug}.html", text=html, codec=codec, add_bom=add_bom)

    # Basic 404 (UTF-8)
    not_found = build_html(
        title="404 - Not Found",
        charset="utf-8",
        description="Page not found",
        canonical_path="/404.html",
    )
    write_text_encoded(path=PUBLIC_DIR / "404.html", text=not_found, codec="utf-8")


if __name__ == "__main__":
    main()

