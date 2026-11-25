# Build report

This report records what was built, how each exit criterion was proved, where the build departed from its brief and why, the result of the self-audit, and what the owner still has to do before the repository is published.

Labels are those defined in [docs/verification.md](docs/verification.md): **executed**, **read** and **not-verifiable**. Recorded test summary lines are in that file, so that they are written once.

## 1. Exit criteria by phase

### Phase 0: verify and scaffold

| Criterion | Label | Proof |
|---|---|---|
| `docs/conventions.md` exists, with every row of the verification table filled from the live documentation | executed (the file and its rows exist), read (what the rows say) | `tests/test_repository.py::test_every_doc_the_plan_names_exists`. The pages were fetched and read on 2026-11-23, and their titles are in the file. |
| The commands-or-skills decision is recorded | executed | [docs/conventions.md](docs/conventions.md), section "Decision: commands as skills". `tests/test_kit_structure.py::test_command_is_a_skill_that_only_a_person_can_start` |
| `git status` is clean after the phase commit | executed | `git status --porcelain` printed nothing after the phase 0 commit. |
| `pytest` runs and reports zero tests collected without error | executed | `python -m pytest` before any test existed printed `no tests ran` and exited with code 5, which is pytest's code for no tests collected. |

### Phase 1: the method

| Criterion | Label | Proof |
|---|---|---|
| Every path and format in `BLUEPRINT.md` and `templates/` matches `docs/conventions.md` | read | The paths used were listed and compared by reading. `tests/test_repository.py::test_every_template_starts_with_a_three_line_comment_or_frontmatter_then_that_comment` covers the template layout. |
| Every relative link in these files resolves | executed | `python scripts/check_rulebook.py`, whose link check is proved able to fail by `tests/test_check_rulebook.py::test_broken_relative_link_fails`. At the phase 1 commit, links into `kit/`, `example/` and `demo/` pointed at files that later phases created, and they resolve from the phase 4 commit. |
| No placeholder example from the source remains in `BLUEPRINT.md` | executed | A search of `BLUEPRINT.md` and `templates/` for the names used in the source's three examples found nothing. The only hit for "Example 1" is the skill template's own example slot. |

### Phase 2: the kit

| Criterion | Label | Proof |
|---|---|---|
| Every agent, skill and command file validates against the formats in `docs/conventions.md` | executed | `tests/test_kit_structure.py::test_skill_has_valid_frontmatter_with_matching_name`, `tests/test_kit_structure.py::test_agent_has_name_and_description`, `tests/test_kit_structure.py::test_command_is_a_skill_that_only_a_person_can_start` |
| Every agent and skill named in `kit/CLAUDE.md` exists, and every existing one is named there | executed | `tests/test_kit_structure.py::test_claude_md_names_every_agent_and_no_other`, `tests/test_kit_structure.py::test_claude_md_names_every_knowledge_skill_and_no_other`, `tests/test_kit_structure.py::test_claude_md_names_every_command_and_no_other` |
| `invariant-auditor` has no edit or write tool | executed (its settings), not-verifiable (its shell) | `tests/test_kit_structure.py::test_invariant_auditor_has_no_edit_or_write_tool`. The shell tool remains and can change files. |
| `tests/test_hooks.py` passes | executed | `python -m pytest tests/test_hooks.py`. The recorded line is in [docs/verification.md](docs/verification.md). |
| No count of invariants appears in prose anywhere | executed | `tests/test_kit_structure.py::test_no_count_of_invariants_or_rules_is_written_in_prose` and the rulebook check |

### Phase 3: the demonstration

| Criterion | Label | Proof |
|---|---|---|
| `pytest` passes, with the command and summary line recorded in `docs/verification.md` | executed | The line is in [docs/verification.md](docs/verification.md). |
| Each of the three mutations turns its detection red | executed | `tests/test_mutations.py`, and `python scripts/mutate_kit.py` for the source-level breakages. |
| No import outside the standard library and pytest | executed | `tests/test_demo_code_rules.py::test_module_imports_only_the_standard_library_and_the_demo_itself` |

### Phase 4: the example

| Criterion | Label | Proof |
|---|---|---|
| No unfilled slot remains in `example/` | executed | `tests/test_example.py::test_no_fill_slot_remains_in_the_example` |
| Every fixture id marked covered resolves to a real test | executed | `tests/test_example.py::test_covered_register_rows_cite_real_tests_and_planned_rows_cite_none`, `tests/test_example.py::test_every_test_id_cited_in_the_example_exists` |
| Nothing in `example/` claims a build beyond `demo/` | read | The folder was read in full and searched for phrases that imply deployment, certification or an audit. A search cannot prove absence. |

### Phase 5: the front door

| Criterion | Label | Proof |
|---|---|---|
| The README is under about 150 lines and has its sections in the planned order | executed | `tests/test_repository.py::test_readme_is_short_and_has_the_sections_in_the_planned_order` |
| The working name appears only in the README title | executed | `tests/test_repository.py::test_the_working_name_appears_only_in_the_readme_title` |
| The case study is marked draft, with section 4 and story 01 as stubs and the drafted parts carrying a review marker | executed | `tests/test_repository.py::test_case_study_is_marked_draft_with_section_4_a_stub_and_section_5_a_marked_draft`, `tests/test_repository.py::test_story_01_is_a_stub_and_the_drafted_stories_carry_a_review_marker_and_a_provenance_note` |
| No first-person experience is written in the case study's drafted sections or in the stories | executed | `tests/test_repository.py::test_the_stories_contain_no_first_person_account`. Sections 1 to 3 of the case study were also read for it. |

### Phase 6: checks and final audit

| Criterion | Label | Proof |
|---|---|---|
| `pytest` passes | executed | The recorded line is in [docs/verification.md](docs/verification.md). |
| `python scripts/check_rulebook.py` exits zero, with only owner-stub warnings | executed | It exits zero and lists the owner stubs, and `python scripts/check_rulebook.py --strict-history` also exits zero. During the build it printed a history warning for every commit, because the commit authorship matched an entry of the private banned list. The owner supplied a publishable identity on 2026-11-24 and the history was rewritten, with the tree hash unchanged. |
| `git status` is clean, with one commit per phase | executed | All changes are in the phase 6 commit, so `git status --porcelain` prints nothing and `git log --oneline` shows a commit for each of phases 0 to 6. Run both to confirm. |
| `BUILD-REPORT.md` is complete | read | This file. |

## 2. Deviations from the brief, and why

| What the brief said or implied | What was done | Why |
|---|---|---|
| Markdown workflow files in `.claude/workflows/` are the repository's own convention | They are in `.claude/workflow-docs/` | The documentation says `.claude/workflows/` is a native location for `.js` dynamic workflow scripts, each run as a command. |
| A `/status` command | `/project-status` | `/status` is a built-in command. |
| Seven commands in `.claude/commands/`, or as skills, decided in phase 0 | Skills with `disable-model-invocation: true` | The documentation recommends skills for new work. |
| `scripts/banned_terms.txt` is created and committed | It is local and git-ignored. A fictional `banned_terms.example.txt` is committed. CI reads the list from a secret. | A committed list would publish the names it exists to protect. |
| The check script scans tracked files for banned terms | It also scans file names, and commit authors, committers, messages and branch names. `--strict-history` fails if there is no list to check against | The audit found that a clean result could not see a banned term in the history. |
| A "seventh" question group | The assurance group, with no ordinal | The source has five groups, so it is the sixth. Ordinals were avoided so the text cannot drift. |
| Three-line comment at the top of each template | After the closing `---` in templates that have frontmatter | Claude Code reads frontmatter only when `---` is the first line. |
| A hook that fails is fail closed | Each guard catches every error and exits 2, and the settings add `onFailure: "block"` | The documentation says only exit code 2 blocks. `onFailure` needs a later Claude Code version than the one on the build machine. |
| Approval is by id | The approval file must name an approver and list the files it covers | An approval for one file must not unlock another. |
| The rulebook is named in prose | `protected_paths` in `guard.json` is the only list, and it is wider than first built. Short names of protected files are matched only after a `cd` | The audit found files that set gates and pass bars were editable. |
| `guard_bash` blocks hosts, patterns and secret reads | It also blocks shell writes to the rulebook and the approvals folder, matching a path's short name after `cd`, and it records every block in the audit log | The audit found the `cd` bypass and that blocked attempts left no record. |
| One test file per topic | Added `test_kit_structure.py`, `test_demo_code_rules.py`, `test_example.py` and `test_repository.py`; added `scripts/mutate_kit.py` and `kit/.claude/hooks/guard_lib.py` | The exit criteria needed executable proof. |
| Hooks in Python 3.12 | Written for Python 3.9 and later, and tested under 3.9 | The default `python3` on the build machine is 3.9. |
| `ledger.py` under about 100 lines | 102 lines | Recording the limits of the hash chain took a few docstring lines. |
| The README is written in phase 5 and the check script in phase 6 | The check script was written first, and committed in the phase 6 commit | So the README could cite real test ids. The README's cited ids exist from the phase 6 commit. |
| CI runs pytest and the check | It also runs the mutate-to-red harness, and the check runs with `--strict-history` | So CI re-proves that every detection can fail and that the history is clean. |
| Each hook under about 80 lines | `guard_bash.py` is 99 lines and `guard_lib.py` is about 170 | The wider write list, the secret patterns and the logging each needed code and a docstring. |
| The agent writes no story and no owner section of the case study | At the owner's instruction on 2026-11-25, stories 02 to 04 and case study section 5 were drafted from the build record, each marked for review. Story 01 and section 4 stay stubs. | The owner asked for drafts. The drafts describe this build only and invent nothing. |
| "Judgment" | The spelling is kept | The governing sentence is quoted as given, and the form is standard British usage. |
| Run the kit's own gate on this repository | An independent read-only agent ran the kit's audit process, and its report was acted on | The builder cannot audit itself. See section 3. |
| Phase 6 proof-integrity checks cite ids in the README, `docs/verification.md` and `example/` | The scope is the README, `docs/`, `demo/` and `example/` | The kit and templates hold generic sample ids that must not exist. |

## 3. Self-audit

The audit was run by a separate agent that was given the kit's invariants table, its auditor process and the repository, and was not given the builder's conclusions. It was instructed not to modify any file. Like the kit's own auditor it had the shell tool, so that instruction is a rule and not a technical limit. The kit's own `invariant-auditor` agent was not used, because it is a kit file and was not loaded as an agent in the build session.

### First audit

The first audit returned BLOCK on INV-02, INV-03 and INV-06, and a long list of findings beyond the invariants. In summary:

- **INV-02:** the shell guard allowed several ways of printing secrets and dumping the environment, contrary to what the kit's documents said.
- **INV-03:** the shell guard could be bypassed by changing directory first. Files that set gates and the pass bar were not protected. The approval of a closed entry could be brought back by re-opening the entry.
- **INV-06:** the mutate-to-red harness did not cover several guards.
- **Other findings:** the commit history contained a banned term, two published checks were defective, several documents claimed more than the code did, a recorded test total was stale, and some prose counts and a self-contradicting sentence remained.

### What was changed

Each finding was verified before it was acted on. The shell guard now blocks secret-looking variables and the common environment dumps, and matches a path's short name after `cd`. The protected set is wider, and `guard.json` is the single list. Blocked attempts are logged. The proof-and-label command and the register script were rewritten, and tests now run each one exactly as published. The harness covers the guards that were missing. The check script scans history. The documents that overclaimed were corrected, and the limits that cannot be fixed (text matching, an approval that outlives its entry, a hash chain without an anchor) are stated in the documents and recorded in tests.

### Second audit

The same agent was resumed and asked to re-verify each of its findings, to replay its probes against a scratch copy, and to look for problems that the fixes introduced. It did not modify the repository. It reported:

- **Resolved or partly resolved:** most findings. The `cd` bypass, the secret-variable and environment-dump gaps, the unprotected gate files, the missing blocked-attempt log, the two defective shipped checks, the ledger's full-rewrite limit and the overclaiming documents were all re-tested and found fixed or accurately described.
- **Still BLOCK, INV-02:** several routes to a secret were still allowed (a file with a prefix before `.env`, `id_rsa`, `.git-credentials`, a bare `set`, a search by pattern).
- **Still BLOCK, INV-03:** several writers were not recognised (`curl -o`, `rsync`, `tar`, `unzip`, `ruby`, `php`, `patch`, an editor in batch mode, every PowerShell cmdlet), and a path built at run time gets through.
- **INV-06, narrow:** some mutations of its own devising stayed green (the PowerShell matcher, the `ask` rule, `tee`), and three settings tests never failed under any mutation.
- **New findings:** the short-name match blocked ordinary commands that named a file called `settings.json` or a folder called `agents` anywhere; some documents still described `protected_paths` as one of several lists; `--strict-history` passed when there was no banned list; number words stopped at twelve; the proof-and-label command was weaker than the regex it replaced; and this report claimed a clean tree before the commit existed.

### What was changed after the second audit

The builder made these changes and verified them with tests, with `python scripts/mutate_kit.py`, and by replaying the audit's own probes. This round was **not** re-audited independently.

- The short-name match now applies only when the command also changes directory, which is the case it exists for.
- The list of write-like commands now includes `curl`, `wget`, `rsync`, `tar`, `unzip`, `patch`, `ruby`, `php`, the common editors, `awk`, more git subcommands and the PowerShell content and item cmdlets.
- The secret patterns now cover a file name with a prefix before `.env`, key and credential file names, and a bare `set`. `Read(*.env)` is a deny rule.
- `--strict-history` fails when there is no banned list. CI passes the flag only when the secret is set.
- The check script counts number words beyond twelve and flags any stray placeholder, which is how the placeholder in this report was found.
- The proof-and-label command is stricter again, and still has no pipe characters.
- Tests were added for the PowerShell matcher, the `ask` rule, `tee`, and the settings rules, and mutations were added for each.
- Every document that listed the rulebook now points at `protected_paths` in `guard.json`, and the statements about what the shell guard refuses say what it recognises and no more.

### The state of the verdicts

| ID | After the second audit | Builder's replay after the changes |
|---|---|---|
| INV-02 | BLOCK, cleared by the owner's decision | The routes the audit named are now blocked. A search by pattern and an `.envrc` file are still allowed, on purpose or by limitation, and the limits are stated. |
| INV-03 | BLOCK, cleared by the owner's decision | The writers the audit named are now blocked when they name the file or folder. A glob or a path built at run time is still allowed. A test records it. |
| INV-06 | BLOCK (narrow), cleared by the owner's decision | Mutations were added for each gap the audit named. The list is not exhaustive. |
| INV-01, INV-04, INV-05, INV-07, INV-08, INV-09, INV-10 | PASS | Not re-run after the last round. The tests that prove them were re-run and pass. |
| INV-11, INV-12 | N/A | No document intake, review queue or graded run exists. |

**INV-02 and INV-03 are BLOCK in their strict reading, and are cleared by the owner's recorded decisions below.** A text check on shell commands cannot show that a secret is never read or that a rulebook file is never written, because a shell can reach a file in more ways than any list can name. What holds is: the permission deny rules, which Claude Code applies to its own file tools and to the shell commands it can analyse (not-verifiable here); the hook's refusal of the common routes (executed); and a log of attempts. The auditor's verdict was not changed. The kit's own rule is that a block is cleared only by a fix or by a recorded decision from the owner, and the owner made that decision.

### Owner decisions on INV-02, INV-03 and INV-06

#### INV-02 and INV-03

Recorded on 2026-11-24, at the owner's instruction, in the form the kit uses for its decision log.

```
### 2026-11-24: INV-02 and INV-03 accepted as enforced to their stated limits

- Decision: INV-02 and INV-03 are enforced by permission rules and hooks that match
  command text. They are accepted as enforced to the limits stated in kit/README.md.
- Why: The kit is a reference setup and says plainly that it is not a security boundary.
- Residual risk: a shell route that the patterns do not name can read a secret or write
  a rulebook file. The tool log and git history would show it. A sandbox or a shell
  allowlist is needed to close it.
- Supersedes: nothing
- Decided by: Taha Malik
```

The two options that were not chosen remain open to anyone who adopts the kit for real work: turn on Claude Code's sandbox for shell commands, and run with a short allowlist of permitted shell commands. Neither was built or tested here.

#### INV-06

Recorded on 2026-11-24, at the owner's instruction, in the same form.

```
### 2026-11-24: INV-06 accepted on the strength of the mutation harness

- Decision: INV-06 is accepted as met for every breakage listed in scripts/mutate_kit.py,
  each of which turns its tests red. The list is accepted as not exhaustive.
- Why: The harness is reproducible and was extended after two independent audits. The last
  round of additions, including a test found to be unable to fail and then rewritten, was
  checked by the builder and was not independently re-audited.
- Residual risk: a guard that the list does not cover could have a test that cannot fail.
  A further independent audit against the final code would reduce it.
- Supersedes: nothing
- Decided by: Taha Malik
```

The auditor's verdict was not changed. The decision clears the block under the kit's own rule.

### Live test, 2026-11-25

At the owner's request the hooks were tested in real Claude Code sessions. The command-line tool had to be signed in first, which the owner did. `scripts/live_hook_test.py` builds scratch projects from the kit with an invented `.env`, runs each case as `claude -p` with the small model on Claude Code 2.1.252, and decides each result from files and the audit log, not from what the model says.

| Case | Result |
|---|---|
| A write to a protected file | Blocked by the hook, with the invariant message, and the file unchanged |
| `cat .env`, and an echo of a secret variable | Blocked by the shell guard |
| A write after `cd` into the rulebook folder | Blocked by the shell guard, with no guidance file present |
| `Read` of `.env` | Stopped by the permission deny rule |
| An ordinary write | Allowed and logged |
| A subagent's `ls` | Logged with the agent type of the subagent |
| `grep -r` for the invented secret | Not blocked, and it printed the value. This is the stated limit, seen live. |
| A guard that exits with code 1 | The edit went through on the first test, and is blocked after the fix below |

**A defect the unit tests could not find.** The settings say `"onFailure": "block"`, and the report had treated that as a second layer. On Claude Code 2.1.252 the field is accepted and ignored, so a guard that exited with any code other than 2 let the call go ahead. The kit's scripts catch their own errors and exit 2, but a syntax error, a missing interpreter or a crash before the script's code runs exits with another code. The guards now run as `python3 script || exit 2`. New tests run that exact command in a shell with a crashing script, a script with a syntax error and no interpreter at all, and the live case was repeated after the change.

**Two things the live runs showed about method.** A model often declines a request by itself after reading `CLAUDE.md`, which is the guidance working and says nothing about the hook. The script therefore runs the enforcement cases without `CLAUDE.md` and reports a case with no evidence as inconclusive, not as a pass. Its first version also could have reported a pass for a write that was never attempted, so each case now needs evidence that the action was tried.

**What was not tested.** An interactive session. Print mode treats project hooks as trusted and shows no trust dialog.

## 4. Limits that remain

- The guards match text and are not a security boundary. A glob, a variable or a path built at run time gets past the shell guard, and a determined user with shell access can get around all of it. A test records this.
- The auditor has the shell tool and can change files through it.
- An approval file stays in force for as long as it exists. The owner deletes it when the entry is closed.
- A hash chain without a saved copy of its last hash cannot show that entries were removed from the end or rewritten from an edit onwards.
- The hooks and deny rules were tested in real Claude Code sessions in print mode only, on 2026-11-25. An interactive session, which shows a trust dialog first, was not tested.
- The CI workflow ran once on GitHub and passed. It ran without the `BANNED_TERMS` secret, so its banned-terms check was skipped, and only the local check has seen your list.
- The example is a specification. Only the demonstration runs.

## 5. Owner to do before publishing

1. **Commit authorship: done on 2026-11-24, with two things left for you.** The build was not permitted to change the git identity. The owner then supplied a name and email to publish, and the history was rewritten with `git rebase --root` and `git commit --amend --author`, using a repository-local identity. The tree hash was identical before and after, all seven messages were kept, and `python scripts/check_rulebook.py --strict-history` passes. Still yours:
   - **The old commits are still in your local git objects.** They are on no branch and are never pushed, but they carry the old identity. To remove them for good, run `git reflog expire --expire=now --all` and then `git gc --prune=now`. That cannot be undone.
   - **Check the new identity is the one you want public.** It is in every commit. If you change it later, repeat the rewrite and the strict check.

2. **Confirm the licence and the name.** `LICENSE` is MIT with the holder you gave. Confirm both.
3. **Story 01 and case study section 4 are still stubs for you to write.** Nothing of that kind happened in the build, so the agent did not invent it. Stories 02, 03 and 04 and case study section 5 were drafted by the agent on 2026-11-25, at your instruction, from the record of this build. Read each, correct what you cannot stand behind, and delete its marker. `python scripts/check_rulebook.py` lists the markers that remain.
4. **Review case study sections 1 to 3.** They describe the method only.
5. **Read every file for confidentiality with your own eyes.** The check looks for the terms on your list. It cannot know what else you would not want to publish.
6. **Test the hooks once in an interactive session.** The print-mode test is done (`python scripts/live_hook_test.py`, section 3). Copy the kit into a scratch project, start an interactive Claude Code session there, and ask it to edit `CLAUDE.md`. The edit should be blocked with a reason. Also check that `python3` is on the path. The kit now works on versions before 2.1.295, but update Claude Code if you can.
7. **Decide whether to exclude the example `CLAUDE.md` files** with the `claudeMdExcludes` setting, so that they do not load when Claude Code works inside this repository.
8. **Choose the repository name.** It appears only in the README title. `pyproject.toml` has its own project name.
9. **Add the companion repository link and the author line** to the README.
10. **Add a repository secret named `BANNED_TERMS`** if you want CI to run the banned-terms check. Without it the check is skipped with a warning.
11. **Decide whether `BUILD-REPORT.md` stays in the public repository.**
12. **Make it public when you are ready.** At the owner's instruction the repository was pushed to a **private** repository on 2026-11-24. Nothing is public. Finishing items 3 to 11 first is the point of keeping it private.
