#!/usr/bin/env python3
"""Regenerate all LaTeX sections that are produced from canonical data files."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from cv_data import CANONICAL_BIB_FILE
from generate_cv_publications import DEFAULT_OUTPUT as PUBLICATIONS_OUTPUT
from generate_cv_publications import generate_publications
from generate_cv_talks import DEFAULT_INPUT as TALKS_INPUT
from generate_cv_talks import DEFAULT_OUTPUT as TALKS_OUTPUT
from generate_cv_talks import generate_talks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bib", type=Path, default=CANONICAL_BIB_FILE, help="Canonical publication BibTeX file.")
    parser.add_argument("--talks", type=Path, default=TALKS_INPUT, help="Canonical talks YAML file.")
    parser.add_argument("--publications-output", type=Path, default=PUBLICATIONS_OUTPUT)
    parser.add_argument("--talks-output", type=Path, default=TALKS_OUTPUT)
    parser.add_argument(
        "--current-year",
        type=int,
        default=dt.date.today().year,
        help="Current year for accepted/to-appear publication ordering.",
    )
    args = parser.parse_args()

    publications = generate_publications(args.bib, args.publications_output, args.current_year)
    talks = generate_talks(args.talks, args.talks_output, args.bib)

    print("Generated CV sections:")
    print(f"- Publications source: {publications.bib_path}")
    print(f"- Publications output: {publications.output_path}")
    print(f"- Preprints: {publications.preprint_count}")
    print(f"- Publications: {publications.publication_count}")
    print(f"- Talks source: {talks.input_path}")
    print(f"- Talks output: {talks.output_path}")
    print(f"- Selected invited talk groups: {talks.included_group_count}")
    print(f"- Selected invited appearances: {talks.included_appearance_count}")

    review_items: list[str] = []
    review_items.extend(
        f"{review.key}: {review.title} ({review.reason})" for review in publications.manual_reviews
    )
    review_items.extend(talks.manual_review_items)
    if review_items:
        print("Manual review needed:")
        for item in review_items:
            print(f"- {item}")
    else:
        print("Manual review needed: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
