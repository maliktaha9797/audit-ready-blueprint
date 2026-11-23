---
name: policy-change
description: Change a business rule that is held as versioned data, with an append-only new version and the owner's sign-off. Run it yourself with /policy-change and a summary. Claude does not start it on its own.
disable-model-invocation: true
argument-hint: "[policy id and summary of the change]"
---

# /policy-change

## Purpose

Change a business rule without changing engine code, and keep a record of which version made each decision.

**Usage:** `/policy-change <policy id and summary>`. The change is: $ARGUMENTS

The workflow is `.claude/workflow-docs/policy-change.md`. Follow that file. Do not repeat its steps here.

## What it does

1. Writes a new policy version as a new file and leaves the old one untouched.
2. Adds a pending entry to the decision log.
3. Lists the register rows the change affects.
4. Runs the regression with the new version.
5. Asks the owner to sign, waits, and records the sign-off.
6. Makes the version active for new cases only.

## Prerequisites

- The `policy-as-data` skill has been read.
- The change is business data. A change to a guardrail on the agent uses `/rule-change`.

## Expected output

A new version file, a pending and then a decided entry in `decisions.md`, a list of affected rows, and a green regression recorded in the phase log.

## Troubleshooting

| Problem | Solution |
|---|---|
| The rule cannot be written as data | Record an engine gap in `open-questions.md` and stop. Do not hardcode it. |
| The regression fails with the new version | Do not activate it. Show the owner the failing rows. |
| The owner has not signed | The version stays inactive. Do not start new cases under it. |
| Someone asks to re-decide old cases | A change applies to new cases only. Ask the owner for a separate decision. |
