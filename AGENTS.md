# AGENTS

## Documentation Workflow

The following terms are to be interpreted as described in RFC 2119:
“MUST”, “MUST NOT”, “SHOULD”, and “MAY”.

1. ADRs MUST be written in `docs/adr/*.md`.

2. When an ADR is added or modified, `docs/adr/index.json` MUST be updated accordingly.

3. The ADR index MUST be generated using the `adr-index` skill.

4. AGENTS.md MUST NOT accumulate completed work logs.
   Architectural decisions MUST be recorded in ADRs.
   AGENTS.md MAY contain only links to ADRs or brief summaries.
