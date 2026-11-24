# Northgate Supplier Desk: build plan

This is the specification for the fictional project described in [README.md](README.md). The plan is the highest authority in the project. Four phases, each ending at a human gate, each with exit criteria that are proved by a test id or a command.

Only part of phase 0 is demonstrated, by the code in [demo/](../demo/README.md) and the kit's hook tests. Every other criterion below is a plan for a build that is not in this repository.

## Phases at a glance

| Phase | Name | Owner agent | Human gate |
|---|---|---|---|
| 0 | Foundations | `foundations-builder` | The owner signs |
| 1 | Policy as data and rule evaluation | `policy-engineer` | The owner signs policy version 1 |
| 2 | Document reading and flagged judgment | `intake-reader` | The owner reviews the red-team results |
| 3 | Human approval screen and full regression run | `approval-screen-builder` | The owner signs the acceptance numbers, then the final gate |

Scenario ids (`SC-nnn`) are rows in [register.csv](register.csv). Invariant ids (`INV-nn`) are rows in [invariants.md](invariants.md).

---

## Phase 0: Foundations

**Goal.** Put in place the three things every later phase relies on: a decision record nobody can quietly change, outbound messages that fail closed, and synthetic data.

**Scope.**

- The append-only decision ledger.
- Sending a message to a supplier, failing closed.
- Six synthetic suppliers, and the mocked registry, tax registry and bank verification service.
- The kit's permissions and hooks in place.

**Exit criteria.**

- [ ] The ledger finds an edited, a deleted and a reordered entry. Proof: `tests/test_ledger.py`. Register row SC-004 cites the edit test. The deletion and reordering tests sit beside it.
- [ ] Outbound sending is suppressed, and the suppression recorded, for a missing, misspelt or unknown mode and for an unlisted recipient. Proof: `tests/test_outbound.py`. Covers SC-001 to SC-003.
- [ ] The six synthetic suppliers exist and each is marked synthetic. Proof: `tests/test_rules.py::test_fixtures_cover_all_six_scenarios` and `tests/test_rules.py::test_every_fixture_supplier_is_marked_synthetic`.
- [ ] The hooks block a write to a real-data path and to the approvals folder. Proof: `tests/test_hooks.py::test_write_to_real_data_path_blocked` and `tests/test_hooks.py::test_write_to_approvals_folder_blocked`.
- [ ] One supplier's file cannot read another's. Proof: planned. Covers SC-005 and INV-14.
- [ ] Every registry is a mock and every live mode is off by default. Proof: planned. Covers INV-16.

**Human gate.** The owner reviews the phase log and signs in the decision log.

---

## Phase 1: Policy as data and rule evaluation

**Goal.** Move every business rule out of code into versioned data, and evaluate the first hard rules.

**Scope.**

- Policy files, append-only, each decision citing its version.
- Rules: registration number matches the registry, tax registration matches the tax registry, insurance certificate valid on the day, bank account name matches the company name.
- Duplicate detection, and the handling of a registry that is down or that returns conflicting data.
- The clamp: whatever the model proposes, a failing rule never ends as verified.

**Exit criteria.**

- [ ] The registration rule fails on a mismatch, and a proposed `verified` is overridden and recorded. Proof: `tests/test_rules.py::test_failing_rule_with_proposed_verified_gives_needs_review_and_a_flag`. Covers SC-006 to SC-011, which include the demonstration's tests.
- [ ] The insurance rule gives the right answer the day before expiry, on the day and the day after. Proof: planned. Covers SC-012 to SC-014.
- [ ] A bank name mismatch, a tax mismatch and a duplicate each raise a flag for a person. Proof: planned. Covers SC-015 to SC-017.
- [ ] A registry that is down pauses the check and tells a person. A registry that conflicts is flagged with both values. Proof: planned. Covers SC-018 and SC-019.
- [ ] A resubmission after rejection is a new case under the current policy, and the earlier decision stays in the record. Proof: planned. Covers SC-020.
- [ ] A change to a policy is a new version and applies to new cases only. Proof: planned.

**Human gate.** The owner signs policy version 1 in the decision log after the policy-change workflow.

---

## Phase 2: Document reading and flagged judgment

**Goal.** Add the three places where a model is allowed, and show that none of them can change a decision.

**Scope.**

- Reading uploaded documents into typed fields.
- Drafting a judgment when the evidence is ambiguous. The draft is always flagged.
- Writing messages to the supplier from typed fields only.
- The red-team probes for every surface where outside text enters.

**Exit criteria.**

- [ ] Instruction text inside a document is treated as data, raises a flag and sends the file to a person, and is never rejected automatically. Proof: planned. Covers SC-021, and INV-11.
- [ ] A supplier's request to skip a check is treated as data, and no check is skipped. Proof: planned. Covers SC-022.
- [ ] A value the reader is unsure of becomes a flagged draft that a person confirms. Proof: planned. Covers SC-023.
- [ ] The text of a document never reaches the model that writes messages. Proof: planned. Covers INV-13.
- [ ] Every detection has a recorded mutate-to-red proof. Proof: planned. Covers INV-06.

**Human gate.** The owner reviews the red-team results before phase 3 starts.

---

## Phase 3: Human approval screen and full regression run

**Goal.** Put a named person in front of every supplier file, and prove the whole system meets the pass bar.

**Scope.**

- The approval screen: the file, the checks that ran, the policy version, what the model proposed and what the system decided.
- Activation, which is only possible with a named approver recorded in the ledger.
- The full regression, the graded run and the final audit.

**Exit criteria.**

- [ ] An approver cannot approve their own submission. Proof: planned. Covers SC-024.
- [ ] A supplier cannot be activated without a named approver in the ledger. Proof: planned. Covers SC-025, and INV-15.
- [ ] The acceptance numbers were signed before the graded run. Proof: the signature line in [acceptance.md](acceptance.md), dated before the run. Covers INV-12.
- [ ] The full regression passes and the register check passes. Proof: planned.
- [ ] The auditor returns no BLOCK. Proof: planned.

**Human gate.** The owner signs the acceptance numbers before the graded run, and signs the final gate after it.
