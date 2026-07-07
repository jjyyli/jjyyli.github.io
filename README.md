# Jingyang Li Personal Homepage

This repository builds the Jekyll site at <https://jjyyli.github.io>.

## Main Content

- `_pages/about.md`: homepage
- `_pages/publications.md`: generated publications page
- `_pages/talks.md`: generated selected talks page
- `_pages/teaching.md`: generated teaching page
- `data/publications.bib`: canonical publication data
- `data/talks.yml`: canonical talk data
- `data/teaching.yml`: canonical teaching data
- `_data/navigation.yml`: top navigation links

## Update Website and CV

Publications, selected invited talks, and teaching are generated from the canonical data files above.
Run this after editing `data/publications.bib`, `data/talks.yml`, or `data/teaching.yml`:

```bash
python3 scripts/update_all.py
```

This updates:

- `_pages/about.md`
- `_pages/publications.md`
- `_pages/talks.md`
- `_pages/teaching.md`
- `Resume/cv/generated/publications.tex`
- `Resume/cv/generated/talks.tex`
- `Resume/cv/generated/teaching.tex`
- `Resume/cv.pdf`

To update the website and CV TeX fragments without compiling the PDF:

```bash
python3 scripts/update_all.py --skip-cv-pdf
```

You can still regenerate only the website pages with:

```bash
python3 scripts/generate_site_pages.py
```

## Preview Locally

```bash
bundle install
bundle exec jekyll serve -l -H localhost
```

## Theme Files

Files that normally do not need day-to-day edits are grouped under:

- `_theme/`: Jekyll layouts, includes, and Sass source
- `assets/theme/`: compiled theme assets loaded by the browser
