# CLAUDE.md

Guidelines for working on the `obsidian-second-brain-research-skills` plugin repository.

---

## Purpose

This repository is a collection of agent skills for managing a second-brain research vault in Obsidian. Skills encode workflows for reading papers, managing research projects, maintaining vault structure, and keeping the knowledge graph consistent.

---

## Repository Structure

```
skills/              → one folder per skill, each containing a SKILL.md
.claude-plugin/      → plugin metadata (plugin.json)
CLAUDE.md            → this file
README.md            → installation and skills overview
LICENSE
```

Each skill lives in its own subdirectory:
```
skills/
  ask_paper/         → answer questions about a paper
  read_paper/        → convert paper into vault note + project links
  create_project/    → create atomic research project notes
  merge_projects/    → identify and consolidate overlapping projects
  update_moc/        → maintain research area MOC hubs
  update_vault_index/ → sync .claude/vault_index.md with vault state
  audit_links/       → validate vault graph consistency
  validate_paper_links/ → validate paper note links against references
  vault_maintenance/ → run all maintenance skills in sequence
```

---

## Skill Format

Each skill is a single `SKILL.md` file with YAML frontmatter followed by skill instructions in Markdown.

**Required frontmatter:**
```yaml
---
name: skill_name
description: One-sentence description of what the skill does
---
```

- `name` must match the folder name exactly
- `description` is used in the README skills table and plugin discovery

**Body:** Plain Markdown. Write instructions as directives to the agent — workflow steps, rules, self-checks, output format. Keep it concise and action-oriented.

---

## Vault Structure These Skills Assume

Skills are designed for a vault with this flat folder structure:

```
Projects/        → atomic research project notes (.md)
Reading/         → paper notes (.md)
MOCs/            → research area hubs (.md)
Templates/       → note templates (.md)
  Paper Note.md  → template for paper notes (REQUIRED)
  Project.md     → template for project notes (REQUIRED)
Inbox/
  Brain Dump.md  → quick-capture file
Daily Notes/     → YYYY-MM-DD.md session logs
Archive/         → finished projects
.claude/
  vault_index.md        → master index of MOCs, projects, recent papers
  vault_maintanance.md  → maintenance counters and last-run timestamps
```

Skills read and write these specific files and folders. Any skill that requires a template or index must document which file it depends on.

---

## Knowledge Flow

```
Paper → Project → MOC
```

- papers = evidence, live in `Reading/`
- projects = research ideas, live in `Projects/`
- MOCs = research area hubs, live in `MOCs/`
- Papers link to projects; projects link to MOCs
- Papers must **never** link directly to MOCs

---

## Note Metadata Conventions

### Paper note frontmatter
```yaml
url: 
code: 
type: paper | blog
authors:
year: yyyy
status: to_read
```

### Project note frontmatter
```yaml
type: project
status: seed | idea | active | writing | finished
novelty: 1-10
feasibility: 1-10
```

### MOC frontmatter
```yaml
type: moc
tags: [moc, index]
```

---

## Maintenance Counter File

`.claude/vault_maintanance.md` tracks when maintenance tasks last ran and how many notes have been added since:

```
update_vault_index: DD-MM-YYYY HH:MM
papers_since_audit_links: 0
projects_since_audit_links: 0
papers_since_vault_index: 0
projects_since_vault_index: 0
papers_since_validate_links: 0
```

Skills that add notes must increment the relevant counters. Maintenance skills reset their counters after running.

---

## Writing Guidelines for Skill Instructions

- Bullet points and fragments preferred — no prose
- Use numbered steps for sequential workflows
- Always include a `## SELF-CHECK` section with a checklist
- Specify which vault files/folders the skill reads and writes
- State non-negotiable rules clearly (use **bold** or ALL CAPS sparingly)
- Token efficiency: skills should read only what they need; document what can be skipped

---

## Plugin Metadata

`plugin.json` in `.claude-plugin/` follows the Agent Skills specification:

```json
{
  "name": "plugin-name",
  "version": "semver",
  "description": "...",
  "author": { "name": "...", "url": "..." },
  "repository": "https://github.com/...",
  "license": "MIT",
  "keywords": [...]
}
```

Bump `version` whenever a skill is added, removed, or significantly changed.

---

## Local Plugin Development

To test the plugin locally before publishing:

1. Create a local marketplace file (e.g. `/tmp/local-marketplace.json`):

```json
{
  "name": "local-marketplace",
  "plugins": [
    {
      "source": "file:///path/to/obsidian-second-brain-research-skills"
    }
  ]
}
```

2. Register the marketplace: `/plugin marketplace add /tmp/local-marketplace.json`
3. Install the plugin: `/plugin install obsidian-second-brain-research-skills`

Skills become available immediately after installation. Re-install after editing any `SKILL.md` to pick up changes.

---

## Release Management

When cutting a release:

1. Update `version` in `.claude-plugin/plugin.json` (semver)
2. Ensure the README skills table matches the skills in `skills/`
3. Commit and tag with the version number

Bump `version` for any of:
- Adding a new skill
- Removing a skill
- Significant changes to an existing skill's workflow

---

## Editing Rules

- Edit only files in `skills/` and `.claude-plugin/`
- Do not create new top-level folders
- Each skill must have exactly one `SKILL.md`; no other files in a skill folder
- README skills table must stay in sync with the skills that exist in `skills/`
- Do not remove a skill without also removing its entry from the README table and `plugin.json` keywords if present
