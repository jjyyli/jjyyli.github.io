# CV Workflow

This folder contains the LaTeX source and generated PDF for the CV. The
canonical academic data lives at the website repository root, not in this
folder.

## Project Structure

```text
.
├── README.md
├── cv.tex
├── cv.pdf
└── cv/
    └── generated/
        ├── publications.tex
        ├── talks.tex
        └── teaching.tex
```

## Canonical Data Sources

Manually edit these files from the repository root:

- `../data/publications.bib`
- `../data/talks.yml`
- `../data/teaching.yml`

Do not manually edit:

- `cv/generated/publications.tex`
- `cv/generated/talks.tex`
- `cv/generated/teaching.tex`

The generated files are produced by scripts and are included by `cv.tex`.

## Publications

Add a new publication or preprint by editing `../data/publications.bib`.

To add a preprint, use an `@article` entry with an arXiv-style journal field or
keywords/notes such as `preprint`, `working paper`, `under review`,
`under revision`, or `major revision`.

To move a paper from preprint to publication, update the same BibTeX entry:

- Replace the arXiv/preprint journal with the journal name.
- Add `volume`, `number`, and `pages` when available.
- Add `note = {To appear}` or `note = {Accepted}` if the paper is accepted but
  not yet fully published.

The CV generator classifies entries into `Preprints` and `Publications` from
the BibTeX metadata. Non-article entries, such as a thesis, are left out and
reported for manual review.

## Selected Invited Talks

Add invited talks by editing `../data/talks.yml`.

Talks are grouped by related paper or research work, not by exact talk title.
Use `paper_key` when the talk is tied to an entry in `data/publications.bib`; the CV
generator will use the BibTeX title when the key exists. If no paper applies,
set `paper_key: null` and provide a `display_label`.

Only appearances with both `include_in_cv: true` at the group level and
`invited: true` at the appearance level are shown in the CV.

## Teaching

Add or revise teaching experience by editing `../data/teaching.yml`.

Each teaching group has an institution and role, and each course can include:

- `title`: compact course title used in the CV
- `site_title`: fuller course title, often with a course code, used on the homepage
- `term`: semester/term shown on the homepage
- `years`: year text shown in the CV

## Regenerate Website and CV

From the repository root, run:

```bash
python3 scripts/update_all.py
```

This updates the homepage/publications/talks/teaching pages, regenerates the
CV publication, talk, and teaching fragments, and compiles `Resume/cv.pdf`.

To skip PDF compilation:

```bash
python3 scripts/update_all.py --skip-cv-pdf
```

## Compile the CV

If you only want to compile the PDF manually:

```bash
cd Resume
latexmk -pdf cv.tex
```

`cv.pdf` is kept here so the compiled CV is available for direct sharing.
