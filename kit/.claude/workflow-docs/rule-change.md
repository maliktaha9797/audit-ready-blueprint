# Rule change

## Overview

How the rulebook is changed. The rulebook is the set of files listed under `protected_paths` in `.claude/guard.json`. That list is the only place it is written. It covers `CLAUDE.md`, the settings, the hooks, the agents, the invariants skill, the gate and regression commands, the workflow files and the pass bar. The agent proposes and stops. A person approves by hand. Only then does the agent make exactly the approved change.

This is the difference between a setup that can be audited and one that cannot: an agent that can rewrite its own rules can make any check pass.

**Started by:** `/rule-change <file and what to change>`

## What counts as a rule

| Change | Kind | Process |
|---|---|---|
| Adding, removing or loosening a prohibition, an invariant, a permission, a hook, an agent's tools, a workflow step, the gate or regression command, the pass bar, or a protected path | Rule | This workflow |
| Adding a violation signature to the invariants skill | Rule | This workflow, because it changes what the auditor looks for |
| Recording a pattern, a gotcha, context, or a lesson learnt | Knowledge | The agent updates the file and appends to the log |

If a change would make a check easier to pass, it is a rule change.

## Steps

1. **Write the proposal.** Add an entry to `.claude/context/rule-changes.md`, in the format shown there: id, status `open`, the files, the exact change, the reason and what triggered it. Use the next free id.
2. **Stop.** Tell the owner the id, where the entry is, and which files it covers. Do not edit any protected file. The hooks would block it, and attempting it is a violation signature.
3. **Wait for the owner.** The owner reviews the entry. If they agree, they create `.claude/context/approvals/<id>.approved` by hand with three lines:

   ```
   Approved by: <name>
   Date: <date>
   Files: <the files the approval covers, comma separated>
   ```

   The agent has no permitted way to create this file. A permission rule and a hook both refuse its writes to the approvals folder, and the shell guard refuses the write-like commands it recognises when they name the folder. A writer it does not recognise, or a path built at run time, can get past a text check.
4. **If the owner declines,** set the entry's status to `declined`, note the owner's reason, and stop.
5. **Apply exactly the proposed change.** Edit only the files named in the approval, and only as the entry describes. If more is needed, write a new proposal.
6. **Close the entry.** Set its status to `closed` and fill in the commit id and date. Closing it ends the approval: the hook no longer lets the files be edited. Then ask the owner to delete the approval file, because it would come back into force if the entry were ever set to open again. Ids are never reused.
7. **Log it.** Append an entry to `decisions.md` with the owner's name, the date and what changed.
8. **Run the checks.** Run `pytest tests/test_hooks.py` and `<<FILL: the project's rulebook check command, for example python3 scripts/check_rulebook.py>>`. Record both in the phase log, labelled executed.

## Completion criteria

- [ ] The proposal existed and was open before any protected file changed.
- [ ] The approval file was created by a person, and its `Files:` line covers what was changed.
- [ ] The change matches the proposal exactly.
- [ ] The entry is closed with a commit id.
- [ ] The decision log records the change.
- [ ] The checks ran and their results are recorded.

## Context to update

| File | What to add |
|---|---|
| `.claude/context/rule-changes.md` | The proposal, then its closing |
| `.claude/context/decisions.md` | The decision and who made it |
| `.claude/context/phases/phase-<n>.md` | The check results |
