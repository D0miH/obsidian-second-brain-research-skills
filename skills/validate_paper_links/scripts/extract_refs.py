#!/usr/bin/env python3
"""
Extract paper titles from an arXiv paper's bibliography.

Usage:
    python3 extract_refs.py <arxiv-url>

Output:
    JSON array of paper titles, one per bibliography entry.
    Errors are written to stderr; exit code 1 on failure.

Strategy:
  1. Fetch the arXiv HTML version (LaTeXML) and parse ltx_bibliography — fast,
     structured, preferred. Frontmatter should always use /html/ URLs.
  2. If HTML is unavailable (old papers, 404, no ltx_bibliography), fall back to
     downloading the arXiv source tarball (arxiv.org/src/<id>), extracting .bib
     files, and parsing BibTeX title fields.

Handles two LaTeXML bibliography formats:

  Format A (numeric refs) — block[0]=authors, block[1]=title+year:
    <li class="ltx_bibitem">
      <span class="ltx_tag …">[1]</span>
      <span class="ltx_bibblock">Author Names</span>
      <span class="ltx_bibblock">Paper Title, Month YYYY.</span>
    </li>

  Format B (author-year refs) — title is in ltx_bib_title span:
    <li class="ltx_bibitem ltx_bib_*">
      <span class="ltx_tag ltx_bib_author-year …">Author (YYYY)</span>
      <span class="ltx_bibblock"><span class="ltx_bib_title">Paper Title</span>.</span>
      <span class="ltx_bibblock">Venue info …</span>
    </li>
"""

import sys
import re
import io
import json
import tarfile
import html as html_lib
import urllib.request


def strip_tags(html: str) -> str:
    """Remove all HTML tags from a string."""
    return re.sub(r'<[^>]+>', '', html)


def clean_title(text: str) -> str:
    """Normalise and trim bibliography strings down to title text."""
    text = html_lib.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Format A often includes venue metadata after the title.
    # Trim common tails while keeping the title itself.
    tail_patterns = [
        r'\.\s+In\s+Proceedings\b',
        r'\.\s+In\s+the\s+Proceedings\b',
        r'\.\s+Proceedings\s+of\b',
        r'\.\s+arXiv\s+preprint\b',
        r'\.\s+Association\s+for\s+Computational\s+Linguistics\b',
        r'\.\s+ACM\b',
        r'\.\s+IEEE\b',
        r'\.\s+Springer\b',
    ]
    for pat in tail_patterns:
        text = re.split(pat, text, maxsplit=1, flags=re.IGNORECASE)[0]

    # Strip trailing "Month YYYY." or ", YYYY."
    text = re.sub(
        r',?\s*(?:January|February|March|April|May|June|July|August|'
        r'September|October|November|December)?\s*(?:20|19)\d{2}\.?\s*$',
        '', text, flags=re.IGNORECASE,
    ).strip().rstrip('.,').strip()
    return text


def extract_paper_id(url: str) -> str | None:
    """Extract arXiv paper ID (with optional version suffix) from a URL."""
    m = re.search(r'arxiv\.org/(?:abs|pdf|html|src)/([^\s?#/]+(?:v\d+)?)', url)
    return m.group(1) if m else None


def to_html_url(url: str) -> str:
    """Convert any arXiv abs/pdf/src URL to the HTML version."""
    return re.sub(
        r'(arxiv\.org)/(abs|pdf|src)/([^\s?#]+)',
        r'\1/html/\3',
        url,
    )


# ---------------------------------------------------------------------------
# Strategy 1: arXiv HTML (LaTeXML)
# ---------------------------------------------------------------------------

def _fetch_html_refs(url: str) -> list[str]:
    """
    Fetch arXiv HTML page and extract bibliography titles via LaTeXML parsing.
    Returns an empty list if HTML is unavailable or has no bibliography section.
    """
    html_url = to_html_url(url)

    req = urllib.request.Request(html_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except Exception as exc:
        print(f'INFO: HTML not available ({exc})', file=sys.stderr)
        return []

    bib_start = html.find('class="ltx_bibliography"')
    if bib_start == -1:
        print('INFO: no ltx_bibliography in HTML — trying source fallback', file=sys.stderr)
        return []

    # Cap at 150 KB to avoid processing the rest of the document
    bib_html = html[bib_start: bib_start + 150_000]

    bibitem_re = re.compile(
        r'<li[^>]+class="[^"]*ltx_bibitem[^"]*"[^>]*>(.*?)</li>',
        re.DOTALL,
    )
    bibblock_re = re.compile(
        r'<span[^>]+class="[^"]*ltx_bibblock[^"]*"[^>]*>(.*?)</span\s*>',
        re.DOTALL,
    )
    bib_title_re = re.compile(
        r'<span[^>]+class="[^"]*ltx_bib_title[^"]*"[^>]*>(.*?)</span\s*>',
        re.DOTALL,
    )

    titles = []
    for item in bibitem_re.finditer(bib_html):
        item_html = item.group(1)

        # --- Format B: explicit ltx_bib_title span (author-year style) ---
        title_match = bib_title_re.search(item_html)
        if title_match:
            title = clean_title(strip_tags(title_match.group(1)))
            if len(title) > 5:
                titles.append(title)
            continue

        # --- Format A: numeric refs, block[0]=authors block[1]=title+year ---
        blocks = bibblock_re.findall(item_html)
        if len(blocks) >= 2:
            raw = strip_tags(blocks[1])
        elif blocks:
            raw = strip_tags(blocks[0])
        else:
            continue

        title = clean_title(raw)
        if len(title) > 5:
            titles.append(title)

    return titles


# ---------------------------------------------------------------------------
# Strategy 2: arXiv source tarball (.bib parsing)
# ---------------------------------------------------------------------------

def _parse_bibtex_titles(bib_text: str) -> list[str]:
    """
    Extract title field values from BibTeX source using brace-count parsing.
    Handles nested braces (e.g. {{BERT}: Pre-training…}) and quoted values.
    """
    titles = []
    for m in re.finditer(r'\btitle\s*=\s*', bib_text, re.IGNORECASE):
        pos = m.end()
        if pos >= len(bib_text):
            continue
        ch = bib_text[pos]
        if ch == '{':
            # Track brace depth to find matching close brace
            depth = 0
            for i in range(pos, len(bib_text)):
                if bib_text[i] == '{':
                    depth += 1
                elif bib_text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        raw = bib_text[pos + 1: i]
                        # Strip one layer of outer protective braces e.g. {{Title}}
                        raw = re.sub(r'^\{(.*)\}$', r'\1', raw.strip(), flags=re.DOTALL)
                        # Remove remaining inline brace groups e.g. {BERT}
                        raw = re.sub(r'\{([^{}]*)\}', r'\1', raw)
                        title = clean_title(raw)
                        if len(title) > 5:
                            titles.append(title)
                        break
        elif ch == '"':
            end = bib_text.find('"', pos + 1)
            if end != -1:
                raw = bib_text[pos + 1: end]
                title = clean_title(raw)
                if len(title) > 5:
                    titles.append(title)
    return titles


def _fetch_source_refs(url: str) -> list[str]:
    """
    Download the arXiv source tarball and extract titles from all .bib files.
    Tries the versioned paper ID first, then the base ID without version suffix.
    """
    paper_id = extract_paper_id(url)
    if not paper_id:
        print('ERROR: could not extract paper ID from URL', file=sys.stderr)
        return []

    # Try versioned ID first (e.g. 2602.16980v2), then base (e.g. 2602.16980)
    ids_to_try = [paper_id]
    base_id = re.sub(r'v\d+$', '', paper_id)
    if base_id != paper_id:
        ids_to_try.append(base_id)

    data = None
    for pid in ids_to_try:
        src_url = f'https://arxiv.org/src/{pid}'
        req = urllib.request.Request(src_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            break
        except Exception as exc:
            print(f'INFO: source fetch failed for {src_url}: {exc}', file=sys.stderr)

    if not data:
        print('ERROR: could not download source tarball', file=sys.stderr)
        return []

    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
            bib_members = [m for m in tar.getmembers() if m.name.endswith('.bib')]
            if not bib_members:
                print('ERROR: no .bib files found in source tarball', file=sys.stderr)
                return []
            titles = []
            for member in bib_members:
                f = tar.extractfile(member)
                if f:
                    bib_text = f.read().decode('utf-8', errors='replace')
                    titles.extend(_parse_bibtex_titles(bib_text))
            return titles
    except Exception as exc:
        print(f'ERROR: parsing source tarball failed: {exc}', file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def fetch_refs(url: str) -> list[str]:
    """
    Fetch bibliography titles for an arXiv paper.
    Tries arXiv HTML first; falls back to source tarball .bib parsing.
    """
    titles = _fetch_html_refs(url)
    if titles:
        return titles
    print('INFO: falling back to source tarball…', file=sys.stderr)
    return _fetch_source_refs(url)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: extract_refs.py <arxiv-url>', file=sys.stderr)
        sys.exit(1)
    result = fetch_refs(sys.argv[1])
    if not result:
        sys.exit(1)
    print(json.dumps(result, indent=2, ensure_ascii=False))
