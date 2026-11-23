# Verification

This file is the repository's own honesty table. It lists what the repository claims about itself, and for each claim the label and the proof.

## Labels

| Label | Meaning |
|---|---|
| **executed** | A command or test was run, and its result is recorded here. |
| **read** | The thing was inspected but not run. |
| **not-verifiable** | It cannot be checked in the build environment. The reason is stated. |

Proof is a test id or a command. An adjective is not proof.

## Claims

| Claim | Label | Proof |
|---|---|---|
| The file formats used by the kit match what the Claude Code documentation said on 2026-11-23. | read | The pages listed in [conventions.md](conventions.md) were read. They were not exercised in a live session. |

This table is extended as each phase adds claims. Claims about links, banned terms and proof ids are added when the check script that tests them exists.
