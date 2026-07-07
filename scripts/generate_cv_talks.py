#!/usr/bin/env python3
"""Generate the CV Selected Invited Talks section from data/talks.yml."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cv_data import CANONICAL_BIB_FILE, escape_latex, load_bib_entries, load_yaml_list, write_text


DEFAULT_INPUT = Path("data/talks.yml")
DEFAULT_OUTPUT = Path("Resume/cv/generated/talks.tex")
DEFAULT_BIB = CANONICAL_BIB_FILE


@dataclass(frozen=True)
class TalkGenerationResult:
    input_path: Path
    output_path: Path
    bib_path: Path | None
    yaml_group_count: int
    included_group_count: int
    included_appearance_count: int
    excluded_appearances: list[str]
    manual_review_items: list[str]


def load_bib_titles(explicit_path: Path | None) -> tuple[Path | None, dict[str, str], list[str]]:
    try:
        bib_path, entries = load_bib_entries(explicit_path or DEFAULT_BIB)
    except FileNotFoundError as exc:
        return None, {}, [str(exc)]

    titles = {entry.key: entry.fields.get("title", "") for entry in entries if entry.fields.get("title")}
    return bib_path, titles, []


def truthy(value: Any) -> bool:
    return value is True


def group_label(group: dict[str, Any]) -> str:
    return str(group.get("display_label") or group.get("paper_title") or group.get("paper_key") or "Untitled work")


def selected_appearances(group: dict[str, Any]) -> list[dict[str, Any]]:
    if not truthy(group.get("include_in_cv")):
        return []
    return [appearance for appearance in group.get("appearances", []) if truthy(appearance.get("invited"))]


def title_for_group(group: dict[str, Any], bib_titles: dict[str, str], issues: list[str]) -> str | None:
    paper_key = group.get("paper_key")
    yaml_title = group.get("paper_title")
    display_label = group.get("display_label")

    if paper_key:
        if paper_key in bib_titles:
            return bib_titles[paper_key]
        if yaml_title:
            issues.append(f'{paper_key}: BibTeX key not found; using paper_title from data/talks.yml')
            return str(yaml_title)
        issues.append(f'{paper_key}: BibTeX key not found and paper_title is missing')
        return str(display_label or paper_key)

    if yaml_title:
        return str(yaml_title)
    if display_label:
        return None

    issues.append("A talk group has neither paper_key, paper_title, nor display_label")
    return None


def appearance_text(appearance: dict[str, Any]) -> str:
    pieces = [str(appearance.get("venue", "")).strip()]
    location = str(appearance.get("location", "")).strip()
    date = str(appearance.get("date", "")).strip()
    if location:
        pieces.append(location)
    if date:
        pieces.append(date)
    return ", ".join(piece for piece in pieces if piece)


def validate_groups(groups: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    for group in groups:
        label = group_label(group)
        if "appearances" not in group:
            issues.append(f"{label}: missing appearances list")
            continue
        if not isinstance(group["appearances"], list):
            issues.append(f"{label}: appearances must be a list")
            continue
        if "include_in_cv" not in group:
            issues.append(f"{label}: missing include_in_cv flag")
        for appearance in group["appearances"]:
            if not appearance.get("venue"):
                issues.append(f"{label}: an appearance is missing venue")
            if not appearance.get("date"):
                issues.append(f"{label}: an appearance is missing date")
            if "invited" not in appearance:
                issues.append(f"{label}: {appearance.get('venue', '(unknown venue)')} is missing invited flag")
    return issues


def excluded_appearances(groups: list[dict[str, Any]]) -> list[str]:
    excluded: list[str] = []
    for group in groups:
        label = group_label(group)
        for appearance in group.get("appearances", []):
            if truthy(group.get("include_in_cv")) and truthy(appearance.get("invited")):
                continue
            reasons = []
            if not truthy(group.get("include_in_cv")):
                reasons.append("include_in_cv=false")
            if not truthy(appearance.get("invited")):
                reasons.append("invited=false")
            excluded.append(f"{label}: {appearance_text(appearance)} ({', '.join(reasons)})")
    return excluded


def render_group(group: dict[str, Any], appearances: list[dict[str, Any]], title: str | None) -> list[str]:
    if title:
        first_line = rf"  \item Related paper: \textit{{{escape_latex(title)}}}"
    else:
        first_line = rf"  \item Research topic: \textit{{{escape_latex(group_label(group))}}}"

    lines = [
        first_line,
        r"  \begin{itemize}[label={}, leftmargin=0pt, labelsep=0pt, itemindent=0pt, itemsep=0pt, topsep=0pt]",
    ]
    for appearance in appearances:
        lines.append(rf"    \item {{{escape_latex(appearance_text(appearance))}}}")
    lines.append(r"  \end{itemize}")
    return lines


def render_talks_file(
    input_path: Path,
    bib_path: Path | None,
    groups: list[dict[str, Any]],
    bib_titles: dict[str, str],
    issues: list[str],
    excluded: list[str],
) -> tuple[str, int, int, list[str]]:
    selected_groups: list[tuple[dict[str, Any], list[dict[str, Any]], str | None]] = []
    render_issues = list(issues)

    for group in groups:
        appearances = selected_appearances(group)
        if not appearances:
            continue
        title = title_for_group(group, bib_titles, render_issues)
        selected_groups.append((group, appearances, title))

    lines = [
        "% This file is generated by scripts/generate_cv_talks.py.",
        f"% Source data file: {input_path.as_posix()}",
    ]
    if bib_path is not None:
        lines.append(f"% BibTeX title source: {bib_path.as_posix()}")
    lines.append("% Do not edit this file manually; update data/talks.yml and rerun the generator.")

    if render_issues:
        lines.append("%")
        lines.append("% Manual review needed:")
        for issue in render_issues:
            lines.append(f"% - {issue}.")

    if excluded:
        lines.append("%")
        lines.append("% Excluded from the CV by include_in_cv/invited flags:")
        for item in excluded:
            lines.append(f"% - {item}.")

    lines.extend(["", r"\vspace{5pt}", r"\section{Selected Invited Talks}", r"\begin{itemize}[leftmargin=*]"])

    for group, appearances, title in selected_groups:
        lines.extend(render_group(group, appearances, title))
        lines.append("")

    lines.append(r"  \vspace{-5pt}")
    lines.append(r"\end{itemize}")
    lines.append("")

    included_appearances = sum(len(appearances) for _, appearances, _ in selected_groups)
    return "\n".join(lines), len(selected_groups), included_appearances, render_issues


def generate_talks(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    bib_path: Path | None = DEFAULT_BIB,
) -> TalkGenerationResult:
    groups = load_yaml_list(input_path)
    resolved_bib_path, bib_titles, bib_issues = load_bib_titles(bib_path)
    validation_issues = validate_groups(groups)
    excluded = excluded_appearances(groups)
    contents, included_groups, included_appearances, manual_review_items = render_talks_file(
        input_path=input_path,
        bib_path=resolved_bib_path,
        groups=groups,
        bib_titles=bib_titles,
        issues=bib_issues + validation_issues,
        excluded=excluded,
    )
    write_text(output_path, contents)
    return TalkGenerationResult(
        input_path=input_path,
        output_path=output_path,
        bib_path=resolved_bib_path,
        yaml_group_count=len(groups),
        included_group_count=included_groups,
        included_appearance_count=included_appearances,
        excluded_appearances=excluded,
        manual_review_items=manual_review_items,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to talks YAML data.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Generated LaTeX output path.")
    parser.add_argument("--bib", type=Path, default=DEFAULT_BIB, help="Optional BibTeX file for canonical titles.")
    args = parser.parse_args()

    result = generate_talks(args.input, args.output, args.bib)
    print(f"Input file: {result.input_path}")
    print(f"Output file: {result.output_path}")
    if result.bib_path is not None:
        print(f"BibTeX title source: {result.bib_path}")
    print(f"Research-work groups in YAML: {result.yaml_group_count}")
    print(f"Research-work groups included in CV: {result.included_group_count}")
    print(f"Invited appearances included in CV: {result.included_appearance_count}")
    if result.excluded_appearances:
        print("Excluded appearances:")
        for item in result.excluded_appearances:
            print(f"- {item}")
    else:
        print("Excluded appearances: none")
    if result.manual_review_items:
        print("Manual review needed:")
        for issue in result.manual_review_items:
            print(f"- {issue}")
    else:
        print("Manual review needed: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
