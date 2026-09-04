from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ORDINAL_RE = re.compile(r"^\s*(\d{1,7})\s*[\.\)\]\-:]\s*")
CONTROL_TOKEN_RE = re.compile(r"<\|[^|>]+(?::[^|>]*)?\|>")


@dataclass(slots=True)
class ParagraphItem:
    sequence: int
    source_number: int | None
    spoken_text: str
    filename: str


def read_text_file(path: str | Path) -> str:
    raw = Path(path).read_bytes()
    encodings = ("utf-8-sig", "utf-8", "utf-16", "cp1258", "cp1252")
    for encoding in encodings:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def split_paragraphs(text: str) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []
    return [p.strip() for p in re.split(r"\n[\t ]*\n+", normalized) if p.strip()]


def strip_leading_ordinal(paragraph: str) -> tuple[int | None, str]:
    match = ORDINAL_RE.match(paragraph)
    if not match:
        return None, paragraph.strip()
    number = int(match.group(1))
    return number, paragraph[match.end() :].strip()


def _ascii_slug(text: str, max_words: int = 5) -> str:
    text = CONTROL_TOKEN_RE.sub(" ", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("Đ", "D").replace("đ", "d")
    words = re.findall(r"[A-Za-z0-9]+", text)
    words = words[:max_words]
    return "_".join(words) if words else "audio"


def make_filename(number: int, text: str, width: int = 3) -> str:
    return f"{number:0{width}d}_{_ascii_slug(text, 5)}.wav"


def parse_document(text: str) -> list[ParagraphItem]:
    paragraphs = split_paragraphs(text)
    width = max(3, len(str(max(len(paragraphs), 1))))
    items: list[ParagraphItem] = []
    used: set[str] = set()

    for sequence, paragraph in enumerate(paragraphs, start=1):
        source_number, spoken = strip_leading_ordinal(paragraph)
        if not spoken:
            continue
        output_number = source_number if source_number is not None else sequence
        base = make_filename(output_number, spoken, width)
        filename = base
        collision = 2
        while filename.lower() in used:
            stem = Path(base).stem
            filename = f"{stem}_{collision}.wav"
            collision += 1
        used.add(filename.lower())
        items.append(
            ParagraphItem(
                sequence=sequence,
                source_number=source_number,
                spoken_text=spoken,
                filename=filename,
            )
        )
    return items
