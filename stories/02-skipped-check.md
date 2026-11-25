# A check that passed when its input was missing

<!-- OWNER: review this draft, which the agent wrote from the build record, correct anything you cannot stand behind, and delete this marker when you are content to publish it. -->

Drafted by the agent that built this repository, from the record of that build (the second independent audit and the test results). It describes this build. It is not an account of earlier work.

Links: [the violation signatures log](../kit/.claude/skills/invariants/SKILL.md#violation-signatures-log).

## What the agent tried to do

The agent added a history check to `scripts/check_rulebook.py`, so that a banned term in a commit author, message or branch name would be found before the repository was published. It made the check a warning by default and added a `--strict-history` flag that turns the warning into a failure. The flag was meant to be the command that proves the history is clean before publishing.

The history check needs the list of banned terms, and the list is private, so it is not in the repository. When no list was available, the script printed "banned-terms check skipped" and carried on. In strict mode it still exited with code 0.

So the command that was supposed to guarantee a clean history passed whenever there was nothing to check against. In CI, where the list is not in the repository, that was the normal case.

## Why that would have broken a rule

The rule is that a check which cannot run must not look like a check that passed. A missing input is the commonest way for a required check to be skipped without anyone deciding to skip it. A person reading "passed" would have published a history that had never been looked at.

The second independent audit found it. It ran the strict check with an empty list and got exit code 0 with a warning. The agent had not tested that case.

## What rule or check was added

In strict mode, a missing list is now a failure: the script says that strict mode needs the list. The CI workflow passes `--strict-history` only when the `BANNED_TERMS` secret is set, so a repository without the secret still runs the ordinary check and is not made to fail for lack of a list that it cannot have.

A test asserts both halves: strict mode with no list exits 1, and the ordinary run exits 0. A mutation in the harness removes the failure and the test goes red.

## Where it lives now

- `scripts/check_rulebook.py`, in `run_checks`, where strict mode handles a missing list.
- `tests/test_check_rulebook.py::test_strict_history_fails_when_there_is_no_banned_list_to_check_against`
- `scripts/mutate_kit.py`, the mutation named "strict mode passes without a banned list".
- `.github/workflows/ci.yml`, the step that checks the rulebook.
