#!/usr/bin/env python3
"""Update website pages and the CV from the canonical data files."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from generate_cv_publications import generate_publications  # noqa: E402
from generate_cv_talks import generate_talks  # noqa: E402
from generate_teaching import generate_teaching  # noqa: E402
from generate_site_pages import generate_site_pages  # noqa: E402


BIB_PATH = REPO_ROOT / "data/publications.bib"
TALKS_PATH = REPO_ROOT / "data/talks.yml"
TEACHING_PATH = REPO_ROOT / "data/teaching.yml"
RESUME_DIR = REPO_ROOT / "Resume"
CV_TEX = RESUME_DIR / "cv.tex"
CV_PUBLICATIONS_OUTPUT = RESUME_DIR / "cv/generated/publications.tex"
CV_TALKS_OUTPUT = RESUME_DIR / "cv/generated/talks.tex"
CV_TEACHING_OUTPUT = RESUME_DIR / "cv/generated/teaching.tex"
TEACHING_PAGE = REPO_ROOT / "_pages/teaching.md"


@dataclass(frozen=True)
class CompileResult:
    skipped: bool
    command: str | None


def run_command(command: list[str], cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, command)


def compile_cv_pdf(skip: bool) -> CompileResult:
    if skip:
        return CompileResult(skipped=True, command=None)

    if not CV_TEX.exists():
        raise FileNotFoundError(f"CV source not found: {CV_TEX.relative_to(REPO_ROOT)}")

    latexmk = shutil.which("latexmk")
    if latexmk:
        command = [latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error", CV_TEX.name]
        run_command(command, RESUME_DIR)
        return CompileResult(skipped=False, command="latexmk")

    pdflatex = shutil.which("pdflatex")
    if pdflatex:
        command = [pdflatex, "-interaction=nonstopmode", "-halt-on-error", CV_TEX.name]
        run_command(command, RESUME_DIR)
        run_command(command, RESUME_DIR)
        return CompileResult(skipped=False, command="pdflatex")

    raise RuntimeError("Neither latexmk nor pdflatex was found; rerun with --skip-cv-pdf to skip PDF compilation.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--current-year",
        type=int,
        default=dt.date.today().year,
        help="Current year for accepted/to-appear publication ordering.",
    )
    parser.add_argument(
        "--skip-cv-pdf",
        action="store_true",
        help="Regenerate CV TeX fragments but do not compile Resume/cv.pdf.",
    )
    args = parser.parse_args()

    site = generate_site_pages(
        bib=BIB_PATH,
        talks=TALKS_PATH,
        home_page=REPO_ROOT / "_pages/about.md",
        publications_page=REPO_ROOT / "_pages/publications.md",
        talks_page=REPO_ROOT / "_pages/talks.md",
        current_year=args.current_year,
    )
    publications = generate_publications(BIB_PATH, CV_PUBLICATIONS_OUTPUT, args.current_year)
    talks = generate_talks(TALKS_PATH, CV_TALKS_OUTPUT, BIB_PATH)
    teaching = generate_teaching(TEACHING_PATH, CV_TEACHING_OUTPUT, TEACHING_PAGE)
    compile_result = compile_cv_pdf(args.skip_cv_pdf)

    print("Updated website pages:")
    print(f"- Homepage: {site.home_page.relative_to(REPO_ROOT)}")
    print(f"- Publications page: {site.publications_page.relative_to(REPO_ROOT)}")
    print(f"- Talks page: {site.talks_page.relative_to(REPO_ROOT)}")
    print(f"- Teaching page: {teaching.site_output_path.relative_to(REPO_ROOT)}")
    print("Updated CV files:")
    print(f"- Publications fragment: {publications.output_path.relative_to(REPO_ROOT)}")
    print(f"- Talks fragment: {talks.output_path.relative_to(REPO_ROOT)}")
    print(f"- Teaching fragment: {teaching.cv_output_path.relative_to(REPO_ROOT)}")
    if compile_result.skipped:
        print("- CV PDF: skipped")
    else:
        print(f"- CV PDF: {CV_TEX.with_suffix('.pdf').relative_to(REPO_ROOT)} via {compile_result.command}")

    review_items: list[str] = []
    review_items.extend(f"{review.key}: {review.title} ({review.reason})" for review in publications.manual_reviews)
    review_items.extend(talks.manual_review_items)
    if site.manual_review_count:
        review_items.append(f"{site.manual_review_count} publication item(s) omitted from website pending manual review")

    if review_items:
        print("Manual review needed:")
        for item in review_items:
            print(f"- {item}")
    else:
        print("Manual review needed: none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
