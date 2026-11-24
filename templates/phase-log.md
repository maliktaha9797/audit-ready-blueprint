<!-- What it is: the record of one phase of work, from scope to sign-off, with proof for every exit criterion. -->
<!-- When to create it: at the start of each phase, with the exit criteria copied in unchecked. -->
<!-- Where it goes: .claude/context/phases/phase-<n>.md. Fill it in as the phase runs, and close it at the human gate. -->

# Phase <<FILL: number>>: <<FILL: name>>

## Scope

<<FILL: what this phase builds, and what it leaves out>>

Register rows in scope: <<FILL: scenario ids from register.csv, or "none">>

## Exit criteria

Tick a box only when the proof has been run. Each line records the proof and one label: **executed** (run, result recorded), **read** (inspected, not run) or **not-verifiable** (cannot be checked here, with the reason).

- [ ] <<FILL: criterion>>. Proof: <<FILL: test id or command, and the recorded result>>. Label: <<FILL: executed, read or not-verifiable>>.

## Slices

Small pieces of work. Each ends with the test that proves it. A ticked slice carries a proof and a label, like an exit criterion.

- [ ] <<FILL: slice>>. Proof: <<FILL: test id>>. Label: <<FILL: executed, read or not-verifiable>>.

## Gate results

| Check | Command or reviewer | Result | Label |
|---|---|---|---|
| Regression suite | <<FILL: command>> | <<FILL: summary line>> | <<FILL: label>> |
| Invariant audit | the auditor agent | <<FILL: verdict on each invariant>> | <<FILL: label>> |
| Red team (if an untrusted input surface changed) | the red-team agent | <<FILL: result>> | <<FILL: label>> |

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
