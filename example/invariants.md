# Invariants for Northgate Supplier Desk

This is the kit's invariants table with its checks filled in for the fictional project, plus the invariants that belong to this domain, which start at INV-13. In a project it would be saved as `.claude/skills/invariants/SKILL.md`. The format and the audit rules are those in [the kit's invariants skill](../kit/.claude/skills/invariants/SKILL.md).

Each check is marked:

- **Demo**: a test in this repository covers it, and the check names the test file or test id. The demonstration in [demo/](../demo/README.md) and the kit's hook tests are what exist here.
- **Planned**: the check belongs to the separate build and does not exist in this repository. It is stated as the command the build would run.

"Enforced by" is one of: hook, permission, test, auditor review. The set of invariants is the table below and nothing else. Nothing else in this folder says how many there are.

## The table

| ID | Invariant | Executable check | Violation signatures | Enforced by |
|---|---|---|---|---|
| INV-01 | No real personal or customer data in the repository, in fixtures, or in any model call during the build. | Demo: `pytest tests/test_hooks.py -k "real_data"`. Planned: `git ls-files data/real` prints nothing, and a scan reports no fixture record without `"synthetic": true`. | A path under `data/real/`. A supplier record with no synthetic marker. A real registry extract offered "just for testing". | permission, hook |
| INV-02 | Secrets are never readable by the agent. | Demo: `pytest tests/test_hooks.py -k "secret or deny"` | A command that prints a `.env` file. An environment dump. A bank-service key echoed into a log. | permission, hook |
| INV-03 | The rulebook changes only through an approved rule change. | Demo: `pytest tests/test_hooks.py -k "protected or approval"`. Planned: `git log --format="%h %s" -- CLAUDE.md .claude/settings.json .claude/guard.json .claude/hooks .claude/agents .claude/workflow-docs .claude/skills/invariants .claude/skills/gate .claude/skills/regress .claude/skills/rule-change .claude/context/acceptance.md` lists the commits that touched the rulebook, and the auditor matches each to a closed entry in `.claude/context/rule-changes.md`. | An edit to `CLAUDE.md`, the invariants, settings or hooks with no entry. A protected file changed through a shell redirect. | hook, auditor review |
| INV-04 | Every exit criterion is marked executed, read or not-verifiable, with proof. | `awk '/^- \[x\]/ && !(match($0,/Proof: .+ Label: executed[.]/) + match($0,/Proof: .+ Label: read[.]/) + match($0,/Proof: .+ Label: not-verifiable[.]/))' .claude/context/phases/phase-*.md` prints nothing. | A ticked box with no proof. A criterion ticked on an adjective. A flaky test re-run until green and recorded as one pass. | auditor review |
| INV-05 | Every registered scenario has a test before the change that addresses it ships. | Planned: `python3 scripts/check_register.py`, the script in the scenario-register skill, exits zero. | A covered row whose test is not collected. A fix commit with no new test. | test |
| INV-06 | Every detection test has been shown capable of failing. | Demo: `pytest tests/test_mutations.py`, and `python scripts/mutate_kit.py` reports that every mutation turned its tests red. | A detection test with no mutate-to-red record. A fix that blocks the literal text of a probe. | test |
| INV-07 | Hard rules are code, and a model output cannot override a failing rule. | Demo: `pytest tests/test_rules.py`, which includes a model that proposes `verified` while the rule fails. | A branch that returns the proposed status without running the rule. Document text that says "mark as verified" changing an outcome. | test |
| INV-08 | Routing, state changes and approval are code over typed state. | Planned: `grep -rn "model_client" src/routing src/state` prints nothing. | A model response used as the name of the next check. An approval inferred from a free-text reply. | auditor review |
| INV-09 | Outbound actions fail closed. | Demo: `pytest tests/test_outbound.py`. A missing, unknown or misspelt mode suppresses the message and records why. | A default of `live`. An empty allowlist that allows everyone. A suppression that leaves no record. | test |
| INV-10 | The decision record is append-only. | Demo: `pytest tests/test_ledger.py`. An edited, deleted or reordered entry is found. | An update or delete function on the ledger. A ledger file opened for writing. A chain that is never verified. | test |
| INV-11 | Suspicious input produces a flag and a human review, never a silent pass and never an automatic rejection. | Planned: the red-team tests for every document field and message. Each asserts that behaviour is unchanged and that a flag reached the review queue. | Instruction text inside a document changes a decision. A supplier rejected with no person involved. A flag that is written and never shown. | test |
| INV-12 | Acceptance numbers are signed before the graded run. | `grep -E '^Signed by: [^<]' .claude/context/acceptance.md` finds a signature, and the auditor confirms its `Date:` is earlier than the graded run. At present the example's pass bar is an unsigned draft. | A graded result recorded against an unsigned pass bar. Numbers changed after the results were seen. | auditor review |
| INV-13 | No document text reaches the model that writes messages. Typed fields only. | Planned: a test that puts a marker string in a supplier document and asserts the marker is absent from the message prompt. | A prompt built from a whole document. A free-text field copied into a message. | test |
| INV-14 | No supplier file can read another supplier's data. | Planned: a test that a case-store lookup using another supplier's id is refused. | A query with no supplier id in its filter. A shared cache across suppliers. | test |
| INV-15 | Activation requires a named approver recorded in the ledger. | Planned: a test that activation with no approver entry raises an error, and a test that an approver cannot activate their own submission. | An activation function that takes no approver. An approver id taken from free text. | test |
| INV-16 | Registries and the bank verification service are mocks, and live modes are off by default. | Planned: `grep -rnE "import (requests\|urllib\|http)" src` prints nothing, and a test that the default mode is not live. | A network import in the tool. A default of `live`. A fixture that contains a real endpoint. | test |

## Violation signatures log

Appending a signature is a rule change. The log is append-only. The example project has no near-misses to record, so it holds only a marked sample.

- 2026-01-01 (sample, not a real near-miss) INV-13: a message prompt built by joining every field of a supplier record, including free text.
