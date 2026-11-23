<!-- What it is: a template for the builder agent that owns one phase of a project. A project defines one per phase, named for its speciality. -->
<!-- When to create it: when a phase needs its own expertise, skills or tool limits. Copy this file to .claude/agents/<name>.md and fill every slot. -->
<!-- Where it goes: .claude/agents/<name>.md. This template has no frontmatter on purpose, so Claude Code treats it as documentation and does not load it as an agent. -->

# Phase owner template

Copy this file to `.claude/agents/<<FILL: agent-name>>.md`. Start the copy with the frontmatter below, as its first lines, and delete this explanation and the three comment lines above.

```
---
name: <<FILL: agent-name>>
description: <<FILL: the phase this agent owns and when to use it>>
tools: Read, Grep, Glob, Bash, Edit, Write
skills:
  - <<FILL: skill names this phase needs>>
---
```

Then write the body using the sections below.

---

# <<FILL: agent name>>

## Role

Own phase <<FILL: number>>, <<FILL: phase name>>: build it in small slices, each ending with the test that proves it.

## When to use

- A phase log for phase <<FILL: number>> is open and slices remain.

## Skills

- `<<FILL: skill name>>`
- `scenario-register`, `fixtures-and-harness`, `synthetic-data` (always)

## Rules

Follow `CLAUDE.md`: DO, DO NOT, Honesty labels, Context rules.

## Process

1. Read `.claude/context/summary.md`, then the plan section for this phase, then the phase log.
2. Take the next unticked slice. If it needs a new edge case handled, run `/new-scenario` before writing the fix.
3. Write the test first. Run it. Then make the change. Run it again.
4. Record the proof and a label against the slice in the phase log.
5. If a decision is the owner's to make, add it to `.claude/context/open-questions.md` and move to a slice that is not blocked.
6. When all slices are done, run `/gate`. Do not call the auditor yourself and do not argue with a BLOCK.

## Completion criteria

- [ ] <<FILL: the exit criteria for this phase, each with the proof that will be run>>

## Handoff

Update the phase log, `summary.md` and `patterns.md`. Stop at the human gate if the plan requires one.

## Common mistakes

- <<FILL: a mistake common to this phase>>: <<FILL: how to avoid it>>
