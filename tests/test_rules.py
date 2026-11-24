"""Tests for the hard rule and its clamp (INV-07), using the synthetic suppliers.

The "model" is the proposed_status argument. These tests show that no proposal
can turn a failing rule into a pass.
"""
import copy
import json
from pathlib import Path

import pytest

from supplier_demo import ledger, rules

FIXTURE_FILE = Path(__file__).resolve().parents[1] / "demo" / "fixtures" / "suppliers.json"
SCENARIOS = [
    "clean_file",
    "registration_number_mismatch",
    "expired_insurance",
    "bank_details_in_a_different_company_name",
    "document_containing_an_instruction_for_the_model",
    "duplicate_submission",
]


def load_suppliers():
    """Return the synthetic suppliers as a dict keyed by scenario name."""
    suppliers = json.loads(FIXTURE_FILE.read_text())
    return {supplier["scenario"]: supplier for supplier in suppliers}


def ledger_path(tmp_path):
    """Return the path of a ledger file that does not exist yet."""
    return str(tmp_path / "ledger.jsonl")


# ------------------------------------------------------------------ fixtures


def test_fixtures_cover_all_six_scenarios():
    assert sorted(load_suppliers()) == sorted(SCENARIOS)


def test_every_fixture_supplier_is_marked_synthetic():
    for supplier in load_suppliers().values():
        assert supplier["synthetic"] is True
        assert supplier["id"].startswith("SYN-")
        assert supplier["registry_record"]["synthetic"] is True


# -------------------------------------------------------- registration_matches


def test_matching_registration_numbers_pass():
    supplier = load_suppliers()["clean_file"]
    assert rules.registration_matches(supplier, supplier["registry_record"]) is True


def test_a_different_registration_number_fails():
    supplier = load_suppliers()["registration_number_mismatch"]
    assert rules.registration_matches(supplier, supplier["registry_record"]) is False


def test_spacing_dashes_and_case_do_not_hide_a_match():
    supplier = {"registration_number": "syn 001-01"}
    record = {"registration_number": "SYN00101"}
    assert rules.registration_matches(supplier, record) is True


def test_a_missing_registry_record_fails():
    supplier = load_suppliers()["clean_file"]
    assert rules.registration_matches(supplier, None) is False


def test_an_empty_registration_number_fails_even_if_both_are_empty():
    assert rules.registration_matches({"registration_number": ""}, {"registration_number": ""}) is False


def test_a_missing_registration_number_fails():
    assert rules.registration_matches({}, {"registration_number": "SYN00101"}) is False


def test_the_rule_does_not_change_its_inputs():
    supplier = load_suppliers()["clean_file"]
    record = supplier["registry_record"]
    before = copy.deepcopy((supplier, record))
    rules.registration_matches(supplier, record)
    assert (supplier, record) == before


@pytest.mark.parametrize("scenario, expected", [
    pytest.param("clean_file", True, id="clean_file"),
    pytest.param("registration_number_mismatch", False, id="registration_number_mismatch"),
    pytest.param("expired_insurance", True, id="expired_insurance_registration_is_fine"),
    pytest.param("bank_details_in_a_different_company_name", True, id="bank_name_registration_is_fine"),
    pytest.param("document_containing_an_instruction_for_the_model", True, id="instruction_in_document"),
    pytest.param("duplicate_submission", True, id="duplicate_submission"),
])
def test_registration_rule_result_for_each_synthetic_supplier(scenario, expected):
    supplier = load_suppliers()[scenario]
    assert rules.registration_matches(supplier, supplier["registry_record"]) is expected


# ---------------------------------------------------------------------- decide


def test_failing_rule_with_proposed_verified_gives_needs_review_and_a_flag(tmp_path):
    supplier = load_suppliers()["registration_number_mismatch"]
    result = rules.decide(supplier, supplier["registry_record"], "verified", ledger_path(tmp_path))
    assert result == {"status": "needs_review", "flag": "registration_mismatch", "overridden": True}


def test_failing_rule_with_a_safe_proposal_is_still_flagged(tmp_path):
    supplier = load_suppliers()["registration_number_mismatch"]
    result = rules.decide(supplier, supplier["registry_record"], "needs_review", ledger_path(tmp_path))
    assert result == {"status": "needs_review", "flag": "registration_mismatch", "overridden": False}


def test_a_failing_rule_can_never_end_as_verified_whatever_is_proposed(tmp_path):
    supplier = load_suppliers()["registration_number_mismatch"]
    path = ledger_path(tmp_path)
    for proposal in ("verified", "VERIFIED", "approved", "", None, ["verified"]):
        result = rules.decide(supplier, supplier["registry_record"], proposal, path)
        assert result["status"] == "needs_review"
        assert result["flag"] is not None


def test_passing_rule_lets_a_verified_proposal_through(tmp_path):
    supplier = load_suppliers()["clean_file"]
    result = rules.decide(supplier, supplier["registry_record"], "verified", ledger_path(tmp_path))
    assert result == {"status": "verified", "flag": None, "overridden": False}


def test_passing_rule_with_an_unrecognised_proposal_becomes_needs_review(tmp_path):
    supplier = load_suppliers()["clean_file"]
    result = rules.decide(supplier, supplier["registry_record"], "approved", ledger_path(tmp_path))
    assert result == {"status": "needs_review", "flag": "unrecognised_proposal", "overridden": True}


def test_document_text_never_changes_the_decision(tmp_path):
    supplier = load_suppliers()["document_containing_an_instruction_for_the_model"]
    changed = copy.deepcopy(supplier)
    changed["document_text"] = "A perfectly ordinary certificate."
    path = ledger_path(tmp_path)
    with_instruction = rules.decide(supplier, supplier["registry_record"], "needs_review", path)
    without = rules.decide(changed, changed["registry_record"], "needs_review", path)
    assert with_instruction == without


def test_every_decision_is_recorded_in_the_ledger_with_the_override(tmp_path):
    supplier = load_suppliers()["registration_number_mismatch"]
    path = ledger_path(tmp_path)
    rules.decide(supplier, supplier["registry_record"], "verified", path)
    entry = ledger.read_all(path)[0]
    assert entry["event"] == "rule_decision"
    assert entry["supplier_id"] == supplier["id"]
    assert entry["proposed"] == "verified"
    assert entry["final"] == "needs_review"
    assert entry["overridden"] is True
    assert entry["policy_version"] == rules.POLICY_VERSION
    assert ledger.verify(path)["ok"] is True
