"""Tests for the repository-level promises: scaffolding, CI, licence and front door.

These read files. They do not run the CI workflow, which only GitHub can do.
"""
import re
import subprocess
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def tracked_or_new_files():
    """Files that git tracks or would track, as relative paths."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return [name for name in out if (REPO / name).is_file()]


def test_ci_runs_the_tests_and_the_rulebook_check_on_push_and_pull_request():
    text = (REPO / ".github" / "workflows" / "ci.yml").read_text()
    assert re.search(r"(?m)^on:\n  push:\n  pull_request:", text)
    assert "python -m pytest" in text
    assert "python scripts/check_rulebook.py" in text
    assert '"3.12"' in text


def test_ci_passes_the_private_banned_terms_in_as_a_secret_and_never_hard_codes_them():
    text = (REPO / ".github" / "workflows" / "ci.yml").read_text()
    assert "secrets.BANNED_TERMS" in text
    assert "banned_terms.txt" not in text


def test_ci_installs_nothing_but_pytest():
    text = (REPO / ".github" / "workflows" / "ci.yml").read_text()
    installs = re.findall(r"pip install (.+)", text)
    assert installs == ["pytest"]


def test_pyproject_requires_python_3_12_and_depends_on_nothing_but_pytest_for_development():
    data = tomllib.loads((REPO / "pyproject.toml").read_text())
    assert data["project"]["requires-python"] == ">=3.12"
    assert data["project"]["dependencies"] == []
    assert data["dependency-groups"]["dev"] == ["pytest"]
    assert data["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]


def test_gitignore_keeps_private_and_generated_files_out_of_the_repository():
    lines = (REPO / ".gitignore").read_text().splitlines()
    for needed in ("BLUEPRINT_REPO_BUILD_PLAN.md", "source/", "scripts/banned_terms.txt",
                   "kit/.claude/context/audit/", ".venv/", ".env", ".env.*", "*.pem", "*.key"):
        assert needed in lines, needed


def test_the_private_files_are_not_tracked_or_staged():
    files = tracked_or_new_files()
    assert "BLUEPRINT_REPO_BUILD_PLAN.md" not in files
    assert "scripts/banned_terms.txt" not in files
    assert not any(name.startswith("source/") for name in files)


def test_the_banned_terms_example_is_committed_and_says_its_terms_are_fictional():
    text = (REPO / "scripts" / "banned_terms.example.txt").read_text()
    assert "Example Employer Ltd" in text
    assert "fictional" in text


def test_licence_is_mit_with_a_named_holder_and_no_placeholder():
    text = (REPO / "LICENSE").read_text()
    assert text.startswith("MIT License")
    assert re.search(r"Copyright \(c\) 20\d\d \S+", text)
    assert "<<" not in text


def test_the_directory_tree_has_every_top_level_part_of_the_plan():
    for name in ("README.md", "BLUEPRINT.md", "CASE-STUDY.md", "LICENSE", "pyproject.toml", ".gitignore",
                 "docs", "templates", "kit", "example", "demo", "tests", "scripts", "stories",
                 ".github/workflows/ci.yml", "BUILD-REPORT.md"):
        assert (REPO / name).exists(), name


def test_every_doc_the_plan_names_exists():
    for name in ("how-the-pieces-connect", "conventions", "context-hygiene", "rulebook-drift", "verification"):
        assert (REPO / "docs" / (name + ".md")).is_file(), name


def test_every_template_the_plan_names_exists():
    for name in ("CLAUDE.md", "workflow.md", "agent.md", "skill/SKILL.md", "command.md", "context-summary.md",
                 "decisions.md", "phase-log.md", "questionnaire.md", "generation-prompt.md"):
        assert (REPO / "templates" / name).is_file(), name


def test_every_template_starts_with_a_three_line_comment_or_frontmatter_then_that_comment():
    for path in (REPO / "templates").rglob("*.md"):
        lines = path.read_text().splitlines()
        body = lines
        if lines[0] == "---":
            body = lines[lines.index("---", 1) + 1:]
            while body and body[0] == "":
                body = body[1:]
        starts = [line.startswith("<!-- What it is:") or line.startswith("<!-- When to create it:") or line.startswith("<!-- Where it goes:")
                  for line in body[:3]]
        assert starts == [True, True, True], str(path.relative_to(REPO))


def test_readme_is_short_and_has_the_sections_in_the_planned_order():
    text = (REPO / "README.md").read_text()
    assert len(text.splitlines()) < 150
    headings = re.findall(r"(?m)^## (.+)$", text)
    order = ["Who it is for", "The idea in one diagram", "What is different here", "Three layers",
             "Quick start", "Verification status", "What this is not", "The companion repository", "Licence and author"]
    assert headings == order


def test_readme_states_what_the_repository_is_not():
    text = (REPO / "README.md").read_text()
    for phrase in ("Not a security boundary", "Not a certified compliance product", "Not a production system", "fictional"):
        assert phrase in text, phrase


def test_the_working_name_appears_only_in_the_readme_title():
    for name in tracked_or_new_files():
        path = REPO / name
        if path.suffix in {".md", ".py", ".json", ".toml", ".yml", ".txt", ".csv"}:
            text = path.read_text()
            if name == "README.md":
                assert text.count("audit-ready-blueprint") == 1 and text.startswith("# audit-ready-blueprint")
            elif name != "tests/test_repository.py":
                assert "audit-ready-blueprint" not in text, name


STUB = r"<!-- OWNER: write this section yourself\. Prompt: .+ -->"
REVIEW = r"<!-- OWNER: review this draft"
STORY_HEADINGS = ("What the agent tried to do", "Why that would have broken a rule",
                  "What rule or check was added", "Where it lives now")
PUBLISHED_PAGES = ("CASE-STUDY.md", "stories/01-real-data.md", "stories/02-skipped-check.md",
                   "stories/03-gaming-the-test.md", "stories/04-rulebook-drift.md")


def test_case_study_sections_4_and_5_carry_a_provenance_note_and_no_review_marker_remains():
    text = (REPO / "CASE-STUDY.md").read_text()
    assert "**DRAFT.**" not in text
    assert "Sections 4 and 5 were drafted by the agent that built the repository" in text.splitlines()[2]
    assert "Nothing in this file describes a past project." in text.splitlines()[2]
    section4 = text.split("## 4. ")[1].split("## 5. ")[0]
    section5 = text.split("## 5. ")[1]
    for section in (section4, section5):
        assert "Drafted by the agent" in section
    assert not re.search(STUB, text), "no stub should remain in the case study"


def test_every_story_carries_a_provenance_note_and_no_review_marker_and_story_01_says_it_is_not_a_real_records_episode():
    for name in ("01-real-data", "02-skipped-check", "03-gaming-the-test", "04-rulebook-drift"):
        text = (REPO / "stories" / (name + ".md")).read_text()
        assert not re.search(r"<!-- OWNER:", text), name
        for heading in STORY_HEADINGS:
            assert "## " + heading in text, name + ": " + heading
        assert "Drafted by the agent that built this repository" in text, name
        assert "It is not an account of earlier work." in text, name
    story_01 = (REPO / "stories" / "01-real-data.md").read_text()
    assert "This is not a story about testing against real records." in story_01
    assert "If the owner has an episode of the first kind, it should replace this draft." in story_01


def test_no_review_marker_remains_and_the_companion_reminder_is_the_only_owner_marker():
    for name in PUBLISHED_PAGES:
        assert not re.search(REVIEW, (REPO / name).read_text()), name
    markers = []
    for relative in sorted(tracked_or_new_files()):
        if not relative.endswith(".md") or relative.split("/")[0] in {"kit", "templates"}:
            continue
        markers += [(relative, found) for found in re.findall(r"<!-- OWNER:[^>]*-->", (REPO / relative).read_text())]
    assert [name for name, _ in markers] == ["README.md"], markers
    assert "companion repository" in markers[0][1]


def test_the_stories_contain_no_first_person_account():
    for path in (REPO / "stories").glob("0*.md"):
        body = re.sub(r"<!--.*?-->", "", path.read_text(), flags=re.S)
        assert not re.search(r"\b(I|my|we|our)\b", body), path.name
