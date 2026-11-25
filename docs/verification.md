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
| A shell command that prints a secret-looking variable, or dumps the environment in the common ways, is blocked (INV-02). | executed | `tests/test_hooks.py::test_secret_variables_and_environment_dumps_in_shell_block`, `tests/test_hooks.py::test_ordinary_variables_pass` |
| Changing directory first does not hide a write to the rulebook or the approvals folder (INV-03). | executed | `tests/test_hooks.py::test_changing_directory_first_does_not_hide_a_write_to_the_rulebook` |
| Every file that sets a gate, an agent's tools or the pass bar is protected, and the knowledge files stay writable. | executed | `tests/test_hooks.py::test_every_file_that_sets_a_gate_or_a_pass_bar_is_protected`, `tests/test_hooks.py::test_knowledge_files_stay_writable_so_the_agent_can_keep_its_notes` |
| A call that a guard blocks is logged with its reason and no contents, and a failure to write the log never changes the block. | executed | `tests/test_hooks.py::test_a_blocked_attempt_is_logged_with_its_reason_and_no_contents`, `tests/test_hooks.py::test_a_failure_to_write_the_log_never_changes_a_block` |
| The logger removes authorisation headers and secret assignments from the command it records. | executed | `tests/test_hooks.py::test_the_logger_redacts_authorization_headers`, `tests/test_hooks.py::test_a_blocked_command_is_logged_without_the_secret_in_it` |
| A glob, or a path built at run time, gets past the shell guard. | executed | `tests/test_hooks.py::test_a_glob_or_a_path_built_at_run_time_gets_past_the_shell_guard_a_known_limit`. This is a limit and not a defect that was fixed. It is stated in [kit/README.md](../kit/README.md). |
| Closing a rule-change entry ends its approval, but setting the entry back to open brings an old approval file back into force. | executed | `tests/test_hooks.py::test_reopening_a_closed_entry_rearms_its_approval_a_known_limit`, `tests/test_hooks.py::test_deleting_the_approval_file_ends_the_approval`. A limit, stated in [kit/README.md](../kit/README.md). |
| The hook settings use exec form with `args` and the `${CLAUDE_PROJECT_DIR}` placeholder as the documentation describes. | read | The pages named in [conventions.md](conventions.md). Not exercised in a live session. |
| A live session fills the `agent_type` field that the logger records. | not-verifiable | The documentation says the field is present when a hook fires inside a subagent. No live session was used. |

## Claims about the demonstration

The demonstration is in [demo/](../demo/README.md). Each claim names the invariant it supports.

| Claim | Label | Proof |
|---|---|---|
| The whole test suite passes. | executed | `python -m pytest` ended with the line `368 passed in 6.41s` on 2026-11-24, in the build environment (Python 3.12, pytest 9). |
| An edited, deleted or reordered ledger entry is detected, and `verify` reports the first bad position (INV-10). | executed | `tests/test_ledger.py::test_editing_an_entry_is_detected`, `tests/test_ledger.py::test_deleting_an_entry_is_detected`, `tests/test_ledger.py::test_reordering_entries_is_detected` |
| The ledger offers no function that updates or deletes an entry (INV-10). | executed | `tests/test_ledger.py::test_ledger_offers_no_way_to_update_or_delete` |
| An entry removed from the end of the ledger, and an edit followed by recomputing every later hash, are not detected from the file alone. Both are detected when the last hash was saved elsewhere. | executed | `tests/test_ledger.py::test_removing_the_last_entry_is_not_detected_without_an_anchor`, `tests/test_ledger.py::test_removing_the_last_entry_is_detected_with_an_anchor`, `tests/test_ledger.py::test_an_edit_that_recomputes_every_later_hash_is_not_detected_without_an_anchor`, `tests/test_ledger.py::test_an_edit_that_recomputes_every_later_hash_is_detected_with_an_anchor` |
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

## Claims about the drafted stories and case study section 5

| Claim | Label | Proof |
|---|---|---|
| Stories 02, 03 and 04 and case study section 5 were drafted by the agent from the record of this build, and each carries a review marker for the owner. Story 01 and section 4 remain stubs. | executed | `tests/test_repository.py::test_story_01_is_a_stub_and_the_drafted_stories_carry_a_review_marker_and_a_provenance_note`, `tests/test_repository.py::test_case_study_is_marked_draft_with_section_4_a_stub_and_section_5_a_marked_draft` |
| Every test id the drafts cite exists. | executed | `python scripts/check_rulebook.py`, whose proof check covers the stories and the case study, and `tests/test_check_rulebook.py::test_a_missing_test_id_cited_in_the_stories_or_the_case_study_fails` |
| The events the drafts describe happened as described. | read | The agent checked each statement against the two audit reports, the test results and the commit history of this build. No command proves a narrative. The owner is to confirm them before publishing. |
| The drafts contain no first-person account and no count of rules or invariants. | executed | `tests/test_repository.py::test_the_stories_contain_no_first_person_account` and the rulebook check |

## Claims about the checks and CI

| Claim | Label | Proof |
|---|---|---|
| The proof-and-label command published in the invariants tables flags exactly the ticked lines that lack a proof or a label, when copied from the table as written. | executed | `tests/test_kit_structure.py::test_the_published_proof_and_label_check_flags_exactly_the_bad_lines` |
| The register script published in the scenario-register skill passes a register whose tests exist, and rejects a test id that only prefixes a real one. | executed | `tests/test_kit_structure.py::test_the_published_register_check_passes_a_register_whose_tests_exist`, `tests/test_kit_structure.py::test_the_published_register_check_rejects_a_prefix_of_a_real_test_id` |
| The rulebook check fails on a banned term, an em dash, a count written in prose, an unknown reference, an undefined invariant id, a test id that does not exist, a broken link, an over-long summary and an unfilled slot. | executed | `tests/test_check_rulebook.py::test_banned_term_fails`, `tests/test_check_rulebook.py::test_em_dash_fails`, `tests/test_check_rulebook.py::test_prose_count_of_invariants_fails`, `tests/test_check_rulebook.py::test_unknown_command_reference_fails`, `tests/test_check_rulebook.py::test_undefined_invariant_id_fails`, `tests/test_check_rulebook.py::test_cited_test_id_that_does_not_exist_fails`, `tests/test_check_rulebook.py::test_broken_relative_link_fails`, `tests/test_check_rulebook.py::test_summary_over_the_cap_fails`, `tests/test_check_rulebook.py::test_fill_slot_outside_kit_and_templates_fails` |
| The rulebook check finds a banned term in a commit's author, committer, message or branch name, without printing the term, and fails on it under `--strict-history`. | executed | `tests/test_check_rulebook.py::test_a_banned_term_in_a_commit_email_is_a_warning_by_default`, `tests/test_check_rulebook.py::test_the_history_warning_never_prints_the_term`, `tests/test_check_rulebook.py::test_strict_history_turns_the_warning_into_a_failure` |
| The banned list is read from a local file or from the `BANNED_TERMS` variable, and the check says so when it has neither. | executed | `tests/test_check_rulebook.py::test_banned_terms_are_read_from_the_environment_when_the_file_is_absent`, `tests/test_check_rulebook.py::test_banned_terms_check_is_skipped_with_a_warning_when_there_is_no_list` |
| This repository passes its own rulebook check. | executed | `tests/test_check_rulebook.py::test_this_repository_passes_its_own_checks`, and `python scripts/check_rulebook.py` exits 0. |
| The commit history of this repository is free of banned terms. | executed | `python scripts/check_rulebook.py --strict-history` exits 0 with no history finding. Before 2026-11-24 it failed on every commit. The owner chose a new identity, and the history was rewritten that day. The rewrite changed authorship only: the tree hash was identical before and after. |
| The CI workflow contains the steps that run the tests, the rulebook check and the mutate-to-red harness, on push and pull request. | executed | `tests/test_repository.py::test_ci_runs_the_tests_and_the_rulebook_check_on_push_and_pull_request` |
| The CI workflow runs successfully on GitHub. | executed | The first run, on a private repository on 2026-11-24, succeeded: every step passed, including the tests, the rulebook check and the mutate-to-red harness. `gh run view 45390770008` shows it. The repository had no `BANNED_TERMS` secret, so the banned-terms check was skipped with a warning in that run. |

## Claims that the detections can fail

| Claim | Label | Proof |
|---|---|---|
| Each of the listed breakages of a hook guard, a structural check on the kit, a behaviour of the three demonstration modules, a code rule on the demonstration, the example's checks and the rulebook check turns its test red. The list is the one in `scripts/mutate_kit.py`. It is not exhaustive. | executed | `python scripts/mutate_kit.py` breaks one thing at a time, runs the test file meant to catch it, and restores the file. Last recorded result on 2026-11-24: every mutation turned its tests red, and the summary line read `mutations that stayed green or failed setup: 0`. |
| For each of the three demonstration modules, the detection reports failure once its guard is broken with `monkeypatch`. | executed | `tests/test_mutations.py::test_tamper_detection_fails_when_verify_always_reports_clean`, `tests/test_mutations.py::test_tamper_detection_fails_when_the_hash_ignores_the_content`, `tests/test_mutations.py::test_fail_closed_detection_fails_when_send_ignores_the_mode`, `tests/test_mutations.py::test_fail_closed_detection_fails_when_send_ignores_the_allowlist`, `tests/test_mutations.py::test_clamp_detection_fails_when_decide_trusts_the_proposal`, `tests/test_mutations.py::test_clamp_detection_fails_when_the_rule_always_passes` |

This table is extended as each phase adds claims. Claims about links, banned terms and proof ids are added when the check script that tests them exists.
