# New scenario

## Overview

How an edge case is added. The rule is that the row and the failing test exist before the fix. That order is what proves the test can detect the problem.

**Started by:** `/new-scenario <short description>`

## Prerequisites

- A phase log is open, or the case arose outside a phase and is logged in `patterns.md`.
- The `scenario-register` skill has been read.

## Steps

1. **Describe the case** as one concrete situation with one input and one expected behaviour. If it is vague, split it, as the scenario-register skill explains.
2. **Choose the decider:** `code`, `model` or `human`. Prefer `code`. A `model` row must also state the flag a person will see.
3. **Add the row** to `.claude/context/register.csv` with the next id, status `planned`, and a fixture id that follows the test naming convention.
4. **Write the fixture** using the synthetic-data skill. It must carry the synthetic marker.
5. **Write the test** that asserts the required behaviour. Run it. It must fail. Set the status to `red` and record the failing run.
6. **Make the change** that addresses the case. Keep it general. Do not match the exact input of the test.
7. **Run the test.** It must pass. Run the full regression with `/regress`.
8. **Set the status to `covered`.** Run `python3 scripts/check_register.py`.
9. **Record** the row id, the test id and the red-then-green evidence in the phase log. If the case was a near-miss, add it to `patterns.md`. If it suggests a new violation signature, propose it with `/rule-change`.
10. **If the scenario touches an untrusted input surface,** ask for a red-team pass in the Verify stage.

## Completion criteria

- [ ] The row exists with a decider, a phase and a fixture id.
- [ ] The test failed before the change, and the failure is recorded.
- [ ] The test passes after the change, and the regression is green.
- [ ] The row's status is `covered` and the register check passes.

## Context to update

| File | What to add |
|---|---|
| `.claude/context/register.csv` | The row and its status changes |
| `.claude/context/phases/phase-<n>.md` | The proof and label |
| `.claude/context/patterns.md` | The near-miss, if there was one |
