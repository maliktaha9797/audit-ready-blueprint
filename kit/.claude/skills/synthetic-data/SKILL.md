---
name: synthetic-data
description: How to build and use invented records so no real personal or customer data enters the build. Covers inventing realistic records, marking them as synthetic, seeding throwaway local databases, and what to do when someone offers a real export. Use whenever you need test data, fixtures or seed data.
---

# Synthetic data

## Purpose

In an audited setting, one real record in a fixture, a log or a prompt is a breach, however good the reason. The build uses invented data only. This skill says how to make invented data good enough to test with, and how to make sure it can never be mistaken for real data.

## When to use

- You need a fixture, a seed file or a sample document.
- Someone offers a data export, a screenshot or a "small sample" to test with.
- You are about to put a record into a prompt.

## The rule

There is no real personal or customer data anywhere in the build: not in the repository, not in fixtures, not in logs, not in a model call. This is INV-01. It is enforced by a permission rule and a hook that block the real-data path, and by the checks in the invariants skill.

## How to invent realistic records

- **Names:** use obviously fictional names and organisations. A name that could belong to a real person or business is not acceptable. Prefer a pattern that is plainly invented, such as a made-up word plus a common suffix.
- **Contact details:** use reserved ranges. For email use the reserved test domains `example.test` or `example.com`. For UK mobile numbers use the range reserved for fiction, `07700 900000` to `07700 900999`.
- **Identifiers:** use a prefix that real identifiers never use, such as `SYN-`, followed by digits. Where a format check is part of the test, build ids that pass the format but start with the prefix.
- **Dates:** generate them relative to a fixed "today" in the test, so boundaries (the day before, the day of, the day after) stay stable.
- **Variety:** include the awkward cases the register lists: missing fields, duplicates, near-duplicates, expired items, mismatches, and text that tries to instruct the model.
- **Volume:** keep fixtures small. A handful of records, each chosen to exercise one scenario, beats a large random set.

## Mark every synthetic record

Every record carries a marker that survives copying:

- a field `"synthetic": true`,
- an id with the `SYN-` prefix,
- a file name or folder that says `synthetic` or `fixtures`.

A record that lacks the marker is treated as possibly real. The check for INV-01 looks for it.

## Throwaway local databases

When a test needs a database:

1. Create it in a temporary folder, never in a shared location.
2. Seed it from the fixture files only.
3. Delete it when the test finishes. Do not keep a copy.
4. Do not point it at, or copy from, any live system.

## If someone offers a real export

Decline, politely and without opening it. Then:

1. Do not read, copy, summarise or describe the file.
2. Record the offer in `.claude/context/open-questions.md`: who offered, what it was meant for, and that it was declined.
3. Offer an invented equivalent that exercises the same scenarios, and add the scenarios to the register.
4. If the real shape matters (field names, formats), ask the owner for a description of the shape, never the data.

## Checklist

- [ ] Every record has the synthetic marker.
- [ ] Contact details use reserved ranges.
- [ ] No fixture sits under a real-data path.
- [ ] Any database is temporary and seeded from fixtures.
- [ ] Nothing real was pasted into a prompt.

## Common mistakes

| Mistake | Why it is wrong | Correct approach |
|---|---|---|
| Using a real name "with the details changed" | Changed details can still identify someone | Invent the name from scratch |
| A fixture copied from a sample someone sent | It may be real | Decline it and invent an equivalent |
| Keeping a seeded database between runs | It can drift into holding something real | Create it fresh and delete it |
| Marking only some records | Unmarked records look real | Mark every record |
