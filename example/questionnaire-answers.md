# Workflow setup questionnaire: answered for Northgate Supplier Desk

This is the questionnaire from [templates/questionnaire.md](../templates/questionnaire.md), answered for the fictional project described in [README.md](README.md). Reading it alongside the files in this folder shows how each answer becomes a file in the kit.

## Basic info

**Workflow name:** Build Northgate Supplier Desk, phase by phase.

**Primary purpose:** Build an internal tool in which agents assemble and check each new supplier file, so that a named person can approve it with the evidence in front of them.

**Trigger command:** /phase

## Task definition

**What is the main task?**

Build the tool in four phases, each proved by tests and each ending at a human gate. The tool assembles a supplier file, runs every check that can be written as a rule, uses a model only to read documents and to draft flagged judgments, and activates nothing until a named person approves.

**What are the phases? (list in order)**

1. Foundations: the decision ledger, fail-closed outbound messages, and synthetic fixtures.
2. Policy as data and rule evaluation.
3. Document reading and flagged judgment.
4. The human approval screen and the full regression run.

In the files, these are numbered phase 0 to phase 3, because the first phase is numbered 0.

**Can phases run in parallel, or must they be sequential?**

Sequential. Each phase builds on the guarantees of the one before, and each ends at a gate that a person signs.

**What does "done" look like?**

Every exit criterion in every phase is marked executed, read or not-verifiable with proof. The auditor returns no BLOCK. The acceptance numbers were signed before the graded run. A named person has signed the final gate.

## Agents

**Do you need specialised agents?** Yes

**If yes, list them:**

| Agent name | Purpose | Runs when | Tools it needs |
|---|---|---|---|
| `foundations-builder` | Owns phase 0 | Phase 0 slices remain | Read, Grep, Glob, Bash, Edit, Write |
| `policy-engineer` | Owns phase 1 | Phase 1 slices remain | Read, Grep, Glob, Bash, Edit, Write |
| `intake-reader` | Owns phase 2 | Phase 2 slices remain | Read, Grep, Glob, Bash, Edit, Write |
| `approval-screen-builder` | Owns phase 3 | Phase 3 slices remain | Read, Grep, Glob, Bash, Edit, Write |
| `invariant-auditor` | Blocks a phase that breaks an invariant | At every gate | Read, Grep, Glob, Bash. No Edit or Write. |
| `red-team` | Attacks documents and messages | When an untrusted input surface changes | Read, Grep, Glob, Bash, Edit, Write |
| `fixture-keeper` | Owns the regression suite and the pass bar | Before any graded run | Read, Grep, Glob, Bash, Edit, Write |

**Should agents work in parallel (worktrees) or on the same branch?**

The same branch. Phases are sequential and the files each phase touches overlap.

**Is there a final reviewer that can block?** Yes. The `invariant-auditor` is read-only and independent of every phase owner.

## Skills

**What technical knowledge is needed?**

1. The invariants and how to check each one.
2. Turning verifications into runnable tests, and proving a detection can fail.
3. Registering an edge case before fixing it.
4. Inventing synthetic supplier records.
5. Keeping business rules as versioned data.

**Are these reusable across projects?** Yes. They are the kit's five knowledge skills, unchanged in purpose.

**What common mistakes must the skills warn about?**

Ticking a criterion on the strength of reading code. Fixing a detection by blocking the exact test input. Re-running a flaky test until it passes. Using a real record "just for testing". Hardcoding a business number.

## Context

**What state needs to persist?**

- [x] Decisions
- [x] Progress
- [x] Patterns discovered
- [x] Issues encountered
- [x] Other: the scenario register, the pass bar, rule-change proposals

**How should context be organised?**

- [ ] By feature
- [ ] By date
- [x] By phase
- [x] Other: the register is one file, and the decision log is split by month once it grows

## Rules

**What conventions must be followed?**

1. The plan is the specification. If this file and the plan disagree, the plan wins and this file is corrected with a decision-log entry.
2. Every edge case gets a register row and a failing test before its fix.
3. Test ids are stable and are the only form of proof.

**What must NEVER be done?**

1. Use real supplier or personal data anywhere in the build.
2. Let the model decide routing, a state change or an approval.
3. Send the text of a supplier document to the model that writes messages.
4. Activate a supplier without a named approver recorded in the ledger.
5. Call a live registry or bank service.

## Self-improvement

**Should the setup be able to change itself when it learns something?** Yes, within limits.

**Which changes are knowledge, which the agent may make freely?**

Patterns, gotchas, near-misses, the summary and the phase logs.

**Which changes are rules, which need a person's approval first?**

The prohibitions in `CLAUDE.md`, the invariants, `settings.json`, `guard.json`, the hooks, the auditor's definition, and any new violation signature.

**What triggers an update?**

- [x] New conventions discovered
- [x] User corrections
- [x] Mistakes found
- [ ] Other:

## Assurance

**Who has to be able to check this work later, and what will they ask to see?**

An internal auditor, and the finance controller who relies on the supplier file. They will ask to see, for any activated supplier: which checks ran, which version of the policy applied, what the model proposed and what the system decided, and who approved and when.

**Which rules must never be broken, and can each one be checked by running something?**

| Rule | The check that proves it | Enforced by (hook, permission, test or auditor review) |
|---|---|---|
| No real data in the build | A test that the hooks block real-data paths, and a scan of fixtures for the synthetic marker | permission, hook |
| A failing rule is never overridden by the model | A test in which the model proposes `verified` and the rule fails | test |
| Outbound messages fail closed | A test for each wrong setting | test |
| The decision record is append-only | A test that an edit, a deletion and a reordering are each found | test |
| No document text reaches the messaging model | A test that a marker string in a document is absent from the prompt | test |
| One supplier's file cannot read another's | A test that a lookup across suppliers is refused | test |
| Activation needs a named approver in the ledger | A test that activation without one is impossible | test |
| Registries are mocks, and live modes are off by default | A scan for network imports, and a test of the default mode | test |

**Which rules can be enforced by the harness (permissions, hooks) instead of being requested in prose?**

Reading secrets and real-data paths, writing to the approvals folder, changing the rulebook without an approved change, and destructive or publishing shell commands. The kit enforces these with deny rules and hooks.

**Is there a reviewer that can block, and is it independent of whatever built the work?**

Yes. The `invariant-auditor` runs the check for each invariant, has no edit or write tool, and cannot clear its own blocks. Only a fix or a recorded decision from the owner clears one.

**What counts as proof that a step is done?**

A test id or a command, run in the session, with the result recorded in the phase log and a label of executed. Reading the code counts as read, and is not enough to tick a criterion.

**Where does a person have to approve before work continues?**

At the end of every phase. The owner signs the gate in the decision log. In phase 3, a named approver signs each supplier file before activation, and the owner signs the acceptance numbers before the graded run.
