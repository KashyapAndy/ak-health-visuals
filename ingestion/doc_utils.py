"""
Shared helper for turning a raw source file (PDF or HTML) into a Claude
message content block. PDFs go in as base64 document blocks; HTML/HTM
files go in as plain text — there's no "document" media type for HTML
in the Messages API.

HTML exports of clinical documents (e.g. a C-CDA/CCD patient record) are
mostly machine-readable XML entries (codes, template IDs, timestamps as
attributes) with no visible text — tag-stripping removes that bloat and
keeps just the rendered narrative, which is what actually contains the
lab values.
"""

import base64
import re
from html import unescape
from pathlib import Path

SUPPORTED_SUFFIXES = {".pdf", ".html", ".htm"}

# Chars, not tokens; ~4 chars/token, so this caps well under the 1M token limit.
_MAX_TEXT_CHARS = 3_000_000

_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.I | re.S)
_TAG_RE = re.compile(r"<[^>]+>")
_BLANK_LINES_RE = re.compile(r"[ \t]*\n[ \t]*")


def _html_to_text(raw: str) -> str:
    text = _SCRIPT_STYLE_RE.sub(" ", raw)
    text = _TAG_RE.sub("\n", text)
    text = unescape(text)
    text = _BLANK_LINES_RE.sub("\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def build_content_blocks(path: Path) -> list[dict]:
    if path.suffix.lower() == ".pdf":
        b64 = base64.standard_b64encode(path.read_bytes()).decode()
        return [{
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": b64},
        }]

    raw = path.read_text(encoding="utf-8", errors="replace")
    text = _html_to_text(raw)
    if len(text) > _MAX_TEXT_CHARS:
        print(f"[doc_utils] WARNING: {path.name} still {len(text)} chars after tag-stripping — "
              f"truncating to {_MAX_TEXT_CHARS}. Extracted data may be incomplete.")
        text = text[:_MAX_TEXT_CHARS]
    return [{"type": "text", "text": f"--- Source file: {path.name} ---\n{text}"}]
