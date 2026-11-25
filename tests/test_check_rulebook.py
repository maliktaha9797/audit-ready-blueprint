"""Tests for scripts/check_rulebook.py.

Each test builds a small temporary repository that is clean except for one fault,
and asserts that the script fails for exactly that reason. One test builds a clean
repository and asserts that the script passes. A last test runs the script over
this repository.
"""
import os
import subprocess
from pathlib import Path

import pytest

import check_rulebook

REPO = Path(__file__).resolve().parents[1]
EM_DASH = chr(0x2014)
SLOT = "<<" + "FILL: something>>"
OWNER_A = "<!-- " + "OWNER: write this section yourself. Prompt: a prompt -->"
OWNER_B = "<<" + "OWNER: link to the other repository>>"

CLEAN = {
    "README.md": "# Title\n\nSee [the guide](docs/guide.md) and `tests/test_sample.py::test_sample_passes`.\n",
    "docs/guide.md": "# Guide\n\nPlain text.\n",
    "tests/test_sample.py": "def test_sample_passes():\n    pass\n",
    "scripts/banned_terms.txt": "# local list\nZorblax\nXYZ\n",
    "kit/CLAUDE.md": (
        "# Kit\n\n## Agents\n\n| Agent | Purpose |\n|---|---|\n| `helper` | Helps. |\n\n"
        "## Skills\n\n| Skill | Purpose |\n|---|---|\n| `invariants` | The table. |\n\n"
        "## Commands\n\n| Command | Purpose |\n|---|---|\n| `/go` | Goes. |\n\n"
        "## DO NOT\n\n- Break it. (INV-01)\n"
    ),
    "kit/.claude/agents/helper.md": "---\nname: helper\ndescription: Helps.\nskills:\n  - invariants\n---\n\n# Helper\n",
    "kit/.claude/skills/invariants/SKILL.md": "---\nname: invariants\ndescription: The table.\n---\n\n| ID | Invariant |\n|---|---|\n| INV-01 | It holds. |\n",
    "kit/.claude/skills/go/SKILL.md": "---\nname: go\ndescription: Goes.\ndisable-model-invocation: true\n---\n\nFollow `.claude/workflow-docs/flow.md`.\n",
    "kit/.claude/workflow-docs/flow.md": "# Flow\n",
    "kit/.claude/context/summary.md": "# Summary\n",
    "example/invariants.md": "| ID | Invariant |\n|---|---|\n| INV-01 | It holds. |\n| INV-13 | A project rule. |\n",
}


def build(root, extra=None, remove=()):
    """Write the clean repository into root, then add or replace some files and remove others."""
    files = dict(CLEAN)
    files.update(extra or {})
    for name in remove:
        files.pop(name, None)
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


def failed_checks(root, env=None):
    """The sorted names of the checks that failed."""
    failures, _, _ = check_rulebook.run_checks(root, env or {})
    return sorted({item["check"] for item in failures})


def test_clean_directory_passes(tmp_path):
    failures, warnings, stubs = check_rulebook.run_checks(build(tmp_path), {})
    assert failures == []
    assert warnings == []
    assert stubs == []


# ---------------------------------------------------------------- banned terms


def test_banned_term_fails(tmp_path):
    root = build(tmp_path, {"docs/leak.md": "This mentions zorblax in passing.\n"})
    assert failed_checks(root) == ["banned-terms"]


def test_banned_term_in_a_file_name_fails(tmp_path):
    root = build(tmp_path, {"docs/zorblax-notes.md": "Plain text.\n"})
    assert failed_checks(root) == ["banned-terms"]


def test_longer_banned_term_matches_inside_another_word(tmp_path):
    root = build(tmp_path, {"docs/leak.md": "The Zorblaxes arrived.\n"})
    assert failed_checks(root) == ["banned-terms"]


def test_banned_term_of_four_characters_or_fewer_matches_whole_words_only(tmp_path):
    inside = build(tmp_path / "inside", {"docs/ok.md": "The XYZZY system.\n"})
    assert failed_checks(inside) == []
    whole = build(tmp_path / "whole", {"docs/leak.md": "The XYZ team.\n"})
    assert failed_checks(whole) == ["banned-terms"]


def test_the_banned_terms_file_itself_is_not_scanned(tmp_path):
    root = build(tmp_path)
    assert "Zorblax" in (root / "scripts" / "banned_terms.txt").read_text()
    assert failed_checks(root) == []


def test_banned_terms_are_read_from_the_environment_when_the_file_is_absent(tmp_path):
    root = build(tmp_path, {"docs/leak.md": "This mentions zorblax.\n"}, remove=["scripts/banned_terms.txt"])
    assert failed_checks(root, {"BANNED_TERMS": "Zorblax\n"}) == ["banned-terms"]


def test_banned_terms_check_is_skipped_with_a_warning_when_there_is_no_list(tmp_path):
    root = build(tmp_path, {"docs/leak.md": "This mentions zorblax.\n"}, remove=["scripts/banned_terms.txt"])
    failures, warnings, _ = check_rulebook.run_checks(root, {})
    assert failures == []
    assert any("skipped" in warning for warning in warnings)


# ---------------------------------------------------------------------- style


def test_em_dash_fails(tmp_path):
    root = build(tmp_path, {"docs/dash.md": "A phrase " + EM_DASH + " with a dash.\n"})
    assert failed_checks(root) == ["em-dash"]


def test_prose_count_of_invariants_fails(tmp_path):
    root = build(tmp_path, {"docs/count.md": "There are 12 invariants in the table.\n"})
    assert failed_checks(root) == ["prose-count"]


def test_prose_count_of_rules_fails(tmp_path):
    root = build(tmp_path, {"docs/count.md": "The seven rules apply.\n"})
    assert failed_checks(root) == ["prose-count"]


def test_a_count_of_something_else_is_allowed(tmp_path):
    root = build(tmp_path, {"docs/count.md": "There are 12 tests and 3 files.\n"})
    assert failed_checks(root) == []


# ------------------------------------------------------------------ references


def test_unknown_command_reference_fails(tmp_path):
    root = build(tmp_path, {"kit/.claude/workflow-docs/flow.md": "# Flow\n\nRun `/nothere` first.\n"})
    assert failed_checks(root) == ["reference-integrity"]


def test_unknown_workflow_reference_fails(tmp_path):
    root = build(tmp_path, {"kit/.claude/skills/go/SKILL.md": CLEAN["kit/.claude/skills/go/SKILL.md"] + "See `.claude/workflow-docs/missing.md`.\n"})
    assert failed_checks(root) == ["reference-integrity"]


def test_unknown_skill_reference_fails(tmp_path):
    root = build(tmp_path, {"kit/.claude/workflow-docs/flow.md": "# Flow\n\nRead `.claude/skills/missing/SKILL.md`.\n"})
    assert failed_checks(root) == ["reference-integrity"]


def test_unknown_agent_reference_fails(tmp_path):
    root = build(tmp_path, {"kit/.claude/workflow-docs/flow.md": "# Flow\n\nCall `.claude/agents/missing.md`.\n"})
    assert failed_checks(root) == ["reference-integrity"]


def test_claude_md_table_naming_a_missing_agent_fails(tmp_path):
    text = CLEAN["kit/CLAUDE.md"].replace("| `helper` | Helps. |", "| `ghost` | Haunts. |")
    assert failed_checks(build(tmp_path, {"kit/CLAUDE.md": text})) == ["reference-integrity"]


def test_agent_that_preloads_a_missing_skill_fails(tmp_path):
    text = CLEAN["kit/.claude/agents/helper.md"].replace("  - invariants", "  - phantom")
    assert failed_checks(build(tmp_path, {"kit/.claude/agents/helper.md": text})) == ["reference-integrity"]


def test_undefined_invariant_id_fails(tmp_path):
    root = build(tmp_path, {"docs/cites.md": "This relies on INV-77.\n"})
    assert failed_checks(root) == ["reference-integrity"]


def test_example_file_must_cite_ids_from_the_example_table(tmp_path):
    root = build(tmp_path, {"example/notes.md": "This cites INV-13 and INV-99.\n"})
    assert failed_checks(root) == ["reference-integrity"]


def test_example_file_may_cite_an_id_that_only_the_example_defines(tmp_path):
    root = build(tmp_path, {"example/notes.md": "This cites INV-13.\n"})
    assert failed_checks(root) == []


# ------------------------------------------------------------------ proof ids


def test_cited_test_id_that_does_not_exist_fails(tmp_path):
    root = build(tmp_path, {"docs/proof.md": "Proof: `tests/test_sample.py::test_missing`.\n"})
    assert failed_checks(root) == ["proof-integrity"]


def test_cited_test_file_that_does_not_exist_fails(tmp_path):
    root = build(tmp_path, {"example/proof.md": "Proof: `tests/test_nowhere.py::test_x`.\n"})
    assert failed_checks(root) == ["proof-integrity"]


def test_cited_test_id_that_exists_passes(tmp_path):
    root = build(tmp_path, {"docs/proof.md": "Proof: `tests/test_sample.py::test_sample_passes`.\n"})
    assert failed_checks(root) == []


def test_a_parametrised_id_is_checked_by_its_function_name(tmp_path):
    root = build(tmp_path, {"docs/proof.md": "Proof: `tests/test_sample.py::test_sample_passes[case_one]`.\n"})
    assert failed_checks(root) == []


def test_a_missing_test_id_cited_in_the_stories_or_the_case_study_fails(tmp_path):
    story = build(tmp_path / "a", {"stories/02.md": "Proof: `tests/test_sample.py::test_missing`.\n"})
    assert failed_checks(story) == ["proof-integrity"]
    case = build(tmp_path / "b", {"CASE-STUDY.md": "Proof: `tests/test_sample.py::test_missing`.\n"})
    assert failed_checks(case) == ["proof-integrity"]


def test_generic_sample_ids_in_the_kit_are_not_checked(tmp_path):
    root = build(tmp_path, {"kit/.claude/context/patterns.md": "Sample: `tests/test_sample.py::test_made_up`.\n"})
    assert failed_checks(root) == []


# ----------------------------------------------------------------------- links


def test_broken_relative_link_fails(tmp_path):
    root = build(tmp_path, {"docs/links.md": "See [nothing](missing.md).\n"})
    assert failed_checks(root) == ["links"]


def test_links_to_the_web_and_to_anchors_pass(tmp_path):
    text = "See [site](https://example.test/page), [mail](mailto:a@example.test) and [top](#top).\n"
    assert failed_checks(build(tmp_path, {"docs/links.md": text})) == []


def test_link_with_a_fragment_resolves_to_its_file(tmp_path):
    assert failed_checks(build(tmp_path, {"docs/links.md": "See [guide](guide.md#section).\n"})) == []


def test_link_inside_a_code_fence_is_ignored(tmp_path):
    text = "```\n[example](does-not-exist.md)\n```\n"
    assert failed_checks(build(tmp_path, {"docs/links.md": text})) == []


# ------------------------------------------------------------------- size caps


def test_summary_over_the_cap_fails(tmp_path):
    root = build(tmp_path, {"example/summary.md": "line\n" * (check_rulebook.SUMMARY_CAP + 1)})
    assert failed_checks(root) == ["size-cap"]


def test_summary_exactly_at_the_cap_passes(tmp_path):
    root = build(tmp_path, {"kit/.claude/context/summary.md": "line\n" * check_rulebook.SUMMARY_CAP})
    assert failed_checks(root) == []


# ----------------------------------------------------------------------- slots


def test_fill_slot_outside_kit_and_templates_fails(tmp_path):
    root = build(tmp_path, {"docs/slot.md": "A name: " + SLOT + "\n"})
    assert failed_checks(root) == ["slots"]


def test_fill_slot_inside_the_kit_passes(tmp_path):
    root = build(tmp_path, {"kit/.claude/context/patterns.md": "A name: " + SLOT + "\n"})
    assert failed_checks(root) == []


def test_fill_slot_inside_templates_passes(tmp_path):
    root = build(tmp_path, {"templates/note.md": "A name: " + SLOT + "\n"})
    assert failed_checks(root) == []


def test_a_python_file_may_name_the_slot_marker(tmp_path):
    root = build(tmp_path, {"tests/helper.py": 'MARKER = "' + SLOT + '"\n'})
    assert failed_checks(root) == []


# --------------------------------------------------------------------- history


def commit(root, email, message="initial", branch=None, committer_email=None):
    """Make a git repository of root with one commit. The committer defaults to the author."""
    git = ["git", "-c", "commit.gpgsign=false", "-c", "user.name=Tester", "-c", "user.email=" + email]
    env = dict(os.environ)
    if committer_email:
        env["GIT_COMMITTER_EMAIL"] = committer_email
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(git + ["commit", "-q", "-m", message], cwd=root, check=True, capture_output=True, env=env)
    if branch:
        subprocess.run(["git", "branch", branch], cwd=root, check=True, capture_output=True)
    return root


def test_a_clean_history_gives_no_warning(tmp_path):
    root = commit(build(tmp_path), "person@example.test")
    failures, warnings, _ = check_rulebook.run_checks(root, {})
    assert failures == [] and warnings == []


def test_a_banned_term_in_a_commit_email_is_a_warning_by_default(tmp_path):
    root = commit(build(tmp_path), "person@zorblax.example")
    failures, warnings, _ = check_rulebook.run_checks(root, {})
    assert failures == []
    assert any(warning.startswith("history:") for warning in warnings)


def test_the_history_warning_never_prints_the_term(tmp_path):
    root = commit(build(tmp_path), "person@zorblax.example")
    _, warnings, _ = check_rulebook.run_checks(root, {})
    assert "zorblax" not in " ".join(warnings).lower()
    assert "entry 1" in " ".join(warnings)


def test_a_banned_term_in_a_commit_message_is_found(tmp_path):
    root = commit(build(tmp_path), "person@example.test", message="Work for Zorblax")
    _, warnings, _ = check_rulebook.run_checks(root, {})
    assert any(warning.startswith("history:") for warning in warnings)


def test_a_banned_term_in_a_branch_name_is_found(tmp_path):
    root = commit(build(tmp_path), "person@example.test", branch="zorblax-work")
    _, warnings, _ = check_rulebook.run_checks(root, {})
    assert any(warning.startswith("history:") for warning in warnings)


def test_strict_history_turns_the_warning_into_a_failure(tmp_path):
    root = commit(build(tmp_path), "person@zorblax.example")
    failures, warnings, _ = check_rulebook.run_checks(root, {}, strict_history=True)
    assert sorted({item["check"] for item in failures}) == ["history"]
    assert not any(warning.startswith("history:") for warning in warnings)


def test_the_exit_code_follows_the_strict_history_flag(tmp_path):
    root = commit(build(tmp_path), "person@zorblax.example")
    assert check_rulebook.main(["--root", str(root)]) == 0
    assert check_rulebook.main(["--root", str(root), "--strict-history"]) == 1


def test_a_long_term_matches_in_history_and_a_short_term_needs_a_whole_word(tmp_path):
    inside = commit(build(tmp_path / "inside"), "person@example.test", message="The XYZZY system")
    assert check_rulebook.run_checks(inside, {}, strict_history=True)[0] == []
    whole = commit(build(tmp_path / "whole"), "person@example.test", message="The XYZ team")
    assert check_rulebook.run_checks(whole, {}, strict_history=True)[0] != []


def test_prose_count_of_the_form_n_of_the_kits_invariants_fails(tmp_path):
    root = build(tmp_path, {"docs/count.md": "It proves three of the kit's invariants.\n"})
    assert failed_checks(root) == ["prose-count"]


def test_a_banned_term_in_the_committer_email_alone_is_found(tmp_path):
    root = commit(build(tmp_path), "person@example.test", committer_email="person@zorblax.example")
    _, warnings, _ = check_rulebook.run_checks(root, {})
    assert any(warning.startswith("history:") for warning in warnings)


def test_a_banned_term_in_the_author_email_alone_is_found(tmp_path):
    root = commit(build(tmp_path), "person@zorblax.example", committer_email="person@example.test")
    _, warnings, _ = check_rulebook.run_checks(root, {})
    assert any(warning.startswith("history:") for warning in warnings)


def test_strict_history_fails_when_there_is_no_banned_list_to_check_against(tmp_path):
    root = commit(build(tmp_path, remove=["scripts/banned_terms.txt"]), "person@zorblax.example")
    assert check_rulebook.main(["--root", str(root), "--strict-history"]) == 1
    assert check_rulebook.main(["--root", str(root)]) == 0


@pytest.mark.parametrize("phrase", ["sixteen invariants", "a dozen rules", "thirteen rules", "fifty invariants", "100 rules"])
def test_larger_counts_written_in_prose_fail(tmp_path, phrase):
    root = build(tmp_path, {"docs/count.md": "There are " + phrase + " in total.\n"})
    assert failed_checks(root) == ["prose-count"]


def test_a_stray_placeholder_that_is_not_the_fill_marker_fails(tmp_path):
    root = build(tmp_path, {"docs/report.md": "Result: <<" + "RESULT>>\n"})
    assert failed_checks(root) == ["slots"]


# ----------------------------------------------------------------- owner stubs


def test_owner_stubs_are_counted_as_warnings_and_do_not_fail(tmp_path):
    root = build(tmp_path, {"CASE-STUDY.md": "# Draft\n\n" + OWNER_A + "\n", "docs/more.md": "Link: " + OWNER_B + "\n"})
    failures, _, stubs = check_rulebook.run_checks(root, {})
    assert failures == []
    assert len(stubs) == 2
    assert stubs[0].startswith("CASE-STUDY.md:3") or stubs[1].startswith("CASE-STUDY.md:3")


# ------------------------------------------------------------ exit code and use


def test_exit_code_is_non_zero_on_a_failure_and_zero_on_a_clean_directory(tmp_path):
    clean = build(tmp_path / "clean")
    assert check_rulebook.main(["--root", str(clean)]) == 0
    broken = build(tmp_path / "broken", {"docs/dash.md": "A " + EM_DASH + " dash.\n"})
    assert check_rulebook.main(["--root", str(broken)]) == 1


def test_each_failure_names_its_check_and_its_location(tmp_path):
    root = build(tmp_path, {"docs/dash.md": "A " + EM_DASH + " dash.\n"})
    failures, _, _ = check_rulebook.run_checks(root, {})
    assert failures[0]["check"] == "em-dash"
    assert failures[0]["where"].startswith("docs/dash.md:")
    assert failures[0]["message"]


def test_the_output_lists_each_failure_with_its_check_name(tmp_path, capsys):
    root = build(tmp_path, {"docs/dash.md": "A " + EM_DASH + " dash.\n"})
    check_rulebook.main(["--root", str(root)])
    assert "FAIL [em-dash] docs/dash.md:1" in capsys.readouterr().out


def test_this_repository_passes_its_own_checks():
    failures, _, _ = check_rulebook.run_checks(REPO, os.environ)
    assert failures == [], failures[:3]
