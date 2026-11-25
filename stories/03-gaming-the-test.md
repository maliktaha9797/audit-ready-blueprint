# A test that could not fail

<!-- OWNER: review this draft, which the agent wrote from the build record, correct anything you cannot stand behind, and delete this marker when you are content to publish it. -->

Drafted by the agent that built this repository, from the record of that build (its own tests, the mutation harness and the second independent audit). It describes this build. It is not an account of earlier work.

This is not the failure of fixing a detection by matching the test's input, or of re-running a flaky test until it passes. Neither happened in this build. It is the same problem seen from the test's side: a green result that does not mean the guard works. Two cases are recorded.

Links: [the fixtures-and-harness skill](../kit/.claude/skills/fixtures-and-harness/SKILL.md).

## What the agent tried to do

**A format test that stopped testing its own subject.** The kit's rule-change file has a format example inside a fenced code block, and the hook that reads the file must ignore anything inside a fence. The agent wrote a test for that, using an approval id that came from the example's placeholder text. Later the agent reworded the example to a different style of placeholder. The test still passed, because the id no longer matched anything, whether or not the hook ignored the fence. The agent noticed when it changed the file, rewrote the test so that it builds its own fenced entry, and showed with a mutation that the new test goes red when the fence handling is removed.

**A logging test that could not tell two behaviours apart.** The agent wrote a test that a long command is cut when it is logged, and that only its first line is kept. The command in the test had its second line after about three hundred characters. The log is cut to a hundred characters, so the second line was gone either way. A change that logged the whole command instead of the first line left the test green.

This was found because the second independent audit listed "logging the whole command" among mutations that stayed green. The agent had added mutations and tests for three of the four gaps the audit named and had not checked the fourth. When the owner asked what was open on the rule about detections, the agent ran that mutation. It stayed green.

## Why that would have broken a rule

The rule is that every detection test has been shown capable of failing. A test that has never failed for the behaviour it names has not been shown to detect that behaviour, so its green result is not evidence. Both tests above would have stayed green with the behaviour they named removed.

The second case mattered more because the audit had named the gap and the agent had treated it as covered.

## What rule or check was added

A new logging test was added beside the old one. Its command is short, and its second line is placed where only a whole-command log could contain it. It fails under the mutation and passes on the real code. The mutation was added to the harness.

The owner then recorded a decision that accepts the mutation list as not exhaustive, so the rule is met for every breakage on the list and not for guards the list does not name.

## Where it lives now

- `tests/test_hooks.py::test_the_logger_records_only_the_first_line_of_a_command`, the new test. The older `tests/test_hooks.py::test_logger_cuts_long_commands_and_removes_secret_assignments` stays, and still checks the cut and the redaction.
- `tests/test_hooks.py::test_entry_inside_a_code_fence_is_never_an_open_entry`
- `scripts/mutate_kit.py`, which runs every mutation and restores each file: `python scripts/mutate_kit.py`.
- `kit/.claude/hooks/guard_lib.py`, where the log target is built.
- The owner's decision on the rule, recorded in `BUILD-REPORT.md`.
