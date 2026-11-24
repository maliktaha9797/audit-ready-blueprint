> Illustrative trail: this file shows the format and maps to what demo/ implements. It describes no build beyond that, and no person signed anything.

# Project context summary

> Read this file first at the start of every session. Update it last.
> Hard cap: 120 lines. Move detail to the phase logs and keep only pointers here.
> Last updated: 2026-11-24

---

## Current state

### Built

- The decision ledger, in `demo/supplier_demo/ledger.py`. Proof: `tests/test_ledger.py`.
- Fail-closed outbound sending, in `demo/supplier_demo/outbound.py`. Proof: `tests/test_outbound.py`.
- The registration rule and its clamp, in `demo/supplier_demo/rules.py`. Proof: `tests/test_rules.py`.
- Six synthetic suppliers, in `demo/fixtures/suppliers.json`.

Nothing else is built. The tool itself, the mocked registries, the case store and the approval screen do not exist.

### In progress

- [ ] Phase 0 exit criteria that the demonstration does not cover. See: `example/context/phases/phase-0.md`

### Blocked

- Phase 1 cannot start until the owner signs the phase 0 gate. No one has signed.

---

## Phase status

| Phase | Name | Status | Gate signed |
|---|---|---|---|
| 0 | Foundations | In progress | No |
| 1 | Policy as data and rule evaluation | Not started | No |
| 2 | Document reading and flagged judgment | Not started | No |
| 3 | Human approval screen and full regression run | Not started | No |

Status words: Complete, In progress, Not started, Blocked.

---

## Tech stack

| Component | Version or details |
|---|---|
| Language | Python 3.12, standard library only |
| Tests | pytest |
| Case store | Planned: SQLite through the standard library |

---

## Recent changes

| Date | Change | Details |
|---|---|---|
| 2026-11-24 | The three demonstration modules and their tests were added | `example/context/phases/phase-0.md` |

---

## Key decisions

The full log is in `example/context/decisions.md`.

| Decision | Date | Reason |
|---|---|---|
| Business rules are held as versioned data | 2026-11-24 | So a rule can change without a code change and each decision cites its version |
| The ledger is a hash chain | 2026-11-24 | So an edit, a removal or a reordering can be found |
| Outbound is suppressed unless the mode is exactly live and the recipient is listed | 2026-11-24 | A wrong or missing setting must never send |
| The registration rule is the first hard rule | 2026-11-24 | It is the smallest rule that shows the clamp |

---

## Known issues

| Issue | Severity | Status |
|---|---|---|
| The ledger cannot see an entry removed from its very end, or a full rewrite, unless the last hash is kept elsewhere | Medium | Recorded by tests. The build would store the last hash outside the file. |
| The demonstration evaluates only the registration rule | Low | Phase 1 adds the others. |

---

## Next steps

1. [ ] Decide how the build mocks the three registries and add a test that live modes are off by default (INV-16).
2. [ ] Add the case store with one folder per supplier and a test that one supplier cannot read another's (INV-14).
3. [ ] Run `/gate` for phase 0 and ask the owner to sign.

---

## Links

- Rules: `example/CLAUDE.md`
- Plan: `example/plan.md`
- Invariants: `example/invariants.md`
- Register: `example/register.csv`
- Phase log: `example/context/phases/phase-0.md`
