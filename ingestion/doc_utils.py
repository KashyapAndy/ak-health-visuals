"""
Shared helper for turning a raw source file (PDF, HTML, or CCD/CDA XML)
into a Claude message content block. PDFs go in as base64 document
blocks; everything else goes in as plain text — there's no "document"
media type for HTML/XML in the Messages API.

C-CDA/CCD clinical document exports (XML, sometimes saved with an
.html extension by portal viewers) carry every section — allergies,
medications, encounters, care plan — twice over: once as rendered
narrative and once as fully coded machine-readable entries (LOINC/
SNOMED codes, template IDs, timestamps, all as attributes with no
visible text). For our purposes only the Results and Vital Signs
sections matter, so we try to pull just those out by LOINC section
code before falling back to whole-document tag-stripping.
"""

import base64
import re
from html import unescape
from pathlib import Path

SUPPORTED_SUFFIXES = {".pdf", ".html", ".htm", ".xml"}

# Chars, not tokens; ~4 chars/token, so this caps well under the 1M token limit.
_MAX_TEXT_CHARS = 3_000_000

_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.I | re.S)
_TAG_RE = re.compile(r"<[^>]+>")
_BLANK_LINES_RE = re.compile(r"[ \t]*\n[ \t]*")

# CDA <section> LOINC codes we care about: Results, Vital Signs.
_RELEVANT_SECTION_CODES = {"30954-2", "8716-3"}
_SECTION_RE = re.compile(r"<section\b.*?</section>", re.I | re.S)
_CODE_RE = re.compile(r'<code\b[^>]*\bcode=["\'](\d[\w.\-]*)["\']', re.I)
_TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
_TEXT_EL_RE = re.compile(r"<text\b[^>]*>(.*?)</text>", re.I | re.S)


def _html_to_text(raw: str) -> str:
    text = _SCRIPT_STYLE_RE.sub(" ", raw)
    text = _TAG_RE.sub("\n", text)
    text = unescape(text)
    text = _BLANK_LINES_RE.sub("\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _extract_ccd_sections(raw: str) -> str | None:
    """Pull just the Results/Vital Signs section narratives out of a CDA
    document by LOINC section code. Returns None if this doesn't look
    like a CCD (no <section> elements, or none with a matching code)."""
    picked = []
    for sec in _SECTION_RE.findall(raw):
        if not set(_CODE_RE.findall(sec)) & _RELEVANT_SECTION_CODES:
            continue
        text_m = _TEXT_EL_RE.search(sec)
        if not text_m:
            continue
        title_m = _TITLE_RE.search(sec)
        title = _html_to_text(title_m.group(1)) if title_m else "Section"
        picked.append(f"=== {title} ===\n{_html_to_text(text_m.group(1))}")
    return "\n\n".join(picked) if picked else None


def build_content_blocks(path: Path) -> list[dict]:
    if path.suffix.lower() == ".pdf":
        b64 = base64.standard_b64encode(path.read_bytes()).decode()
        return [{
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": b64},
        }]

    raw = path.read_text(encoding="utf-8", errors="replace")
    ccd_text = _extract_ccd_sections(raw)
    if ccd_text is not None:
        print(f"[doc_utils] {path.name}: found CCD Results/Vital-Signs sections "
              f"({len(ccd_text)} chars) — using those instead of the full document.")
        text = ccd_text
    else:
        text = _html_to_text(raw)

    if len(text) > _MAX_TEXT_CHARS:
        print(f"[doc_utils] WARNING: {path.name} still {len(text)} chars after filtering — "
              f"truncating to {_MAX_TEXT_CHARS}. Extracted data may be incomplete.")
        text = text[:_MAX_TEXT_CHARS]
    return [{"type": "text", "text": f"--- Source file: {path.name} ---\n{text}"}]
