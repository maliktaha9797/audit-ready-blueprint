"""Tests that the kit's files follow the formats recorded in docs/conventions.md.

These tests read the kit and do not run Claude Code. They prove the files are
well formed and consistent with each other. They do not prove Claude Code loads
them, which can only be checked in a live session.
"""
import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
KIT = REPO / "kit"
SKILLS = KIT / ".claude" / "skills"
AGENTS = KIT / ".claude" / "agents"
COMMANDS = ["phase", "gate", "regress", "new-scenario", "policy-change", "rule-change", "project-status"]
EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def frontmatter(path):
    """Parse the simple frontmatter used in the kit: key: value lines and '- item' lists.

    Returns None if the file does not start with a frontmatter block. Claude Code
    reads frontmatter only when the opening --- is the first line.
    """
    lines = path.read_text().splitlines()
    if not lines or lines[0] != "---":
        return None
    data, key = {}, None
    for line in lines[1:]:
        if line == "---":
            return data
        item = re.match(r"^\s+-\s+(.*)$", line)
        pair = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if item and key:
            data[key].append(item.group(1).strip().strip('"'))
        elif pair:
            key = pair.group(1)
            value = pair.group(2).strip().strip('"')
            data[key] = [] if value == "" else value
    raise AssertionError(str(path) + ": frontmatter has no closing ---")


def skill_dirs():
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


def agent_files():
    return sorted(p for p in AGENTS.glob("*.md") if not p.name.startswith("_"))


def table_first_column(text, heading):
    """Return the first cell of each data row in the table under a '## heading'."""
    section = re.search(r"(?ms)^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", text)
    cells = []
    for line in section.group(1).splitlines():
        if line.startswith("|") and not line.startswith("|---") and not line.startswith("| Agent") \
                and not line.startswith("| Skill") and not line.startswith("| Command"):
            cells.append(line.split("|")[1].strip())
    return cells


# --------------------------------------------------------------------- skills


@pytest.mark.parametrize("folder", skill_dirs(), ids=lambda p: p.name)
def test_skill_has_valid_frontmatter_with_matching_name(folder):
    meta = frontmatter(folder / "SKILL.md")
    assert meta is not None, "frontmatter must start on line 1"
    assert meta["name"] == folder.name
    description = meta["description"]
    assert description and len(description) <= 1536
    assert "<" not in description and ">" not in description, "angle brackets are shown escaped"


@pytest.mark.parametrize("name", COMMANDS)
def test_command_is_a_skill_that_only_a_person_can_start(name):
    meta = frontmatter(SKILLS / name / "SKILL.md")
    assert meta["disable-model-invocation"] == "true"


def test_knowledge_skills_stay_available_to_claude():
    for folder in skill_dirs():
        if folder.name not in COMMANDS:
            assert "disable-model-invocation" not in frontmatter(folder / "SKILL.md")


def test_no_command_is_named_after_a_built_in_command():
    assert "status" not in COMMANDS and "project-status" in COMMANDS


def test_workflow_files_named_by_commands_exist():
    for name in COMMANDS:
        text = (SKILLS / name / "SKILL.md").read_text()
        for ref in re.findall(r"\.claude/workflow-docs/([\w-]+\.md)", text):
            assert (KIT / ".claude" / "workflow-docs" / ref).is_file(), name + " -> " + ref


def test_no_markdown_file_sits_in_the_native_workflows_folder():
    assert not (KIT / ".claude" / "workflows").exists()


# --------------------------------------------------------------------- agents


@pytest.mark.parametrize("path", agent_files(), ids=lambda p: p.name)
def test_agent_has_name_and_description(path):
    meta = frontmatter(path)
    assert meta is not None and meta["name"] and meta["description"]
    assert meta["name"] == path.stem


def test_phase_owner_template_has_no_frontmatter_so_it_is_not_loaded_as_an_agent():
    assert frontmatter(AGENTS / "_phase-owner.template.md") is None


def test_invariant_auditor_has_no_edit_or_write_tool():
    meta = frontmatter(AGENTS / "invariant-auditor.md")
    tools = {t.strip() for t in meta["tools"].split(",")}
    assert tools and not (tools & EDIT_TOOLS)
    denied = {t.strip() for t in meta["disallowedTools"].split(",")}
    assert {"Write", "Edit", "NotebookEdit"} <= denied


def test_agents_preload_only_skills_that_exist_and_that_claude_may_invoke():
    for path in agent_files():
        for skill in frontmatter(path).get("skills", []):
            assert (SKILLS / skill / "SKILL.md").is_file(), path.name + " -> " + skill
            assert skill not in COMMANDS, "a user-only skill cannot be preloaded"


# ------------------------------------------------------------------ CLAUDE.md


def claude_md():
    return (KIT / "CLAUDE.md").read_text()


def test_claude_md_is_under_the_documented_length_target():
    assert len(claude_md().splitlines()) < 200


def test_claude_md_names_every_agent_and_no_other():
    named = {c.strip("`") for c in table_first_column(claude_md(), "Agents") if "<<" not in c}
    assert named == {p.stem for p in agent_files()}


def test_claude_md_names_every_knowledge_skill_and_no_other():
    named = {c.strip("`") for c in table_first_column(claude_md(), "Skills")}
    assert named == {p.name for p in skill_dirs() if p.name not in COMMANDS}


def test_claude_md_names_every_command_and_no_other():
    named = {c.strip("`").split()[0].lstrip("/") for c in table_first_column(claude_md(), "Commands")}
    assert named == set(COMMANDS)


def test_phase_owner_template_is_mentioned_in_claude_md():
    assert "_phase-owner.template.md" in claude_md()


# ----------------------------------------------------------------- invariants


def defined_invariants():
    text = (SKILLS / "invariants" / "SKILL.md").read_text()
    return set(re.findall(r"(?m)^\| (INV-\d+) \|", text))


def test_every_invariant_id_cited_in_the_kit_is_defined_in_the_table():
    defined = defined_invariants()
    assert defined, "the invariants table defines no ids"
    for path in KIT.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".json", ".csv"}:
            for cited in set(re.findall(r"INV-\d+", path.read_text())):
                assert cited in defined, str(path.relative_to(REPO)) + " cites " + cited


def test_every_invariant_row_names_how_it_is_enforced():
    text = (SKILLS / "invariants" / "SKILL.md").read_text()
    table = text.split("## The table")[1].split("## Audit output format")[0]
    allowed = ("hook", "permission", "test", "auditor review")
    rows = [line for line in table.splitlines() if re.match(r"\| INV-\d+ \|", line)]
    assert rows
    for line in rows:
        last_cell = line.rstrip().rstrip("|").rsplit("|", 1)[1]
        assert all(part.strip() in allowed for part in last_cell.split(",")), line[:60]


def test_the_hook_scripts_state_the_invariant_they_serve():
    for name in ("guard_paths.py", "guard_bash.py", "log_tool_use.py", "guard_lib.py"):
        assert re.search(r"INV-\d+", (KIT / ".claude" / "hooks" / name).read_text()), name


# -------------------------------------------------------------------- context


def test_summary_is_within_its_line_cap():
    assert len((KIT / ".claude" / "context" / "summary.md").read_text().splitlines()) <= 120


def test_register_sample_matches_the_documented_columns():
    header = (KIT / ".claude" / "context" / "register.csv").read_text().splitlines()[0]
    assert header == "id,scenario,required_behaviour,decider,phase,fixture_id,status"


def test_approvals_folder_ships_empty():
    folder = KIT / ".claude" / "context" / "approvals"
    assert [p.name for p in folder.iterdir()] == [".gitkeep"]


def test_rule_changes_sample_entry_is_never_open():
    text = (KIT / ".claude" / "context" / "rule-changes.md").read_text()
    assert "- Status: sample" in text
    assert "- Status: open\n- Files" not in re.sub(r"(?s)```.*?```", "", text)


def test_guard_json_is_valid_and_has_every_key_the_hooks_need():
    config = json.loads((KIT / ".claude" / "guard.json").read_text())
    for key in ("protected_paths", "real_data_paths", "approvals_dir", "rule_changes_file",
                "blocked_hosts", "blocked_command_patterns", "secret_command_patterns"):
        assert key in config


def test_every_slot_file_is_listed_in_the_kit_readme():
    readme = (KIT / "README.md").read_text()
    for path in KIT.rglob("*"):
        if path.is_file() and path != KIT / "README.md" and "<<FILL" in path.read_text():
            assert path.relative_to(KIT).as_posix() in readme, path.relative_to(KIT).as_posix()


# ------------------------------------------------------------- prose and style


def markdown_files():
    """Markdown files that git tracks or would track. Ignored files are not published."""
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return [REPO / name for name in listed if (REPO / name).is_file()]


def test_no_count_of_invariants_or_rules_is_written_in_prose():
    words = r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
    pattern = re.compile(r"\b" + words + r"\s+(invariants|rules)\b", re.I)
    for path in markdown_files():
        assert not pattern.search(path.read_text()), str(path.relative_to(REPO))


def test_no_em_dash_in_any_text_file():
    for path in markdown_files() + list(KIT.rglob("*.py")) + list((REPO / "tests").glob("*.py")):
        assert chr(0x2014) not in path.read_text(), str(path.relative_to(REPO))
