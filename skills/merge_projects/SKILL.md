---
name: merge_projects
description: Identify overlapping projects and merge them into consolidated notes
---

## 🔀 Merge Projects Skill

Detect overlapping or closely related projects and merge them into a single consolidated project note. Also critically evaluate all projects for novelty and feasibility, and flag or remove those that don't meet the bar for a publishable research contribution.

---

## CRITICAL RULES

- **Never merge automatically** — always present candidates and get user approval
- **Never delete source projects** until merged project is verified
- **Never remove projects automatically** — always explain why and get user approval first
- Merged project inherits the **highest status** of its sources (seed < idea < active < writing < finished)
- All paper links from source projects **must be preserved** in merged project
- All MOC links from source projects **must be preserved** in merged project
- Bidirectional links must be updated: papers that linked to old projects must link to merged project
- Vault index must be updated after merge

---

## WORKFLOW

### 1. Choose mode

Ask user:
- **Scan for candidates?** (analyze all projects for overlap, then critically evaluate all projects)
- **Merge specific projects?** (user names 2-3 projects to merge)

---

### 2a. Scan mode — Spawn analysis subagent

Use the Agent tool to spawn a subagent. Pass it the **SCAN SUBAGENT PROMPT** below verbatim.

The subagent reads all project files, scores overlap between pairs, and evaluates every project for novelty and feasibility. It returns a structured report. Wait for it to finish before proceeding.

Present the subagent's findings to the user and get approval before proceeding to merges or removals.

---

### 2b. Direct merge mode — Spawn read subagent

Use the Agent tool to spawn a subagent. Pass it the **DIRECT MERGE SUBAGENT PROMPT** below, with the project names filled in.

The subagent reads the specified project files in full and returns their content. Use the returned content to confirm overlap and proceed with the merge.

---

### 3. Execute merge (main session)

**After user approves which projects to merge:**

Read the full content of the source project files (if not already returned by subagent).

Create merged project by integrating content section by section:

| Section | Merge strategy |
|---|---|
| Current Focus | Keep primary's; note secondary's angle if distinct |
| Seed Idea | Combine triggers from all sources |
| Current Working Idea | Synthesize into broader framing |
| Research Question | Merge into unified question; keep sub-questions if distinct |
| Hypothesis / Claim | Keep primary; add secondary as alternative hypothesis if different |
| Context & Motivation | Union of all motivations |
| Possible Approaches | Union of all approaches (deduplicate) |
| Research Ideas & Variants | Secondary project's main direction becomes a variant |
| Related Work | Union (deduplicate) |
| Relationship to Prior Work | Union (deduplicate) |
| Possible Experiments | Union (deduplicate) |
| Open Questions & Risks | Union (deduplicate) |
| Next Actions | Union; remove completed/redundant |
| Relevant Papers | Union of ALL paper links (no paper lost) |

**Decide on merged title:**
- If primary title is broad enough → keep it
- If both titles are narrow → create new title capturing combined scope
- Title must be concise and descriptive

**Set merged status:** Use highest status among source projects.

Write the merged project file.

---

### 4. Find and update all references — Spawn reference-finder subagent

After the merged project is written, spawn a subagent with the **REFERENCE FINDER SUBAGENT PROMPT** below (fill in the absorbed project names and merged project name).

The subagent greps across Reading/, MOCs/, and Projects/ to find every file that references the absorbed project(s). It returns a list of files and the specific link text to replace.

Use the returned list to make edits in the main session:
- Replace `[[Old Project Name]]` with `[[Merged Project Name]]` in each listed file

---

### 5. Remove absorbed projects

**Only after verification:**
- Confirm merged project file exists and is complete
- Confirm all paper links updated
- Confirm all MOC links updated
- Confirm no remaining references to old project names (verified by subagent in step 4)

**Then delete** secondary (absorbed) project files — only with user approval.

---

### 6. Update vault index

Notify user to run `/update_vault_index`, or spawn update_vault_index subagent directly.

---

## SCAN SUBAGENT PROMPT

Pass this prompt verbatim to the Agent tool:

```
You are a research project analyst for an Obsidian vault.
Vault root: {{VAULT_ROOT}}

STEP 1: Read vault index
Read .claude/vault_index.md to get all project names, statuses, and one-line descriptions.

STEP 2: Read all project files
For each project in Projects/:
- Read YAML frontmatter (status, type)
- Read "Seed Idea", "Current Working Idea", "Research Question", "Hypothesis / Claim", and "Relevant Papers" sections
- Do NOT read full file — only these sections

STEP 3: Identify merge candidates
For every pair of projects, assess overlap signals:
- Similar research questions or hypotheses
- Shared relevant papers (≥2 papers in common)
- Overlapping MOC links
- Complementary seed ideas (one project's approach is another's variant)
- Same phenomenon studied from slightly different angles

Score each pair:
- 🔴 High overlap: same core question, ≥3 shared papers, nearly identical hypotheses
- 🟡 Moderate overlap: related questions, 2 shared papers, one could be a variant of the other
- 🟢 Low overlap: distinct questions, ≤1 shared paper, different mechanisms (skip these)

Only report 🔴 and 🟡 pairs.

STEP 4: Critical evaluation — every project
For every project (not just merge candidates), assess:

Novelty:
- Does it propose something meaningfully different from existing published work?
- Is the contribution incremental to the point of being unpublishable at a top venue?
- Is the claimed insight already implicit or explicit in prior work?

Feasibility:
- Can the core hypothesis be tested with realistic resources?
- Is the method technically well-defined enough to implement?
- Are there fundamental blockers (proprietary model internals, unavailable datasets, unclear operationalization)?

Verdict per project:
- ✅ Keep — novel, feasible
- ⚠️ Borderline — minor concern; keep but flag
- ❌ Remove — fails novelty or feasibility; must state specific reason (2-4 sentences)

STEP 5: Return findings in EXACTLY this format:

MERGE_CANDIDATES:
🔴 [[Project A]] + [[Project B]]
Reason: <shared papers, similar question>
Suggested primary: [[Project A]]
Suggested merged title: <title if needed>

🟡 [[Project C]] + [[Project D]]
Reason: <...>
Suggested primary: [[Project C]]
Suggested merged title: <title if needed>

(or "none" if no candidates)

CRITICAL_EVALUATION:
✅ [[Project Name]]
✅ [[Project Name]]
⚠️ [[Project Name]] | <brief concern>
❌ [[Project Name]] | <specific reason why it fails novelty or feasibility bar>

(list every project)
```

---

## DIRECT MERGE SUBAGENT PROMPT

Pass this prompt to the Agent tool (fill in project names):

```
You are a research project reader for an Obsidian vault.
Vault root: {{VAULT_ROOT}}
Projects to read: <PROJECT_NAME_1>, <PROJECT_NAME_2> (add more if needed)

For each project file in Projects/<name>.md:
- Read the FULL file content

Return the full content of each file verbatim, clearly separated by project name headers.
```

---

## REFERENCE FINDER SUBAGENT PROMPT

Pass this prompt to the Agent tool (fill in absorbed project names and merged project name):

```
You are a reference finder for an Obsidian vault.
Vault root: {{VAULT_ROOT}}
Absorbed project(s) to find references to: <OLD_PROJECT_NAME_1>, <OLD_PROJECT_NAME_2>
Merged project name: <MERGED_PROJECT_NAME>

For each absorbed project name, search for all references across the vault:
Run (from vault root):
grep -rl "[[<OLD_PROJECT_NAME>]]" "Reading/" "MOCs/" "Projects/"

For each file found, extract the specific line(s) containing the old project link.

Return results in EXACTLY this format:

REFERENCES_TO_UPDATE:
File: Reading/<filename>.md
  Line: [[Old Project Name]] → replace with [[Merged Project Name]]

File: MOCs/<filename>.md
  Line: [[Old Project Name]] → replace with [[Merged Project Name]]

File: Projects/<filename>.md
  Line: [[Old Project Name]] → replace with [[Merged Project Name]]

(or "NO_REFERENCES_FOUND" if nothing found)
```

---

## TOKEN EFFICIENCY

- Scan subagent reads all project files in isolation — does not pollute main context
- Reference finder subagent uses grep, no file reads — fast and cheap
- Direct merge subagent returns raw file content for main session to synthesize
- Main session handles only: user interaction, content synthesis, file writes

---

## OUTPUT RULES

- Scan results: candidate pairs with overlap score + rationale, then full evaluation table
- Merge summary: before/after (projects consolidated, papers preserved, links updated)
- Bullets only, no prose
- Confirm paper count preserved: "X papers linked before → X papers linked after"

---

## SELF-CHECK

✅ Did I spawn the scan subagent before presenting findings?
✅ Did I get user approval before merging?
✅ Did I critically evaluate every project for novelty AND feasibility?
✅ Did I provide a brief explanation for every ❌ project before flagging it for removal?
✅ Did I get user approval before removing any project?
✅ Are ALL paper links from source projects preserved in merged project?
✅ Are ALL MOC links preserved?
✅ Did I spawn the reference finder subagent after the merge?
✅ Did I update all files returned by the reference finder?
✅ Is the merged project status correct (highest of sources)?
✅ Did I delete absorbed/removed project files only after full verification and user approval?
✅ Is the vault index updated or user notified to update?
✅ No orphan references remain to deleted project names?
