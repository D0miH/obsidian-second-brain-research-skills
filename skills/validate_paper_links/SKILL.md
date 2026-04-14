---
name: validate_paper_links
description: Validate paper note links against actual paper references and influence
---

## ✅ Validate Paper Links Skill

Validate all `[[Paper Title]]` links in a paper note against the actual paper's references and citation patterns.

**Goal:** Prevent:
1. Links to papers NOT referenced in the current paper (hallucination)
2. Links to papers with incorrect titles or formatting
3. Links to low-influence papers (cited once, not foundational)
4. Broken file names (`:` not exchanged to `-`)

---

## CRITICAL RULES

**A link should exist only if:**
1. ✅ The paper IS referenced in the current paper's bibliography/references
2. ✅ The paper is INFLUENTIAL (cited ≥2 times OR explicitly foundational/cited in intro/abstract)
3. ✅ Title is in exact Title Case matching the reference
4. ✅ File name properly formats `:` as `-` (e.g., `Attention - Is All You Need`)

**A link should be removed if:**
- ❌ Paper is NOT in the current paper's references
- ❌ Paper is cited only once in methods/results (low influence)
- ❌ Title formatting is incorrect
- ❌ File name violates naming convention

---

## WORKFLOW

### 0. Find modified papers (main session)

Read `.claude/vault_maintanance.md` and note the `validate_paper_links:` timestamp.

Default: incremental — only validate papers modified after that timestamp.
Convert timestamp (DD-MM-YYYY HH:MM) to YYYYMMDDHHMI format.
Run (from vault root): `touch -t YYYYMMDDHHMI /tmp/validate_ref && find "Reading/" -newer /tmp/validate_ref -name "*.md"`

If no papers were modified: report "All paper links already validated." and stop.
Only run full rescan if user explicitly requests it or no timestamp exists yet.

This produces a list of paper file paths to validate.

### 1. Spawn parallel subagents (one per paper)

For each paper file path from step 0, spawn one subagent using the Agent tool.
**Send all subagent calls in a single message** (parallel execution).

If there are >5 papers: process in batches of 5 — send one batch, wait for results, then send the next.

Pass each subagent the **PER-PAPER SUBAGENT PROMPT** below with the paper's file path filled in.

### 2. Collect and consolidate findings

Wait for all subagents to return. Merge their structured outputs into a single report grouped by severity across all papers:

**🔴 CRITICAL (remove immediately):**
- Papers not in references
- Papers cited only once in low-importance sections

**🟡 NEEDS FIXING:**
- Title case errors
- File name formatting errors (`:` not converted to `-`)

**🟢 OK:**
- Papers properly referenced, formatted, and influential

**❓ NEEDS USER JUDGMENT:**
- Borderline influence cases

### 3. Apply fixes (with user approval only)

- **Remove links:** Delete `[[Paper Title]]` lines from "🔗 Connections to Other Work"
- **Fix titles:** Correct Title Case and formatting to match references
- **Fix file names:** Ensure `:` → `-` conversion
- **Update note:** Save corrected paper note

### 4. Update vault_maintanance.md

After completing validation (regardless of whether fixes were applied):
- Run `date` via Bash to get the current system time
- Read `.claude/vault_maintanance.md`
- Update `validate_paper_links:` line to current date and time in format `DD-MM-YYYY HH:MM`
- Reset `papers_since_validate_links:` to `0`
- Write the updated file

---

## PER-PAPER SUBAGENT PROMPT

For each paper, pass this prompt to the Agent tool (replace `<PAPER_FILE_PATH>` with the actual path):

```
You are a paper link validator for an Obsidian research vault.
Vault root: {{VAULT_ROOT}}
Paper to validate: <PAPER_FILE_PATH>

STEP 1: Read paper note
- Read the paper note at the given path
- Extract: URL from frontmatter (must be arxiv.org/html/ format), paper title, authors, year
- Extract all [[Paper Title]] links from the "🔗 Connections to Other Work" section

STEP 2: Fetch references via extraction script
Run (from vault root):
python3 .claude/skills/validate_paper_links/extract_refs.py <url-from-frontmatter>

- Accepts arxiv.org/html/ or arxiv.org/abs/ URLs (converts automatically)
- Returns a JSON array of reference titles — zero AI tokens consumed
- Strategy 1 (HTML/LaTeXML): fast, preferred
- Strategy 2 (source tarball fallback): for old papers where HTML unavailable
- If script fails entirely (exit code 1): fall back to WebFetch with prompt "Extract ONLY bibliography/references section titles."

STEP 3: Validate each [[link]] in the paper note

Check 1 — Reference exists?
- Does this paper appear in the bibliography JSON? (match case-insensitively)
- If NO → FLAG CRITICAL: "Not referenced in paper"

Check 2 — Influence level (only if passes Check 1)
- Citations ≥2 in this paper = influential ✓
- Cited once but in abstract/intro = influential ✓
- Cited once only in methods/results = LOW influence → FLAG CRITICAL
- Borderline → FLAG JUDGMENT

Check 3 — Title formatting
- Is it Title Case matching the reference?
- Are colons `:` in reference converted to `-` in link?
- If mismatch → FLAG FIX_NEEDED with corrected form

Check 4 — File name validity
- Link text should match exact file name (`:` → `-`)
- If mismatch → FLAG FIX_NEEDED

STEP 4: Return findings in EXACTLY this format (nothing else):

PAPER: [[filename-without-extension]]
CRITICAL: [[link]] | reason
FIX_NEEDED: [[link]] | reason | corrected form: [[correct link]]
OK: [[link]]
JUDGMENT: [[link]] | reason

Use one line per link. If a category has no entries, omit that category header entirely.
If all links are OK, return only: PAPER: [[filename]] / ALL_OK
```

---

## TOKEN EFFICIENCY

- Each subagent runs `extract_refs.py` independently — zero AI tokens for reference extraction
- Subagents run in parallel — total wall-clock time ≈ time for the slowest single paper
- Main session cost: only consolidation + user interaction reasoning

**Avoid:**
- WebFetch for reference extraction (costs ~500–2000 tokens per paper)
- Sequential paper processing (use parallel subagents instead)
- PDF parsing or PDF URLs

---

## OUTPUT RULES

- Grouped by severity (CRITICAL → needs fixing → OK → judgment)
- File name / Link text / Issue / Suggested fix
- No prose, bullets only

---

## SELF-CHECK

✅ Did I find modified papers before spawning subagents?
✅ Did I spawn one subagent per paper (in parallel where possible)?
✅ Did I collect and consolidate findings from all subagents before presenting?
✅ Did I group findings by severity across all papers?
✅ Did I get user approval before removing or fixing links?
✅ Did I update vault_maintanance.md with current timestamp?
