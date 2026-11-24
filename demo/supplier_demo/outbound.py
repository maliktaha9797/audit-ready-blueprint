"""Sending a message to a supplier, failing closed.

Serves INV-09: outbound actions fail closed. A message is sent only when the
mode is exactly "live" AND the recipient is on the allowlist. In every other
case, including a missing, unknown or misspelt setting, the message is
suppressed and the suppression is written to the ledger.

"Sending" here only adds to an in-memory list called OUTBOX. There is no
network code in this demonstration.
"""
from supplier_demo import ledger

OUTBOX: list[dict] = []


def why_suppressed(recipient: str, config: dict) -> str | None:
    """Return the reason a message must not be sent, or None if sending is allowed.

    Every check answers "no" unless the setting is present and exactly right.
    Serves INV-09.
    """
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


def send(message: str, recipient: str, config: dict, ledger_path: str) -> dict:
    """Send the message only if every condition holds. Otherwise suppress it and record why.

    The ledger entry is written BEFORE anything is sent. If the ledger cannot be
    written, this function raises and nothing is sent. The message text is never
    stored in the ledger, only its length.
    Serves INV-09 (fail closed) and INV-10 (the outcome is recorded either way).
    """
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
