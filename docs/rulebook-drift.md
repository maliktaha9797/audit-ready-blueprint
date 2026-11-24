# Rulebook drift

A rulebook is the set of files that say what is allowed. In this kit the list is `protected_paths` in `.claude/guard.json`, and that file is the only place the list is written. It covers `CLAUDE.md`, the settings, the hooks, the agents, the invariants skill, the gate and regression commands, the workflow files and the pass bar. Drift is what happens when these files stop agreeing with each other.

## How drift happens

A rulebook is written once and then grows. Each new rule is added where it is convenient. The rule is stated in one file, summarised in a second, and cited by id in a third. Later a rule is added, removed or reworded in one of those files and not the others.

The most visible form is a number. One file says there are a certain number of rules. A second file says a different number. A third lists them, and the list has a different length again. None of the files is lying. Each was right on the day it was written.

Drift matters in an audited setting for a plain reason. A reviewer who finds two files that disagree cannot tell which one the build followed. The disagreement is itself a finding, and it casts doubt on every other claim in the same files.

## Why prose counts are banned

A count written in prose is a second copy of information that already exists in a table. It has to be updated by hand every time the table changes, and nothing tells anyone it has gone stale.

So this repository never writes a count of rules or invariants in prose. A sentence refers to "the invariants" and lets the table be the only source. If a number is needed, a script computes it from the table at the moment it is wanted.

The same logic applies to ids. An id that is cited must be defined in the same repository, where a search finds it. An id that is cited but defined nowhere is private shorthand, and it is a form of drift.

## How the check script catches it

`scripts/check_rulebook.py` reads the repository and fails, with a non-zero exit code, when any of these is true:

| Check | What it catches |
|---|---|
| No prose counts | A phrase such as "<number> invariants" or "<number> rules" in any Markdown file |
| Reference integrity | A file refers to an agent, skill, command or workflow that does not exist, or cites an invariant id that the invariants table does not define |
| Proof integrity | A test id cited as proof does not exist in `tests/` |
| Links | A relative Markdown link points nowhere |
| Size caps | A summary file is longer than its cap |
| Slots | An unfilled slot marker is left outside the kit and the templates |
| Banned terms | A term from the local banned-terms list appears anywhere outside that list |
| Style | An em dash in any text file |

It also counts the owner stubs that are still to be written and prints them as a publication checklist. The stubs are warnings and not failures.

The script's own behaviour is tested in `tests/test_check_rulebook.py`. Each test builds a small temporary folder that breaks exactly one check and asserts that the script fails for that reason, and one clean folder that passes.

## What the script cannot catch

It cannot tell whether two files that both mention a rule agree about what the rule says. That is a human review, and it is part of every rule change: the person approving a change looks at every file that cites the rule.
