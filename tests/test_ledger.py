"""Tests for the append-only ledger (INV-10).

Each test writes a small ledger in a temporary folder. Where a test damages the
file on purpose, it does so with plain text edits, the way a person with a text
editor could.
"""
import json
from pathlib import Path

from supplier_demo import ledger


def new_ledger(tmp_path):
    """Return the path of a ledger file that does not exist yet."""
    return str(tmp_path / "ledger.jsonl")


def write_three(path):
    """Append three entries numbered 1, 2 and 3."""
    for number in (1, 2, 3):
        ledger.append(path, {"actor": "tester", "policy_version": "v1", "event": "step", "number": number})


def read_lines(path):
    """Return the file as a list of lines."""
    return Path(path).read_text().splitlines()


def write_lines(path, lines):
    """Replace the file with the given lines."""
    Path(path).write_text("\n".join(lines) + "\n")


def test_append_then_verify_passes(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    assert ledger.verify(path) == {"ok": True, "entries": 3}


def test_first_entry_links_to_the_genesis_hash(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    assert ledger.read_all(path)[0]["prev_hash"] == ledger.GENESIS


def test_each_entry_after_the_first_links_to_the_one_before(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    entries = ledger.read_all(path)
    assert entries[1]["prev_hash"] == entries[0]["hash"]
    assert entries[2]["prev_hash"] == entries[1]["hash"]


def test_entry_records_timestamp_actor_policy_version_and_previous_hash(tmp_path):
    path = new_ledger(tmp_path)
    stored = ledger.append(path, {"actor": "tester", "policy_version": "v7", "event": "step"})
    for key in ("timestamp", "actor", "policy_version", "prev_hash", "hash"):
        assert stored[key]
    assert stored["policy_version"] == "v7"


def test_append_without_an_actor_is_refused(tmp_path):
    path = new_ledger(tmp_path)
    try:
        ledger.append(path, {"policy_version": "v1"})
    except ValueError as error:
        assert "actor" in str(error)
    else:
        raise AssertionError("append accepted an entry with no actor")
    assert ledger.read_all(path) == []


def test_append_without_a_policy_version_is_refused(tmp_path):
    path = new_ledger(tmp_path)
    try:
        ledger.append(path, {"actor": "tester"})
    except ValueError as error:
        assert "policy_version" in str(error)
    else:
        raise AssertionError("append accepted an entry with no policy version")


def test_read_all_returns_entries_in_order(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    assert [entry["number"] for entry in ledger.read_all(path)] == [1, 2, 3]


def test_a_missing_ledger_reads_as_empty_and_verifies_clean(tmp_path):
    path = new_ledger(tmp_path)
    assert ledger.read_all(path) == []
    assert ledger.verify(path) == {"ok": True, "entries": 0}


def test_editing_an_entry_is_detected(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    lines = read_lines(path)
    lines[1] = lines[1].replace('"number": 2', '"number": 99')
    write_lines(path, lines)
    result = ledger.verify(path)
    assert result["ok"] is False
    assert result["index"] == 1
    assert "changed" in result["reason"]


def test_deleting_an_entry_is_detected(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    lines = read_lines(path)
    del lines[1]
    write_lines(path, lines)
    result = ledger.verify(path)
    assert result["ok"] is False
    assert result["index"] == 1
    assert "chain is broken" in result["reason"]


def test_reordering_entries_is_detected(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    lines = read_lines(path)
    lines[1], lines[2] = lines[2], lines[1]
    write_lines(path, lines)
    result = ledger.verify(path)
    assert result["ok"] is False
    assert result["index"] == 1


def test_an_edit_with_a_recomputed_hash_is_still_detected_at_the_next_entry(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    lines = read_lines(path)
    edited = json.loads(lines[0])
    edited["number"] = 99
    edited["hash"] = ledger.hash_entry(edited)
    lines[0] = json.dumps(edited, sort_keys=True)
    write_lines(path, lines)
    result = ledger.verify(path)
    assert result["ok"] is False
    assert result["index"] == 1


def test_a_line_that_is_not_json_is_detected(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    lines = read_lines(path)
    lines[2] = "this line is not json"
    write_lines(path, lines)
    result = ledger.verify(path)
    assert result["ok"] is False
    assert result["index"] == 2


def test_removing_the_last_entry_is_not_detected_without_an_anchor(tmp_path):
    """A known limit, tested so it is written down: the chain of the remaining entries is valid."""
    path = new_ledger(tmp_path)
    write_three(path)
    write_lines(path, read_lines(path)[:2])
    assert ledger.verify(path)["ok"] is True


def test_removing_the_last_entry_is_detected_with_an_anchor(tmp_path):
    path = new_ledger(tmp_path)
    write_three(path)
    saved_elsewhere = ledger.read_all(path)[-1]["hash"]
    write_lines(path, read_lines(path)[:2])
    result = ledger.verify(path, expected_last_hash=saved_elsewhere)
    assert result["ok"] is False
    assert "ends earlier" in result["reason"]


def test_ledger_offers_no_way_to_update_or_delete(tmp_path):
    names = [name.lower() for name in dir(ledger)]
    for word in ("update", "delete", "remove", "rewrite", "overwrite", "truncate"):
        for name in names:
            assert word not in name, name + " would let a caller change the record"
    source = Path(ledger.__file__).read_text()
    assert 'open(path, "a")' in source
    assert '"w"' not in source and '"r+"' not in source
