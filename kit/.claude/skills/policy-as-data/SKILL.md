---
name: policy-as-data
description: How to keep business rules in versioned configuration and not in engine code, so a rule can change without a code change and every decision cites the version it used. Use when adding or changing a business rule, threshold, window or list, or when a rule seems impossible to express as data.
---

# Policy as data

## Purpose

A business rule that is buried in code can only be changed by a developer, and nobody can say which version of it made a past decision. Keeping rules as data fixes both problems. The engine stays small and stable. The rules change through a controlled, recorded process.

## When to use

- You are adding a threshold, window, list, mapping or limit.
- A rule is about to be written as an `if` statement with a business number in it.
- A request says "change the rule so that..."

## Principles

1. **Rules are data.** Thresholds, windows, lists and mappings live in versioned configuration files, not in engine code.
2. **Versions are append-only.** A change creates a new version. An old version is never edited or deleted, because past decisions cite it.
3. **A change applies to new cases only.** Cases already decided keep the version they were decided under. A decision records the version it used.
4. **The engine only evaluates.** It reads a version, applies it to typed fields, and returns a result. It contains no business number.
5. **If a rule cannot be expressed as data, that is an engine gap.** Raise it. Do not hardcode the rule to get past it. Record the gap in `open-questions.md` and let the owner decide how to extend the engine.

## A policy file

```json
{
  "policy_id": "document-validity",
  "version": 3,
  "effective_from": "2026-01-01",
  "supersedes": 2,
  "rules": [
    {"id": "min-days-remaining", "field": "expiry_date", "min_days": 30},
    {"id": "accepted-types", "field": "document_type", "allowed": ["type-a", "type-b"]}
  ],
  "approved_by": "sample owner (synthetic)"
}
```

Each version is a separate file, for example `policies/document-validity.v3.json`. Version 3 does not replace the file for version 2.

## Changing a policy

Follow `.claude/workflow-docs/policy-change.md`. In short: write the new version, add a pending entry to the decision log, list the register rows it affects, run the regression suite, get the owner's sign-off, then make it active for new cases.

A policy file is not part of the rulebook that needs a rule change, because it is business data and not a guardrail on the agent. If the project decides that policy files are protected, add them to `protected_paths` in `guard.json` through the rule-change process.

## Checklist

- [ ] No business number appears in engine code.
- [ ] The new version is a new file, and the old file is untouched.
- [ ] A decision records the policy version it used.
- [ ] The regression suite passed before the version became active.
- [ ] The owner signed the change.

## Common mistakes

| Mistake | Why it is wrong | Correct approach |
|---|---|---|
| Editing version 2 to make version 3 | Past decisions now cite a changed rule | Add a new file |
| Re-deciding old cases under the new version | It rewrites history | Apply the change to new cases only |
| Hardcoding a rule the data format cannot hold | The rule is now invisible to reviewers | Raise an engine gap |
| A decision that does not record the version | It cannot be explained later | Record the version in every decision |
