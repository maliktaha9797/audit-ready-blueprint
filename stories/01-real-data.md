# Real names nearly in the repository

<!-- OWNER: review this draft, which the agent wrote from the build record, correct anything you cannot stand behind, and delete this marker when you are content to publish it. -->

Drafted by the agent that built this repository, from the record of that build (the build brief, the gate reports and the checks). It describes this build. It is not an account of earlier work.

This is not a story about testing against real records. The agent never reached for real records in this build. It is the closest event that did happen: real names nearly entering a public repository, in a form that the kit's own real-data guard would not have caught. If the owner has an episode of the first kind, it should replace this draft.

Links: [the synthetic-data skill](../kit/.claude/skills/synthetic-data/SKILL.md), [the path guard](../kit/.claude/hooks/guard_paths.py) and [the check script](../scripts/check_rulebook.py).

## What the agent tried to do

The build brief asked for a file listing the terms that must never appear in the repository, which are names of organisations, products and people, and for a check that scans every tracked file except that one. Read literally, that file is a tracked file at `scripts/banned_terms.txt`. The owner supplied the list at the first gate.

The quickest path was to write the file as specified and commit it. The check would have passed, the build would have matched the brief, and the repository would have published, in one file, every name the owner wanted kept out of it.

The agent did not do that. It kept the real list on the owner's machine, left it out of version control, and committed a fictional example in its place. It told the owner in the next gate report and asked whether to handle it differently. The owner did not object.

## Why that would have broken a rule

The rule is that no real personal or customer data enters the repository. A list of real names is personal data, and a public list of the names to be kept out is itself a disclosure. The check built to protect the owner would have been the thing that leaked.

The kit's real-data guard would not have stopped it. That guard watches `data/real/**`, and the list was to live in `scripts/`. So the protection could not be a hook. It had to be a git-ignore rule and tests.

## What rule or check was added

- The list is excluded from version control, and a committed example file shows the format with fictional terms.
- The check reads the list from the local file, or from the `BANNED_TERMS` variable so that CI can hold it as a secret. If neither exists it says the check was skipped. It never prints a term, only which entry of the list matched.
- The list is not scanned as one of the files being checked.
- Later, after an audit, the check also scanned file names and commit metadata, and its strict mode failed when no list was available. The second of these is [story 02](02-skipped-check.md).
- After the push, the agent listed the files on the remote and found none of the private ones. That was a command run once, and no test repeats it.

## Where it lives now

- `.gitignore`, which excludes the local list.
- `scripts/banned_terms.example.txt`, the committed example with fictional terms.
- `scripts/check_rulebook.py`, which reads the list and never prints a term.
- `tests/test_repository.py::test_gitignore_keeps_private_and_generated_files_out_of_the_repository`
- `tests/test_repository.py::test_the_private_files_are_not_tracked_or_staged`
- `tests/test_repository.py::test_the_banned_terms_example_is_committed_and_says_its_terms_are_fictional`
- `tests/test_check_rulebook.py::test_banned_terms_are_read_from_the_environment_when_the_file_is_absent`
- `tests/test_check_rulebook.py::test_the_banned_terms_file_itself_is_not_scanned`
- `kit/.claude/skills/synthetic-data/SKILL.md`, for the principle that real data stays out of the build.
