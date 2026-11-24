---
name: rule-change
description: Propose a change to the rulebook (the files listed under protected_paths in guard.json) and stop for a person's approval. Run it yourself with /rule-change and a description. Claude does not start it on its own.
disable-model-invocation: true
argument-hint: "[file and what to change]"
---

# /rule-change

## Purpose

Change a rule only with a person's approval, so that no check can be made easier to pass by the agent being checked.

**Usage:** `/rule-change <file and what to change>`. The change is: $ARGUMENTS

The workflow is `.claude/workflow-docs/rule-change.md`. Follow that file. Do not repeat its steps here.

## What it does

1. Writes a proposal in `.claude/context/rule-changes.md`: id, status `open`, files, exact change, reason and trigger.
2. Stops and tells the owner the id and where to look.
3. After the owner creates `.claude/context/approvals/<id>.approved` by hand, applies exactly the proposed change and nothing else.
4. Closes the entry with the commit id and logs the decision.
5. Runs the hook tests and the rulebook check and records them.

## Prerequisites

- A person is available to review.
- The change really is a rule. A lesson or a pattern is knowledge: record it directly.

## Expected output

An open proposal, then, after approval, a closed one with a commit id and a decision-log entry. The proposal is open before any protected file changes.

## Troubleshooting

| Problem | Solution |
|---|---|
| A hook blocks the edit | There is no open proposal with a matching approval. Write the proposal, or wait for the approval. |
| The approval file is rejected | It needs `Approved by:` with a real name and a `Files:` line that covers the file. The owner writes it by hand. |
| The owner wants more than the proposal says | Write a new proposal. The approval covers only the files it lists. |
| The agent is asked to create the approval | It cannot and must not. Only a person creates it. |
