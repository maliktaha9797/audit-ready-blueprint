"""Tests for fail-closed outbound sending (INV-09).

The rule: a message is sent only when the mode is exactly "live" and the
recipient is on the allowlist. Every other case suppresses it and records why.
"""
import pytest

from supplier_demo import ledger, outbound

GOOD = {"mode": "live", "allowlist": ["buyer@example.test"], "policy_version": "v1"}
RECIPIENT = "buyer@example.test"


@pytest.fixture(autouse=True)
def empty_outbox():
    """Start and finish every test with nothing in the outbox."""
    outbound.OUTBOX.clear()
    yield
    outbound.OUTBOX.clear()


def config_without(key):
    """Return the good config with one key removed."""
    config = dict(GOOD)
    del config[key]
    return config


def config_with(**changes):
    """Return the good config with some values changed."""
    config = dict(GOOD)
    config.update(changes)
    return config


def assert_suppressed(tmp_path, config, reason, recipient=RECIPIENT):
    """Send once and check that it was suppressed for the expected reason."""
    path = str(tmp_path / "ledger.jsonl")
    result = outbound.send("Hello", recipient, config, path)
    assert result == {"sent": False, "reason": reason}
    assert outbound.OUTBOX == []
    entries = ledger.read_all(path)
    assert len(entries) == 1
    assert entries[0]["event"] == "outbound_suppressed"
    assert entries[0]["reason"] == reason


def test_message_is_sent_only_in_live_mode_to_an_allowlisted_recipient(tmp_path):
    path = str(tmp_path / "ledger.jsonl")
    result = outbound.send("Hello", RECIPIENT, GOOD, path)
    assert result == {"sent": True, "reason": None}
    assert outbound.OUTBOX == [{"recipient": RECIPIENT, "message": "Hello"}]
    assert ledger.read_all(path)[0]["event"] == "outbound_sent"


def test_send_is_suppressed_when_mode_is_missing(tmp_path):
    assert_suppressed(tmp_path, config_without("mode"), "mode_missing")


def test_send_is_suppressed_when_mode_is_unknown(tmp_path):
    assert_suppressed(tmp_path, config_with(mode="test"), "mode_not_live")


def test_send_is_suppressed_when_mode_is_misspelt(tmp_path):
    assert_suppressed(tmp_path, config_with(mode="lvie"), "mode_not_live")


def test_send_is_suppressed_when_mode_has_the_wrong_case(tmp_path):
    assert_suppressed(tmp_path, config_with(mode="LIVE"), "mode_not_live")


def test_send_is_suppressed_when_mode_is_not_text(tmp_path):
    assert_suppressed(tmp_path, config_with(mode=True), "mode_not_live")


def test_send_is_suppressed_when_the_allowlist_is_missing(tmp_path):
    assert_suppressed(tmp_path, config_without("allowlist"), "allowlist_missing_or_empty")


def test_send_is_suppressed_when_the_allowlist_is_empty(tmp_path):
    assert_suppressed(tmp_path, config_with(allowlist=[]), "allowlist_missing_or_empty")


def test_send_is_suppressed_when_the_recipient_is_not_on_the_allowlist(tmp_path):
    assert_suppressed(tmp_path, GOOD, "recipient_not_allowlisted", recipient="stranger@example.test")


def test_send_is_suppressed_when_the_config_is_missing(tmp_path):
    assert_suppressed(tmp_path, None, "config_missing")


def test_the_ledger_records_a_sent_message_without_its_text(tmp_path):
    path = str(tmp_path / "ledger.jsonl")
    outbound.send("A private sentence", RECIPIENT, GOOD, path)
    entry = ledger.read_all(path)[0]
    assert entry["message_chars"] == len("A private sentence")
    assert "A private sentence" not in open(path).read()


def test_the_ledger_stays_valid_after_a_mix_of_sent_and_suppressed_messages(tmp_path):
    path = str(tmp_path / "ledger.jsonl")
    outbound.send("one", RECIPIENT, GOOD, path)
    outbound.send("two", RECIPIENT, config_with(mode="lvie"), path)
    outbound.send("three", "stranger@example.test", GOOD, path)
    assert ledger.verify(path) == {"ok": True, "entries": 3}


def test_nothing_is_sent_if_the_ledger_cannot_be_written(tmp_path):
    missing_folder = str(tmp_path / "no_such_folder" / "ledger.jsonl")
    with pytest.raises(FileNotFoundError):
        outbound.send("Hello", RECIPIENT, GOOD, missing_folder)
    assert outbound.OUTBOX == []
