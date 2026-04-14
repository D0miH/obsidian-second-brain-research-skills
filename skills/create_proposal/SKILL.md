---
name: create_proposal
description: Create research proposal notes with proper linking and structure
---

## 📋 Create Proposal Skill

Create new research proposal notes in `Proposals/` with proper linking and structure.

---

## CRITICAL RULES

- Proposal notes live **only** in `Proposals/`
- Use `Templates/Proposal.md` **exactly**
- Status must be: `planned | submitted | accepted | rejected`
- Every proposal **must link to at least one project** (in "Research Plan → Core idea" and "Relevant Projects")
- No orphan proposals

---

## WORKFLOW

### 1. Get proposal details
Ask user for:
- **Proposal title** (short descriptive name)
- **Funder / call** (who is funding this?)
- **Deadline** (if known)
- **Related projects** (which project(s) does this build on?)
- **Website** (call URL, if available)

### 2. Read template
```
Read: Templates/Proposal.md
```
Study the exact structure before creating.

### 3. Create proposal file

**File name:** Exact proposal title
**Location:** `Proposals/`
**Template:** `Templates/Proposal.md` (copy EXACTLY)

### 4. Fill minimal sections

**Mandatory fields (frontmatter):**
- `funder:` — funding body or call name
- `deadline:` — submission deadline (if known)
- `website:` — call URL (if available)
- `status: planned`

**Mandatory content:**
- Summary: 1–2 sentences
- Core idea: link to project(s) this builds on
- Relevant Projects: link to project(s)

**Optional (fill if user provides):**
- Call requirements
- Team / budget / timeline
- Open questions

### 5. Verify structure
- All template sections present
- Status field filled correctly
- At least one project link present
- No orphan proposals

---

## OUTPUT RULES

- Ultra-concise bullets only
- Fragments OK
- No prose
- Clarity > grammar
- >5 bullets → split section

---

## SELF-CHECK

✅ Did I read `Templates/Proposal.md` first?
✅ Are ALL template sections present?
✅ Is status valid (planned|submitted|accepted|rejected)?
✅ Does proposal link to at least one project?
✅ Are project links in `[[brackets]]`?
✅ No orphan proposals created?
