"""One hard rule and its clamp.

Serves INV-07: hard rules are code, and a model output cannot override a
failing rule. In this demonstration the "model" is just the argument
proposed_status. Whatever it proposes, a failing rule can never end as verified.
"""
from supplier_demo import ledger

POLICY_VERSION = "demo-1"
ALLOWED_PROPOSALS = ("verified", "needs_review")


def clean_number(number: str) -> str:
    """Return a registration number in capitals, with spaces and dashes removed.

    Serves INV-07: the rule compares cleaned values, so spacing cannot hide a match.
    """
    return number.replace(" ", "").replace("-", "").upper()


def registration_matches(supplier: dict, registry_record: dict | None) -> bool:
    """Return True only if the registry holds the registration number the supplier gave.

    A pure function: it reads its two arguments and changes nothing. A missing
    record, a missing number or an empty number all give False.
    Serves INV-07.
    """
    if registry_record is None:
        return False
    given = supplier.get("registration_number")
    held = registry_record.get("registration_number")
    if not isinstance(given, str) or not isinstance(held, str):
        return False
    if clean_number(given) == "":
        return False
    return clean_number(given) == clean_number(held)


def decide(supplier: dict, registry_record: dict | None, proposed_status: str, ledger_path: str) -> dict:
    """Return the final status for a supplier, whatever the model proposed.

    If the rule fails, the status is "needs_review" and a flag is raised, even if
    the proposal was "verified". If the proposal is not one we recognise, the
    status is also "needs_review". Every decision is written to the ledger,
    including whether the proposal was overridden.
    Serves INV-07, and INV-10 (the decision is recorded).
    """
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
    ledger.append(ledger_path, {
        "actor": "rules",
        "policy_version": POLICY_VERSION,
        "event": "rule_decision",
        "supplier_id": supplier.get("id"),
        "proposed": proposed_status,
        "final": status,
        "rule_passed": rule_passed,
        "flag": flag,
        "overridden": overridden,
    })
    return {"status": status, "flag": flag, "overridden": overridden}
