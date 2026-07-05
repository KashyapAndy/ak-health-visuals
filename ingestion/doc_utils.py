"""
Shared helper for turning a raw source file (PDF or HTML) into a Claude
message content block. PDFs go in as base64 document blocks; HTML/HTM
files go in as plain text — Claude reads raw markup fine inline, and
there's no "document" media type for HTML in the Messages API.
"""

import base64
from pathlib import Path

SUPPORTED_SUFFIXES = {".pdf", ".html", ".htm"}


def build_content_blocks(path: Path) -> list[dict]:
    if path.suffix.lower() == ".pdf":
        b64 = base64.standard_b64encode(path.read_bytes()).decode()
        return [{
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": b64},
        }]
    text = path.read_text(encoding="utf-8", errors="replace")
    return [{"type": "text", "text": f"--- Source file: {path.name} ---\n{text}"}]
