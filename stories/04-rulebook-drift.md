# Rulebook drift

Drafted by the agent that built this repository, from the record of that build (its own checks, both independent audits and the commit history). It describes this build. It is not an account of earlier work.

Links: [the drift explanation](../docs/rulebook-drift.md) and [the check script](../scripts/check_rulebook.py).

## What the agent tried to do

The agent wrote the kit's rules in many files, and the files came to disagree. Four kinds of disagreement are recorded.

**A count written in prose.** The repository bans writing how many invariants there are, because the count goes stale. During the example phase the agent wrote the number of the domain's extra invariants, in words, in a sentence in a Markdown file, and the agent's own test caught it. The first audit then found two more in other files that the test's pattern missed, because the number was not directly before the word: it was followed by "of the" and a possessive. The agent fixed them and broadened the pattern. The second audit found that the number words stopped at twelve, so a larger number written in words would pass. The pattern was broadened again. This story avoids quoting the phrases for that reason: quoting a count is writing one, and the check says so.

**A recorded total that went stale.** The verification table recorded a test total for the whole suite. The suite grew, and the first audit found the recorded total far below the real one.

**A template and a check that disagreed.** The kit's phase-log template let a slice be ticked with a proof and no label. The kit's own check for the rule that every ticked criterion carries a proof and a label would have flagged every ticked slice. A test on the example phase log found it.

**Several lists of what the rulebook is.** After the first audit the agent widened the set of protected files in the guard configuration. The proposals file, the skill description and two `CLAUDE.md` files still named narrower sets, and the build report called the configuration "the only list". The second audit found it.

## Why that would have broken a rule

A rulebook whose files disagree about what the rules are cannot be audited. A reviewer who finds two lists cannot tell which one the build followed, and the disagreement casts doubt on every other claim in the same files.

## What rule or check was added

- The guard configuration is now the only place the protected files are listed, and each document that used to enumerate them points to it.
- The check script fails on a count written in prose, in the forms found, and tests cover each form.
- The phase-log templates carry a label on slices, and a test runs the published proof-and-label command exactly as it is written in the table.
- The test total is quoted in one place, `docs/verification.md`, with its date, and the README and report point to it.

The script cannot catch the fourth kind. It cannot tell whether two files that both mention the rulebook agree about what it contains. That was found by an independent reader and fixed by editing, and the drift document says so.

## Where it lives now

- `docs/rulebook-drift.md`, including its section on what the script cannot catch.
- `scripts/check_rulebook.py`, the prose-count pattern and the placeholder check.
- `tests/test_kit_structure.py::test_no_count_of_invariants_or_rules_is_written_in_prose`
- `tests/test_check_rulebook.py::test_prose_count_of_the_form_n_of_the_kits_invariants_fails`
- `tests/test_check_rulebook.py::test_larger_counts_written_in_prose_fail`
- `tests/test_example.py::test_ticked_boxes_in_the_phase_log_carry_a_proof_and_a_label`
- `tests/test_kit_structure.py::test_the_published_proof_and_label_check_flags_exactly_the_bad_lines`
- `kit/.claude/guard.json`, the list of protected files.
