<!-- What it is: a form that turns the discovery questions into answers you can hand to Claude with the generation prompt. -->
<!-- When to create it: each time you set up a new workflow or project. Copy this file and fill in the copy. -->
<!-- Where it goes: anywhere you like. The answered copy for the example project is example/questionnaire-answers.md. -->

# Workflow setup questionnaire

## Basic info

**Workflow name:**

**Primary purpose:**

**Trigger command:** /

## Task definition

**What is the main task?**

**What are the phases? (list in order)**

1.
2.
3.
4.

**Can phases run in parallel, or must they be sequential?**

**What does "done" look like?**

## Agents

**Do you need specialised agents?** Yes / No

**If yes, list them:**

| Agent name | Purpose | Runs when | Tools it needs |
|---|---|---|---|
| | | | |

**Should agents work in parallel (worktrees) or on the same branch?**

**Is there a final reviewer that can block?** Yes / No

## Skills

**What technical knowledge is needed?**

1.
2.
3.

**Are these reusable across projects?** Yes / No

**What common mistakes must the skills warn about?**

## Context

**What state needs to persist?**

- [ ] Decisions
- [ ] Progress
- [ ] Patterns discovered
- [ ] Issues encountered
- [ ] Other:

**How should context be organised?**

- [ ] By feature
- [ ] By date
- [ ] By phase
- [ ] Other:

## Rules

**What conventions must be followed?**

1.
2.
3.

**What must NEVER be done?**

1.
2.
3.

## Self-improvement

**Should the setup be able to change itself when it learns something?** Yes / No

**Which changes are knowledge, which the agent may make freely?** (patterns, gotchas, context)

**Which changes are rules, which need a person's approval first?** (prohibitions, invariants, settings, hooks)

**What triggers an update?**

- [ ] New conventions discovered
- [ ] User corrections
- [ ] Mistakes found
- [ ] Other:

## Assurance

Answer these when someone other than the builder will have to check the work later.

**Who has to be able to check this work later, and what will they ask to see?**

**Which rules must never be broken, and can each one be checked by running something?**

| Rule | The check that proves it | Enforced by (hook, permission, test or auditor review) |
|---|---|---|
| | | |

**Which rules can be enforced by the harness (permissions, hooks) instead of being requested in prose?**

**Is there a reviewer that can block, and is it independent of whatever built the work?**

**What counts as proof that a step is done?**

**Where does a person have to approve before work continues?**
