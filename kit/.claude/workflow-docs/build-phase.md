# Build phase

## Overview

How one phase of the plan is built, checked and signed. Every phase follows the same five stages, so a reviewer can read any phase log and know what to expect.

**Started by:** `/phase <n>`

## Prerequisites

- The plan section for the phase exists in <<FILL: path of the plan or specification>>.
- The previous phase's human gate is signed in `decisions.md`, or this is the first phase.
- `.claude/context/summary.md` has been read.

## Phase owners

| Phase | Owner agent | Skills it reads | Human gate |
|---|---|---|---|
| <<FILL: phase number and name>> | <<FILL: agent name>> | <<FILL: skills>> | <<FILL: yes or no, and who signs>> |

The auditor, red team and fixture keeper are not phase owners. They serve every phase.

---

## Stage 1: Orient

**Purpose:** start from the facts, not from memory.

**Agent:** the phase owner.

**Steps:**

1. Read `.claude/context/summary.md`.
2. Read the plan section for this phase.
3. Create `.claude/context/phases/phase-<n>.md` from `.claude/context/phases/TEMPLATE.md`. Copy the exit criteria in, unchecked. List the register rows in scope.
4. Read `.claude/context/open-questions.md`. Note any question that blocks a slice.

**Completion criteria:** the phase log exists with scope, unchecked exit criteria and register rows.

---

## Stage 2: Implement

**Purpose:** build in small slices, each proved by a test.

**Agent:** the phase owner.

**Steps:**

1. Take the next slice. Keep it small enough to prove with one test or a few.
2. If the slice reveals an edge case, run `/new-scenario` first. The row and the failing test come before the fix.
3. Write the test, run it, make the change, run it again.
4. Tick the slice in the phase log with the proof and a label.
5. If a decision is the owner's to make, add it to `open-questions.md` and continue with a slice that is not blocked.
6. If a rule would need to change, run `/rule-change` and wait. Never edit the rulebook directly.

**Completion criteria:** every slice is ticked with proof.

---

## Stage 3: Verify

**Purpose:** prove every exit criterion, and let an independent reviewer try to block the phase.

**Steps:**

1. Execute every exit criterion. Record the proof and label each one executed, read or not-verifiable.
2. Run `/regress`.
3. If the phase added or changed an untrusted input surface, run the red-team agent and record its result.
4. Run `/gate`. It runs the regression if needed, calls the `invariant-auditor` agent, and records the audit in the phase log.
5. If the audit blocks, fix the problem or get a recorded decision from the owner. The phase owner cannot clear a block. Then run `/gate` again.

**Completion criteria:** every exit criterion is ticked with proof and a label, and the audit has no BLOCK.

---

## Stage 4: Human gate

**Purpose:** a named person decides whether the phase may close.

**Steps:**

1. If the plan requires sign-off for this phase, stop. Tell the owner what is ready and where to look.
2. Wait for the owner's answer. Do not start the next phase.
3. Record the sign-off in the phase log's sign-off table and add an entry to `decisions.md` with the person's name, the date and any conditions.

**Completion criteria:** the sign-off is recorded, or the plan states that this phase needs none.

---

## Stage 5: Close

**Steps:**

1. Update the phase log: gate results, session notes, handoff notes.
2. Update `.claude/context/summary.md`. Keep it under its line cap and move detail to the phase log.
3. Append anything learnt to `patterns.md`.
4. Commit with the message `phase <n>: <what was completed>`.

**Completion criteria:** the working tree is clean and the summary describes the new state.

---

## Checklist

### Starting a session

- [ ] Read `summary.md`.
- [ ] Open the current phase log.

### After each slice

- [ ] The test ran and its id is recorded.
- [ ] The label is true.

### Before closing a phase

- [ ] Every exit criterion has proof and a label.
- [ ] `/regress` is green.
- [ ] The audit has no BLOCK.
- [ ] The gate is signed, if the plan requires it.
