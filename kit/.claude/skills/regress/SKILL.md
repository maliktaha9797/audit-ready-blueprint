---
name: regress
description: Run the full regression suite and the register check, and record the result in the phase log. Run it yourself with /regress. Claude does not start it on its own.
disable-model-invocation: true
---

# /regress

## Purpose

Run every test and the register check, and record the real result.

**Usage:** `/regress`

## What it does

1. Runs the project's regression command: `<<FILL: the full test command, for example python -m pytest>>`.
2. Runs the register check: `python3 scripts/check_register.py`.
3. Records both summary lines in the phase log under "Gate results", labelled executed, with the command.
4. If anything fails, lists each failing test id and stops. It does not re-run the suite hoping for a pass.
5. If a test passes on one run and fails on another, logs it as a finding in `patterns.md` and treats the criterion as not met.

## Prerequisites

- The test command above is filled in.
- A phase log is open.

## Expected output

Two recorded lines: the test summary, for example the counts of passed and failed tests, and the register check result. Failing test ids are listed by name.

## Troubleshooting

| Problem | Solution |
|---|---|
| The test command is still a slot | Stop and ask the owner for the command. |
| A test fails | Fix it through `/new-scenario` if it is a new case. Do not weaken the test. |
| A test is flaky | Record every run, log it in `patterns.md`, fix the cause or mark the criterion not-verifiable. |
| The register check names a missing test | Either write the test or set the row back to `planned`. |
