---
name: "<<FILL: command-name>>"
description: "<<FILL: what the command does, in one sentence>>"
disable-model-invocation: true
argument-hint: "<<FILL: [argument], or delete this line>>"
---

<!-- What it is: a command, written as a skill that only a person can start, which triggers one workflow. -->
<!-- When to create it: when you want a quick trigger for a workflow that people run on purpose. -->
<!-- Where it goes: .claude/skills/<command-name>/SKILL.md. The folder name is the command. The older location .claude/commands/<name>.md also works and takes the same frontmatter except name. Delete these three comment lines. -->

# <<FILL: command name>>

## Purpose

<<FILL: what this command does>>

**Usage:** `/<<FILL: command-name>> <<FILL: arguments>>`

The workflow this command starts is `.claude/workflow-docs/<<FILL: workflow>>.md`. Follow that file. Do not repeat its steps here.

---

## What it does

1. <<FILL: step>>
2. <<FILL: step>>
3. <<FILL: step>>

---

## Prerequisites

- <<FILL: what must be true before the command runs>>

---

## Detailed instructions

### Step 1: <<FILL: name>>

<<FILL: detailed instructions>>

```bash
<<FILL: commands to run>>
```

### Step 2: <<FILL: name>>

<<FILL: repeat the structure>>

---

## Expected output

<<FILL: what should exist or be reported when the command finishes>>

---

## Troubleshooting

| Problem | Solution |
|---|---|
| <<FILL: problem>> | <<FILL: solution>> |
