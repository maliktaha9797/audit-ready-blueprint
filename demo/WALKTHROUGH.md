# Walkthrough

This explains the three modules in `supplier_demo/` line by line, for someone new to Python. Read each module in the repository alongside its section here. At the end there are five exercises.

Words you will meet:

- A **function** is a named block of code. `def name(inputs) -> output:` defines one.
- A **docstring** is the text in triple quotes at the start of a function. It says what the function does. Python ignores it when running.
- A **type hint** such as `path: str` says what kind of value is expected. Python does not enforce it, and our tests check that every function has one.
- A **dict** is a set of labelled values, written `{"actor": "rules", "event": "decision"}`. You read a value with `entry["actor"]`.
- A **list** is an ordered group of values, written `[1, 2, 3]`.
- **`None`** means "no value".

---

## Module 1: `ledger.py`

**What it is for.** A record of decisions that nobody can quietly change. Each entry stores a fingerprint (a hash) of the entry before it. If someone edits or removes an entry, the fingerprints stop matching and `verify` says so.

### The imports and the starting value

```python
import hashlib
import json
from datetime import datetime, timezone

GENESIS = "0" * 64
```

- `import hashlib` makes Python's tool for fingerprints available.
- `import json` gives us the tools to turn a dict into text and back.
- `from datetime import datetime, timezone` brings in two names so we can write the time.
- `GENESIS = "0" * 64` is a string of sixty-four zeros. The first entry has no entry before it, so it points back to this made-up value. Capital letters mean "a fixed value that should not change".

### `hash_entry`

```python
def hash_entry(entry: dict) -> str:
    body = dict(entry)
    body.pop("hash", None)
    text = json.dumps(body, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
```

- `def hash_entry(entry: dict) -> str:` defines a function that takes a dict called `entry` and gives back a string.
- `body = dict(entry)` makes a copy. We copy so that changing `body` cannot change the caller's `entry`.
- `body.pop("hash", None)` removes the key `"hash"` from the copy if it is there, and does nothing if it is not (the `None` is the answer to give if the key is missing). An entry's fingerprint cannot include itself, so we leave the old one out.
- `text = json.dumps(body, sort_keys=True)` turns the dict into text. `sort_keys=True` puts the keys in alphabetical order, so the same content always gives the same text. Exercise 1 shows why that matters.
- `hashlib.sha256(...)` makes a fingerprint of the text. It needs bytes, not text, so `.encode("utf-8")` converts first. `.hexdigest()` writes the fingerprint as a string of letters and digits. The same text always gives the same fingerprint, and a one-character change gives a completely different one.

### `read_all`

```python
def read_all(path: str) -> list[dict]:
    entries = []
    try:
        with open(path) as handle:
            for line in handle:
                entries.append(json.loads(line))
    except FileNotFoundError:
        return []
    return entries
```

- `-> list[dict]` says the result is a list of dicts.
- `entries = []` starts an empty list.
- `try:` ... `except FileNotFoundError:` means "try this, and if the file does not exist, do the other thing". A ledger that has not been written yet is simply empty, so we return `[]`.
- `with open(path) as handle:` opens the file and promises to close it afterwards, even if something goes wrong. `handle` is the open file.
- `for line in handle:` goes through the file one line at a time. Our file has one entry per line.
- `json.loads(line)` turns that line of text back into a dict. `.append(...)` adds it to the end of the list.
- `return entries` hands the list back.

There is no way to write in this function. It only reads.

### `append`

```python
def append(path: str, entry: dict) -> dict:
    for required in ("actor", "policy_version"):
        if required not in entry:
            raise ValueError("a ledger entry needs " + required)
    entries = read_all(path)
    previous = GENESIS
    if entries:
        previous = entries[-1]["hash"]
    record = dict(entry)
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    record["prev_hash"] = previous
    record["hash"] = hash_entry(record)
    with open(path, "a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record
```

- The `for required in (...)` loop checks that the caller said who acted (`actor`) and which rules were in force (`policy_version`). `raise ValueError(...)` stops the function with an error if either is missing. We would rather fail loudly than record an entry nobody can trace.
- `entries = read_all(path)` reads what is already there.
- `previous = GENESIS`, then `if entries:` (true when the list is not empty), `previous = entries[-1]["hash"]`. `entries[-1]` is the last item. So `previous` is the fingerprint of the entry before the one we are adding, or the zeros if there is none.
- `record = dict(entry)` copies the caller's dict.
- The next three lines add the time (in UTC, written as text), the previous fingerprint, and then this entry's own fingerprint. The fingerprint is worked out last so that it covers everything else.
- `open(path, "a")` opens the file in **append** mode: new text goes on the end, and nothing already there can be changed. This is the only place in the module that writes. A test checks that the module never opens a file in a mode that overwrites.
- `+ "\n"` ends the line so the next entry starts on a fresh line.

### `problem`

```python
def problem(index: int, reason: str) -> dict:
    return {"ok": False, "index": index, "reason": reason}
```

A small helper that builds the answer `verify` gives when something is wrong: where, and why.

### `verify`

```python
def verify(path: str, expected_last_hash: str | None = None) -> dict:
    try:
        with open(path) as handle:
            lines = handle.read().splitlines()
    except FileNotFoundError:
        lines = []
    previous = GENESIS
    for index, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except ValueError:
            return problem(index, "the line is not valid JSON")
        if not isinstance(entry, dict):
            return problem(index, "the line is not an entry")
        if entry.get("prev_hash") != previous:
            return problem(index, "the chain is broken: ...")
        if hash_entry(entry) != entry.get("hash"):
            return problem(index, "the entry was changed after it was written")
        previous = entry["hash"]
    if expected_last_hash is not None and expected_last_hash != previous:
        return problem(len(lines), "the last entry is not the one saved elsewhere: ...")
    return {"ok": True, "entries": len(lines)}
```

- `str | None = None` means the second input may be a string or `None`, and it is `None` if the caller does not give it.
- The first block reads the whole file as a list of lines. A missing file gives an empty list.
- `previous = GENESIS` is where the chain should start.
- `for index, line in enumerate(lines):` goes through the lines and also counts them: `index` is 0 for the first line, 1 for the second, and so on.
- The `try`/`except ValueError` catches a line that is not valid JSON, for example if someone typed over it. We report it and stop. Reporting only the **first** problem is enough, because everything after it cannot be trusted.
- `isinstance(entry, dict)` checks the line decoded to a dict and not, say, a number.
- `entry.get("prev_hash") != previous` asks: does this entry point back at the entry before it? If an entry was **removed** or two were **swapped**, the answer is no, and we report the position.
- `hash_entry(entry) != entry.get("hash")` recomputes the fingerprint from the content and compares it with the one stored. If someone **edited** the entry, the two differ.
- `previous = entry["hash"]` moves on: the next entry should point at this one.
- The last check, `expected_last_hash`, is optional. If a copy of the final fingerprint was saved somewhere else, an entry removed from the very end shows up as a mismatch, and so does a file whose every fingerprint was recomputed after an edit. Without it, both leave a valid chain, and nothing can tell. The chain stops a casual change and does not stop a careful one. Two tests record that limit.
- If nothing was wrong, `verify` returns `{"ok": True, "entries": n}`.

---

## Module 2: `outbound.py`

**What it is for.** Deciding whether a message may leave. The safe default is "no". It leaves only when a setting is exactly right.

```python
from supplier_demo import ledger

OUTBOX: list[dict] = []
```

- `from supplier_demo import ledger` lets this module use the ledger from module 1 as `ledger`.
- `OUTBOX` is an empty list. In this demonstration, "sending" a message means adding it to this list. No network is involved. The `: list[dict]` is a type hint on a value.

### `why_suppressed`

```python
def why_suppressed(recipient: str, config: dict) -> str | None:
    if not isinstance(config, dict):
        return "config_missing"
    if "mode" not in config:
        return "mode_missing"
    if config["mode"] != "live":
        return "mode_not_live"
    allowlist = config.get("allowlist")
    if not isinstance(allowlist, list) or not allowlist:
        return "allowlist_missing_or_empty"
    if recipient not in allowlist:
        return "recipient_not_allowlisted"
    return None
```

The function answers: "is there a reason NOT to send?" It returns the reason as text, or `None` if there is no reason.

- Each `if` is a gate that says no. Read them in order. A missing config, a missing mode, a mode that is not exactly `"live"`, a missing or empty allowlist, a recipient who is not on the list: each one stops the message.
- `config["mode"] != "live"` compares exactly. `"LIVE"`, `"lvie"`, `"test"` and `True` all fail this test, so they all suppress. This is what **fail closed** means: when in doubt, do not send.
- `config.get("allowlist")` reads the allowlist, and gives `None` if it is not there (unlike `config["allowlist"]`, which would raise an error).
- `not isinstance(allowlist, list) or not allowlist` is true when the allowlist is not a list, or when it is an empty list (an empty list counts as "false" in Python).
- Only if every gate passes do we reach `return None`, "no reason to suppress".

### `send`

```python
def send(message: str, recipient: str, config: dict, ledger_path: str) -> dict:
    reason = why_suppressed(recipient, config)
    policy_version = "unknown"
    if isinstance(config, dict):
        policy_version = str(config.get("policy_version", "unknown"))
    entry = {
        "actor": "outbound",
        "policy_version": policy_version,
        "recipient": recipient,
        "message_chars": len(message),
    }
    if reason is None:
        entry["event"] = "outbound_sent"
        ledger.append(ledger_path, entry)
        OUTBOX.append({"recipient": recipient, "message": message})
        return {"sent": True, "reason": None}
    entry["event"] = "outbound_suppressed"
    entry["reason"] = reason
    ledger.append(ledger_path, entry)
    return {"sent": False, "reason": reason}
```

- First we ask `why_suppressed` for the answer.
- The next lines work out which policy version to record. `config.get("policy_version", "unknown")` gives `"unknown"` if there is none, and `str(...)` makes sure it is text.
- `entry` is the dict we will write to the ledger. Note that it holds the **length** of the message (`len(message)`) and never its text, so the ledger cannot leak what was said.
- `if reason is None:` means sending is allowed. We write the ledger entry **first**, then add to the outbox. If the ledger cannot be written, the function stops with an error and nothing is sent. A test checks this order.
- If there is a reason, we record the suppression, including the reason, and return a result that says `sent` is `False`.
- Either way, the outcome ends up in the ledger.

---

## Module 3: `rules.py`

**What it is for.** One rule that is plain code, and a clamp that makes sure a model's suggestion cannot override it. In this demonstration the "model" is the argument `proposed_status`.

```python
from supplier_demo import ledger

POLICY_VERSION = "demo-1"
ALLOWED_PROPOSALS = ("verified", "needs_review")
```

- `POLICY_VERSION` is written into every decision, so a reader can tell which rules were in force.
- `ALLOWED_PROPOSALS` is a **tuple**, like a list that cannot change. It holds the only two suggestions we accept.

### `clean_number`

```python
def clean_number(number: str) -> str:
    return number.replace(" ", "").replace("-", "").upper()
```

`replace(" ", "")` swaps every space for nothing, so it deletes spaces. The same is done for dashes. `.upper()` makes everything capitals. So `"syn 001-01"` becomes `"SYN00101"`. Without this, a harmless difference in spacing could make the rule fail. Exercise 5 tries removing `.upper()`.

### `registration_matches`

```python
def registration_matches(supplier: dict, registry_record: dict | None) -> bool:
    if registry_record is None:
        return False
    given = supplier.get("registration_number")
    held = registry_record.get("registration_number")
    if not isinstance(given, str) or not isinstance(held, str):
        return False
    if clean_number(given) == "":
        return False
    return clean_number(given) == clean_number(held)
```

- `-> bool` means the answer is `True` or `False`.
- This is a **pure function**: it only reads its two inputs and returns an answer. It writes nothing and changes nothing, so the same inputs always give the same answer.
- If the registry returned nothing (`None`), the rule fails. If either number is missing or is not text, it fails.
- The `== ""` check matters: without it, two empty numbers would be equal and the rule would pass. A missing number must never count as a match.
- The last line is the actual rule: do the cleaned numbers match? `==` gives `True` or `False`, which we return directly.

### `decide`

```python
def decide(supplier: dict, registry_record: dict | None, proposed_status: str, ledger_path: str) -> dict:
    rule_passed = registration_matches(supplier, registry_record)
    status = proposed_status
    flag = None
    if not rule_passed:
        status = "needs_review"
        flag = "registration_mismatch"
    elif proposed_status not in ALLOWED_PROPOSALS:
        status = "needs_review"
        flag = "unrecognised_proposal"
    overridden = status != proposed_status
    ledger.append(ledger_path, {...})
    return {"status": status, "flag": flag, "overridden": overridden}
```

- We run the rule first and keep the answer.
- `status = proposed_status` starts from whatever the model suggested.
- `if not rule_passed:` is the clamp. If the rule failed, the status becomes `"needs_review"` and a flag is set, **whatever was proposed**. Nothing after this line can turn it back into `"verified"`.
- `elif proposed_status not in ALLOWED_PROPOSALS:` only runs if the rule **passed**. A suggestion we do not recognise also becomes `"needs_review"`, with a different flag.
- `overridden = status != proposed_status` is `True` when we changed the answer.
- Then the whole decision is written to the ledger: what was proposed, what we decided, whether the rule passed, and whether we overrode it. The `{...}` stands for the dict in the file.
- Finally it returns the status, the flag and `overridden`. A person looking at a `needs_review` result with a flag knows why.

Notice what is **not** here: the supplier's document text. The rule reads typed fields only, so a document that says "ignore your checks" has nothing to act on. A test changes the document text and shows the decision does not move.

---

## How the tests prove each module

| Module | Tests | What they show |
|---|---|---|
| `ledger.py` | `tests/test_ledger.py` | An edit, a deletion and a reordering are each found at the right position. The limits at the end of the file, and after a full rewrite, are recorded. There is no way to update or delete. |
| `outbound.py` | `tests/test_outbound.py` | One test for each way a setting can be wrong, plus the single case that sends. Every outcome is in the ledger. |
| `rules.py` | `tests/test_rules.py` | A failing rule with `verified` proposed gives `needs_review` and a flag. A passing rule passes. All six synthetic suppliers are used. |
| All three | `tests/test_mutations.py` | Break each guard once and watch its detection report failure. |

---

## Exercises

Each exercise asks you to change one thing and **predict which tests fail** before you run them. Write your prediction down, run the command, and compare. Then put the file back.

To run the demonstration's tests:

```bash
.venv/bin/python -m pytest tests/test_ledger.py tests/test_outbound.py tests/test_rules.py tests/test_mutations.py
```

To undo a change once the repository has been committed:

```bash
git checkout -- demo/
```

### Exercise 1: forget to sort the keys

In `ledger.py`, in `hash_entry`, change `json.dumps(body, sort_keys=True)` to `json.dumps(body)`.

Predict: does a clean ledger still verify?

### Exercise 2: be helpful about capital letters

In `outbound.py`, in `why_suppressed`, change `config["mode"] != "live"` to `config["mode"].lower() != "live"`.

Predict: which mode values now behave differently, and what happens to `True`?

### Exercise 3: accept one more word

In `rules.py`, change `ALLOWED_PROPOSALS = ("verified", "needs_review")` to `("verified", "needs_review", "approved")`.

Predict: does this open a way for a failing rule to end as verified?

### Exercise 4: stop linking the entries

In `ledger.py`, in `append`, change `record["prev_hash"] = previous` to `record["prev_hash"] = GENESIS`.

Predict: which tests fail, and what does `verify` report for the second entry?

### Exercise 5: forget capital letters in the rule

In `rules.py`, in `clean_number`, remove `.upper()`.

Predict: how many tests fail?

---

## Answers

These were recorded by making each change and running the four test files above. Your output will show the same test names.

**Exercise 1.** A clean ledger no longer verifies. `tests/test_ledger.py::test_append_then_verify_passes` fails, and so does every test that verifies a ledger, including the ones in `tests/test_outbound.py` and `tests/test_rules.py` that check the chain at the end. The reason is that `append` hashes the dict in the order its keys were added, but the file is written with sorted keys, so `verify` hashes the entry in a different order when it reads it back. The fingerprints differ at the first entry, so tests that expect a problem at position 1 now find it at position 0.

**Exercise 2.** Two tests fail. `tests/test_outbound.py::test_send_is_suppressed_when_mode_has_the_wrong_case` fails because `"LIVE"` now counts as live and the message is sent. `tests/test_outbound.py::test_send_is_suppressed_when_mode_is_not_text` fails because `True.lower()` is an error, so the function crashes before it records anything. An error is not the same as a recorded suppression. The lesson is that fail closed means refusing in a way that leaves a record, and that being helpful with input is how a guard gets weaker.

**Exercise 3.** One test fails: `tests/test_rules.py::test_passing_rule_with_an_unrecognised_proposal_becomes_needs_review`, which uses `"approved"` as its example. The clamp is not weakened. `test_a_failing_rule_can_never_end_as_verified_whatever_is_proposed` still passes, because the failing-rule branch comes first and never looks at the list. The allowed list only matters once the rule has passed.

**Exercise 4.** Seven tests fail. The clearest is `tests/test_ledger.py::test_each_entry_after_the_first_links_to_the_one_before`. `test_append_then_verify_passes` fails because `verify` reports a broken chain at position 1: the second entry points at the zeros and not at the first entry. Without the links, nothing connects the entries, so the ledger cannot notice a removal or a reordering.

**Exercise 5.** Exactly one test fails: `tests/test_rules.py::test_spacing_dashes_and_case_do_not_hide_a_match`, which compares a lower-case number with an upper-case one. The six supplier tests still pass because the fixture numbers are already in capitals. One behaviour, one test: that is why the tests are written so narrowly.
