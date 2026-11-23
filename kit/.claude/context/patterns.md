# Patterns and near-misses

Gotchas, near-misses and lessons learnt. The agent may append to this file freely, because these are knowledge and not rules. If a lesson suggests a new prohibition or a new violation signature, propose it with `/rule-change`. Do not edit the rulebook from here.

Do not edit past entries. Append only.

## Entry format

```
### <date>: <short title>

- **What happened:** the pattern or near-miss, in one or two sentences
- **Where:** the file, test id or phase
- **Action taken:** what was done about it, or "none yet"
- **Rule change proposed:** the id, or "none"
```

## Entries

### 2026-01-01: sample entry (synthetic, not a real near-miss)

- **What happened:** A test passed on three runs and failed on the fourth when two tests shared one temporary folder.
- **Where:** `tests/test_sample.py::test_sample_case` (synthetic id)
- **Action taken:** Each test now creates its own temporary folder. The four runs are recorded in the phase log.
- **Rule change proposed:** none
