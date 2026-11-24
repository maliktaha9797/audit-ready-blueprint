"""An append-only decision record, stored as JSON lines.

Serves INV-10: the decision record is append-only. Nothing in this module
updates or deletes an entry. Each entry holds the hash of the entry before it,
so an edit, a removal or a reordering breaks the chain, and verify() finds it.
"""
import hashlib
import json
from datetime import datetime, timezone

GENESIS = "0" * 64


def hash_entry(entry: dict) -> str:
    """Return the SHA-256 hash of an entry, leaving out its own hash field.

    Serves INV-10: the hash is what makes an edit visible.
    """
    body = dict(entry)
    body.pop("hash", None)
    text = json.dumps(body, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_all(path: str) -> list[dict]:
    """Return every entry in the file, oldest first. A missing file is an empty record.

    Serves INV-10: reading never changes the record.
    """
    entries = []
    try:
        with open(path) as handle:
            for line in handle:
                entries.append(json.loads(line))
    except FileNotFoundError:
        return []
    return entries


def append(path: str, entry: dict) -> dict:
    """Add one entry to the end of the record and return it as stored.

    The caller gives an actor and a policy_version. This function adds the
    timestamp, the hash of the previous entry, and the entry's own hash.
    Serves INV-10: this is the only function that writes to the record.
    """
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


def problem(index: int, reason: str) -> dict:
    """Build the result that verify() returns when it finds something wrong.

    Serves INV-10: the result names the first bad position and says why.
    """
    return {"ok": False, "index": index, "reason": reason}


def verify(path: str, expected_last_hash: str | None = None) -> dict:
    """Recompute the hash chain. Report the first problem, or that the record is clean.

    Returns {"ok": True, "entries": n} or {"ok": False, "index": i, "reason": text}.
    Serves INV-10: an edited, removed or reordered entry is found here.

    An entry removed from the END leaves a valid chain, so the file alone cannot
    show it. Save the last hash somewhere else and pass it as expected_last_hash
    to catch that case too.
    """
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
            return problem(index, "the chain is broken: an earlier entry was removed, moved or changed")
        if hash_entry(entry) != entry.get("hash"):
            return problem(index, "the entry was changed after it was written")
        previous = entry["hash"]
    if expected_last_hash is not None and expected_last_hash != previous:
        return problem(len(lines), "the record ends earlier than expected")
    return {"ok": True, "entries": len(lines)}
