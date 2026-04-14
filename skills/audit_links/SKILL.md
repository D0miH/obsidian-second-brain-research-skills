---
name: audit_links
description: Validate vault graph consistency and structural integrity
---

## 🔍 Audit Links Skill

Fast audit of vault structure to catch:
- Orphan papers (not linked to any project)
- Orphan projects (not linked to any MOC)
- Broken bidirectional links (paper→project without reciprocal project→paper)
- Forbidden concept links (e.g., `[[Attention Mechanism]]`)
- Papers linking directly to MOCs (forbidden)
- Malformed wiki links

---

## CRITICAL RULES

**Vault constraints (non-negotiable):**
1. Every paper in `Reading/` must link to ≥1 project in `Projects/`
2. Every project in `Projects/` must link to ≥1 MOC in `MOCs/`
3. Bidirectional links: If paper→project exists, project→paper must exist
4. Papers **never** link directly to MOCs
5. Papers link **only** to projects and other papers
6. Concept/method/technique links forbidden (e.g., `[[Transformer]]`, `[[Attention Mechanism]]`)

---

## WORKFLOW

### 1. Spawn scan subagent

Use the Agent tool to spawn a subagent. Pass it the prompt from the **SCAN SUBAGENT PROMPT** section below verbatim. Wait for the subagent to return its structured findings before proceeding.

### 2. Present findings to user

Parse the subagent's output and display violations grouped by severity:

1. **Orphan papers** (not linked to any project)
2. **Orphan projects** (not linked to any MOC)
3. **Broken bidirectional links** (paper→project without project→paper)
4. **Forbidden concept links** (in papers)
5. **Forbidden paper→MOC links**
6. **Malformed links** (broken wiki syntax)

Each violation: file name + issue + suggested fix. If subagent returned `NO_VIOLATIONS`, report clean audit.

Prioritize by severity (orphans > broken bidirectional > concept links).
Offer fixes: "Should I remove this link?" / "Should I add reciprocal link?"

### 3. Apply fixes (with user approval only)

- Remove orphan papers/projects (ask first)
- Fix broken bidirectional links
- Remove forbidden concept links
- Remove paper→MOC links

### 4. Update vault_maintanance.md

After completing the audit (regardless of whether fixes were applied):
- Run `date` via Bash to get the current system time
- Read `.claude/vault_maintanance.md`
- Update `audit_links:` line to current date and time in format `DD-MM-YYYY HH:MM`
- Reset `papers_since_audit_links:` to `0`
- Reset `projects_since_audit_links:` to `0`
- Write the updated file

---

## SCAN SUBAGENT PROMPT

Pass this prompt verbatim to the Agent tool:

```
You are a vault structure auditor for an Obsidian research vault.
Vault root: {{VAULT_ROOT}}

STEP 1: Get audit scope
Read `.claude/vault_maintanance.md` and note the `audit_links:` timestamp.
Default: incremental scan — only files modified after that timestamp.
Convert the timestamp (DD-MM-YYYY HH:MM) to YYYYMMDDHHMI format for `touch -t`.
Run: touch -t YYYYMMDDHHMI /tmp/audit_ref && find "Reading/" "Projects/" "MOCs/" -newer /tmp/audit_ref
(Run this bash command from the vault root directory)
Only do a full scan if no audit_links: timestamp exists yet.

STEP 2: Scan for violations
Exclude: Inbox/, Daily Notes/
For Archive/: skip orphan checks, but include in bidirectional validation.

For papers in Reading/:
- Run: grep -rl "\[\[" "Reading/" to get files, then grep "\[\[" on each to extract links
- Flag: Papers with zero links pointing to files in Projects/ (orphan papers)
- Flag: Papers with any link pointing to a file in MOCs/ (forbidden)
- Flag: Concept links — single-concept terms with no paper-like specificity e.g. [[Attention]], [[Transformers]], [[Softmax]]

For projects in Projects/:
- Extract all [[wiki links]] from each project using grep
- Flag: Projects with zero links pointing to files in MOCs/ (orphan projects)

For bidirectional consistency:
- For each paper→project link: verify the project file contains a reciprocal link back to the paper
- Flag: Missing reciprocal links

STEP 3: Return findings in EXACTLY this format (nothing else):

ORPHAN_PAPERS:
- [[filename]] | no project links found | add link to relevant project
(or write "none" if no violations in this category)

ORPHAN_PROJECTS:
- [[filename]] | no MOC links found | add link to relevant MOC
(or "none")

BROKEN_BIDIR:
- [[paper]] → [[project]] | project missing reciprocal link | add [[paper]] to project's Relevant Papers
(or "none")

FORBIDDEN_CONCEPT_LINKS:
- [[filename]] | [[ConceptLink]] | remove link
(or "none")

FORBIDDEN_MOC_LINKS:
- [[paper]] | links to [[MOC Name]] directly | remove link
(or "none")

MALFORMED_LINKS:
- [[filename]] | malformed link text | fix
(or "none")

If zero violations across ALL categories, return only the single line: NO_VIOLATIONS
```

---

## TOKEN EFFICIENCY

Scan work is fully isolated in a subagent — it does not pollute the main context window.
Main session only handles user interaction and writes.

---

## OUTPUT RULES

- Concise summary first
- Group violations by type
- Each violation: file name + issue + suggested fix
- No prose, bullets only

---

## SELF-CHECK

✅ Did I spawn the scan subagent and receive structured findings?
✅ Did I present findings grouped by violation type?
✅ Did I get user approval before fixing?
✅ Did I update vault_maintanance.md with current timestamp and reset counters?
