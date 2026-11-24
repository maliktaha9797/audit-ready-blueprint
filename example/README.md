# The example: Northgate Supplier Desk

This folder is the specification side only. It shows the kit's slots filled in for one fictional project, and the questionnaire that leads there. The full build is meant to live in a separate repository. Nothing in this repository can show that it exists or how far it has got, so nothing here claims that it does. The only running code that belongs to this example is the small demonstration in [demo/](../demo/README.md), and every statement in this folder about what is verified is limited to what that demonstration tests.

## The fictional project

Northgate Supplier Desk is an invented internal tool for an invented company. Before a new supplier can be paid, someone must check its company registration, its tax registration, its bank details and its insurance certificate. In the imagined tool, agents assemble and check each supplier file, and a named person approves it.

The governing sentence of the project is:

> Software performs every check that can be written as a rule; the model only reads documents and drafts judgments that are always flagged; no supplier is activated until a named person approves the file.

Every company, person and record in this folder is invented. The registry, the tax registry and the bank verification service are mocks with outcomes chosen by fixtures. No real service is called anywhere.

## What is here

| File | What it is |
|---|---|
| [questionnaire-answers.md](questionnaire-answers.md) | The method's questionnaire, answered for this project, including the assurance group. It is the proof that the method produces the rest. |
| [CLAUDE.md](CLAUDE.md) | The kit's `CLAUDE.md` with every slot filled. |
| [plan.md](plan.md) | A short phased plan, with exit criteria and a human gate for each phase. |
| [invariants.md](invariants.md) | The kit's invariants plus those that belong to this domain, each with a check. |
| [register.csv](register.csv) | The scenario register. |
| [acceptance.md](acceptance.md) | An unsigned draft of the pass bar, to show the format. |
| [context/](context/summary.md) | An illustrative trail for phase 0: summary, decision log and phase log. |

## Where these files would live in a project

The files sit in this folder so they are easy to browse and so that Claude Code does not load them as configuration. In a real project they would be here:

| In this folder | In a project |
|---|---|
| `CLAUDE.md` | `CLAUDE.md` at the project root |
| `invariants.md` | `.claude/skills/invariants/SKILL.md` |
| `register.csv` | `.claude/context/register.csv` |
| `acceptance.md` | `.claude/context/acceptance.md` |
| `context/summary.md`, `context/decisions.md` | `.claude/context/summary.md`, `.claude/context/decisions.md` |
| `context/phases/phase-0.md` | `.claude/context/phases/phase-0.md` |

The commands in `CLAUDE.md` and the paths in the checks refer to the build, which would be a separate repository. Where a check can be run against this repository, because the demonstration or the kit's hook tests cover it, the file names the test id. Everything else is marked planned.

## How to read the labels

Each statement about verification in this folder carries one of three labels, defined in [docs/verification.md](../docs/verification.md): **executed** (a test or command was run and its result recorded), **read** (inspected but not run) or **not-verifiable** (cannot be checked here, with the reason). A check is marked **Demo** when a test in this repository covers it, and **Planned** when it belongs to the separate build.

## The trail is illustrative

The files under `context/` show what a summary, a decision log and a phase log look like partway through phase 0. They describe only what the demonstration implements. No person signed anything, no audit was run for a project that does not exist, and each file says so in its first line.
