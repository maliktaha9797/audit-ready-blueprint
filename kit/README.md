# The kit

An opinionated Claude Code setup for work that has to be audited. It is domain-neutral: the rules, agents, skills, workflows, hooks and context files are written, and the parts that depend on your project are marked with slots that you fill in. The method that produces it is in [BLUEPRINT.md](../BLUEPRINT.md). The kit's slots filled in for one fictional project are in [example/](../example/README.md).

The idea behind it: in a regulated setting, the hard part of AI-assisted building is being able to show that every decision traces to a rule and to a person. So the kit does not only ask for good behaviour in prose. It enforces what it can with permissions and hooks, checks the rest with a reviewer that can block, and records proof.

## What is in it

```
kit/
|-- CLAUDE.md                        Rules, with slots for the project
`-- .claude/
    |-- settings.json                Deny rules and hook registration
    |-- guard.json                   What the hooks protect and block
    |-- hooks/                       The guard scripts and the logger
    |-- agents/                      Auditor, red team, fixture keeper, phase-owner template
    |-- skills/                      Five knowledge skills and seven commands
    |-- workflow-docs/               The four shared processes
    `-- context/                     State that survives between sessions
```

## Copy it into a project

Run these from the root of this repository. Replace the path with your project.

```bash
cp -R kit/. /path/to/your-project/
```

If the project already has a `CLAUDE.md` or a `.claude/` folder, merge by hand instead of overwriting.

Then, in the project:

1. Add these lines to the project's `.gitignore`: `.claude/context/audit/` and `.claude/settings.local.json`.
2. Find every slot with `grep -rn "<<FILL" .` and fill it. The slots are listed below.
3. Copy `tests/test_hooks.py` from this repository into the project's `tests/` folder. Change the `KIT` line near the top so it points at the project root (`Path(__file__).resolve().parents[1]`). Run it. It copies only the project's `.claude/` folder and `CLAUDE.md` into a temporary folder and runs the hooks there. It reads nothing else in the project.
4. Save the register check from the `scenario-register` skill as `scripts/check_register.py`. Note that the hooks constrain the agent and not you. Copying the phase-owner template into `.claude/agents/`, and filling the slots in the protected files, are changes to the rulebook, so make them by hand at setup, or through `/rule-change`.
5. Check that `python3` is on the path. The hooks run as `python3` and need Python 3.9 or later. The settings use `onFailure: "block"`, which the Claude Code documentation says needs version 2.1.295 or later. See [docs/conventions.md](../docs/conventions.md).
6. Start a session and try to edit `CLAUDE.md`. The edit should be blocked and the reason shown. This live check is not-verifiable in this repository, so do it yourself once.

## Slots

Search for `<<FILL` in the project. A slot looks like `<<FILL: what goes here>>`.

| File | What to fill in |
|---|---|
| `CLAUDE.md` | Project name, overview, governing sentence, the path of the plan, tech stack and layout, quick-reference commands, the phase-owner rows in the agents table, and any project prohibitions with their invariant ids |
| `.claude/guard.json` | `blocked_hosts`: the production hostnames the agent must never touch. One entry per host. An unfilled entry is ignored |
| `.claude/skills/invariants/SKILL.md` | The check for INV-01, INV-06, INV-07, INV-08, INV-09, INV-10 and INV-11, which depend on your code, and the project invariants row |
| `.claude/skills/regress/SKILL.md` | The project's full test command |
| `.claude/workflow-docs/build-phase.md` | The path of the plan, and the table of phase owners |
| `.claude/workflow-docs/rule-change.md` | The project's rulebook check command |
| `.claude/context/summary.md` | The date, the tech stack, and the sample rows |
| `.claude/context/acceptance.md` | The pass bar, and the owner's signature before any graded run |
| `.claude/context/phases/TEMPLATE.md` | Nothing now. It is filled when a phase starts and the file is copied |
| `.claude/agents/_phase-owner.template.md` | Nothing now. Copy it once for each phase owner and fill the copy |

The marker also appears in prose in `.claude/skills/invariants/SKILL.md` and `.claude/agents/invariant-auditor.md`, where it explains that an unfilled check is a BLOCK. There is nothing to fill there.

## How the guards work

### Permissions

`.claude/settings.json` denies, with rules the harness enforces:

- reading `.env` files, `*.pem` and `*.key` files, and anything under `data/real/`;
- editing anything under `data/real/` and the approvals folder, and anything in the user's `~/.claude/`;
- force pushes, hard resets, recursive deletes of the repository root, and publishing commands.

A plain `git push` asks first.

### Hooks

| Script | Runs | Enforces |
|---|---|---|
| `guard_paths.py` | Before Edit, Write and NotebookEdit | No write under a real-data path (INV-01). No write to the approvals folder. No write to a protected file without an approved rule change (INV-03). |
| `guard_bash.py` | Before Bash and PowerShell | No command that mentions a blocked host or a real-data path (INV-01). No command that reads a secret file, prints a secret-looking variable, or dumps the environment in the common ways (INV-02). No shell write to a protected file or the approvals folder (INV-03). |
| `log_tool_use.py` | After every successful tool call | Appends one JSON line to `.claude/context/audit/tool-log.jsonl`: time, tool, agent type and target. Never file contents. A call that a guard blocks never reaches this hook, so each guard tries to write its own line, marked `blocked` with the reason, before it exits. Writing it is best effort, and a failure never changes the block. |
| `guard_lib.py` | Imported by the above | Shared configuration loading and the approval check. |

Both guards **fail closed**. Claude Code lets a call go ahead when a hook crashes or times out, because only exit code 2 blocks. So each guard catches every error itself and exits 2. A missing, malformed or incomplete `guard.json` blocks every edit and every command until it is restored.

### guard.json

| Key | Meaning |
|---|---|
| `protected_paths` | The rulebook. A file, or a folder written as `folder/**`. Matching ignores case. |
| `real_data_paths` | Paths that are never written to or mentioned in a shell command. |
| `approvals_dir` | The folder where a person creates approval files. The agent may not write there. |
| `rule_changes_file` | The file that holds rule-change proposals. |
| `blocked_hosts` | Hostnames that no shell command may mention. |
| `blocked_command_patterns` | Regular expressions for destructive or publishing commands. |
| `secret_command_patterns` | Regular expressions for commands that read secrets. |

### Approvals

A protected file can be edited only when both of these are true:

1. `.claude/context/rule-changes.md` has an entry with the status line `- Status: open`.
2. A person has created `.claude/context/approvals/<id>.approved` by hand, where the id matches the entry. The file has three lines:

```
Approved by: Your Name
Date: 2026-01-01
Files: CLAUDE.md
```

The approval covers only the files on its `Files:` line. Closing the entry ends it, and the owner then deletes the approval file. The agent has no tool that is permitted to create the file: a permission rule and the hook both refuse writes to that folder, and the shell guard refuses the write-like commands it recognises when they name it in full, or by its short name after a `cd`. Another writer, a glob, or a path built at run time can get past a text check. The permission rule, which Claude Code applies to the shell commands it can analyse, is the stronger protection, and the tool log and the git history are what would show a bypass. The process is in [the rule-change workflow](.claude/workflow-docs/rule-change.md).

## Limits

These are stated plainly because an audit reader will ask.

- **Not a security boundary.** Hooks and deny rules raise the cost of breaking a rule and leave evidence. A determined user with shell access can get around text matching, edit the settings by hand, or run Claude Code in a mode that skips permissions. The kit constrains the agent. It does not constrain the person.
- **Shell commands are matched as text.** The shell guard can block a harmless command that mentions a protected file next to a write-like word. It matches a fixed list of write-like commands (`WRITERS` in `guard_bash.py`) and does not know every program that can write a file, including every PowerShell cmdlet. It can miss a command that builds a path at run time, that names a file through a glob or a variable (for example `data/r*/x`), or that searches for a secret by a pattern and not by name (for example `grep -r SECRET .`). The secret patterns also block any command that mentions a variable whose name contains key, token, secret, password or auth, and any command that searches for `os.environ`, `process.env` or `getenv(`, even when it is only reading code. After a `cd`, it catches a file or folder named by its short name and does not catch every other way of reaching it. Use the Read tool to read protected files. The `Read` deny rules, which Claude Code applies to its own file tools, are the stronger protection for secrets and real-data paths.
- **A subagent with Bash can still change files.** The auditor has no Edit or Write tool, and Bash remains. Its definition tells it not to write, and its calls are logged with its agent type. Nothing in the tool settings stops it.
- **Hooks do not see `@` file mentions.** A file mentioned with `@` in a prompt is inserted without a tool call. The `Read` deny rules cover that path.
- **Older Claude Code versions.** Before the version that added `onFailure`, a hook that cannot start (for example when `python3` is missing) is a non-blocking error and the call goes ahead. The scripts themselves still fail closed once they are running.
- **Managed settings sit above project settings.** An organisation can deploy managed settings that a project file cannot override, so a project rule may be supplemented by policy that this kit does not control.
- **An approval outlives its entry.** Closing an entry ends the approval, but the approval file stays in the folder, and the rule-changes file is not protected because the agent must be able to write proposals. Setting a closed entry back to open would bring an old approval back into force. The owner deletes the approval file when the entry is closed, and git history shows any re-opening. A test records this limit.
- **Live behaviour is not verified here.** The hook tests feed the scripts the stdin shape the documentation describes. They do not prove a live session sends the same input. See [docs/verification.md](../docs/verification.md).

## Working on the kit itself

The `CLAUDE.md` files and the `.claude/` folder in `kit/`, `templates/` and `example/` are examples. Claude Code loads a subfolder's `CLAUDE.md` and skills on demand when it touches files there, so they can take effect for anyone running Claude Code inside this repository. Use the `claudeMdExcludes` setting to skip them.
