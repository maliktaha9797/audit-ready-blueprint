# Claude Code Setup Blueprint

## Purpose

This blueprint is a method for deciding what Claude Code setup a task needs, and for building it. Use it when you set up a new project, or a repeatable process such as debugging, refactoring, review or migration. When the work has to be auditable, add the assurance layer described in this file.

The method does not depend on a domain. The worked result of running it is in [kit/](kit/README.md) and [example/](example/README.md), described in [The worked result](#the-worked-result).

File paths and formats in this file follow [docs/conventions.md](docs/conventions.md), which records what the Claude Code documentation said on 2026-11-23.

---

## The components

| Component | What it is | Where it lives | When you need it |
|---|---|---|---|
| **CLAUDE.md** | Project rules and conventions. It is guidance that Claude Code does not enforce. | `CLAUDE.md` at the project root | Always. Every project needs this. |
| **Workflow** | A step-by-step description of a repeatable, multi-phase process. | `.claude/workflow-docs/<name>.md` (a convention of this repository, not a Claude Code feature) | When you have a repeatable multi-step process. |
| **Agents** | Specialised personas, each with its own tools and instructions. In Claude Code they are subagents. | `.claude/agents/<name>.md` | When different parts of the workflow need different expertise. |
| **Skills** | Technical how-to guides that load when they are relevant. | `.claude/skills/<name>/SKILL.md` | When agents need specific technical knowledge. |
| **Context** | Project state and history. | `.claude/context/` (a convention of this repository) | Always. It keeps continuity across sessions. |
| **Commands** | Shortcuts that trigger a workflow. Written as skills that only a person can start. | `.claude/skills/<command-name>/SKILL.md` with `disable-model-invocation: true` | When you want quick access to common tasks. |

Two settings files sit beside these and matter when a rule has to be enforced and not only requested: `.claude/settings.json` (permissions and hooks) and any scripts the hooks call. They are covered under [the assurance layer](#the-assurance-layer).

### How they connect

```
A person triggers a Command
    |
    v
The Command starts a Workflow
    |
    v
The Workflow reads Context (current state)
    |
    v
The Workflow assigns an Agent to a phase
    |
    v
The Agent reads Skills for technical guidance
    |
    v
The Agent follows the rules in CLAUDE.md
    |
    v
The work is checked by a reviewer that can block
    |
    v
A person signs the gate
    |
    v
The Agent updates Context with progress
    |
    v
Loop until complete
```

The same flow as a diagram, with the checks and the human gate marked, is in [docs/how-the-pieces-connect.md](docs/how-the-pieces-connect.md).

---

## Step 1: Discovery questions

Before creating anything, answer these questions. The answers determine what you need to build. The same questions, as a form to fill in, are in [templates/questionnaire.md](templates/questionnaire.md).

### About the task

```
1. What is the primary task or workflow?
   Example: "Building new features", "Debugging issues", "Refactoring code"

2. Is this task repeatable with a consistent process?
   - Yes: create a workflow
   - No: you may only need rules and context

3. What are the major phases of this task?
   List them in order. Example:
   - Phase 1: Understand the problem
   - Phase 2: Plan the solution
   - Phase 3: Implement
   - Phase 4: Verify

4. Can phases run in parallel or must they be sequential?
   This affects agent design.

5. What does "done" look like?
   Define completion criteria for the workflow.
```

### About specialisation

```
6. Does each phase need different expertise?
   - Yes: create separate agents
   - No: a single agent, or no agents

7. List the distinct roles needed.
   Example: "Database expert", "Frontend builder", "Tester", "Reviewer"

8. Should agents work in isolation (worktrees) or on the same branch?
   - Parallel work: worktrees
   - Sequential work: same branch

9. Is there a final quality gate?
   - Yes: create a reviewer agent that can block
```

### About technical knowledge

```
10. What technical knowledge is needed?
    List specific technologies, patterns or techniques.
    Example: "database migrations", "React hooks", "file uploads"

11. Is this knowledge project-specific or reusable?
    - Project-specific: put it in CLAUDE.md
    - Reusable: create skills

12. Are there common patterns that must be followed?
    Document these as skills.

13. Are there common mistakes to avoid?
    Document these in skills or in CLAUDE.md.
```

### About context

```
14. Does this workflow need to keep state across sessions?
    - Yes: design a context structure
    - No: minimal context is enough

15. What information needs to persist?
    - Decisions made
    - Progress on tasks
    - Patterns discovered
    - Issues encountered

16. Should context be organised by feature, by date, or another way?
    Design the folder structure to match.
```

### About self-improvement

```
17. Should the setup be able to change itself when it learns something?
    - Knowledge (patterns, gotchas, context): yes, the agent can update it freely
    - Rules (prohibitions, invariants, settings, hooks): only with a person's approval
    See "Changing the setup later" below.

18. What kinds of updates are expected?
    - New conventions
    - Corrections to guidance
    - New requirements
    - Pattern discoveries
    For each, say whether it is knowledge or a rule.
```

### About assurance

Answer these when someone other than the builder will have to check the work later. They decide whether you add the assurance layer.

```
19. Who has to be able to check this work later, and what will they ask to see?

20. Which rules must never be broken, and can each one be checked by running something?

21. Which rules can be enforced by the harness (permissions, hooks) instead of being
    requested in prose?

22. Is there a reviewer that can block, and is it independent of whatever built the work?

23. What counts as proof that a step is done?

24. Where does a person have to approve before work continues?
```

---

## Step 2: Design the structure

Based on your answers, design what you need.

### Decision tree

```
Is this a repeatable process?
|-- No: create CLAUDE.md and Context only
`-- Yes: create a Workflow
    |
    |-- Does it have distinct phases?
    |   |-- No: a simple workflow, no agents
    |   `-- Yes: create the workflow with phases
    |       |
    |       `-- Do the phases need different expertise?
    |           |-- No: no agents needed
    |           `-- Yes: create an agent for each role
    |
    `-- Does it need technical guidance?
        |-- No: rules in CLAUDE.md are enough
        `-- Yes: create skills
            |
            `-- Is the knowledge reusable across projects?
                |-- No: put it in CLAUDE.md
                `-- Yes: create skill files

Must the work be auditable? (checked at any point above)
`-- Yes: add the assurance layer
    |-- an invariants skill: one table, each row with a check you can run
    |-- a blocking auditor: read-only, and independent of the builder
    |-- a scenario register: every edge case has a row and a test before its fix
    |-- phase logs: every exit criterion carries proof and a label
    `-- enforced guardrails: permissions and hooks, not only prose
```

### File structure

This is the structure after the formats in [docs/conventions.md](docs/conventions.md) are applied.

```
.claude/
|-- settings.json              # Permissions and hooks (enforcement)
|-- agents/
|   `-- <agent-name>.md        # One file per agent, with name and description in frontmatter
|-- skills/
|   |-- <skill-name>/
|   |   `-- SKILL.md           # One folder per skill
|   `-- <command-name>/
|       `-- SKILL.md           # A command: a skill with disable-model-invocation: true
|-- workflow-docs/
|   `-- <workflow-name>.md     # One file per workflow (convention of this repository)
`-- context/                   # State that survives between sessions (convention of this repository)
    |-- summary.md             # Always: concise current state
    |-- decisions.md           # Always: decision log
    |-- codebase.md            # If you are analysing existing code
    `-- <domain>/
        `-- <item>.md          # Domain-specific context

CLAUDE.md                      # Root: project rules
```

Three file shapes that are easy to assume do not work in Claude Code. An ignore file (`.claudeignore`) has no effect, so use `Read` deny rules in `.claude/settings.json`. A flat `skills/<name>.md` file is not a skill, so each skill is a folder with a `SKILL.md`. A separate `commands.md` quick-reference file is not read by Claude Code, so the command list goes in `CLAUDE.md`.

---

## Step 3: Create the components

One template per component, each updated to the verified formats. Each file starts with a short comment saying what it is, when to create it and where it goes.

| Component | Template |
|---|---|
| CLAUDE.md | [templates/CLAUDE.md](templates/CLAUDE.md) |
| Workflow | [templates/workflow.md](templates/workflow.md) |
| Agent | [templates/agent.md](templates/agent.md) |
| Skill | [templates/skill/SKILL.md](templates/skill/SKILL.md) |
| Command | [templates/command.md](templates/command.md) |
| Context summary | [templates/context-summary.md](templates/context-summary.md) |
| Decision log | [templates/decisions.md](templates/decisions.md) |
| Phase log | [templates/phase-log.md](templates/phase-log.md) |

---

## Step 4: The questioning script

Use [templates/questionnaire.md](templates/questionnaire.md) when you set up a new workflow. Copy it and answer each question. It covers the discovery questions above, including the assurance group.

---

## Step 5: The generation prompt

Once you have answered the questions, give the answers to Claude with [templates/generation-prompt.md](templates/generation-prompt.md). It asks for each file, an explanation of how the files connect, and a folder structure and setup checklist at the end.

---

## Changing the setup later

A setup that can edit its own rules cannot be audited, because the person checking cannot tell whether a rule was kept or quietly rewritten. So the method separates two kinds of change.

| Kind | Examples | Who changes it | How |
|---|---|---|---|
| **Knowledge** | Patterns, gotchas, context, the summary, near-misses | The agent, freely | The agent updates the file and appends a line to the log. |
| **Rules** | Prohibitions in CLAUDE.md, invariants, permission settings, hooks, the list of protected files | A person approves, then the agent applies | The agent writes a proposal and stops. A person reviews it and records the approval. Only then does the agent make exactly the approved change. |

The rule-change process is written out in [kit/.claude/workflow-docs/rule-change.md](kit/.claude/workflow-docs/rule-change.md). In the kit, a hook enforces it: the protected files cannot be edited without an approval that the agent has no permission to create.

Two cases decide which kind a change is. If a change makes a check easier to pass, it is a rule change. If a change records something that was learnt and does not alter what is allowed, it is knowledge.

---

## The assurance layer

Add this layer when the answers to the assurance questions say the work must be auditable. It has five parts.

1. **Invariants.** One table of statements that must always hold. Each row names the check that proves it and what enforces it: a hook, a permission, a test, or the auditor's review.
2. **A reviewer that can block.** An auditor agent that has no edit or write tool, so it cannot fix what it audits or alter the evidence. It reports a verdict on each invariant. A block is cleared by a fix or by a recorded decision from the owner, never by the builder.
3. **A scenario register.** Every edge case is registered, with the behaviour required and who decides (code, a model, or a person), and gets a test before the fix that addresses it.
4. **Phase logs with labelled proof.** Every exit criterion is marked **executed**, **read** or **not-verifiable**, and proof is a test id or a command, not an adjective.
5. **Enforced guardrails.** Permissions deny what must never happen. Hooks block what needs a condition and record what was done. These raise the cost of breaking a rule and leave evidence. They are not a security boundary against a determined user with shell access.

---

## The worked result

Running this method for a regulated, audited setting produces the setup in [kit/](kit/README.md): a domain-neutral kit with marked slots to fill. The questionnaire answered for one fictional project, and the kit's slots filled in for it, are in [example/](example/README.md). The hooks that enforce the guardrails are in `kit/.claude/hooks/`, and a small Python demonstration with tests is in [demo/](demo/README.md).

---

## Quick reference card

### Minimum setup (any project)

- `CLAUDE.md`
- `.claude/context/summary.md`

### Standard setup (a repeatable process)

- `CLAUDE.md`
- `.claude/workflow-docs/<name>.md`
- `.claude/context/summary.md`
- `.claude/context/decisions.md`

### Full setup (a complex, multi-phase process)

- `CLAUDE.md`
- `.claude/workflow-docs/<name>.md`
- `.claude/agents/<several>.md`
- `.claude/skills/<several>/SKILL.md`
- `.claude/skills/<command>/SKILL.md` for each command
- `.claude/context/` with its full structure

### Assurance setup (auditable work)

Everything in the full setup, plus:

- `.claude/settings.json` with deny rules and hooks
- An invariants skill and a read-only auditor agent
- A scenario register and a phase log for each phase
- An approvals folder that the agent cannot write to

### When to create each

| Create | When |
|---|---|
| Agent | A phase needs specialised expertise. |
| Skill | Technical knowledge needs documenting. |
| Workflow | A process has multiple steps that repeat. |
| Command | You want a quick trigger for a workflow. |
| Context | State needs to persist across sessions. |
| Invariants and an auditor | Someone else will have to check the work. |

---

## Checklist: setting up a new workflow

- [ ] Answer the discovery questions (Step 1).
- [ ] Design the structure from the answers (Step 2).
- [ ] Create `CLAUDE.md` with the project rules.
- [ ] Create the workflow file with all phases.
- [ ] Create the agent files, if needed.
- [ ] Create the skill files, if needed.
- [ ] Create the command files, if needed.
- [ ] Create the context files.
- [ ] Decide which changes are knowledge and which are rules, and write the rule-change process.
- [ ] If the work is auditable: add the invariants, the auditor, the register, the phase logs and the guardrails.
- [ ] Test the workflow end to end, and label each check executed, read or not-verifiable.
- [ ] Refine based on what you learn.
