---
name: new-scenario
description: Register a new edge case, write its failing test, then fix it. Run it yourself with /new-scenario and a short description. Claude does not start it on its own.
disable-model-invocation: true
argument-hint: "[short description of the case]"
---

# /new-scenario

## Purpose

Make sure an edge case has a register row and a failing test before any fix is written.

**Usage:** `/new-scenario <short description>`. The case is: $ARGUMENTS

The workflow is `.claude/workflow-docs/new-scenario.md`. Follow that file. Do not repeat its steps here.

## What it does

1. Turns the description into one concrete scenario with one input and one expected behaviour.
2. Adds a row to `.claude/context/register.csv` with status `planned`.
3. Writes a synthetic fixture and a test, runs it, and confirms it fails.
4. Makes the general fix, runs the test, and confirms it passes.
5. Sets the row to `covered` and records the proof in the phase log.

## Prerequisites

- A phase log is open.
- The `scenario-register`, `synthetic-data` and `fixtures-and-harness` skills have been read.

## Expected output

A new register row, a test that failed and now passes, and a phase log entry with both runs recorded.

## Troubleshooting

| Problem | Solution |
|---|---|
| The description is vague | Split it into rows that each have one input and one expected behaviour. |
| The new test passes before the fix | The test does not detect the case. Fix the test first. |
| The fix would match only the test input | Stop. Fix the class of input. |
| The case needs a real record to reproduce | Decline it. Invent an equivalent and log the offer in `open-questions.md`. |
