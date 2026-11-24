> Illustrative trail: this file shows the format and maps to what demo/ implements. It describes no build beyond that, and no person signed anything.

# Decision log

This log is append-only and holds the current period only. Add new entries at the end. Never edit or delete a past entry. If a decision changes, add a new entry that names the one it supersedes.

The dates are the dates this repository was built. "Decided by" names a role in the fictional project, and not a real person.

## Entries

### 2026-11-24: business rules are held as versioned data

- **Decision:** Thresholds, windows, lists and mappings live in versioned policy files. The engine holds no business number. A change is a new version and applies to new cases only.
- **Why:** So a rule can change without a code change, and so every decision can cite the version it used.
- **Supersedes:** nothing
- **Decided by:** the product owner (a role in this fictional project)

### 2026-11-24: the ledger is a hash chain

- **Decision:** Each ledger entry stores the hash of the entry before it. `verify` recomputes the chain and reports the first bad position. There is no function that updates or deletes an entry.
- **Why:** So an edit, a removal or a reordering of the decision record can be found (INV-10).
- **Supersedes:** nothing
- **Decided by:** the product owner (a role in this fictional project)

### 2026-11-24: the ledger's end-of-file limit is accepted for the demonstration

- **Decision:** An entry removed from the very end of the file cannot be seen from the file alone. The demonstration records this with a test. The build will keep the last hash somewhere other than the ledger file and pass it to `verify`.
- **Why:** The limit is inherent to a hash chain. Writing it down is more honest than hiding it.
- **Supersedes:** nothing
- **Decided by:** the product owner (a role in this fictional project)

### 2026-11-24: outbound is suppressed unless the mode is exactly live and the recipient is listed

- **Decision:** A message is sent only when the mode setting is exactly `live` and the recipient is on the allowlist. Any other state suppresses the message and records why. The ledger entry is written before anything is sent.
- **Why:** A missing, misspelt or unknown setting must never result in a message leaving (INV-09).
- **Supersedes:** nothing
- **Decided by:** the product owner (a role in this fictional project)

### 2026-11-24: the registration rule is the first hard rule

- **Decision:** The first rule built is that the registry holds the registration number the supplier gave. Whatever a model proposes, a failing rule ends as `needs_review` with a flag. The other rules, such as insurance validity and the bank name, are phase 1.
- **Why:** It is the smallest rule that shows the clamp working (INV-07).
- **Supersedes:** nothing
- **Decided by:** the product owner (a role in this fictional project)

### 2026-11-24: the ledger's limit also covers a full rewrite

- **Decision:** The end-of-file limit is wider than first recorded. An edit followed by recomputing every later hash also leaves a valid chain. The demonstration now records this with tests. The remedy is unchanged: the build keeps the last hash somewhere other than the ledger file and passes it to `verify`.
- **Why:** A review of the demonstration found the wider case. The decision log is append-only, so this entry adds to the earlier one and does not change it.
- **Supersedes:** 2026-11-24, the ledger's end-of-file limit is accepted for the demonstration (in scope only)
- **Decided by:** the product owner (a role in this fictional project)
