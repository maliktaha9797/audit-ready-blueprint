<!-- What it is: the project rules file that Claude Code loads at the start of every session. It is guidance, so pair every prohibition with something that enforces it. -->
<!-- When to create it: always, for every project. Keep it under 200 lines. -->
<!-- Where it goes: CLAUDE.md at the project root. Replace each <<FILL: ...>> slot and delete these three comment lines. -->

# <<FILL: project name>>

## Project overview

<<FILL: two or three sentences on what this project is and who uses it>>

## Governing sentence

<<FILL: one sentence that every design decision can be tested against. It says what software decides, what the model may do, and what a person must approve.>>

## Authority order

When two documents disagree, the earlier one in this list wins, and the later one is corrected at once with an entry in the decision log.

1. <<FILL: the specification or plan>>
2. This file
3. The skills and workflow files
4. Everything else

## Tech stack

- <<FILL: language and version>>
- <<FILL: framework or libraries>>

## Repository layout

```
<<FILL: the top-level folders and what each holds>>
```

## Quick reference

```bash
<<FILL: the commands to run the tests, the checks and the application>>
```

## Conventions

| Element | Convention | Example |
|---|---|---|
| <<FILL: element>> | <<FILL: pattern>> | <<FILL: example>> |

<<FILL: any further conventions, grouped by category>>

## Agents

| Agent | Purpose | Skills it reads |
|---|---|---|
| <<FILL: name>> | <<FILL: what it does>> | <<FILL: skills>> |

## Skills

| Skill | Purpose | Read by |
|---|---|---|
| <<FILL: name>> | <<FILL: what it teaches>> | <<FILL: agents>> |

## Commands

| Command | Purpose |
|---|---|
| `/<<FILL: name>>` | <<FILL: what it does and which workflow it starts>> |

## DO

- Read `.claude/context/summary.md` first in every session.
- <<FILL: a practice that is always followed>>

## DO NOT

Each line ends with the id of the invariant whose check catches a breach.

- <<FILL: a prohibition>> (<<FILL: invariant id>>)

## Changing the rules

- **Knowledge** (patterns, gotchas, context): update the file and append a line to the log.
- **Rules** (this file's prohibitions, the invariants, settings, hooks): write a proposal, stop, and wait for a person to approve it. Then make exactly the approved change. See `.claude/workflow-docs/rule-change.md`.

## Context rules

- `summary.md` is read first and updated last. Keep it under <<FILL: line cap>> lines.
- `decisions.md` is append-only. Move old entries to `archive/` by month. Never edit a past entry.
- <<FILL: any further rules for the context files>>

## Honesty labels

Every verification is labelled one of three ways.

- **executed**: a command or test was run, and its result is recorded.
- **read**: the thing was inspected but not run.
- **not-verifiable**: it cannot be checked here, and the reason is stated.

Proof is a test id or a command. An adjective is not proof.
