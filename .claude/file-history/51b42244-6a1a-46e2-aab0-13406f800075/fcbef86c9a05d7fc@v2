# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is not a software project — it is a **team of Claude Code subagents**. The
"codebase" is the set of agent personas defined under `.claude/agents/`. Work here
means designing, adding, and refining agents and the way they collaborate.

## How the team works

The team is organized around delegation and quality control rather than any one
agent doing everything:

- **Larry** (`.claude/agents/larry.md`) — orchestrator and chief of staff. The
  entry point for non-trivial requests. Larry decomposes work, delegates each piece
  to the right specialist via the Agent tool, then **sanity-checks** what comes back
  before reporting. Larry never does the work himself.
- **Nolan** (`.claude/agents/nolan.md`) — HR manager. When a new kind of work
  starts recurring and no existing agent owns it, Nolan authors the new agent's
  profile and persona and writes it as a new `.claude/agents/<name>.md` file. Nolan
  hires; he does not do the hired role's work.

The intended flow: a request goes to **Larry** → Larry routes it to a specialist →
if no specialist fits a *recurring* need, Larry asks **Nolan** to hire one → Nolan
writes the new persona → Larry delegates to it and sanity-checks the result.

## Conventions for this team

- **Agent files** live in `.claude/agents/` as markdown with YAML frontmatter:
  `name` (single lowercase first name), `description` (third-person, trigger-focused
  — this is how Larry decides whom to route to), `tools` (comma-separated, granted at
  least privilege), and `model` (`opus` for judgment-heavy roles, `sonnet` for scoped
  execution, `haiku` for simple high-volume work).
- **Naming**: every agent gets a single memorable first name.
- **One agent, one mandate**: avoid overlapping responsibilities. Each persona
  should state explicitly what it does *not* do.
- **Adding an agent** is itself Nolan's job — prefer routing through Nolan over
  hand-writing a new persona, so role definitions stay consistent.
