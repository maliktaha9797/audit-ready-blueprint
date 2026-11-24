> Illustrative trail: this file shows the format and maps to what demo/ implements. It describes no build beyond that, and no person signed anything.

# Phase 0: Foundations

## Scope

The decision ledger, fail-closed outbound sending, synthetic fixtures, and the kit's hooks. It leaves out the mocked registries and the case store, which have not been built.

Previous gate commit: none, because this is the first phase.

Register rows in scope: SC-001, SC-002, SC-003, SC-004, SC-005.

## Exit criteria

Each line records the proof and one label. A box is ticked only when the proof has been run. The criteria that this repository cannot test are left unticked, with the reason.

- [x] The ledger finds an edited, a deleted and a reordered entry. Proof: `tests/test_ledger.py::test_editing_an_entry_is_detected`, `tests/test_ledger.py::test_deleting_an_entry_is_detected` and `tests/test_ledger.py::test_reordering_entries_is_detected`, all passing in the run below. Label: executed.
- [x] Outbound sending is suppressed, and the suppression recorded, for a missing, unknown and misspelt mode, a missing allowlist and an unlisted recipient. Proof: `tests/test_outbound.py::test_send_is_suppressed_when_mode_is_missing`, `tests/test_outbound.py::test_send_is_suppressed_when_mode_is_unknown`, `tests/test_outbound.py::test_send_is_suppressed_when_mode_is_misspelt`, `tests/test_outbound.py::test_send_is_suppressed_when_the_allowlist_is_missing` and `tests/test_outbound.py::test_send_is_suppressed_when_the_recipient_is_not_on_the_allowlist`. Label: executed.
- [x] The six synthetic suppliers exist and each is marked synthetic. Proof: `tests/test_rules.py::test_fixtures_cover_all_six_scenarios` and `tests/test_rules.py::test_every_fixture_supplier_is_marked_synthetic`. Label: executed.
- [x] The hooks block a write to a real-data path and to the approvals folder. Proof: `tests/test_hooks.py::test_write_to_real_data_path_blocked` and `tests/test_hooks.py::test_write_to_approvals_folder_blocked`. Label: executed.
- [ ] One supplier's file cannot read another's (INV-14). Proof: none possible here, because this repository has no case store. Label: not-verifiable.
- [ ] Every registry is a mock, and every live mode is off by default (INV-16). Proof: none possible here, because this repository has no registry mock. The demonstration's outbound default is already closed, which is related but is not this criterion. Label: not-verifiable.
- [ ] The owner has signed the phase 0 gate. Proof: none. No person signed this illustrative log. Label: not-verifiable.

## Slices

Small pieces of work. Each ends with the test that proves it. A ticked slice carries a proof and a label, like an exit criterion.

- [x] The ledger: append, read, verify. Proof: `tests/test_ledger.py::test_append_then_verify_passes`. Label: executed.
- [x] The ledger has no way to update or delete. Proof: `tests/test_ledger.py::test_ledger_offers_no_way_to_update_or_delete`. Label: executed.
- [x] Outbound: the single case that sends. Proof: `tests/test_outbound.py::test_message_is_sent_only_in_live_mode_to_an_allowlisted_recipient`. Label: executed.
- [x] Outbound: nothing is sent if the ledger cannot be written. Proof: `tests/test_outbound.py::test_nothing_is_sent_if_the_ledger_cannot_be_written`. Label: executed.
- [x] The registration rule and its clamp. Proof: `tests/test_rules.py::test_failing_rule_with_proposed_verified_gives_needs_review_and_a_flag`. Label: executed.
- [x] Each detection shown able to fail. Proof: `tests/test_mutations.py::test_tamper_detection_fails_when_verify_always_reports_clean`. Label: executed.
- [ ] The case store with one folder per supplier. Proof: not started.
- [ ] The mocked registries with fixture-selectable outcomes. Proof: not started.

## Gate results

| Check | Command or reviewer | Result | Label |
|---|---|---|---|
| Regression suite | `python -m pytest tests/test_ledger.py tests/test_outbound.py tests/test_rules.py tests/test_mutations.py` | `59 passed in 0.14s`, run on 2026-11-24 | executed |
| Mutate-to-red | `python scripts/mutate_kit.py` | Every mutation turned its tests red. The summary line read `mutations that stayed green or failed setup: 0`. | executed |
| Register check | `python3 scripts/check_register.py` | Not run. The script would belong to the build and is not in this repository. | not-verifiable |
| Invariant audit | the `invariant-auditor` agent, called by `/gate` | Not run. There is no project to audit. This repository's own audit is in `BUILD-REPORT.md`. | not-verifiable |
| Red team | the `red-team` agent | Not applicable to phase 0, which reads no outside text. | read |

## Session notes

2026-11-24: the demonstration modules were written and tested. The five exercises in the walkthrough were run to record which tests fail for each change.

## Human gate sign-off

| Field | Value |
|---|---|
| Gate required by the plan | yes |
| Approved by | not signed |
| Date | none |
| Conditions | none. No person signed this illustrative log. |

## Handoff notes

Phase 1 starts only after the owner signs this gate. Before that, the case store, the three mocked registries and their live-mode test are still to do. The demonstration's registration rule is the only rule built.
