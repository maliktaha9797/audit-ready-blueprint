<!-- What it is: a step-by-step description of one repeatable, multi-phase process that several commands and agents share. -->
<!-- When to create it: when a process has several steps, repeats, and would otherwise be re-explained in more than one place. -->
<!-- Where it goes: .claude/workflow-docs/<name>.md. Claude Code does not read this folder; commands and agents read it because their instructions say to. -->

# <<FILL: workflow name>>

## Overview

<<FILL: what this workflow accomplishes>>

**Started by:** `/<<FILL: command name>>`

---

## Prerequisites

- <<FILL: what must be true before starting>>

---

## Context

Files this workflow reads and updates:

```
.claude/context/
|-- summary.md
`-- <<FILL: other context files>>
```

Rules:

1. Read `summary.md` first.
2. Update the context files after each phase.
3. <<FILL: further rules>>

---

## Phase 1: <<FILL: phase name>>

### Purpose

<<FILL: what this phase accomplishes>>

### Agent

`<<FILL: agent name>>`, or "none".

### Skills to read

- `<<FILL: skill name>>`

### Steps

1. <<FILL: step>>
2. <<FILL: step>>

### Completion criteria

Each criterion is checked by running something. Record the proof and a label (executed, read or not-verifiable).

- [ ] <<FILL: criterion>>. Proof: <<FILL: test id or command>>. Label: <<FILL: label>>.

### Update context

```
Update: <<FILL: which context file>>
Add: <<FILL: what to add>>
```

---

## Phase 2: <<FILL: phase name>>

<<FILL: repeat the structure above for each phase. The last phase is usually verification or review.>>

---

## Agent, skill and rule reference

| Phase | Agent | Skills | Section of CLAUDE.md |
|---|---|---|---|
| <<FILL: phase>> | <<FILL: agent>> | <<FILL: skills>> | <<FILL: section>> |

---

## Changing this workflow

Changing a step is a rule change if it makes a check easier to pass or removes a gate. Use the rule-change workflow. Fixing a typo or recording a lesson is knowledge, and the agent may do it and log it.

---

## Checklist

### Starting a session

- [ ] Read `summary.md`.
- [ ] <<FILL: check>>

### After each phase

- [ ] Every completion criterion has proof and a label.
- [ ] Context files are updated.
- [ ] <<FILL: check>>

### Before completing

- [ ] A person has signed the final gate.
- [ ] <<FILL: check>>
