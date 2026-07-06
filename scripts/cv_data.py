"""Shared data loading helpers for the CV and future website scripts."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CANONICAL_BIB_FILE = Path("publications.bib")
CANDIDATE_BIB_FILES = (CANONICAL_BIB_FILE,)


@dataclass(frozen=True)
class BibEntry:
    entry_type: str
    key: str
    fields: dict[str, str]
    index: int


def find_matching_delimiter(text: str, open_pos: int, open_char: str) -> int:
    close_char = "}" if open_char == "{" else ")"
    depth = 0
    in_quote = False
    escaped = False

    for pos in range(open_pos, len(text)):
        char = text[pos]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if in_quote:
            continue
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return pos
    raise ValueError(f"Unclosed BibTeX entry starting at character {open_pos}")


def split_top_level(text: str, separator: str = ",") -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    in_quote = False
    escaped = False

    for pos, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if in_quote:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif char == separator and depth == 0:
            parts.append(text[start:pos])
            start = pos + 1
    parts.append(text[start:])
    return parts


def find_top_level_comma(text: str) -> int:
    depth = 0
    in_quote = False
    escaped = False

    for pos, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if in_quote:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif char == "," and depth == 0:
            return pos
    return -1


def strip_wrapping_delimiters(value: str) -> str:
    value = value.strip()
    changed = True
    while changed and len(value) >= 2:
        changed = False
        if value[0] == "{" and value[-1] == "}":
            try:
                if find_matching_delimiter(value, 0, "{") == len(value) - 1:
                    value = value[1:-1].strip()
                    changed = True
            except ValueError:
                pass
        elif value[0] == '"' and value[-1] == '"':
            value = value[1:-1].strip()
            changed = True
    return value


def normalize_bibtex_value(raw_value: str) -> str:
    pieces = [strip_wrapping_delimiters(piece) for piece in split_top_level(raw_value.strip().rstrip(","), "#")]
    value = " ".join(piece for piece in pieces if piece)
    return re.sub(r"\s+", " ", value).strip()


def parse_bibtex(text: str) -> list[BibEntry]:
    entries: list[BibEntry] = []
    pos = 0

    while True:
        at_pos = text.find("@", pos)
        if at_pos == -1:
            break

        type_start = at_pos + 1
        type_end = type_start
        while type_end < len(text) and (text[type_end].isalnum() or text[type_end] in "_-"):
            type_end += 1
        entry_type = text[type_start:type_end].strip().lower()

        open_pos = type_end
        while open_pos < len(text) and text[open_pos].isspace():
            open_pos += 1
        if open_pos >= len(text) or text[open_pos] not in "{(":
            pos = type_end
            continue

        close_pos = find_matching_delimiter(text, open_pos, text[open_pos])
        body = text[open_pos + 1 : close_pos]
        pos = close_pos + 1

        if entry_type in {"comment", "preamble", "string"}:
            continue

        key_end = find_top_level_comma(body)
        if key_end == -1:
            continue

        key = body[:key_end].strip()
        fields_body = body[key_end + 1 :]
        fields: dict[str, str] = {}
        for field_text in split_top_level(fields_body):
            if "=" not in field_text:
                continue
            field_name, raw_value = field_text.split("=", 1)
            fields[field_name.strip().lower()] = normalize_bibtex_value(raw_value)

        entries.append(BibEntry(entry_type=entry_type, key=key, fields=fields, index=len(entries)))

    return entries


def locate_bib_file(explicit_path: Path | None = None) -> Path:
    if explicit_path is not None:
        if not explicit_path.exists():
            raise FileNotFoundError(f"BibTeX file not found: {explicit_path}")
        return explicit_path

    for candidate in CANDIDATE_BIB_FILES:
        if candidate.exists():
            return candidate

    candidates = ", ".join(str(path) for path in CANDIDATE_BIB_FILES)
    raise FileNotFoundError(f"No BibTeX file found. Checked: {candidates}")


def load_bib_entries(path: Path | None = None) -> tuple[Path, list[BibEntry]]:
    bib_path = locate_bib_file(path)
    return bib_path, parse_bibtex(bib_path.read_text(encoding="utf-8"))


def escape_latex(text: str) -> str:
    specials = {"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_"}
    escaped: list[str] = []
    pos = 0
    while pos < len(text):
        char = text[pos]
        if char == "\\":
            escaped.append(char)
            pos += 1
            if pos < len(text):
                escaped.append(text[pos])
                pos += 1
            continue
        escaped.append(specials.get(char, char))
        pos += 1
    return "".join(escaped)


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    lowered = value.lower()
    if lowered == "null":
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return ast.literal_eval(value)
    return value


def split_key_value(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise ValueError(f"Expected key/value pair: {text}")
    key, value = text.split(":", 1)
    return key.strip(), value.strip()


def parse_project_yaml_list(path: Path) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    current_group: dict[str, Any] | None = None
    current_nested_item: dict[str, Any] | None = None
    current_nested_key: str | None = None

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        text = raw_line.strip()

        if indent == 0 and text.startswith("- "):
            current_group = {}
            current_nested_item = None
            current_nested_key = None
            groups.append(current_group)
            remainder = text[2:].strip()
            if remainder:
                key, value = split_key_value(remainder)
                current_group[key] = parse_scalar(value)
        elif indent == 2:
            if current_group is None:
                raise ValueError(f"Line {line_number}: field found before a group")
            key, value = split_key_value(text)
            if value == "":
                current_group[key] = []
                current_nested_key = key
                current_nested_item = None
            else:
                current_group[key] = parse_scalar(value)
        elif indent == 4 and text.startswith("- "):
            if current_group is None or current_nested_key is None:
                raise ValueError(f"Line {line_number}: nested list item found before a list field")
            current_nested_item = {}
            current_group[current_nested_key].append(current_nested_item)
            remainder = text[2:].strip()
            if remainder:
                key, value = split_key_value(remainder)
                current_nested_item[key] = parse_scalar(value)
        elif indent == 6:
            if current_nested_item is None:
                raise ValueError(f"Line {line_number}: nested field found before a nested list item")
            key, value = split_key_value(text)
            current_nested_item[key] = parse_scalar(value)
        else:
            raise ValueError(f"Line {line_number}: unsupported YAML indentation")

    return groups


def load_yaml_list(path: Path) -> list[dict[str, Any]]:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return parse_project_yaml_list(path)

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        raise ValueError(f"Expected {path} to contain a YAML list")
    return data


def write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")
