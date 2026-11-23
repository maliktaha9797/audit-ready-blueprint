# Decision log

This log is append-only and holds the current period only. Add new entries at the end. Never edit or delete a past entry. If a decision changes, add a new entry that names the one it supersedes.

At the end of each month, move that month's entries to `archive/decisions-YYYY-MM.md`. Moving an entry copies it unchanged. This keeps the file small enough to read at the start of a session.

## Entry format

```
### <date, YYYY-MM-DD>: <short title>

- **Decision:** what was decided
- **Why:** the reason, in one or two sentences
- **Supersedes:** the date and title of an earlier entry, or "nothing"
- **Decided by:** the person's name or role, or "agent, within knowledge changes"
```

## Entries

### 2026-01-01: sample entry (synthetic, not a real decision)

- **Decision:** Business rules are held as versioned data, not in engine code.
- **Why:** So a rule can change without a code change and every decision cites the version it used.
- **Supersedes:** nothing
- **Decided by:** sample owner (synthetic)
