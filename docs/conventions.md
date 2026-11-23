# Claude Code conventions used in this repository

This file records what the current Claude Code documentation says about each file format and setting that the kit relies on. It was written by reading the live documentation pages on 2026-11-23, before any file under `kit/.claude/` was created. Where the documentation differs from what was first assumed, the documentation wins and the difference is recorded here.

Verification labels used in this repository are defined in [verification.md](verification.md). Every row below is labelled **read**: the pages were read, and the formats were not exercised inside a live Claude Code session during the build. See [What has not been checked](#what-has-not-been-checked).

The pages are under `https://code.claude.com/docs/en/`. The installed command line tool on the build machine reported version 2.1.252. Some documented features name a later minimum version, and those are called out where they matter.

The last column of the first table says whether the documentation agreed with the assumption this repository started from. "Yes" means it agreed. Where it did not, the cell says what changed and what the repository does instead.

## Verified items

| Item | What the documentation says | Page title | Checked | Agreed with the starting assumption |
|---|---|---|---|---|
| Skill location and format | A project skill is `.claude/skills/<name>/SKILL.md`. YAML frontmatter sits between `---` lines at the top of the file. Every field is optional, but `description` is recommended because Claude uses it to decide when to apply the skill. `name` defaults to the folder name. Unknown fields are ignored without an error. | Extend Claude with skills | 2026-11-23 | Yes. The kit sets `name` and `description` on every skill anyway. |
| Subagent location and format | A project subagent is `.claude/agents/<name>.md`. `name` and `description` are required. `tools` is an allowlist and `disallowedTools` is a denylist (the field names are camelCase). `skills` preloads skill content. A file with no `name`, or no `description`, is skipped. | Create custom subagents | 2026-11-23 | Yes. |
| Slash commands | Files in `.claude/commands/` still work. Custom commands have been merged into skills, and the documentation says to prefer a skill for new work because a skill folder can hold supporting files. A skill folder's name becomes the command. | Extend Claude with skills; Explore the .claude directory | 2026-11-23 | Yes, with a change in recommendation. See [Decision: commands as skills](#decision-commands-as-skills). |
| Making a skill or command user-invoked only | Set `disable-model-invocation: true` in the frontmatter. Claude then cannot load the skill on its own, and the description is kept out of context. The opposite field is `user-invocable: false`, which hides a skill from the menu and leaves it to Claude. | Extend Claude with skills | 2026-11-23 | Yes. |
| Permissions in `settings.json` | Rules sit under `permissions.allow`, `permissions.ask` and `permissions.deny`. Order of evaluation is deny, then ask, then allow, and the first match wins. A rule is `Tool` or `Tool(specifier)`. `Read` and `Edit` rules use gitignore-style patterns: `//path` is absolute, `~/path` is from the home directory, `/path` is relative to the project root for a project settings file, and `./path` is relative to the current directory. A `Read` deny rule also blocks Edit and Write on the same path. A `Write(path)` rule does not match anything, so edit denials must be written as `Edit(path)`. Bash rules match command text with `*` as a wildcard, for example `Bash(git push *)`. | Configure permissions; Settings files and precedence | 2026-11-23 | Partly. `Write(path)` as a rule does not work, so the kit uses `Edit(path)`. |
| Hooks: where and how | Hooks are set in `settings.json` under `hooks`, with three levels: event, matcher group, handler. A handler of `type: "command"` receives JSON on stdin. `PreToolUse` runs before a tool call and can block it. `PostToolUse` runs after a successful call. Hooks in settings also run inside subagents. | Hooks reference | 2026-11-23 | Yes. |
| Hooks: stdin shape | Common fields include `session_id`, `cwd`, `hook_event_name`, `tool_name`, `tool_input` and `tool_use_id`. For the file tools (Write, Edit, Read), `tool_input.file_path` is always absolute. Bash carries `tool_input.command`. `PostToolUse` adds `tool_response`. The notebook editing tool is not described in the hook input tables, so its path field is not documented there. | Hooks reference | 2026-11-23 | Yes, with one gap (the notebook tool). |
| Hooks: how a block works | Exit code 2 blocks the tool call and the text on stderr is the reason. Any other non-zero exit code, a crash, a script that fails to start, and a timeout are all non-blocking: the tool call goes ahead. A hook that prints valid JSON with a deny decision on exit 0 also blocks. | Hooks reference | 2026-11-23 | No. Failing closed is not the default. Each guard script must catch every error and exit 2 itself. |
| Hooks: failing closed at the harness | A command hook can set `"onFailure": "block"`, which blocks the action when the hook fails or times out. The documentation says this needs Claude Code 2.1.295 or later. | Hooks reference | 2026-11-23 | Not in the starting assumptions. Added to the kit as a second layer. The build machine reported an older version (2.1.252), so whether an older version ignores the field is not-verifiable here. |
| Ignoring files | A `.claudeignore` file has no effect. Use `Read` deny rules to keep files out of Claude's reach. For operating-system level enforcement of shell commands, use the sandbox. | Configure permissions | 2026-11-23 | Yes. Ignore files are not supported, and deny rules are the supported route. |
| Project memory file | `./CLAUDE.md` or `./.claude/CLAUDE.md` is loaded every session. `@path` imports are supported (relative to the importing file, up to four hops). The documentation targets under 200 lines per file. It states that this file is guidance Claude Code does not enforce, and that enforced behaviour belongs in hooks and permissions. | How Claude remembers your project; Explore the .claude directory | 2026-11-23 | Yes. |

## Findings beyond the initial list of items

| Finding | What the documentation says | Consequence for this repository |
|---|---|---|
| `.claude/workflows/` is a native location | Files in `.claude/workflows/` are `.js` dynamic workflow scripts that a runtime executes to coordinate many subagents. Each saved script runs as a `/<name>` command. (Page: Orchestrate subagents at scale with dynamic workflows; Explore the .claude directory.) | This repository's Markdown workflow descriptions must not live there. They live in `.claude/workflow-docs/`. See [Decision: workflow folder name](#decision-workflow-folder-name). |
| `/status` is a built-in command | It opens the settings interface on the status tab. (Page: Commands.) | The kit's command that reports project state is named `/project-status`. |
| Bash deny rules are not a boundary | A deny rule for a program stops the usual spelling of the command and does not stop `/usr/bin/<program>`, `sh -c '<command>'` or an option placed before the subcommand. The documentation recommends the sandbox when a restriction must hold. (Page: Configure permissions.) | The kit says plainly that hooks and deny rules raise the cost of breaking a rule and leave evidence. They are not a security boundary. |
| A hook does not override a deny rule | A matching deny rule blocks a call whatever a hook returns. A hook that exits 2 blocks a call even when an allow rule matches. (Page: Configure permissions.) | The kit uses deny rules for what must never happen (secrets, approvals folder) and hooks for what needs a condition (the rulebook, which may change once approved). |
| Hooks do not fire for `@` file mentions | Files mentioned with `@` in a prompt are inserted without a tool call, so no `PreToolUse` hook runs. A `Read` deny rule does cover them. (Page: Hooks reference.) | Secret and real-data paths are protected by `Read` deny rules and not by hooks alone. |
| A skill can start a subagent | `context: fork` with an `agent` field runs the skill body in a new subagent that does not see the conversation. Alternatively the main session can delegate to a named subagent. (Page: Extend Claude with skills.) | `/gate` is not forked. It tells the main session to delegate to `invariant-auditor` with an explicit brief, so that the audit returns to the session that writes the phase log. |
| Nested `CLAUDE.md` files and skills load on demand | A `CLAUDE.md` in a subfolder is loaded once Claude reads, writes or edits another file in that folder. A `.claude/skills/` folder inside a subfolder is picked up in the same way. A setting called `claudeMdExcludes` skips named files. (Page: How Claude remembers your project; Extend Claude with skills.) | The files under `templates/`, `kit/` and `example/` are examples and apply only after they are copied to a project root. Anyone running Claude Code inside this repository can load them by touching files there, and can prevent it with `claudeMdExcludes`. |
| Frontmatter must be the first line | Claude Code reads frontmatter only when the opening `---` is the first line of the file. Otherwise the whole file is treated as content. (Page: Extend Claude with skills; Create custom subagents.) | In templates that carry frontmatter, the three-line comment follows the closing `---`. In the copied file, the comment is deleted. |
| A subagent that has Bash can still change files | Removing Edit and Write from a subagent's tools does not stop it changing files through Bash. (Page: Create custom subagents.) | `invariant-auditor` has no edit or write tool, and the kit records that Bash remains a gap, which the tool log and the audit trail make visible. It does not close the gap. |

## Decisions

### Decision: commands as skills

The seven user-triggered commands are written as skills, each with `disable-model-invocation: true`, in `.claude/skills/<command-name>/SKILL.md`. The reason is that the documentation presents skills as the current form and recommends them over files in `.claude/commands/`. Files in `.claude/commands/` still work, so a project that prefers the older location can move each `SKILL.md` body into a command file without changing behaviour.

Naming follows the folder name. The command for each folder is: `/phase`, `/gate`, `/regress`, `/new-scenario`, `/policy-change`, `/rule-change` and `/project-status`. The last is not `/status` because of the built-in command noted above.

### Decision: workflow folder name

The method uses the word **workflow** for a multi-phase process that several commands and agents share. In this kit each workflow is a Markdown file in `.claude/workflow-docs/`. The folder is not named `.claude/workflows/` because that name is a native Claude Code location for `.js` scripts, and putting Markdown there risks confusing readers and the tool.

### What is a convention of this repository and not a Claude Code feature

| Path | Why it exists |
|---|---|
| `.claude/workflow-docs/` | Holds the multi-phase process descriptions that several commands and agents share, so each command file can point to one description and not repeat it. Claude Code does not read this folder. Agents and commands read it because their instructions tell them to. |
| `.claude/context/` | Holds project state that must survive between sessions: the summary, the decision log, the scenario register, rule-change proposals and phase logs. Claude Code does not read this folder either. The session-start instruction in `CLAUDE.md` is what makes the summary the first thing read. |
| `.claude/guard.json` | Project-editable configuration read by the kit's own hook scripts: which paths are protected, which hosts and commands are blocked. It is not a Claude Code setting. |
| `.claude/context/approvals/` | Holds files that a person creates by hand to approve a rule change. The agent is denied write access to it by a permission rule. |

## What has not been checked

- **not-verifiable:** The behaviour of any file in this repository inside a live Claude Code session. The documentation was read. The kit's hook scripts are exercised by tests that feed them the documented stdin shape, and that does not prove that a live session sends the same shape.
- **not-verifiable:** Whether Claude Code 2.1.252 accepts or ignores the `onFailure` field. The documentation names 2.1.295 as the minimum.
- **not-verifiable:** The field that the notebook editing tool uses for its path. The kit's file guard reads `file_path` and, defensively, `notebook_path`, and it blocks a notebook edit whose path it cannot find.
- **read, not run:** The documentation may change after 2026-11-23. Re-run the check against the live pages before relying on any row.
