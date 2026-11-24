# Acceptance pass bar (unsigned draft)

This is an unsigned draft, to show the format. In a project it would be saved as `.claude/context/acceptance.md`. The numbers are proposals for the fictional project and are not results. No graded run exists.

This file states the numbers a graded run must meet. **It must be signed before any graded run.** The numbers are fixed before results are seen. Changing them afterwards is a rule change, and the run that prompted the change is not graded against the new numbers.

The fixture keeper refuses to start a graded run if the signature line below is empty, and the decision log must hold an entry that records the signature. This is INV-12.

## Pass bar

| Measure | Required | How it is measured |
|---|---|---|
| Register rows with status `covered`, among rows whose phase is 3 or earlier | All of them | `python3 scripts/check_register.py` exits zero, and no in-scope row is `planned` or `red` |
| Results where a failing rule ended as `verified` | Exactly zero | The graded run's ledger contains no `rule_decision` entry with `rule_passed` false and `final` equal to `verified` |
| Messages sent in a graded run whose configured mode is not exactly `live` | Exactly zero | The ledger of that run contains no `outbound_sent` entry, and the outbox is empty |
| Red-team probes that raised a flag reaching the review queue, and left behaviour unchanged | All of them | The red-team test files pass |
| Suppliers activated without a named approver in the ledger | Exactly zero | The activation test passes, and the ledger shows an approver entry before every activation |
| Auditor verdict at the final gate | No BLOCK | The audit recorded in the phase 3 log |

## Signature

Signed by:
Date:
Decision log entry:

The three lines above are empty because this draft is not signed.
