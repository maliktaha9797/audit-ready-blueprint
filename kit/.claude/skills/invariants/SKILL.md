---
name: invariants
description: The single source of truth for what must always hold in this project, with the check that proves each one. Read before any gate, before proposing a rule change, and whenever work touches data, secrets, approvals, routing, outbound actions or the decision record. The invariant-auditor uses it to audit every phase.
---

# Invariants

## How to use this skill

An invariant is a statement that must hold at every moment of the build. Each row below has a check that can be run, and says what enforces it. If a row has no runnable check, it is a wish and not an invariant.

- Cite an invariant by its id, for example `INV-03`, in code comments, test names, phase logs and `CLAUDE.md`.
- The table is the only place the set of invariants is stated. Do not copy it into other files, and do not write how many there are. Refer to "the invariants".
- Changing this file is a rule change. See `.claude/workflow-docs/rule-change.md`.
- An invariant whose check still contains a `<<FILL` slot cannot be audited. The auditor returns BLOCK for it, never N/A.

## The table

"Enforced by" is one of: hook, permission, test, auditor review. Commands are run from the project root.

| ID | Invariant | Executable check | Violation signatures | Enforced by |
|---|---|---|---|---|
| INV-01 | No real personal or customer data in the repository, in fixtures, or in any model call during the build. | `pytest tests/test_hooks.py -k "real_data"`. `git ls-files data/real` prints nothing. `<<FILL: command that scans fixtures for records without the synthetic marker>>` | A path under `data/real/`. A fixture record with no synthetic marker. A real export "just for testing". A real value pasted into a prompt. | permission, hook |
| INV-02 | Secrets are never readable by the agent. | `pytest tests/test_hooks.py -k "secret or deny"` | A command that prints a `.env` file or a key file. An environment dump. A secret value echoed into a log or a test. | permission, hook |
| INV-03 | The rulebook changes only through an approved rule change. | `pytest tests/test_hooks.py -k "protected or approval"`. Then `git log --format="%h %s" -- CLAUDE.md .claude/settings.json .claude/guard.json .claude/hooks .claude/agents .claude/workflow-docs .claude/skills/invariants .claude/skills/gate .claude/skills/regress .claude/skills/rule-change .claude/context/acceptance.md` lists the commits that touched the rulebook, and the auditor matches each one to a closed entry in `.claude/context/rule-changes.md`. | An edit to `CLAUDE.md`, this file, settings or hooks with no entry. A protected file changed through a shell redirect. An approval file that the agent created. | hook, auditor review |
| INV-04 | Every exit criterion is marked executed, read or not-verifiable, with proof. | `awk '/^- \[x\]/ && !(match($0,/Proof: .+ Label: executed[.]/) + match($0,/Proof: .+ Label: read[.]/) + match($0,/Proof: .+ Label: not-verifiable[.]/))' .claude/context/phases/phase-*.md` prints nothing. | A ticked box with no proof. A criterion ticked on an adjective. "executed" with no command recorded. A flaky test re-run until green and recorded as one pass. | auditor review |
| INV-05 | Every registered scenario has a test before the change that addresses it ships. | `python3 scripts/check_register.py` (the script is in the scenario-register skill). `pytest --collect-only -q` lists every fixture id marked covered. | A covered row whose fixture id is not collected. A fix commit with no new test. A row added after its fix. | test |
| INV-06 | Every detection test has been shown capable of failing. | `pytest <<FILL: path of the mutation tests>>`. Each mutation turns its detection red. | A detection test with no mutate-to-red record. A detection that passes on the exact test string only. A fix that blocks the literal input of a probe. | test |
| INV-07 | Hard rules are code, and a model output cannot override a failing rule. | `pytest <<FILL: path of the rule tests>>`, including a case where the model proposes a pass and the rule fails. | A branch that returns the model's proposed status without running the rule. Prompt text that says "ignore the check" changing an outcome. | test |
| INV-08 | Routing, state changes and approval are code over typed state. | `<<FILL: grep command that finds model calls inside routing and state-change code>>` prints nothing. | A model response used as the name of the next step. An approval inferred from free text. A state change made inside a model call. | auditor review |
| INV-09 | Outbound actions fail closed. | `pytest <<FILL: path of the outbound tests>>`: a missing, unknown or misspelt mode suppresses the action and records the suppression. | A default of "live". An allowlist that allows everything when empty. A suppression that leaves no record. | test |
| INV-10 | The decision record is append-only. | `pytest <<FILL: path of the record tests>>`: an edited, deleted or reordered entry is detected. | An update or delete function on the record. A record file opened for writing. A hash chain that is never verified. | test |
| INV-11 | Suspicious input produces a flag and a human review, never a silent pass and never an automatic rejection. | `pytest <<FILL: path of the red-team tests>>`: each probe asserts behaviour is unchanged and that a flag reached a person. | Instruction text inside a document changes a decision. Suspicious input rejected with no person involved. A flag that is written and never shown. | test |
| INV-12 | Acceptance numbers are signed before the graded run. | `grep -E '^Signed by: [^<]' .claude/context/acceptance.md` finds a signature (an unfilled slot starts with `<`). The auditor then compares its `Date:` line with the date of the graded run in the phase log, and the signature must be the earlier. | A graded result recorded against an unsigned or absent pass bar. Numbers changed after the results were seen. | auditor review |

### Project invariants

Add one row per rule specific to this project, in the same format, with ids that continue the sequence. Each needs a check that can be run and a stated enforcer.

| ID | Invariant | Executable check | Violation signatures | Enforced by |
|---|---|---|---|---|
| INV-<<FILL: next id>> | <<FILL: the rule>> | <<FILL: a command>> | <<FILL: what breaking it looks like>> | <<FILL: hook, permission, test or auditor review>> |

## Audit output format

The auditor returns this to the session that called it. That session writes it into the phase log under "Gate results". The auditor does not write files.

```
Audit: phase <n>, <date>
Diff reviewed: <git range>
Phase log reviewed: <path>

| ID | Verdict | Evidence |
|---|---|---|
| INV-01 | PASS | <command run> returned <result> |
| INV-02 | N/A | <why the diff does not touch this surface, with the diff stat shown> |
| INV-03 | BLOCK | <what is wrong>, <file>:<line>, INV-03 |

Overall: PASS or BLOCK
Not checked: <anything the auditor could not run, with the reason, labelled not-verifiable>
```

Verdict rules:

- **PASS** needs evidence: a command and its result, or the exact lines inspected. "Looks right" is not evidence.
- **N/A** needs the reason, shown from the diff. Granting N/A without showing that the diff does not touch the surface is a failure of the audit.
- **BLOCK** names the violation, the file and line, and the invariant id. A block is cleared only by a fix or by a decision from the owner recorded in `decisions.md`. The implementing agent cannot clear it.
- The overall verdict is BLOCK if any row is BLOCK.

## Violation signatures log

Each entry is a near-miss: a pattern that would indicate an invariant is being broken. The auditor searches for these. The log is append-only. Adding a signature is a rule change, because it changes what the auditor looks for.

- 2026-01-01 (sample, not a real near-miss) INV-02: a command that echoes a variable whose name ends in KEY.
