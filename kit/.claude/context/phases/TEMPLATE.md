# Phase <<FILL: number>>: <<FILL: name>>

Copy this file to `phase-<n>.md` when a phase starts. Fill it in as the phase runs and close it at the human gate. Do not edit the template when copying.

## Scope

<<FILL: what this phase builds, and what it leaves out>>

Previous gate commit: <<FILL: commit id, or "none" for the first phase>>

Register rows in scope: <<FILL: scenario ids from register.csv, or "none">>

## Exit criteria

Tick a box only when the proof has been run. Each ticked line must contain `Proof:` and `Label:`, in that order. The label is one of: **executed** (run, result recorded), **read** (inspected, not run) or **not-verifiable** (cannot be checked here, with the reason).

- [ ] <<FILL: criterion>>. Proof: <<FILL: test id or command, and the recorded result>>. Label: <<FILL: executed, read or not-verifiable>>.

## Slices

Small pieces of work. Each ends with the test that proves it.

- [ ] <<FILL: slice>>. Proof: <<FILL: test id>>.

## Gate results

| Check | Command or reviewer | Result | Label |
|---|---|---|---|
| Regression suite | `/regress` | <<FILL: summary line>> | <<FILL: label>> |
| Register check | `python3 scripts/check_register.py` | <<FILL: result>> | <<FILL: label>> |
| Invariant audit | the `invariant-auditor` agent, called by `/gate` | <<FILL: paste the audit, with a verdict on each invariant>> | <<FILL: label>> |
| Red team, if an untrusted input surface changed | the `red-team` agent | <<FILL: result>> | <<FILL: label>> |

## Session notes

<<FILL: dated notes. Append only.>>

## Human gate sign-off

| Field | Value |
|---|---|
| Gate required by the plan | <<FILL: yes or no>> |
| Approved by | <<FILL: name>> |
| Date | <<FILL: date>> |
| Conditions | <<FILL: any conditions, or "none">> |

## Handoff notes

<<FILL: what the next session or phase needs to know, in a few lines>>
