# Policy change

## Overview

How a business rule held as data is changed. Versions are append-only, and a change applies to new cases only. The owner signs before the new version becomes active.

**Started by:** `/policy-change <policy id and summary>`

## Prerequisites

- The `policy-as-data` skill has been read.
- The change is a business rule held as data. If it is a guardrail on the agent, use `/rule-change` instead.

## Steps

1. **Write the new version** as a new file, for example `policies/<policy-id>.v<n+1>.json`, with `supersedes` set to the current version. Do not edit the current file.
2. **Add a pending entry to the decision log** in this form:

   ```
   ### <date>: policy <policy-id> v<n+1> proposed

   - **Decision:** pending
   - **Why:** <the reason for the change>
   - **Supersedes:** policy <policy-id> v<n>
   - **Decided by:** pending owner sign-off
   ```

3. **List the register rows the change affects.** Search the register for the policy id and the fields it covers. Add a row for any case the new version creates.
4. **Run the regression** with the new version selected. It must be green. Record the summary line and label it executed.
5. **If the rule cannot be expressed as data,** stop. Record an engine gap in `open-questions.md`. Do not hardcode the rule.
6. **Ask the owner to sign.** Show the diff between the versions, the affected rows and the regression result. Wait.
7. **On sign-off,** append a new decision-log entry that records the owner's name and the date and says the pending entry is now decided. Do not edit the pending entry.
8. **Make the version active for new cases only.** Cases already decided keep the version they used.

## Completion criteria

- [ ] The new version is a new file and the old file is untouched.
- [ ] The affected register rows are listed.
- [ ] The regression is green with the new version.
- [ ] The owner's sign-off is in the decision log.
- [ ] The version is active for new cases only.

## Context to update

| File | What to add |
|---|---|
| `.claude/context/decisions.md` | The pending entry, then the sign-off entry |
| `.claude/context/register.csv` | New or changed rows |
| `.claude/context/open-questions.md` | An engine gap, if one was found |
