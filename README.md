# obsidian-second-brain-research-skills

Agent skills for managing a second-brain research vault in Obsidian.

These skills follow the [Agent Skills specification](https://agentskills.io/specification) so they can be used by any skills-compatible agent, including Claude Code and Codex CLI.

## Installation

### npx skills

```
npx skills add git@github.com:D0miH/obsidian-second-brain-research-skills.git
```

### Manually

#### Claude Code

Add the contents of this repo to a `/.claude` folder in the root of your Obsidian vault (or whichever folder you're using with Claude Code). See more in the [official Claude Skills documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

#### Codex CLI

Copy the `skills/` directory into your Codex skills path (typically `~/.codex/skills`). See the [Agent Skills specification](https://agentskills.io/specification) for the standard skill format.

#### OpenCode

Clone the entire repo into the OpenCode skills directory (`~/.opencode/skills/`):

```sh
git clone https://github.com/D0miH/obsidian-second-brain-research-skills.git ~/.opencode/skills/obsidian-second-brain-research-skills
```

Do not copy only the inner `skills/` folder — clone the full repo so the directory structure is `~/.opencode/skills/obsidian-second-brain-research-skills/skills/<skill-name>/SKILL.md`.

OpenCode auto-discovers all `SKILL.md` files under `~/.opencode/skills/`. No changes to `opencode.json` or any config file are needed. Skills become available after restarting OpenCode.

## Skills

| Skill | Description |
|-------|-------------|
| [ask_paper](skills/ask_paper) | Answer questions about a paper in the vault, using note first and arXiv HTML as fallback |
| [read_paper](skills/read_paper) | Convert a research paper into structured Obsidian notes and link research projects |
| [create_project](skills/create_project) | Create atomic research project notes with minimal overhead |
| [create_proposal](skills/create_proposal) | Create research proposal notes with proper linking and structure |
| [merge_projects](skills/merge_projects) | Identify overlapping projects and merge them into consolidated notes |
| [update_moc](skills/update_moc) | Manage research area hubs (MOCs) with lean, project-focused organization |
| [update_vault_index](skills/update_vault_index) | Keep `vault_index.md` synchronized with current vault structure |
| [audit_links](skills/audit_links) | Validate vault graph consistency and structural integrity |
| [validate_paper_links](skills/validate_paper_links) | Validate paper note links against actual paper references and influence |
| [vault_maintenance](skills/vault_maintenance) | Run all vault maintenance skills in sequence — `audit_links`, `update_vault_index`, `validate_paper_links` |
