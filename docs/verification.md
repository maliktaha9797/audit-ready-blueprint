# Verification

This file is the repository's own honesty table. It lists what the repository claims about itself, and for each claim the label and the proof.

## Labels

| Label | Meaning |
|---|---|
| **executed** | A command or test was run, and its result is recorded here. |
| **read** | The thing was inspected but not run. |
| **not-verifiable** | It cannot be checked in the build environment. The reason is stated. |

Proof is a test id or a command. An adjective is not proof. To run one test, pass its id to pytest, for example `python -m pytest tests/test_hooks.py::test_protected_path_blocked_without_approval`.

## Claims about the kit

| Claim | Label | Proof |
|---|---|---|
| The file formats used by the kit match what the Claude Code documentation said on 2026-11-23. | read | The pages named in [conventions.md](conventions.md) were read. They were not exercised in a live session. |
| Every skill and agent file has frontmatter that starts on line 1, a `name` that matches its file or folder, and a `description` without angle brackets. | executed | `tests/test_kit_structure.py::test_skill_has_valid_frontmatter_with_matching_name` and `tests/test_kit_structure.py::test_agent_has_name_and_description` |
| Every command is a skill that Claude cannot start on its own. | executed | `tests/test_kit_structure.py::test_command_is_a_skill_that_only_a_person_can_start` |
| The invariant auditor has no edit or write tool. | executed | `tests/test_kit_structure.py::test_invariant_auditor_has_no_edit_or_write_tool` |
| The auditor cannot change files through the shell. | not-verifiable | It has the shell tool, and tool settings cannot remove its ability to write through it. The kit says so in [kit/README.md](../kit/README.md) and in the auditor's own file. |
| `kit/CLAUDE.md` names every agent, knowledge skill and command that exists, and no other. | executed | `tests/test_kit_structure.py::test_claude_md_names_every_agent_and_no_other`, `tests/test_kit_structure.py::test_claude_md_names_every_knowledge_skill_and_no_other`, `tests/test_kit_structure.py::test_claude_md_names_every_command_and_no_other` |
| Every invariant id cited in the kit is defined in the invariants table. | executed | `tests/test_kit_structure.py::test_every_invariant_id_cited_in_the_kit_is_defined_in_the_table` |
| No count of invariants or rules is written in prose. | executed | `tests/test_kit_structure.py::test_no_count_of_invariants_or_rules_is_written_in_prose` |

## Claims about the hooks

| Claim | Label | Proof |
|---|---|---|
| A write to a protected file is blocked when there is no approved rule change. | executed | `tests/test_hooks.py::test_protected_path_blocked_without_approval` |
| The same write is allowed when an open proposal and a matching approval file exist. | executed | `tests/test_hooks.py::test_protected_path_allowed_with_matching_approval_and_open_proposal` |
| An approval covers only the files it lists, and stops working when its entry is closed. | executed | `tests/test_hooks.py::test_approval_for_a_different_file_does_not_unlock_this_file`, `tests/test_hooks.py::test_approval_stops_working_once_the_entry_is_closed` |
| The hooks block a write to the approvals folder. | executed | `tests/test_hooks.py::test_write_to_approvals_folder_blocked` |
| The hooks block a write to a real-data path. | executed | `tests/test_hooks.py::test_write_to_real_data_path_blocked` |
| A missing, malformed or incomplete `guard.json` blocks (fail closed). | executed | `tests/test_hooks.py::test_missing_guard_json_blocks_every_guard`, `tests/test_hooks.py::test_malformed_guard_json_blocks`, `tests/test_hooks.py::test_wrong_type_in_guard_json_blocks`, `tests/test_hooks.py::test_empty_protected_paths_in_guard_json_blocks` |
| An unreadable event or a missing path blocks. | executed | `tests/test_hooks.py::test_unreadable_event_blocks`, `tests/test_hooks.py::test_missing_path_in_tool_input_blocks` |
| A shell command that mentions a blocked host, reads a secret file, or writes to a protected file is blocked. | executed | `tests/test_hooks.py::test_blocked_host_in_shell_command_blocks`, `tests/test_hooks.py::test_secret_file_read_in_shell_blocks`, `tests/test_hooks.py::test_shell_write_to_a_protected_file_blocks` |
| An ordinary write and an ordinary command pass. | executed | `tests/test_hooks.py::test_ordinary_write_passes`, `tests/test_hooks.py::test_ordinary_command_passes` |
| The logger writes one line per call and never file contents. | executed | `tests/test_hooks.py::test_logger_writes_one_line_and_no_file_contents` |
| The hook scripts run under Python 3.9, the default `python3` on the build machine. | executed | `tests/test_hooks.py::test_hooks_run_under_the_default_python3` |
| The settings register the guards before tool use with `onFailure` set to block, and deny secret reads and approval writes. | executed | `tests/test_hooks.py::test_settings_make_the_guards_fail_closed_at_the_harness`, `tests/test_hooks.py::test_settings_deny_secret_reads_and_approval_writes` |
| The hooks and permission rules work inside a live Claude Code session. | not-verifiable | The tests feed the scripts the stdin shape in the documentation. No live session was used in the build. |
| The `onFailure` field is accepted by the Claude Code version on the build machine (2.1.252). | not-verifiable | The documentation names 2.1.295 as the minimum. Whether an older version ignores or rejects the field was not tested. |
| The permission deny rules block the agent. | not-verifiable | The rules are present in the settings file, and a test asserts that. Enforcement is done by Claude Code and was not exercised. |

## Claims that the detections can fail

| Claim | Label | Proof |
|---|---|---|
| Every guard condition in the hooks, and every structural check on the kit, can fail: breaking each one turns its test red. | executed | `python scripts/mutate_kit.py` breaks one thing at a time, runs the test file meant to catch it, and restores the file. Last recorded result: every mutation turned its tests red, and the summary line read `mutations that stayed green or failed setup: 0`. |

This table is extended as each phase adds claims. Claims about links, banned terms and proof ids are added when the check script that tests them exists.
