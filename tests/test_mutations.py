"""Mutate-to-red proofs for the demonstration (INV-06).

A detection test is only worth trusting if it can fail. Each detection below is a
small function that answers "did the guard do its job?". For each one, a test:

1. runs it on the real code and checks the answer is True, then
2. breaks the guard with monkeypatch and checks the answer is now False.

If step 2 ever stayed True, the detection would be detecting nothing.
"""
import json
from pathlib import Path

from supplier_demo import ledger, outbound, rules

FIXTURE_FILE = Path(__file__).resolve().parents[1] / "demo" / "fixtures" / "suppliers.json"
GOOD_CONFIG = {"mode": "live", "allowlist": ["buyer@example.test"], "policy_version": "v1"}


# ----------------------------------------------------------------- detections


def tamper_is_detected(folder) -> bool:
    """Edit one entry of a three-entry ledger by hand. True if verify notices."""
    folder.mkdir()
    path = str(folder / "ledger.jsonl")
    for number in (1, 2, 3):
        ledger.append(path, {"actor": "tester", "policy_version": "v1", "number": number})
    lines = Path(path).read_text().splitlines()
    lines[1] = lines[1].replace('"number": 2', '"number": 99')
    Path(path).write_text("\n".join(lines) + "\n")
    return ledger.verify(path)["ok"] is False


def send_without_mode_is_suppressed(folder) -> bool:
    """Try to send to an allowlisted recipient with no mode set. True if nothing is sent."""
    folder.mkdir()
    outbound.OUTBOX.clear()
    config = dict(GOOD_CONFIG)
    del config["mode"]
    result = outbound.send("Hello", "buyer@example.test", config, str(folder / "ledger.jsonl"))
    return result["sent"] is False and outbound.OUTBOX == []


def send_to_a_stranger_is_suppressed(folder) -> bool:
    """Try to send in live mode to a recipient who is not listed. True if nothing is sent."""
    folder.mkdir()
    outbound.OUTBOX.clear()
    result = outbound.send("Hello", "stranger@example.test", GOOD_CONFIG, str(folder / "ledger.jsonl"))
    return result["sent"] is False and outbound.OUTBOX == []


def clamp_holds(folder) -> bool:
    """Propose "verified" for a supplier whose rule fails. True if the result is not verified and is flagged."""
    folder.mkdir()
    suppliers = json.loads(FIXTURE_FILE.read_text())
    supplier = suppliers[1]
    assert supplier["scenario"] == "registration_number_mismatch"
    result = rules.decide(supplier, supplier["registry_record"], "verified", str(folder / "ledger.jsonl"))
    return result["status"] != "verified" and result["flag"] is not None


# ------------------------------------------------------------------ mutations


def test_tamper_detection_fails_when_verify_always_reports_clean(tmp_path, monkeypatch):
    assert tamper_is_detected(tmp_path / "real") is True

    def always_clean(path, expected_last_hash=None):
        return {"ok": True, "entries": 0}

    monkeypatch.setattr(ledger, "verify", always_clean)
    assert tamper_is_detected(tmp_path / "broken") is False


def test_tamper_detection_fails_when_the_hash_ignores_the_content(tmp_path, monkeypatch):
    assert tamper_is_detected(tmp_path / "real") is True

    def same_hash_every_time(entry):
        return "the-same-hash"

    monkeypatch.setattr(ledger, "hash_entry", same_hash_every_time)
    assert tamper_is_detected(tmp_path / "broken") is False


def test_fail_closed_detection_fails_when_send_ignores_the_mode(tmp_path, monkeypatch):
    assert send_without_mode_is_suppressed(tmp_path / "real") is True

    def checks_only_the_allowlist(recipient, config):
        if recipient in config.get("allowlist", []):
            return None
        return "recipient_not_allowlisted"

    monkeypatch.setattr(outbound, "why_suppressed", checks_only_the_allowlist)
    assert send_without_mode_is_suppressed(tmp_path / "broken") is False


def test_fail_closed_detection_fails_when_send_ignores_the_allowlist(tmp_path, monkeypatch):
    assert send_to_a_stranger_is_suppressed(tmp_path / "real") is True

    def checks_only_the_mode(recipient, config):
        if config.get("mode") == "live":
            return None
        return "mode_not_live"

    monkeypatch.setattr(outbound, "why_suppressed", checks_only_the_mode)
    assert send_to_a_stranger_is_suppressed(tmp_path / "broken") is False


def test_clamp_detection_fails_when_decide_trusts_the_proposal(tmp_path, monkeypatch):
    assert clamp_holds(tmp_path / "real") is True

    def trusts_the_proposal(supplier, registry_record, proposed_status, ledger_path):
        return {"status": proposed_status, "flag": None, "overridden": False}

    monkeypatch.setattr(rules, "decide", trusts_the_proposal)
    assert clamp_holds(tmp_path / "broken") is False


def test_clamp_detection_fails_when_the_rule_always_passes(tmp_path, monkeypatch):
    assert clamp_holds(tmp_path / "real") is True

    def always_passes(supplier, registry_record):
        return True

    monkeypatch.setattr(rules, "registration_matches", always_passes)
    assert clamp_holds(tmp_path / "broken") is False
