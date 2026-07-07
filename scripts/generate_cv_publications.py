#!/usr/bin/env python3
"""Generate the CV Preprints and Publications sections from data/publications.bib."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cv_data import BibEntry, CANONICAL_BIB_FILE, escape_latex, load_bib_entries, write_text


DEFAULT_BIB = CANONICAL_BIB_FILE
DEFAULT_OUTPUT = Path("Resume/cv/generated/publications.tex")
ORDER_FIELDS = ("order", "sortkey", "numbering", "cvorder", "cv_order", "cv-number", "cvnumber")
PREPRINT_MARKERS = (
    "preprint",
    "working paper",
    "under review",
    "under revision",
    "major revision",
    "submitted",
)


@dataclass(frozen=True)
class ManualReview:
    key: str
    title: str
    reason: str


@dataclass(frozen=True)
class PublicationGenerationResult:
    bib_path: Path
    output_path: Path
    preprint_count: int
    publication_count: int
    manual_reviews: list[ManualReview]


def lower_fields(entry: BibEntry, *field_names: str) -> str:
    return " ".join(entry.fields.get(name, "") for name in field_names).lower()


def is_preprint_journal(journal: str) -> bool:
    lowered = journal.lower()
    return "arxiv" in lowered or "biorxiv" in lowered or "medrxiv" in lowered


def status_label(entry: BibEntry) -> str | None:
    note = entry.fields.get("note", "").lower()
    if "to appear" in note:
        return "To appear"
    if "accepted" in note:
        return "Accepted"
    if "in press" in note:
        return "In press"
    if "forthcoming" in note:
        return "Forthcoming"
    return None


def has_preprint_marker(entry: BibEntry) -> bool:
    haystack = lower_fields(entry, "note", "keywords", "journal")
    return any(marker in haystack for marker in PREPRINT_MARKERS)


def title_for_review(entry: BibEntry) -> str:
    return entry.fields.get("title", "(untitled)")


def classify_entries(entries: list[BibEntry]) -> tuple[list[BibEntry], list[BibEntry], list[ManualReview]]:
    preprints: list[BibEntry] = []
    publications: list[BibEntry] = []
    manual_reviews: list[ManualReview] = []

    for entry in entries:
        journal = entry.fields.get("journal", "").strip()
        status = status_label(entry)
        preprintish = has_preprint_marker(entry)
        preprint_journal = is_preprint_journal(journal)

        if entry.entry_type != "article":
            manual_reviews.append(
                ManualReview(
                    key=entry.key,
                    title=title_for_review(entry),
                    reason=f'entry type "{entry.entry_type}" is not automatically placed in Preprints or Publications',
                )
            )
            continue

        if status and journal and not preprint_journal:
            publications.append(entry)
        elif preprint_journal or preprintish:
            preprints.append(entry)
        elif journal:
            publications.append(entry)
        else:
            manual_reviews.append(
                ManualReview(
                    key=entry.key,
                    title=title_for_review(entry),
                    reason="missing journal/status/preprint information for classification",
                )
            )

    return preprints, publications, manual_reviews


def year_value(entry: BibEntry) -> int:
    match = re.search(r"\d{4}", entry.fields.get("year", ""))
    return int(match.group(0)) if match else 0


def arxiv_month_value(entry: BibEntry) -> int:
    text = " ".join(entry.fields.get(name, "") for name in ("journal", "eprint", "archiveprefix"))
    match = re.search(r"arxiv\s*:\s*(\d{2})(\d{2})\.", text, flags=re.IGNORECASE)
    if match:
        return int(match.group(2))
    return 0


def natural_key(value: str) -> tuple[Any, ...]:
    parts: list[Any] = []
    for piece in re.split(r"(\d+)", value.lower()):
        if piece.isdigit():
            parts.append(int(piece))
        elif piece:
            parts.append(piece)
    return tuple(parts)


def explicit_order(entry: BibEntry) -> tuple[int, Any] | None:
    for field_name in ORDER_FIELDS:
        value = entry.fields.get(field_name, "").strip()
        if not value:
            continue
        if re.fullmatch(r"\d+(?:\.\d+)?", value):
            return (0, float(value))
        return (1, natural_key(value))
    return None


def publication_default_sort_key(entry: BibEntry, current_year: int) -> tuple[int, int, int, int]:
    year = year_value(entry)
    status = status_label(entry)
    status_priority = 0 if status and year >= current_year else 1
    return (status_priority, -year, -arxiv_month_value(entry), entry.index)


def preprint_default_sort_key(entry: BibEntry) -> tuple[int, int, int]:
    return (-year_value(entry), -arxiv_month_value(entry), entry.index)


def sort_section(entries: list[BibEntry], section: str, current_year: int) -> list[BibEntry]:
    has_explicit_order = any(explicit_order(entry) is not None for entry in entries)

    if section == "publications":
        default_key = lambda entry: publication_default_sort_key(entry, current_year)
    else:
        default_key = lambda entry: preprint_default_sort_key(entry)

    if has_explicit_order:
        return sorted(
            entries,
            key=lambda entry: (
                explicit_order(entry) is None,
                explicit_order(entry) if explicit_order(entry) is not None else (9, ()),
                default_key(entry),
            ),
        )

    return sorted(entries, key=default_key)


def normalize_initials(text: str) -> str:
    tokens = []
    for token in text.split():
        if re.fullmatch(r"[A-Z]", token):
            tokens.append(f"{token}.")
        else:
            tokens.append(token)
    return " ".join(tokens)


def format_author_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip()
    if "," not in name:
        return normalize_initials(name)

    pieces = [piece.strip() for piece in name.split(",")]
    if len(pieces) == 2:
        last, given = pieces
        return normalize_initials(f"{given} {last}".strip())
    if len(pieces) >= 3:
        last, suffix, given = pieces[0], pieces[1], pieces[2]
        return normalize_initials(f"{given} {last} {suffix}".strip())
    return normalize_initials(name.replace(",", " "))


def format_authors(author_field: str) -> str:
    authors = [format_author_name(name) for name in re.split(r"\s+and\s+", author_field) if name.strip()]
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    return f"{', '.join(authors[:-1])}, and {authors[-1]}"


def format_volume_number_pages(entry: BibEntry) -> str:
    pieces: list[str] = []
    volume = entry.fields.get("volume", "").strip()
    number = entry.fields.get("number", "").strip()
    pages = entry.fields.get("pages", "").strip()

    if volume:
        volume_text = escape_latex(volume)
        if number:
            volume_text += f" ({escape_latex(number)})"
        pieces.append(volume_text)
    elif number:
        pieces.append(f"({escape_latex(number)})")

    if pages:
        pages_text = escape_latex(pages.replace("-", "--") if "--" not in pages else pages)
        if pieces:
            pieces[-1] += f", {pages_text}"
        else:
            pieces.append(pages_text)

    return " ".join(pieces)


def format_journal_line(entry: BibEntry) -> str:
    journal = escape_latex(entry.fields.get("journal", "").strip())
    status = status_label(entry)
    details = format_volume_number_pages(entry)

    if status:
        line = rf"\textit{{{status}, \textbf{{{journal}}}}}"
    else:
        line = rf"\textit{{\textbf{{{journal}}}}}"

    if details:
        line += f" {details}"
    return line


def format_entry(entry: BibEntry, include_journal: bool) -> list[str]:
    title = escape_latex(entry.fields.get("title", "").strip())
    authors = escape_latex(format_authors(entry.fields.get("author", "").strip()))
    lines = [
        rf"  \item \textit{{{title}}}\\",
        f"  {authors}" + (r"\\" if include_journal else ""),
    ]
    if include_journal:
        lines.append(f"  {format_journal_line(entry)}")
    return lines


def render_section(name: str, entries: list[BibEntry], include_journal: bool) -> list[str]:
    lines = [
        rf"\section{{{name}}}",
        r"\begin{enumerate}[label={[{\arabic*}]}, leftmargin=*]",
    ]
    for entry in entries:
        lines.extend(format_entry(entry, include_journal=include_journal))
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    lines.append(r"\end{enumerate}")
    return lines


def render_publications_file(
    bib_path: Path,
    preprints: list[BibEntry],
    publications: list[BibEntry],
    manual_reviews: list[ManualReview],
) -> str:
    lines = [
        "% This file is generated by scripts/generate_cv_publications.py.",
        f"% Source BibTeX file: {bib_path.as_posix()}",
        "% Do not edit this file manually; update data/publications.bib and rerun the generator.",
    ]

    if manual_reviews:
        lines.append("%")
        lines.append("% Manual review needed:")
        for review in manual_reviews:
            lines.append(f"% - {review.key}: {review.title} ({review.reason}).")

    lines.extend(["", r"\vspace{20pt}"])
    lines.extend(render_section("Publications", publications, include_journal=True))
    lines.extend(["", r"\vspace{5pt}"])
    lines.extend(render_section("Preprints", preprints, include_journal=False))
    lines.append("")
    return "\n".join(lines)


def generate_publications(
    bib_path: Path | None = None,
    output_path: Path = DEFAULT_OUTPUT,
    current_year: int | None = None,
) -> PublicationGenerationResult:
    if current_year is None:
        current_year = dt.date.today().year

    resolved_bib_path, entries = load_bib_entries(bib_path or DEFAULT_BIB)
    preprints, publications, manual_reviews = classify_entries(entries)
    preprints = sort_section(preprints, "preprints", current_year)
    publications = sort_section(publications, "publications", current_year)

    contents = render_publications_file(resolved_bib_path, preprints, publications, manual_reviews)
    write_text(output_path, contents)
    return PublicationGenerationResult(
        bib_path=resolved_bib_path,
        output_path=output_path,
        preprint_count=len(preprints),
        publication_count=len(publications),
        manual_reviews=manual_reviews,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bib", type=Path, default=DEFAULT_BIB, help="Path to the canonical BibTeX file.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Generated LaTeX output path.")
    parser.add_argument(
        "--current-year",
        type=int,
        default=dt.date.today().year,
        help="Current year for accepted/to-appear publication ordering.",
    )
    args = parser.parse_args()

    result = generate_publications(args.bib, args.output, args.current_year)
    print(f"BibTeX file: {result.bib_path}")
    print(f"Output file: {result.output_path}")
    print(f"Preprints: {result.preprint_count}")
    print(f"Publications: {result.publication_count}")
    if result.manual_reviews:
        print("Manual review needed:")
        for review in result.manual_reviews:
            print(f"- {review.key}: {review.title} ({review.reason})")
    else:
        print("Manual review needed: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
