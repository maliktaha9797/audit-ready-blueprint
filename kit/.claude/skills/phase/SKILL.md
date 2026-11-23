---
name: phase
description: Start or resume a numbered build phase. Run it yourself with /phase followed by the phase number. Opens the phase log and runs the build-phase workflow. Claude does not start it on its own.
disable-model-invocation: true
argument-hint: "[phase number]"
---

# /phase

## Purpose

Start, or pick up, one numbered phase of the plan, using the same five stages every time.

**Usage:** `/phase <number>`. The phase requested is: $ARGUMENTS

The workflow is `.claude/workflow-docs/build-phase.md`. Follow that file. Do not repeat its steps here.

## What it does

1. Checks that the previous phase's gate is signed in `.claude/context/decisions.md`.
2. Reads `.claude/context/summary.md` and the plan section for the phase.
3. Creates, or reopens, `.claude/context/phases/phase-<n>.md`.
4. Hands the phase to its owner agent, as listed in the workflow's table of phase owners.
5. Works through Orient, Implement, Verify, Human gate and Close.

## Prerequisites

- The plan section for the phase exists.
- The previous phase's gate is signed, unless this is the first phase.
- No open BLOCK from a previous audit.

## Expected output

A phase log with scope, exit criteria and slices. The owner agent starts the first unticked slice. The command stops at the human gate if the plan requires one.

## Troubleshooting

| Problem | Solution |
|---|---|
| No phase number was given | Ask which phase. Do not guess. |
| The previous gate is not signed | Stop and tell the owner. Do not start the phase. |
| The plan has no section for this phase | Stop. Add the question to `open-questions.md`. |
| The phase log already exists | Reopen it and continue from the first unticked slice. |
