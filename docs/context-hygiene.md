# Context hygiene

Context files are what lets a new session pick up where the last one stopped. They are also the part of a setup most likely to rot, because nothing forces them to stay small.

## Why context files grow without limit

Every session adds a line. Nothing removes one. A decision log gains an entry per decision, a summary gains a bullet per piece of work, and a patterns file gains a note per surprise. Each addition is reasonable, and the sum is not.

Three things follow.

1. **The first file read gets longer.** The summary is read at the start of every session. A long summary spends the session's attention on history, and the current state is buried in it.
2. **Old and new contradict.** An old entry says one thing, a later one says another, and a reader cannot tell which holds unless the file says so.
3. **Rewriting becomes tempting.** When a file is hard to read, the quick fix is to tidy it. In an audited setting, tidying a log destroys the record that the log exists to keep.

The answer is a small number of rules that keep the files short without rewriting history.

## The caps

| File | Rule |
|---|---|
| `summary.md` | At most 120 lines. It holds the current state and pointers. It is read first and updated last. A check script fails if it is longer. |
| `decisions.md` | Append-only, and holds the current period only. |
| Phase logs | One file per phase. Appended to while the phase is open, and never rewritten after the gate is signed. |
| `patterns.md` | Append-only. Entries are short. |
| `open-questions.md` | Entries are never deleted. Their status changes. |

## The archive rule

At the end of each month, move that month's entries from `decisions.md` to `archive/decisions-YYYY-MM.md`.

- Moving an entry copies it unchanged. The text is identical, and the date and author are kept.
- Nothing is edited, merged or summarised on the way. A summary of an old decision is a new document and goes in `summary.md`, not in the archive.
- The decision log keeps a one-line pointer to each archive file.

## What belongs where

| Belongs in `summary.md` | Belongs in a log |
|---|---|
| What is built and what is in progress | How it was built, step by step |
| What is blocked, and a pointer to why | The reasoning, the alternatives and the evidence |
| The next few steps | Every session's notes |
| The key decisions, one line each, with a pointer | The full text of each decision |
| Links to the files that hold detail | The detail |

A useful test: if a line would still be true and useful in a month, it may belong in the summary. If it describes what happened in one session, it belongs in the phase log.

## What never goes in a context file

Real data, secrets, and the contents of files that the permission rules protect. The context files are read by every session and committed to the repository.
