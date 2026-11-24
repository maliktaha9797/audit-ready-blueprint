<!-- Example only: this is the kit's CLAUDE.md with the slots filled for a fictional project. The build it describes is in a separate repository and is not part of this one. -->

# Northgate Supplier Desk

## Overview

Northgate Supplier Desk is a fictional internal tool for a fictional company. Before a new supplier can be paid, someone must check its company registration, its tax registration, its bank details and its insurance certificate. Agents assemble and check each supplier file, and a named person approves it. It is built in an audited setting, so every decision must trace to a rule and to a person.

## Governing sentence

Software performs every check that can be written as a rule; the model only reads documents and drafts judgments that are always flagged; no supplier is activated until a named person approves the file.

Where the model is allowed, and nowhere else:

1. Reading uploaded documents into typed fields.
2. Drafting a judgment when the evidence is ambiguous. The draft is always flagged for a person.
3. Writing messages to the supplier.

Everything else is code: routing, rule evaluation, deciding which check runs next, state changes and activation.

## Authority order

When two documents disagree, the earlier one wins. The later one is corrected at once, with an entry in `.claude/context/decisions.md`.

1. The plan: `plan.md`. It is the specification.
2. This file.
3. The invariants skill, then the other skills and the workflow files.
4. Everything else.

## Tech stack and layout

- Python 3.12, standard library only for the core, and pytest.
- SQLite through the standard library for the case store.
- A mocked company registry, a mocked tax registry and a mocked bank verification service, each driven by fixtures.
- `src/`: the tool. `tests/`: every proof. `fixtures/`: synthetic suppliers. `policies/`: versioned rule files. `scripts/`: the register and rulebook checks.

## Quick reference

```bash
python -m pytest                      # the full regression
python3 scripts/check_register.py     # the register check
python3 scripts/check_rulebook.py     # the rulebook check
```

## Agents

| Agent | Purpose | Skills it reads |
|---|---|---|
| `invariant-auditor` | Read-only audit of each phase against every invariant. Can block. Cannot edit. | `invariants` |
| `red-team` | Attacks documents and messages and turns each probe into a test. | `invariants`, `fixtures-and-harness`, `scenario-register`, `synthetic-data` |
| `fixture-keeper` | Owns the regression suite, fixtures and the acceptance pass bar. | `fixtures-and-harness`, `scenario-register`, `synthetic-data`, `invariants` |
| `foundations-builder` | Owns phase 0: the ledger, fail-closed outbound and synthetic fixtures. | `invariants`, `fixtures-and-harness`, `synthetic-data` |
| `policy-engineer` | Owns phase 1: policy as data and rule evaluation. | `policy-as-data`, `scenario-register`, `fixtures-and-harness` |
| `intake-reader` | Owns phase 2: reading documents, drafting flagged judgments and writing messages. | `synthetic-data`, `scenario-register`, `invariants` |
| `approval-screen-builder` | Owns phase 3: the approval screen and the full regression run. | `fixtures-and-harness`, `invariants` |

Phase owners are defined from `.claude/agents/_phase-owner.template.md`. That file is a template and is not loaded as an agent.

## Skills

| Skill | Purpose | Read by |
|---|---|---|
| `invariants` | The table of what must always hold, with the check for each | Every agent, and `/gate` |
| `fixtures-and-harness` | Runnable tests, test ids, mutate-to-red, flaky tests | Phase owners, `red-team`, `fixture-keeper` |
| `scenario-register` | Register an edge case before fixing it | Phase owners, `red-team`, `fixture-keeper` |
| `synthetic-data` | Invented records only, always marked | Phase owners, `red-team`, `fixture-keeper` |
| `policy-as-data` | Business rules as versioned data | `policy-engineer` |

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
- Edit the rulebook (this file, the invariants skill, settings, hooks) without an approved rule change. (INV-03)
- Fix a failed detection by matching the exact test input. (INV-06)
- Re-run a flaky test until it passes. (INV-04)
- Let a model decide routing, state changes or approval. (INV-08)
- Send the text of a supplier document to the model that writes messages. Typed fields only. (INV-13)
- Let one supplier's file read another supplier's data. (INV-14)
- Activate a supplier without a named approver recorded in the ledger. (INV-15)
- Call a live registry or bank service, or turn a live mode on. (INV-16)

## Honesty labels

Every verification is labelled one of three ways.

- **executed**: a command or test was run, and its result is recorded.
- **read**: the thing was inspected but not run.
- **not-verifiable**: it cannot be checked here, and the reason is stated.

Proof is a test id or a command. An adjective such as "robust" or "thoroughly tested" is not proof. Do not claim production use, customers or certification anywhere.

## Changing the rules

- **Knowledge** (patterns, gotchas, context, the summary): update the file and append a line to the log.
- **Rules** (the prohibitions above, the invariants, settings, `guard.json`, hooks, the auditor): write a proposal with `/rule-change`, stop, and wait for a person to approve it. Then make exactly the approved change. The hooks enforce this for the protected files listed in `.claude/guard.json`.

If a change would make a check easier to pass, it is a rule change.

## Context rules

- `summary.md` is read first and updated last. Hard cap of 120 lines. Move detail to the phase logs.
- `decisions.md` is append-only and holds the current period only. Move older entries to `archive/` by month. Never edit a past entry.
- Phase logs are append-only while a phase is open and are never rewritten after the gate is signed.
- Questions only the owner can answer go in `open-questions.md`. Continue with work that is not blocked.
- Never put real data, secrets or file contents in any context file.
