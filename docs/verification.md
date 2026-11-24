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

## Claims about the demonstration

The demonstration is in [demo/](../demo/README.md). Each claim names the invariant it supports.

| Claim | Label | Proof |
|---|---|---|
| The whole test suite passes. | executed | `python -m pytest` ended with the line `187 passed in 1.72s` on 2026-11-24. |
| An edited, deleted or reordered ledger entry is detected, and `verify` reports the first bad position (INV-10). | executed | `tests/test_ledger.py::test_editing_an_entry_is_detected`, `tests/test_ledger.py::test_deleting_an_entry_is_detected`, `tests/test_ledger.py::test_reordering_entries_is_detected` |
| The ledger offers no function that updates or deletes an entry (INV-10). | executed | `tests/test_ledger.py::test_ledger_offers_no_way_to_update_or_delete` |
| An entry removed from the end of the ledger is not detected from the file alone, and is detected when the last hash was saved elsewhere. | executed | `tests/test_ledger.py::test_removing_the_last_entry_is_not_detected_without_an_anchor`, `tests/test_ledger.py::test_removing_the_last_entry_is_detected_with_an_anchor` |
| A message is sent only in `live` mode to an allowlisted recipient (INV-09). | executed | `tests/test_outbound.py::test_message_is_sent_only_in_live_mode_to_an_allowlisted_recipient` |
| A missing, unknown, misspelt or wrongly capitalised mode, a missing or empty allowlist, an unlisted recipient and a missing config each suppress the message and record why (INV-09). | executed | `tests/test_outbound.py::test_send_is_suppressed_when_mode_is_missing`, `tests/test_outbound.py::test_send_is_suppressed_when_mode_is_unknown`, `tests/test_outbound.py::test_send_is_suppressed_when_mode_is_misspelt`, `tests/test_outbound.py::test_send_is_suppressed_when_the_allowlist_is_missing`, `tests/test_outbound.py::test_send_is_suppressed_when_the_recipient_is_not_on_the_allowlist` |
| Nothing is sent if the ledger cannot be written (INV-09, INV-10). | executed | `tests/test_outbound.py::test_nothing_is_sent_if_the_ledger_cannot_be_written` |
| A failing rule with a proposed `verified` gives `needs_review` and a flag, and the override is recorded (INV-07). | executed | `tests/test_rules.py::test_failing_rule_with_proposed_verified_gives_needs_review_and_a_flag`, `tests/test_rules.py::test_every_decision_is_recorded_in_the_ledger_with_the_override` |
| No proposal can make a failing rule end as verified (INV-07). | executed | `tests/test_rules.py::test_a_failing_rule_can_never_end_as_verified_whatever_is_proposed` |
| Document text does not change a decision, because the rule reads typed fields only. | executed | `tests/test_rules.py::test_document_text_never_changes_the_decision` |
| The demonstration follows its code rules: standard library only, no classes, decorators or lambdas, type hints and an invariant-naming docstring on every function, short modules. | executed | `tests/test_demo_code_rules.py::test_module_imports_only_the_standard_library_and_the_demo_itself`, `tests/test_demo_code_rules.py::test_module_has_no_classes_decorators_or_lambdas`, `tests/test_demo_code_rules.py::test_every_function_has_type_hints`, `tests/test_demo_code_rules.py::test_every_function_docstring_names_the_invariant_it_serves` |
| The five exercises in the walkthrough fail the tests that the answers name. | executed | Each change was made, the four demonstration test files were run, and the failing test names were recorded. The answers in [WALKTHROUGH.md](../demo/WALKTHROUGH.md) are those results. |
| The demonstration evaluates only the registration rule. The expired certificate, the bank name and the duplicate in the fixtures are not evaluated by any code here. | read | `demo/supplier_demo/rules.py` holds one rule. This is stated in [demo/README.md](../demo/README.md). |

## Claims about the example

The example is in [example/](../example/README.md). It is a specification, and the build it describes is not in this repository.

| Claim | Label | Proof |
|---|---|---|
| No unfilled slot remains anywhere in the example. | executed | `tests/test_example.py::test_no_fill_slot_remains_in_the_example` |
| Every test id the example cites as proof exists. | executed | `tests/test_example.py::test_every_test_id_cited_in_the_example_exists` |
| A register row marked covered cites a real test, and a planned row cites none. | executed | `tests/test_example.py::test_covered_register_rows_cite_real_tests_and_planned_rows_cite_none` |
| The register has the documented columns, a decider on every row, and unique ids. | executed | `tests/test_example.py::test_register_uses_the_documented_columns_deciders_and_unique_ids`, `tests/test_example.py::test_register_size_is_in_the_planned_range` |
| The register covers mismatches, the three expiry boundaries, duplicates, instructions in a document, a request to skip a check, a registry that is down or conflicting, a resubmission and an approver approving their own submission. | executed | `tests/test_example.py::test_register_covers_every_family_of_scenario_the_plan_asks_for` |
| Every invariant id cited in the example is defined in the example's table, and the table keeps every kit invariant. | executed | `tests/test_example.py::test_every_invariant_id_cited_in_the_example_is_defined_in_its_table`, `tests/test_example.py::test_the_example_table_keeps_the_kit_invariants_and_adds_its_own` |
| Every check in the example's invariants table is marked as covered by the demonstration or planned for the build. | executed | `tests/test_example.py::test_every_check_in_the_example_invariants_is_marked_demo_or_planned_or_generic` |
| The trail files say in their first line that they are illustrative, and the phase log shows mixed labels. A criterion labelled not-verifiable is never ticked. | executed | `tests/test_example.py::test_every_trail_file_starts_with_the_illustrative_notice`, `tests/test_example.py::test_the_phase_log_shows_mixed_labels_honestly`, `tests/test_example.py::test_criteria_marked_not_verifiable_are_not_ticked` |
| Every ticked box in the example's phase log carries a proof and a label. | executed | `tests/test_example.py::test_ticked_boxes_in_the_phase_log_carry_a_proof_and_a_label` |
| The example's pass bar is unsigned, and the phase log records no sign-off. | executed | `tests/test_example.py::test_the_example_pass_bar_is_unsigned`, `tests/test_example.py::test_the_example_phase_log_records_no_sign_off` |
| Nothing in the example claims a build beyond the demonstration. | read | The folder was read in full, and searched for phrases that imply deployment, certification or an audit. No such claim was found. A search cannot prove absence, so this is labelled read. |
| The checks the example marks Planned do not exist in this repository. | read | By definition. They describe the separate build. |

## Claims that the detections can fail

| Claim | Label | Proof |
|---|---|---|
| Every guard condition in the hooks, every structural check on the kit, every behaviour of the three demonstration modules and every code rule on the demonstration can fail: breaking each one turns its test red. | executed | `python scripts/mutate_kit.py` breaks one thing at a time, runs the test file meant to catch it, and restores the file. Last recorded result on 2026-11-24: every mutation turned its tests red, and the summary line read `mutations that stayed green or failed setup: 0`. |
| For each of the three demonstration modules, the detection reports failure once its guard is broken with `monkeypatch`. | executed | `tests/test_mutations.py::test_tamper_detection_fails_when_verify_always_reports_clean`, `tests/test_mutations.py::test_tamper_detection_fails_when_the_hash_ignores_the_content`, `tests/test_mutations.py::test_fail_closed_detection_fails_when_send_ignores_the_mode`, `tests/test_mutations.py::test_fail_closed_detection_fails_when_send_ignores_the_allowlist`, `tests/test_mutations.py::test_clamp_detection_fails_when_decide_trusts_the_proposal`, `tests/test_mutations.py::test_clamp_detection_fails_when_the_rule_always_passes` |

This table is extended as each phase adds claims. Claims about links, banned terms and proof ids are added when the check script that tests them exists.
