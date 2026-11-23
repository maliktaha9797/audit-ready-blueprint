---
name: fixtures-and-harness
description: How to turn every verification into a runnable test, name test ids, prove a detection test can fail (mutate-to-red), and handle flaky tests. Use when writing or reviewing tests, closing an exit criterion, or recording proof in a phase log.
---

# Fixtures and harness

## Purpose

An exit criterion that depends on someone's say-so cannot be audited. Every verification the plan depends on must be a test that can be run again, and a test that has never failed has not been shown to detect anything.

## When to use

- You are about to tick an exit criterion.
- You are writing a test for a detection, a block, a clamp or a flag.
- A test failed once and passed on re-run.

## Test ids

A test id is the string a person can type to run exactly that test, for example `tests/test_ledger.py::test_edited_entry_is_detected`. Proof in a phase log is a test id or a command, never a sentence about quality.

Naming convention:

- File: `tests/test_<area>.py`, one area per file.
- Test: `test_<behaviour>_<condition>`, written so that the name alone says what failing means. For example `test_send_is_suppressed_when_mode_is_missing`.
- The id never changes after it is cited. If a test is renamed, search for the old id and update every citation in the same change.

## Fixtures

- A fixture is a synthetic record or file kept in the repository so a test is repeatable. Every fixture follows the synthetic-data skill.
- Each fixture has an id that a register row cites in its `fixture_id` column.
- A fixture's name says what is special about it, for example `supplier_expired_certificate`, not `case_7`.

## Mutate to red

To trust a detection test, break the thing it guards once and confirm the test fails.

1. Pick the guard: the check, the clamp, the rule, the hook condition.
2. Break it in the smallest way that should defeat the detection. For example make the verifier always report clean, make the send ignore its mode, or make the rule trust the proposal.
3. Run the detection test. It must fail.
4. Restore the guard exactly. Run the test again. It must pass.
5. Record the proof in the phase log: the mutation, the test id that failed, and the restore. Label it executed.

If the test stays green when the guard is broken, the test detects nothing. That is a finding: fix the test, then repeat.

Automate the proof where you can. A test that applies the mutation with a patching tool and asserts that the detection now reports a failure is repeatable evidence. The demonstration in this repository's `demo/` shows the pattern.

Never fix a failed detection by matching the exact test input. A fix must work for a class of input. If the only change is that one string is now blocked, the detection is worse, not better.

## Flaky tests

A test that passes on some runs and fails on others is a finding, not an annoyance.

- Do not re-run it until it passes. Record every run that failed.
- Log it in `patterns.md`: the test id, how it failed, and the suspected cause (time, ordering, shared state, randomness).
- Fix the cause, or mark the criterion not-verifiable with the reason. Do not mark it executed.

## Checklist

Before ticking a criterion:

- [ ] The proof is a test id or a command.
- [ ] The test was run in this session, and the result is recorded.
- [ ] If it detects something, a mutate-to-red record exists.
- [ ] The label is executed, read or not-verifiable, and is true.

## Common mistakes

| Mistake | Why it is wrong | Correct approach |
|---|---|---|
| Ticking a criterion because the code looks right | Looking is the label **read**, not **executed** | Run it, or label it read |
| Citing a test that has never failed | It may detect nothing | Mutate to red once and record it |
| Blocking the literal string from a probe | The next phrasing passes | Fix the class of input |
| Re-running a flaky test until green | Hides a real defect | Log it in `patterns.md` and fix the cause |
