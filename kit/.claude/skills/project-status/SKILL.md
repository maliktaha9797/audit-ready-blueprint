---
name: project-status
description: Report where the project stands against the plan, from the context files only. Run it yourself with /project-status. Claude does not start it on its own. This is not the built-in /status command, which shows version and account details.
disable-model-invocation: true
---

# /project-status

## Purpose

Say where the project stands against the plan, using only what the context files record, so the answer matches what a reviewer would find.

**Usage:** `/project-status`

## What it does

1. Reads `.claude/context/summary.md`.
2. Reads the open phase log and lists exit criteria that are not yet ticked, with the label each one has so far.
3. Reads `open-questions.md` and lists questions that wait for the owner.
4. Reads `rule-changes.md` and lists proposals that are open.
5. Reads `register.csv` and reports how many rows are in each status.
6. Reports the next step and whether a human gate is waiting.

It does not read source code, run tests or change any file. If the context files disagree with each other, it says so and does not choose between them.

## Prerequisites

- The context files exist.

## Expected output

A short report with five parts: current state, unticked criteria, questions for the owner, open rule changes and register status. Each statement names the file it came from.

## Troubleshooting

| Problem | Solution |
|---|---|
| The summary is out of date | Say so. The phase log and the decision log are the record. Update the summary through the Close stage. |
| No phase log exists | Report that no phase has started. |
| The files contradict each other | Report the contradiction with both file names. Do not resolve it. |
