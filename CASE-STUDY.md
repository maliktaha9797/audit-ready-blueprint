# Case study: setting up Claude Code for audited work

**DRAFT.** Sections 1 to 3 describe the method as it appears in this repository, and the owner is to review them. Section 4 is for the owner to write from their own experience. Section 5 was drafted by the agent that built the repository, at the owner's instruction on 2026-11-25, from the record of that build, and the owner is to review it. Nothing in this file describes a past project, and the file must not be published until the markers are gone.

---

## 1. The constraint

Software built in an audited setting has to meet a different test from software built anywhere else. It is not enough that it works. A person who was not in the room has to be able to establish, after the fact, what the software did, why it did it, under which rules, and who was accountable.

In general terms, an audited environment asks the following of the work.

1. **Traceability.** Every decision can be traced to a rule that was in force at the time, and to a person or a named role who owns that rule.
2. **Evidence.** A claim that something was checked comes with the check: a command that was run, the result, and when. Reading code and believing it is correct does not count.
3. **Separation of duties.** The party that builds is not the party that approves, and the party that checks cannot alter what it checks.
4. **Change control.** The rules themselves change only through a recorded process with an approver, so a rule cannot be loosened to make a check pass.
5. **Protection of real data.** Personal and customer data does not enter the build, the test fixtures or any prompt, because once it is there it cannot be taken back.

An AI agent that writes and changes software makes these harder, not easier. It works fast, it can edit its own instructions, and when it is wrong it is often wrong with confidence. A setup that relies on asking the agent to behave gives an auditor nothing to inspect. The constraint is therefore that good behaviour must be enforced where it can be, and evidenced where it cannot.

## 2. Spec before build

The method puts the specification first, so that the work can be checked against something other than the agent's own account of it. Three pieces of it appear in this repository.

**The governing sentence.** A single sentence that every design decision can be tested against. It states what software decides, what the model may do, and what a person must approve. For the fictional example, it is: software performs every check that can be written as a rule; the model only reads documents and drafts judgments that are always flagged; no supplier is activated until a named person approves the file. If the sentence cannot settle a design question, it is not finished. The guide to writing one is in [kit/CLAUDE.md](kit/CLAUDE.md).

**The scenario register.** A list of the situations the system must handle, each with the behaviour required, who decides (code, a model or a person), and the test that proves it. A scenario is registered and its test is written, and seen to fail, before the fix. The format and a checker are in [the scenario-register skill](kit/.claude/skills/scenario-register/SKILL.md). A worked register for the fictional project is in [example/register.csv](example/register.csv), and it marks plainly which rows a test covers and which are only planned.

**A phased plan with proof per phase.** Each phase has exit criteria, each criterion names the test id or command that proves it, and each phase ends at a human gate that a named person signs. The plan is the highest authority: when a rule file and the plan disagree, the plan wins and the rule file is corrected with a decision-log entry. The worked plan is [example/plan.md](example/plan.md). Its phase log shows mixed labels honestly, because most of the project is a plan and only a small part of it runs ([example/context/phases/phase-0.md](example/context/phases/phase-0.md)).

Every verification is labelled executed, read or not-verifiable. The labels exist so that a reader can see at a glance what was run, what was only inspected, and what could not be checked at all.

## 3. Two layers of guardrails

There are two different things to constrain, and they need different guardrails.

**Rules on the agent that builds.** These govern what Claude Code may do while it writes the software.

- Permission rules deny reading secrets and real-data paths, writing to the approvals folder, and destructive or publishing commands. The permission system enforces them.
- Hooks run before a file edit and before a shell command. They block writes to the rulebook unless a person has approved the change, block commands that mention a production host or a secret, and log every successful tool call and every blocked attempt, without file contents. They fail closed: if their configuration is missing or unreadable, they block. See [kit/README.md](kit/README.md).
- An auditor agent runs the check for each invariant and returns a verdict. It has no edit or write tool and cannot clear its own blocks.
- A rule-change workflow lets the agent propose a change to its own rules and then stop. A person approves by creating a file that the agent is not permitted to write. The agent applies exactly what was approved. See [the workflow](kit/.claude/workflow-docs/rule-change.md).

**Rules on the system being built.** These govern what the finished software does, whoever or whatever wrote it. The demonstration shows three.

- Hard rules are code, and a model output cannot override a failing rule ([demo/supplier_demo/rules.py](demo/supplier_demo/rules.py)).
- Outbound actions fail closed: a message is sent only when a setting is exactly right, and every other case is suppressed and recorded ([demo/supplier_demo/outbound.py](demo/supplier_demo/outbound.py)).
- The decision record is append-only, and an edit, removal or reordering is found ([demo/supplier_demo/ledger.py](demo/supplier_demo/ledger.py)).

The two layers share one discipline. Each guardrail has a check that can be run, and each check has been shown, once, to be capable of failing. A check that has never failed has not been shown to detect anything.

The limits are stated in the kit. Hooks and deny rules raise the cost of breaking a rule and leave evidence. They are not a security boundary against a determined user with shell access, and an agent that has the shell tool can still change files through it.

## 4. What I stopped the agent from doing, and why

<!-- OWNER: write this section yourself. Prompt: Describe two or three specific things you stopped an agent from doing while building audited software, and why each would have broken a rule. For each, say which file in the kit now carries the rule. Use only facts you can stand behind. Do not name any real employer, client, vendor, person or system. -->

## 5. What went wrong

<!-- OWNER: review this draft, which the agent wrote from the build record, correct anything you cannot stand behind, and delete this marker when you are content to publish it. -->

Drafted by the agent that built this repository, from the record of that build: two independent audits by a separate read-only agent, the test results and the commit history. It describes this build, not earlier work.

Building this repository with an agent, under the rules it describes, did not go cleanly. The places it went wrong are the best evidence that the rules are needed.

**The guards were weaker than their documentation said.** The first audit returned BLOCK on the invariants for secrets and for the rulebook. The shell guard allowed `echo $API_KEY`, `export -p` and `cat /proc/self/environ`. A command that changed directory first, such as `cd .claude && sed -i ... settings.json`, wrote to a protected file. Several files that set gates and the pass bar were not protected at all. The documents said otherwise. The guard was widened, the protected set was extended, and tests were added for each route. Blocked attempts, which had left no record, are now logged.

**Checks the builder published were defective.** The command that checks every ticked criterion for a proof and a label printed wrongly when copied from its table, because a table forces an escaped pipe. The script that checks the scenario register accepted a test id that was only the start of a real one. Both were rewritten, and tests now run each exactly as published.

**Documents claimed more than the code did.** One said every tool call was logged, when only successful calls were. Another said the agent could not approve its own change, when a shell route to the approvals folder existed. They were corrected to state the limits, and tests record the limits that remain.

**A clean result could hide a gap.** The check for banned terms looked at files and not at commit author names, messages or branch names, and its strict mode passed when there was no list to check against. A history scan was added, and strict mode now fails without a list. See [the story](stories/02-skipped-check.md).

**Tests that could not fail.** One test would have stayed green if the code it guarded were removed, and a mutation of the logging code stayed green against a test written to catch it. See [the story](stories/03-gaming-the-test.md).

**Rule files that disagreed.** A count written in prose, a recorded test total that went stale, a template that contradicted its own check, and several lists of what the rulebook is. See [the story](stories/04-rulebook-drift.md).

How the changes are known to work: each has a test, and `python scripts/mutate_kit.py` breaks the guards and checks one at a time and confirms that the tests go red.

**What is still open.** The shell guard matches text, so a glob, a path built at run time or a program it does not know gets past it, and a test records this. The owner recorded decisions that accept this limit for the secrets and rulebook invariants, and that accept the list of mutations as not exhaustive. A sandbox or an allowlist of shell commands would close the gap, and neither was built. Nothing in the build ran inside an interactive Claude Code session, so the live behaviour of the hooks and deny rules has not been checked. The last round of changes was checked by the builder and not re-audited independently.
