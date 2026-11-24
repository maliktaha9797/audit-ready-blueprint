# Stories

A story is a short account of one moment when a rule in the kit earned its place. It is written by the owner, from their own experience, and is the evidence that the rules are not theoretical.

This folder holds stubs only. The agent that built the repository did not write the stories and must not: a story is a claim about something that happened, and only the person it happened to can make it.

## The format

One short file per story. Each has four parts, in this order.

| Part | What it says |
|---|---|
| What the agent tried to do | The action, in one or two plain sentences. |
| Why that would have broken a rule | The rule, and what would have followed if it had gone through. |
| What rule or check was added | The change you made, and how you know it works (a test id or a command). |
| Where it lives now | The file in the kit that carries the rule. |

## How to write one

- State facts you can stand behind. Do not invent incidents, outcomes or numbers. If you do not remember, leave that part out and say so.
- Do not name any real employer, client, vendor, person or system. Say "a regulated environment" or "an audited setting".
- Do not include real data, even a fragment, and do not quote a prompt that contained any.
- Keep it short. A story that cannot be read in a minute is two stories.
- When you finish a story, delete its owner marker. The check script counts the markers that remain, and lists them as a publication checklist.

## The stories

| File | Subject |
|---|---|
| [01-real-data.md](01-real-data.md) | A shortcut that would have used real records |
| [02-skipped-check.md](02-skipped-check.md) | A code path that went around a required check |
| [03-gaming-the-test.md](03-gaming-the-test.md) | A detection "fixed" by matching its test, or a flaky test re-run |
| [04-rulebook-drift.md](04-rulebook-drift.md) | Rule files that disagreed as the rule set grew |
