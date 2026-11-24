# <<FILL: project name>>

## Overview

<<FILL: two or three sentences on what this project is, who uses it, and why it is built in an audited setting>>

## Governing sentence

<<FILL: one sentence that every design decision can be tested against>>

How to write it: a single sentence that states three things. What software decides, meaning everything that can be written as a rule. What the model may do, and that its output is always checked or flagged. What a person must approve, and that nothing proceeds without it. Test it by taking any design choice and asking whether the sentence says it is allowed. If the sentence cannot settle the question, the sentence is not finished.

## Authority order

When two documents disagree, the earlier one wins. The later one is corrected at once, with an entry in `.claude/context/decisions.md`.

1. The plan: <<FILL: path of the specification or plan>>. It is the specification.
2. This file.
3. The invariants skill, then the other skills and the workflow files.
4. Everything else.

## Tech stack and layout

- <<FILL: language, version and main libraries>>
- <<FILL: the top-level folders and what each holds>>

## Quick reference

```bash
<<FILL: the commands that run the tests, the checks and the application>>
```

## Agents

| Agent | Purpose | Skills it reads |
|---|---|---|
| `invariant-auditor` | Read-only audit of each phase against every invariant. Can block. Cannot edit. | `invariants` |
| `red-team` | Attacks untrusted input surfaces and turns each probe into a test. | `invariants`, `fixtures-and-harness`, `scenario-register`, `synthetic-data` |
| `fixture-keeper` | Owns the regression suite, fixtures and the acceptance pass bar. | `fixtures-and-harness`, `scenario-register`, `synthetic-data`, `invariants` |
| <<FILL: phase owner name>> | <<FILL: the phase it owns>> | <<FILL: skills>> |

Phase owners are defined by the project from `.claude/agents/_phase-owner.template.md`, one per phase. That file is a template and is not loaded as an agent.

## Skills

| Skill | Purpose | Read by |
|---|---|---|
| `invariants` | The table of what must always hold, with the check for each | Every agent, and `/gate` |
| `fixtures-and-harness` | Runnable tests, test ids, mutate-to-red, flaky tests | Phase owners, `red-team`, `fixture-keeper` |
| `scenario-register` | Register an edge case before fixing it | Phase owners, `red-team`, `fixture-keeper` |
| `synthetic-data` | Invented records only, always marked | Phase owners, `red-team`, `fixture-keeper` |
| `policy-as-data` | Business rules as versioned data | Phase owners |

## Commands

A command is a skill that only a person can start. The command files are in `.claude/skills/`. The workflow each one follows is in `.claude/workflow-docs/`.

| Command | Purpose |
|---|---|
| `/phase <n>` | Start or resume a phase through the five stages |
| `/gate` | Run the regression, call the auditor, record the audit |
| `/regress` | Run the full regression and the register check |
| `/new-scenario` | Register an edge case, write the failing test, then fix |
| `/policy-change` | Change a business rule held as data |
| `/rule-change` | Propose a change to the rulebook and wait for approval |
| `/project-status` | Report state against the plan from the context files |

## DO

- Read `.claude/context/summary.md` first in every session.
- Let code decide everything that can be written as a rule.
- Turn every verification into a runnable test.
- Label every verification executed, read or not-verifiable.
- Register a new edge case before writing the fix for it.
- Stop at human gates.
- Commit at every phase gate, with the message `phase <n>: <what was completed>`.

## DO NOT

Each line ends with the id of the invariant whose check catches a breach. The ids are defined in `.claude/skills/invariants/SKILL.md`.

- Use real personal or customer data anywhere in the build. (INV-01)
- Read or print secrets. (INV-02)
- Mark a criterion done that was not executed. (INV-04)
- Weaken, skip or reinterpret an invariant to make a gate pass. (INV-03)
- Edit the rulebook (the files listed under `protected_paths` in `.claude/guard.json`) without an approved rule change. (INV-03)
- Fix a failed detection by matching the exact test input. (INV-06)
- Re-run a flaky test until it passes. (INV-04)
- Let a model decide routing, state changes or approval. (INV-08)
<<FILL: project prohibitions, each ending with an invariant id>>

## Honesty labels

Every verification is labelled one of three ways.

- **executed**: a command or test was run, and its result is recorded.
- **read**: the thing was inspected but not run.
- **not-verifiable**: it cannot be checked here, and the reason is stated.

Proof is a test id or a command. An adjective such as "robust" or "thoroughly tested" is not proof. Do not claim production use, customers or certification anywhere.

## Changing the rules

- **Knowledge** (patterns, gotchas, context, the summary): update the file and append a line to the log.
- **Rules** (the files listed under `protected_paths` in `.claude/guard.json`: the prohibitions above, the invariants, settings, hooks, agents, workflow files, the gate and regression commands, and the pass bar): write a proposal with `/rule-change`, stop, and wait for a person to approve it. Then make exactly the approved change. The hooks enforce this for the protected files listed in `.claude/guard.json`.

If a change would make a check easier to pass, it is a rule change.

## Context rules

- `summary.md` is read first and updated last. Hard cap of 120 lines. Move detail to the phase logs.
- `decisions.md` is append-only and holds the current period only. Move older entries to `archive/` by month. Never edit a past entry.
- Phase logs are append-only while a phase is open and are never rewritten after the gate is signed.
- Questions only the owner can answer go in `open-questions.md`. Continue with work that is not blocked.
- Never put real data, secrets or file contents in any context file.
