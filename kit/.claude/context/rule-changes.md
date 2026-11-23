# Rule-change proposals

A rule is anything that decides what is allowed: the prohibitions in `CLAUDE.md`, the invariants skill, `settings.json`, `guard.json`, the hooks, and the auditor's definition. The agent proposes a change here, stops, and waits. A person reviews it and, if they agree, creates the approval file by hand. Only then does the agent make exactly the approved change. The process is in `.claude/workflow-docs/rule-change.md`.

## How the hooks read this file

- An entry heading starts with `### ` followed by the id, for example `### RC-001`.
- The line `- Status: open` marks an entry as open. Any other status, including `closed` and `sample`, is not open.
- A protected file may be edited only if an open entry exists and a file named `.claude/context/approvals/<id>.approved` exists whose `Files:` line covers that file. See the approvals section of `kit/README.md`.

## Entry format

```
### RC-<number>: <short title>

- Status: open
- Files: <the file or files to change, comma separated>
- Change: <the exact change, as a diff or the exact new text>
- Reason: <why the change is needed>
- Triggered by: <the scenario, near-miss or request that led to it>
- Closed: <commit id and date, added when the entry is closed>
```

Ids are `RC-` followed by three digits, never reused. Statuses are `open`, `closed`, `declined` and `sample`.

## Entries

### RC-000: sample entry, not a real proposal

- Status: sample
- Files: CLAUDE.md
- Change: none. This entry shows the format and is never open.
- Reason: to show a reader what a filled entry looks like.
- Triggered by: the kit's own documentation.
- Closed: not applicable
