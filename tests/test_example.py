"""Tests for the example folder: the kit's slots filled in for a fictional project.

The example is a specification. These tests check that it is complete, that every
test id it cites as proof is real, and that it keeps to the labels and notices the
repository promises. They cannot check that the described build exists, because it
does not.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "example"
KIT = REPO / "kit"
TRAIL = [
    EXAMPLE / "context" / "summary.md",
    EXAMPLE / "context" / "decisions.md",
    EXAMPLE / "context" / "phases" / "phase-0.md",
]
NOTICE_START = "> Illustrative trail:"


def example_files():
    """Every file in the example folder."""
    return sorted(path for path in EXAMPLE.rglob("*") if path.is_file())


def collected_test_ids():
    """The test ids that pytest collects, one per line."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO, capture_output=True, text=True,
    )
    return result.stdout.splitlines()


def ids_cited_in_example():
    """Every pytest id written in the example, as a set."""
    cited = set()
    for path in example_files():
        cited |= set(re.findall(r"tests/\w+\.py::\w+", path.read_text()))
    return cited


def register_rows():
    with open(EXAMPLE / "register.csv", newline="") as handle:
        return list(csv.DictReader(handle))


def test_no_fill_slot_remains_in_the_example():
    for path in example_files():
        assert "<<FILL" not in path.read_text(), str(path.relative_to(REPO))


def test_every_test_id_cited_in_the_example_exists():
    collected = collected_test_ids()
    cited = ids_cited_in_example()
    assert cited, "the example cites no test ids, which is not credible"
    for test_id in sorted(cited):
        found = any(line == test_id or line.startswith(test_id + "[") for line in collected)
        assert found, test_id + " is cited in the example but does not exist"


def test_covered_register_rows_cite_real_tests_and_planned_rows_cite_none():
    collected = collected_test_ids()
    for row in register_rows():
        if row["status"] == "covered":
            assert row["fixture_id"] in collected, row["id"]
        else:
            assert row["status"] == "planned", row["id"]
            assert row["fixture_id"] == "planned", row["id"]


def test_register_uses_the_documented_columns_deciders_and_unique_ids():
    rows = register_rows()
    assert list(rows[0]) == ["id", "scenario", "required_behaviour", "decider", "phase", "fixture_id", "status"]
    assert {row["decider"] for row in rows} <= {"code", "model", "human"}
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))


def test_register_size_is_in_the_planned_range():
    assert 20 <= len(register_rows()) <= 25


def test_register_covers_every_family_of_scenario_the_plan_asks_for():
    text = " ".join(row["scenario"].lower() for row in register_rows())
    for phrase in ("differs", "expires tomorrow", "expires today", "expired yesterday", "twice",
                   "instruction addressed to the model", "skip a check", "unavailable",
                   "conflicts", "resubmits", "their own submission"):
        assert phrase in text, phrase


def test_every_register_row_names_a_decider_and_a_phase():
    for row in register_rows():
        assert row["decider"] and row["phase"] in {"0", "1", "2", "3"}


def test_every_invariant_id_cited_in_the_example_is_defined_in_its_table():
    table = (EXAMPLE / "invariants.md").read_text()
    defined = set(re.findall(r"(?m)^\| (INV-\d+) \|", table))
    for path in example_files():
        for cited in set(re.findall(r"INV-\d+", path.read_text())):
            assert cited in defined, str(path.relative_to(REPO)) + " cites " + cited


def test_the_example_table_keeps_the_kit_invariants_and_adds_its_own():
    kit_text = (KIT / ".claude" / "skills" / "invariants" / "SKILL.md").read_text()
    kit_ids = set(re.findall(r"(?m)^\| (INV-\d+) \|", kit_text))
    example_ids = set(re.findall(r"(?m)^\| (INV-\d+) \|", (EXAMPLE / "invariants.md").read_text()))
    assert kit_ids < example_ids


def test_every_check_in_the_example_invariants_is_marked_demo_or_planned_or_generic():
    table = (EXAMPLE / "invariants.md").read_text()
    rows = [line for line in table.splitlines() if re.match(r"\| INV-\d+ \|", line)]
    generic = {"INV-04", "INV-12"}
    for line in rows:
        invariant = line.split("|")[1].strip()
        if invariant not in generic:
            assert "Demo:" in line or "Planned:" in line, invariant


def test_example_claude_md_names_the_kit_agents_and_skills_that_exist():
    text = (EXAMPLE / "CLAUDE.md").read_text()
    for agent in ("invariant-auditor", "red-team", "fixture-keeper"):
        assert (KIT / ".claude" / "agents" / (agent + ".md")).is_file()
        assert "`" + agent + "`" in text
    for skill in ("invariants", "fixtures-and-harness", "scenario-register", "synthetic-data", "policy-as-data"):
        assert (KIT / ".claude" / "skills" / skill / "SKILL.md").is_file()
        assert "`" + skill + "`" in text


def test_the_example_has_a_phase_owner_for_each_of_four_phases():
    text = (EXAMPLE / "CLAUDE.md").read_text()
    for owner in ("foundations-builder", "policy-engineer", "intake-reader", "approval-screen-builder"):
        assert "`" + owner + "`" in text


def test_example_readme_says_in_its_first_paragraph_that_it_is_the_specification_side_only():
    body = (EXAMPLE / "README.md").read_text().split("\n\n")[1]
    assert "specification side only" in body
    assert "separate repository" in body


def test_every_trail_file_starts_with_the_illustrative_notice():
    for path in TRAIL:
        first_line = path.read_text().splitlines()[0]
        assert first_line.startswith(NOTICE_START), str(path.relative_to(REPO))
        assert "demo/" in first_line


def test_ticked_boxes_in_the_phase_log_carry_a_proof_and_a_label():
    lines = (EXAMPLE / "context" / "phases" / "phase-0.md").read_text().splitlines()
    ticked = [line for line in lines if line.startswith("- [x]")]
    assert ticked
    for line in ticked:
        assert re.search(r"Proof: .+ Label: (executed|read|not-verifiable)", line), line[:80]


def test_the_phase_log_shows_mixed_labels_honestly():
    text = (EXAMPLE / "context" / "phases" / "phase-0.md").read_text()
    assert "Label: executed" in text
    assert "Label: not-verifiable" in text


def test_criteria_marked_not_verifiable_are_not_ticked():
    for line in (EXAMPLE / "context" / "phases" / "phase-0.md").read_text().splitlines():
        if "Label: not-verifiable" in line:
            assert line.startswith("- [ ]"), line[:80]


def test_the_example_pass_bar_is_unsigned():
    text = (EXAMPLE / "acceptance.md").read_text()
    assert re.search(r"(?m)^Signed by:\s*$", text)
    assert not re.search(r"(?m)^Signed by: [^<\s]", text)


def test_the_example_phase_log_records_no_sign_off():
    text = (EXAMPLE / "context" / "phases" / "phase-0.md").read_text()
    assert "| Approved by | not signed |" in text


def test_the_example_summary_is_within_its_line_cap():
    assert len((EXAMPLE / "context" / "summary.md").read_text().splitlines()) <= 120


def test_the_example_claude_md_is_under_the_documented_length_target():
    assert len((EXAMPLE / "CLAUDE.md").read_text().splitlines()) < 200
