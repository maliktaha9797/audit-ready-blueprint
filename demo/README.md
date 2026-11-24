# The demonstration

A small piece of working code that proves the kit's invariants INV-07, INV-09 and INV-10. It is written to be read: the code is plain, every function has a docstring and type hints, and each module is about a hundred lines or fewer. A reader who is learning Python should be able to explain every line, and [WALKTHROUGH.md](WALKTHROUGH.md) does that.

It does not build a supplier onboarding tool. It shows three building blocks that such a tool would need if its decisions had to be traced to a rule and to a person.

## What it shows

| Module | What it does | Invariant | Tests that prove it |
|---|---|---|---|
| `supplier_demo/ledger.py` | An append-only decision record stored as JSON lines. Each entry holds the hash of the one before, so an edit, a removal or a reordering is found by `verify`. There is no function to update or delete. | INV-10 | `tests/test_ledger.py` |
| `supplier_demo/outbound.py` | Sending a message to a supplier, failing closed. It sends only when the mode is exactly `live` and the recipient is on the allowlist. Anything else is suppressed, and the suppression is recorded. | INV-09 | `tests/test_outbound.py` |
| `supplier_demo/rules.py` | One hard rule (the registry holds the registration number the supplier gave) and its clamp: whatever a model proposes, a failing rule can never end as `verified`. | INV-07 | `tests/test_rules.py` |

The invariant ids are defined in the table in [the invariants skill](../kit/.claude/skills/invariants/SKILL.md).

## How to run it

From the root of the repository, with Python 3.12 or later:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install pytest
.venv/bin/python -m pytest
```

To run only the demonstration's tests:

```bash
.venv/bin/python -m pytest tests/test_ledger.py tests/test_outbound.py tests/test_rules.py tests/test_mutations.py
```

To see that the tests can fail, run the mutate-to-red harness. It breaks one thing at a time, runs the tests that should notice, and restores the file:

```bash
.venv/bin/python scripts/mutate_kit.py
```

## Proof that the detections can fail

`tests/test_mutations.py` holds one test for each guarded behaviour. Each test runs a small detection on the real code and expects it to succeed, then breaks the guard with `monkeypatch` and expects the same detection to report failure. The guards broken are: a `verify` that always reports clean, a hash that ignores the content, a `send` that ignores the mode, a `send` that ignores the allowlist, a `decide` that trusts the proposal, and a rule that always passes.

`scripts/mutate_kit.py` goes one step further. It edits the source of each module, runs the main tests, and checks that they go red.

## The code rules

Written so a beginner can read every line, and checked by `tests/test_demo_code_rules.py`:

- Python 3.12, standard library only. No other import, in the code or the tests, except `pytest`.
- No classes where a function will do. No decorators. No lambdas.
- Type hints on every function, and a docstring on every function that says what it does and names the invariant it serves.
- No comprehension longer than one clause. In practice there are none.
- Each module is about a hundred lines or fewer.

## The synthetic suppliers

`fixtures/suppliers.json` holds six invented suppliers, each marked `"synthetic": true`, with an id that starts `SYN-`. Their names and registration numbers are made up. No real company is described.

| Id | Scenario | Used by the demo |
|---|---|---|
| SYN-001 | A clean file | The rule passes, and a `verified` proposal goes through |
| SYN-002 | The registration number differs from the registry's | The rule fails, and a `verified` proposal is clamped to `needs_review` with a flag |
| SYN-003 | An expired insurance certificate | Fixture only. The demo has no insurance rule. |
| SYN-004 | Bank details in a different company name | Fixture only. The demo has no bank rule. |
| SYN-005 | A document containing an instruction aimed at the model | Shows that document text never changes the decision, because the rule reads typed fields only |
| SYN-006 | A duplicate submission | Fixture only. The demo has no duplicate check. |

## What it is not

- It is not a supplier onboarding tool. It evaluates one rule. The other scenarios are fixtures that a larger build would test.
- It calls no model and no network. The "model" is an argument named `proposed_status`, and "sending" adds to a list in memory.
- The ledger stops a casual change, not a determined one. It cannot see an entry removed from the very end of the file, or an edit followed by recomputing every later hash, because what remains is still a valid chain. `verify` catches both if it is given the last hash saved somewhere else. Tests record these limits.
