---
name: scenario-register
description: How to register an edge case before fixing it. Covers the register row format, who decides (code, model or human), splitting a vague scenario into checkable rows, and the check script. Use when a new edge case, bug or near-miss appears, or when planning the scenarios a phase must cover.
---

# Scenario register

## Purpose

The register is the list of situations the system must handle, with the behaviour required in each and the test that proves it. A scenario is registered, and its test is written, before the change that addresses it. That order is what makes the test meaningful: it must be able to fail first.

The register lives in `.claude/context/register.csv`.

## When to use

- A new edge case, bug or near-miss appears.
- A phase is being planned and its scenarios need listing.
- A reviewer asks "where is that case tested?"

## Row format

One row per scenario, with these columns in this order:

| Column | Meaning |
|---|---|
| `id` | A stable id such as `SC-014`. Never reused, never renumbered. |
| `scenario` | The situation, in one sentence, concrete enough to build a fixture from. |
| `required_behaviour` | What must happen, stated so that a test can assert it. |
| `decider` | Who decides the outcome: `code`, `model` or `human`. |
| `phase` | The phase in which the scenario must be covered. |
| `fixture_id` | The test id that proves it (see the fixtures-and-harness skill), or `planned` until one exists. |
| `status` | `planned` (no test yet), `red` (the test exists and fails) or `covered` (the test exists and passes). |

Deciders:

- **code**: a rule decides. This should be most rows.
- **model**: the model drafts a judgment. The draft is always flagged for a person, so a `model` row also states the flag.
- **human**: a named person decides. The row states what the system shows them.

## The order of work

1. Add the row with status `planned`.
2. Write the test. Run it. It must fail. Set the status to `red`.
3. Make the change that addresses it.
4. Run the test. It must pass. Set the status to `covered`.

A fix with no row, or a row added after its fix, breaks INV-05.

## Splitting a vague scenario

A row such as "handles bad documents" cannot be tested. Split it until each row has one input and one expected behaviour.

| Vague | Checkable rows |
|---|---|
| Handles bad documents | The file is empty. The file is the wrong type. The file is unreadable. The file is larger than the limit. The file is readable but a required field is missing. |
| Handles an unreliable service | The service times out. The service returns an error code. The service returns data that conflicts with what we hold. The service is down for the whole run. |

## Five generic example rows

These show the format. Replace them with your own.

| id | scenario | required_behaviour | decider | phase | fixture_id | status |
|---|---|---|---|---|---|---|
| SC-001 | A required field is missing from a submission | The submission is rejected with a named reason and nothing is saved | code | 1 | planned | planned |
| SC-002 | Two submissions arrive with the same reference | The second is flagged as a duplicate for a person and neither is dropped | code | 1 | planned | planned |
| SC-003 | An external service is unavailable | Work pauses, a person is told, and nothing is marked as passed | code | 2 | planned | planned |
| SC-004 | The evidence is ambiguous and a judgment is needed | The model drafts a judgment, the draft is flagged, and a person decides | model | 2 | planned | planned |
| SC-005 | A reviewer tries to approve their own submission | The approval is refused and the attempt is recorded | human | 3 | planned | planned |

## The check script

Save this as `scripts/check_register.py` and run `python3 scripts/check_register.py`. It exits non-zero if a row is malformed, or if a `red` or `covered` row cites a test id that pytest does not collect. The id must match a collected id exactly: a prefix of a real id does not count. It is the check behind INV-05.

```python
"""Check the scenario register against the collected tests."""
import csv
import subprocess
import sys

REGISTER = ".claude/context/register.csv"
COLUMNS = ["id", "scenario", "required_behaviour", "decider", "phase", "fixture_id", "status"]


def main() -> int:
    """Return 0 if the register is well formed and its tests exist."""
    with open(REGISTER, newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            print("columns must be: " + ",".join(COLUMNS))
            return 1
        rows = list(reader)
    output = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True, text=True,
    ).stdout
    collected = set()
    for line in output.splitlines():
        collected.add(line)
        collected.add(line.split("[")[0])
    problems = []
    for row in rows:
        if row["decider"] not in ("code", "model", "human"):
            problems.append(row["id"] + ": decider must be code, model or human")
        if row["status"] not in ("planned", "red", "covered"):
            problems.append(row["id"] + ": status must be planned, red or covered")
        if row["status"] in ("red", "covered") and row["fixture_id"] not in collected:
            problems.append(row["id"] + ": test " + row["fixture_id"] + " is not collected")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
```

## Common mistakes

| Mistake | Why it is wrong | Correct approach |
|---|---|---|
| Writing the fix, then the row | The test cannot be shown to fail first | Row, failing test, fix, passing test |
| A row with no `required_behaviour` that a test can assert | It cannot be covered | Split it until each row has one input and one expected behaviour |
| Marking a row `covered` on the strength of a manual check | The check cannot be repeated | Write the test, or label the criterion read or not-verifiable |
| Reusing or renumbering ids | Citations in logs and tests stop resolving | Append new ids only |
