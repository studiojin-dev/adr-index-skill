![License](https://img.shields.io/badge/License-MIT-green.svg)
![Release](https://img.shields.io/github/v/release/studiojin-dev/adr-index-skill)

# adr-index Skill

**TL;DR**  
Record architectural decisions as ADRs, generate a lightweight `index.json`,  
and keep `AGENTS.md` small.  
Run `$adr-index` (Codex) or `/adr-index` (Claude/Gemini) after ADR changes.

`adr-index` is a lightweight Codex / Claude / Gemini skill that generates a
searchable index for Architecture Decision Records (ADRs) while keeping agent
context usage minimal.

It is designed to prevent `AGENTS.md` from growing indefinitely and to avoid
full-document scans or expensive RAG setups.

---

## Purpose

The purpose of this skill is to:

- Keep architectural decision history without bloating agent context
- Provide a fast, deterministic way to locate relevant ADRs
- Enforce a consistent ADR metadata format
- Separate decision history from agent operating rules

Instead of storing completed work or long histories in `AGENTS.md`, decisions
are recorded as ADRs and summarized in a small `index.json` file that agents
can read efficiently.

---

## Installation

### Option 1: Install globally (recommended)

Install the skill into the global Codex skills directory:

```bash
git clone https://github.com/studiojin-dev/adr-index-skill.git \
  ~/.codex/skills/adr-index
```

Restart Codex after installation so the skill is detected.

---

### Option 2: Repository-scoped installation

You can also install the skill per repository:

```bash
mkdir -p .codex/skills
git clone https://github.com/studiojin-dev/adr-index-skill.git \
  .codex/skills/adr-index
```

This is useful if the skill configuration is tightly coupled to a specific
project.

---

### Tool-specific Installation Notes

```
#### Codex CLI
- Install the skill under `~/.codex/skills/adr-index` for global use.
- Use `$adr-index` to invoke the skill.
- Restart Codex after installation so the skill is detected.

#### Claude Code
- Place the skill directory under `.claude/skills/adr-index` (repo-scoped)
  or `~/.claude/skills/adr-index` (global).
- Invoke the skill using `/adr-index`.

#### Gemini CLI
- Place the skill directory under `.gemini/skills/adr-index` or the
  global Gemini skills directory for your environment.
- Invoke the skill using `/adr-index`.
```

## Usage

### ADR format

Each ADR must be written in `docs/adr/*.md`.

At the top of each file, use the following format:

```md
# ADR-YYYYMMDD-####-XXX: Short descriptive title

Tags: api, database, performance
Status: Proposed | Accepted | Deprecated
Date: YYYY-MM-DD
TL;DR: One short sentence summarizing the decision.
```

Only the header is required. Metadata lines are optional but strongly recommended
to improve indexing and search quality.

---

### Generating the ADR index

Run the skill from your CLI:

```
$adr-index        # Codex CLI
/adr-index        # Claude Code, Gemini CLI
```

The skill will:

1. Scan ADR files (top section only)
2. Generate or update `docs/adr/index.json`
3. Print a minimal summary (ADR count and output path)

The generated index contains only lightweight metadata:

```json
{
  "id": "ADR-YYYYMMDD-####-XXX",
  "title": "Short descriptive title",
  "tags": ["api", "database"],
  "status": "Accepted",
  "date": "2026-01-31",
  "tldr": "One short sentence summarizing the decision.",
  "path": "docs/adr/ADR-YYYYMMDD-####-XXX-short-title.md"
}
```

Agents can use this file to locate relevant ADRs without reading all documents.

---

## Recommended AGENTS.md Snippet

```md
## Documentation Workflow

- ADRs MUST be written in `docs/adr/*.md`.
- When an ADR is added or modified, `docs/adr/index.json` MUST be updated.
- The ADR index MUST be generated using the `adr-index` skill.
- AGENTS.md MUST NOT accumulate completed work logs.
  Decisions MUST be recorded in ADRs; only links or short summaries are allowed here.

### ADR Detection Rule

If you make or rely on a decision that:
- introduces architectural constraints,
- involves trade-offs,
- or is not obvious from code alone,

you MUST pause and explicitly state:
"An ADR is required for this decision."
```

## When to Write an ADR

Write an ADR if **any** of the following is true:

- You are making a decision that you may need to explain later.
- You compared alternatives and chose one (trade-offs were involved).
- The decision introduces constraints on future code or architecture.
- Reversing the decision later would be costly.
- You feel tempted to document the decision in `AGENTS.md`.
- An agent is likely to ask the same “why was this chosen?” question again.

Do **not** write an ADR for:
- Simple bug fixes
- Pure refactoring with no behavioral or architectural change
- Experimental work where no decision has been finalized
- Implementations that strictly follow an existing ADR

---

## Quick ADR Decision Rule (For Agents)

Use this rule before starting documentation work:

> If this change affects **how the system is designed or constrained**,  
> and the reason is **not obvious from the code alone**,  
> then an ADR is required.

If unsure, default to writing an ADR.
ADR documents are cheap; lost decision context is expensive.

## Practical Examples

### Example 1: Introducing a New Error Response Format

You decide to standardize all API error responses using RFC 7807.

- This affects multiple services and clients.
- Alternative approaches were considered.
- Reverting later would be costly.

✅ Action:
- Write a new ADR describing the decision.
- Run `$adr-index` or `/adr-index`.
- Remove any related completion notes from AGENTS.md, leaving only a link if needed.

---

### Example 2: Refactoring Without Architectural Impact

You refactor internal functions to improve readability without changing
external behavior or constraints.

- No new rules or contracts are introduced.
- The system design remains unchanged.

❌ Action:
- Do NOT write an ADR.
- Do NOT run `adr-index`.

---

### Example 3: Choosing a Database Technology

You choose PostgreSQL over MySQL due to JSONB support and indexing needs.

- Multiple alternatives were evaluated.
- The decision constrains future schema design.
- Other components will depend on this choice.

✅ Action:
- Write an ADR capturing the context, decision, and consequences.
- Run `adr-index` before committing.
- Ensure AGENTS.md does not retain the decision details.

---

### Example 4: Agent-Assisted Work Completion

An agent finishes implementing a feature and marks it as complete in AGENTS.md.

- The work introduced a new architectural rule or constraint.

✅ Action:
- Convert the completed item into an ADR.
- Run `adr-index`.
- Remove the completed item from AGENTS.md.

## Notes, Caveats, and Benefits

- This skill intentionally does NOT store completed work logs.
  Decisions are recorded as ADRs, while execution history should live in issues,
  pull requests, or changelogs.

- Using `adr-index` helps keep `AGENTS.md` small and stable.
  Instead of accumulating historical details, AGENTS.md can focus on:
  - project rules
  - current context
  - links or short summaries pointing to ADRs

- By relying on a lightweight `index.json`, agents can locate relevant decisions
  without scanning all ADR documents.
  This significantly reduces context usage and token consumption.

- The workflow enables long-term decision tracking without introducing
  embeddings, vector databases, or RAG pipelines.
  All outputs are deterministic, local, and easy to audit.

- Only the top section of ADR files is scanned.
  This keeps execution fast and avoids pulling unnecessary content into context.

- If repository root detection fails, the script falls back to the current
  working directory and prints a warning.

---

## Recommended PR Checklist (Optional)

For teams using GitHub (or similar platforms), it is recommended to add an
**“ADR needed?”** checklist to the pull request template.

This skill does **not** modify repository workflows or PR templates automatically.
The checklist is a **human and team-level guardrail**, not a function of the
`adr-index` skill itself.

### Example PR Checklist

Add the following to `.github/pull_request_template.md`:

```
### ADR Check

- [ ] This PR introduces a new architectural or design decision
- [ ] An ADR has been added or updated
- [ ] `adr-index` has been run and `docs/adr/index.json` is up to date

If no ADR is required, briefly explain why:
```

### Why this helps

- Prevents architectural decisions from being merged without documentation
- Encourages early ADR consideration during reviews
- Keeps `AGENTS.md` from becoming a long-term history log
- Aligns human review and agent behavior around the same decision rules

---

## License

MIT License