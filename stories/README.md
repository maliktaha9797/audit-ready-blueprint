# Stories

A story is a short account of one moment when a rule in the kit earned its place. It is written by the owner, from their own experience, and is the evidence that the rules are not theoretical.

All four stories were drafted by the agent that built the repository, at the owner's instruction on 2026-11-25, from the real record of that build: the build brief, the independent audits, the test results and the commit history. They describe what the agent did and what the checks caught in this build. They are not accounts of earlier work, and they are not the owner's experience until the owner has read them, corrected them and decided to publish them as their own. Each carries a review marker until then.

Story 01 is not about testing against real records, because that did not happen in this build: the agent never reached for real records. It is about the closest real event, real names nearly entering the repository, and it says so at the top. If the owner has a real episode of the first kind, it should replace the draft. A story is a claim about something that happened, and a draft that invented one would be worse than a stub.

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
- When you finish a story, or finish reviewing a draft, delete its owner marker. The check script counts the markers that remain, and lists them as a publication checklist.

## The stories

| File | Subject |
|---|---|
| [01-real-data.md](01-real-data.md) | Real names that nearly entered the repository: the closest real event, not a real-records episode (draft) |
| [02-skipped-check.md](02-skipped-check.md) | A check that passed when its input was missing (draft) |
| [03-gaming-the-test.md](03-gaming-the-test.md) | A test that could not fail, which is the same problem seen from the test's side (draft) |
| [04-rulebook-drift.md](04-rulebook-drift.md) | Rule files that disagreed as the rule set grew (draft) |
