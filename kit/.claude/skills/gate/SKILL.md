---
name: gate
description: Run the independent audit for the current phase. Run it yourself with /gate. Runs the regression, calls the invariant-auditor agent, and records its verdicts in the phase log. Claude does not start it on its own.
disable-model-invocation: true
---

# /gate

## Purpose

Get an independent verdict on whether the phase respects every invariant, and record it where a reviewer will look.

**Usage:** `/gate`

This command is the Verify stage of `.claude/workflow-docs/build-phase.md`.

## What it does

1. Confirms the phase log has every slice ticked with proof.
2. Runs the regression, as `/regress` does, unless it was run after the last change.
3. Works out the git range since the last gate. The phase log records the previous gate's commit. For the first phase, use the whole history.
4. Delegates to the `invariant-auditor` agent, naming it explicitly. The brief gives it the phase number, the phase log path and the git range, and tells it to return the audit in the format in the invariants skill and to write no files.
5. Copies the audit it returns into the phase log under "Gate results", unchanged.
6. If the overall verdict is BLOCK, stops and lists each block. A block is cleared by a fix or by the owner's recorded decision. Fix the problem and run `/gate` again.
7. If the overall verdict is PASS, says that the human gate is next.

## Prerequisites

- The phase log exists with the exit criteria and slices.
- The regression command is filled in.

## Expected output

An audit table with a verdict and evidence for every invariant, an overall verdict, and a list of anything not-verifiable. The phase log's "Gate results" table is updated.

## Troubleshooting

| Problem | Solution |
|---|---|
| The auditor says "cannot audit: no diff range given" | Give it the range. Find the previous gate's commit in the phase log. |
| An invariant is BLOCK because its check has an unfilled slot | Fill the slot through `/rule-change`. The invariants file is protected. |
| The implementing agent wants to argue with a BLOCK | It cannot clear it. Only a fix or the owner's recorded decision does. |
| The regression fails | Do not call the auditor yet. Fix the failure, or log it as a finding. Never re-run until green. |
