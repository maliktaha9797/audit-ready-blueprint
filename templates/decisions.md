<!-- What it is: an append-only log of decisions. Each entry says what was decided, why, and what it replaces. -->
<!-- When to create it: always. Start it with the first decision that shapes the project. -->
<!-- Where it goes: .claude/context/decisions.md for the current period. Move older entries to .claude/context/archive/ by month. -->

# Decision log

This log is append-only. Add new entries at the end. Never edit or delete a past entry. If a decision changes, add a new entry that names the one it supersedes.

## Entry format

```
### <<FILL: date, YYYY-MM-DD>>: <<FILL: short title>>

- **Decision:** <<FILL: what was decided>>
- **Why:** <<FILL: the reason, in one or two sentences>>
- **Supersedes:** <<FILL: the date and title of an earlier entry, or "nothing">>
- **Decided by:** <<FILL: the person's name or role, or "agent, within knowledge changes">>
```

## Entries

### <<FILL: date>>: <<FILL: title>>

- **Decision:** <<FILL: decision>>
- **Why:** <<FILL: reason>>
- **Supersedes:** nothing
- **Decided by:** <<FILL: name or role>>
