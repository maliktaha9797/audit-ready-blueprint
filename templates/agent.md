---
name: "<<FILL: agent-name>>"
description: "<<FILL: when Claude should delegate to this agent, in one or two sentences>>"
tools: "<<FILL: Read, Grep, Glob, Bash>>"
skills:
  - "<<FILL: skill-name>>"
---

<!-- What it is: a subagent definition. The text below the frontmatter is the agent's system prompt. -->
<!-- When to create it: when a phase needs different expertise, tools or independence from the work being done. -->
<!-- Where it goes: .claude/agents/<name>.md. The first line of the real file must be the opening --- of the frontmatter. Delete these three comment lines. -->

# <<FILL: agent name>>

## Role

<<FILL: one sentence describing this agent's job>>

## When to use

Use this agent when:

- <<FILL: situation>>
- <<FILL: situation>>

## Skills

The `skills` field in the frontmatter loads these into the agent's context at startup. Name them here too, so a reader of this file can see them:

- `<<FILL: skill-1>>`

## Rules

Follow these sections of CLAUDE.md:

- <<FILL: section>>

## Isolation

- [ ] Uses a worktree (parallel work)
- [ ] Uses the main branch (sequential work)

## Tools

State which tools the agent has, and why any are missing. An agent that audits other work should have no edit or write tool. Note that an agent with the shell tool can still change files through it.

## Process

### Step 1: <<FILL: name>>

<<FILL: what to do>>

### Step 2: <<FILL: name>>

<<FILL: what to do>>

## Completion criteria

- [ ] <<FILL: criterion, each checkable by running something>>

## Handoff

When complete:

1. <<FILL: what to record and where>>
2. <<FILL: what to hand to the next agent or to the person>>

## Common mistakes

- <<FILL: mistake>>: <<FILL: how to avoid it>>
