---
name: update_vault_index
description: Keep vault_index.md synchronized with current vault structure
---

## 📇 Update Vault Index Skill

Automatically sync `.claude/vault_index.md` with your actual `MOCs/`, `Projects/`, and `Reading/` directories.

---

## PURPOSE

The vault index is the **entry point** to your research graph (per CLAUDE.md rules). It must stay current to reflect:
- All MOCs (research areas)
- All projects categorized by status (Seed/Idea/Active/Writing/Finished)
- Quick access to recent papers

---

## WORKFLOW

### 0. Bootstrap vault index
If `.claude/vault_index.md` does not exist, create it with this initial structure:

```markdown
# Vault Index

## Research Areas (MOCs)
- [[MOC Name]] - scope description (1 line)
[One entry per MOC created]

## Seed Projects
- [[Project Name]] - brief description (1 line)
[One entry per seed project]

## Idea Projects
[Empty if none]

## Active Projects
- [[Project Name]] - brief description (1 line)
[One entry per active project]

## Writing Projects
[Empty if none]

## Finished Projects
[Empty if none]

## Inbox
- [[Brain Dump]] — quick capture, triaged at session start

## Daily Notes
- (populated as notes are created)

## Archive
- (populated as projects are finished)
```

If the file already exists, skip this step.

### 1. Spawn subagent

Use the Agent tool to spawn a subagent. Pass it the prompt from the **SUBAGENT PROMPT** section below verbatim.

The subagent handles everything: scan, build, write vault_index.md, update vault_maintanance.md. It returns a one-line summary.

### 2. Report summary to user

Report the subagent's one-line summary to the user verbatim.

---

## SUBAGENT PROMPT

Pass this prompt verbatim to the Agent tool:

```
You are a vault index builder for an Obsidian research vault.
Vault root: {{VAULT_ROOT}}

STEP 0: Read last-run timestamp
Read `.claude/vault_maintanance.md` and note the `update_vault_index:` timestamp.
Default: incremental — only process files modified after that timestamp.
Convert timestamp (DD-MM-YYYY HH:MM) to YYYYMMDDHHMI format for touch -t.
Run (from vault root): touch -t YYYYMMDDHHMI /tmp/vault_index_ref && find "Projects/" "MOCs/" -newer /tmp/vault_index_ref
If no files were modified: skip to STEP 6 and return "Index already up to date."
Only run a full rescan if no timestamp exists yet.
Always do a full scan of Projects/ for status categorization even in incremental mode (status may change without modifying mtime).

STEP 1: Scan vault structure
- MOCs/ → list all .md file names
- Projects/ → list all .md file names + read YAML frontmatter for status field
- Reading/ → list 5-10 most recently modified .md files (optional, for context)
- Archive/ → list all .md file names

STEP 2: Categorize projects by status
Groups (maintain this order): Seed → Idea → Active → Writing → Finished
Sort alphabetically within each group.

STEP 3: Get descriptions
- For MOCs: extract first non-heading paragraph or subtitle (1 line max, 70 chars)
- For projects: extract "Seed Idea" or "Current Working Idea" field (1 line max, 70 chars)
- Extract from actual file content — do not invent descriptions
- Use present tense, factual, no marketing language

STEP 4: Build vault_index.md content using EXACTLY this structure (no deviations):

# Vault Index

## Research Areas (MOCs)
- [[MOC Name]] - brief description (1 line)

## Seed Projects
- [[Project Name]] - brief description (1 line)

## Idea Projects
- [[Project Name]] - brief description (1 line)

## Active Projects
- [[Project Name]] - brief description (1 line)

## Writing Projects
- [[Project Name]] - brief description (1 line)

## Finished Projects
- [[Project Name]] - brief description (1 line)

## Archive
- [[Archived Project Name]] - brief description (1 line)

STEP 5: Write .claude/vault_index.md with the generated content (replace entire file).
Verify: all wiki links use exact file names, no broken links, correct section order.

STEP 6: Update vault_maintanance.md
- Run `date` via Bash for current system time
- Read `.claude/vault_maintanance.md`
- Update `update_vault_index:` to current date/time in format `DD-MM-YYYY HH:MM`
- Reset `papers_since_vault_index:` to `0`
- Reset `projects_since_vault_index:` to `0`
- Write the updated file

STEP 7: Return ONLY this one-line summary (nothing else):
"Index updated: X MOCs, Y seed, Z idea, A active, B writing, C finished, D archived"
Or if no changes were needed: "Index already up to date."
```

---

## TOKEN EFFICIENCY

All scan, build, and write work is fully isolated in a subagent. Main session only spawns the subagent and reports the one-line result to the user.

---

## SELF-CHECK

✅ Did I spawn the subagent with the full prompt?
✅ Did I report the subagent's summary line to the user?
