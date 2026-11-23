"""Tests for the kit's three hook scripts and the settings that register them.

Each test copies the kit into a temporary folder and runs the hook scripts there,
feeding them the stdin shape documented for PreToolUse and PostToolUse. A block is
exit code 2 with the reason on stderr. These tests prove the scripts behave as
specified. They do not prove that a live Claude Code session sends the same input.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1] / "kit"
RULE_CHANGES = ".claude/context/rule-changes.md"


@pytest.fixture
def root(tmp_path):
    """A fresh copy of the kit, standing in for a project root."""
    copy = tmp_path / "project"
    shutil.copytree(KIT, copy)
    return copy


def event(tool, name="PreToolUse", **tool_input):
    """Build a hook input document in the documented shape."""
    return {
        "session_id": "test-session",
        "hook_event_name": name,
        "tool_name": tool,
        "tool_input": tool_input,
        "tool_use_id": "toolu_test",
    }


def run(root, script, payload, interpreter=sys.executable):
    """Run one hook script with a payload on stdin and return the finished process."""
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [interpreter, str(root / ".claude" / "hooks" / script)],
        input=text, capture_output=True, text=True, cwd=root,
    )


def write_event(root, relative_path, tool="Write"):
    """An Edit or Write event for a path inside the project."""
    return event(tool, file_path=str(root / relative_path), content="x")


def open_proposal(root, rc_id="RC-001"):
    """Append an open rule-change entry."""
    entry = "\n### " + rc_id + ": test proposal\n\n- Status: open\n- Files: CLAUDE.md\n"
    with (root / RULE_CHANGES).open("a") as handle:
        handle.write(entry)


def approve(root, rc_id="RC-001", files="CLAUDE.md", who="A Named Person"):
    """Create an approval file by hand, as the owner would."""
    folder = root / ".claude" / "context" / "approvals"
    (folder / (rc_id + ".approved")).write_text(
        "Approved by: " + who + "\nDate: 2026-01-01\nFiles: " + files + "\n")


def edit_guard(root, change):
    """Rewrite guard.json with a change applied to its parsed content."""
    path = root / ".claude" / "guard.json"
    config = json.loads(path.read_text())
    change(config)
    path.write_text(json.dumps(config))


def assert_blocked(result, *words):
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stderr.startswith("BLOCKED:")
    for word in words:
        assert word in result.stderr


def assert_allowed(result):
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------- guard_paths


def test_protected_path_blocked_without_approval(root):
    assert_blocked(run(root, "guard_paths.py", write_event(root, "CLAUDE.md")), "INV-03", "/rule-change")


def test_protected_path_allowed_with_matching_approval_and_open_proposal(root):
    open_proposal(root)
    approve(root)
    assert_allowed(run(root, "guard_paths.py", write_event(root, "CLAUDE.md")))


def test_approval_file_without_open_proposal_still_blocks(root):
    approve(root)
    assert_blocked(run(root, "guard_paths.py", write_event(root, "CLAUDE.md")), "INV-03")


def test_open_proposal_without_approval_file_still_blocks(root):
    open_proposal(root)
    assert_blocked(run(root, "guard_paths.py", write_event(root, "CLAUDE.md")), "INV-03")


def test_approval_for_a_different_file_does_not_unlock_this_file(root):
    open_proposal(root)
    approve(root, files=".claude/settings.json")
    assert_blocked(run(root, "guard_paths.py", write_event(root, "CLAUDE.md")), "INV-03")


def test_approval_with_placeholder_approver_still_blocks(root):
    open_proposal(root)
    approve(root, who="<<unfilled name>>")
    assert_blocked(run(root, "guard_paths.py", write_event(root, "CLAUDE.md")), "INV-03")


def test_approval_stops_working_once_the_entry_is_closed(root):
    open_proposal(root)
    approve(root)
    text = (root / RULE_CHANGES).read_text().replace("- Status: open\n- Files: CLAUDE.md\n", "- Status: closed\n- Files: CLAUDE.md\n")
    (root / RULE_CHANGES).write_text(text)
    assert_blocked(run(root, "guard_paths.py", write_event(root, "CLAUDE.md")), "INV-03")


def test_entry_inside_a_code_fence_is_never_an_open_entry(root):
    fenced = "\n```\n### RC-777: only an example\n\n- Status: open\n- Files: CLAUDE.md\n```\n"
    with (root / RULE_CHANGES).open("a") as handle:
        handle.write(fenced)
    approve(root, rc_id="RC-777")
    assert_blocked(run(root, "guard_paths.py", write_event(root, "CLAUDE.md")), "INV-03")


def test_write_to_approvals_folder_blocked(root):
    result = run(root, "guard_paths.py", write_event(root, ".claude/context/approvals/RC-001.approved"))
    assert_blocked(result, "INV-03", "approvals")


def test_agent_cannot_approve_even_with_an_open_proposal(root):
    open_proposal(root)
    result = run(root, "guard_paths.py", write_event(root, ".claude/context/approvals/RC-001.approved"))
    assert_blocked(result, "INV-03")


def test_write_to_real_data_path_blocked(root):
    assert_blocked(run(root, "guard_paths.py", write_event(root, "data/real/customers.csv")), "INV-01")


def test_notebook_path_is_checked(root):
    payload = event("NotebookEdit", notebook_path=str(root / "CLAUDE.md"), new_source="x")
    assert_blocked(run(root, "guard_paths.py", payload), "INV-03")


def test_path_case_variant_of_a_protected_file_blocks(root):
    assert_blocked(run(root, "guard_paths.py", write_event(root, "claude.MD")), "INV-03")


def test_protected_directory_blocks_every_file_under_it(root):
    assert_blocked(run(root, "guard_paths.py", write_event(root, ".claude/hooks/new_hook.py")), "INV-03")


def test_symlink_to_a_protected_file_blocks(root):
    (root / "notes.md").symlink_to(root / "CLAUDE.md")
    assert_blocked(run(root, "guard_paths.py", write_event(root, "notes.md")), "INV-03")


def test_ordinary_write_passes(root):
    assert_allowed(run(root, "guard_paths.py", write_event(root, "src/app.py")))


def test_write_outside_the_project_is_left_to_permissions(root, tmp_path):
    payload = event("Write", file_path=str(tmp_path / "elsewhere.txt"), content="x")
    assert_allowed(run(root, "guard_paths.py", payload))


def test_missing_path_in_tool_input_blocks(root):
    assert_blocked(run(root, "guard_paths.py", event("Write", content="x")), "fail closed")


def test_unreadable_event_blocks(root):
    assert_blocked(run(root, "guard_paths.py", "this is not json"), "fail closed")


def test_missing_guard_json_blocks_every_guard(root):
    (root / ".claude" / "guard.json").unlink()
    assert_blocked(run(root, "guard_paths.py", write_event(root, "src/app.py")), "guard.json", "fail closed")
    assert_blocked(run(root, "guard_bash.py", event("Bash", command="ls")), "guard.json", "fail closed")


def test_malformed_guard_json_blocks(root):
    (root / ".claude" / "guard.json").write_text("{ not json")
    assert_blocked(run(root, "guard_paths.py", write_event(root, "src/app.py")), "fail closed")


def test_wrong_type_in_guard_json_blocks(root):
    edit_guard(root, lambda config: config.update(protected_paths="CLAUDE.md"))
    assert_blocked(run(root, "guard_paths.py", write_event(root, "src/app.py")), "fail closed")


def test_empty_protected_paths_in_guard_json_blocks(root):
    edit_guard(root, lambda config: config.update(protected_paths=[]))
    assert_blocked(run(root, "guard_paths.py", write_event(root, "src/app.py")), "fail closed")


def test_missing_rule_changes_file_blocks_a_protected_write(root):
    (root / RULE_CHANGES).unlink()
    assert_blocked(run(root, "guard_paths.py", write_event(root, "CLAUDE.md")), "fail closed")


# ----------------------------------------------------------------- guard_bash


def bash(root, command):
    return run(root, "guard_bash.py", event("Bash", command=command))


def test_blocked_host_in_shell_command_blocks(root):
    edit_guard(root, lambda config: config.update(blocked_hosts=["prod.example.test"]))
    assert_blocked(bash(root, "curl https://PROD.example.test/api"), "INV-01", "prod.example.test")


def test_unfilled_host_slot_is_ignored(root):
    assert_allowed(bash(root, "curl https://example.test/api"))


def test_real_data_path_in_shell_command_blocks(root):
    assert_blocked(bash(root, "head data/real/customers.csv"), "INV-01")


@pytest.mark.parametrize("command", [
    "cat .env",
    "cat config/.env.production",
    "head -n 3 server.pem",
    "cp deploy.key /tmp/k",
    "printenv",
    "ls && env",
])
def test_secret_file_read_in_shell_blocks(root, command):
    assert_blocked(bash(root, command), "INV-02")


@pytest.mark.parametrize("command", ["ls .envrc", "echo environment", "cat monkey.keys.txt", "pytest -q"])
def test_names_that_only_look_like_secrets_pass(root, command):
    assert_allowed(bash(root, command))


@pytest.mark.parametrize("command", [
    "git push --force origin main",
    "git push origin main -f",
    "git reset --hard HEAD~3",
    "rm -rf /",
    "rm -rf .",
    "npm publish",
])
def test_destructive_or_publishing_command_blocks(root, command):
    assert_blocked(bash(root, command), "blocked pattern")


def test_removing_a_build_folder_is_not_blocked(root):
    assert_allowed(bash(root, "rm -rf build/"))


def test_shell_write_to_a_protected_file_blocks(root):
    assert_blocked(bash(root, "echo 'DO NOT' >> CLAUDE.md"), "INV-03")
    assert_blocked(bash(root, "sed -i 's/a/b/' .claude/settings.json"), "INV-03")
    assert_blocked(bash(root, "python3 -c \"open('.claude/hooks/guard_bash.py','w')\""), "INV-03")


def test_shell_write_to_a_protected_file_allowed_with_approval(root):
    open_proposal(root)
    approve(root)
    assert_allowed(bash(root, "echo 'DO NOT' >> CLAUDE.md"))


def test_shell_write_to_the_approvals_folder_blocks_but_reading_it_passes(root):
    assert_blocked(bash(root, "touch .claude/context/approvals/RC-001.approved"), "INV-03")
    assert_allowed(bash(root, "ls .claude/context/approvals/"))


def test_ordinary_command_passes(root):
    assert_allowed(bash(root, "python -m pytest -q tests/"))


def test_missing_command_blocks(root):
    assert_blocked(run(root, "guard_bash.py", event("Bash")), "fail closed")


# ----------------------------------------------------------- log_tool_use


def log_lines(root):
    path = root / ".claude" / "context" / "audit" / "tool-log.jsonl"
    return path.read_text().splitlines() if path.exists() else []


def test_logger_writes_one_line_and_no_file_contents(root):
    secret_text = "UNIQUE-CONTENT-MARKER-12345"
    payload = event("Write", name="PostToolUse", file_path=str(root / "src" / "a.py"), content=secret_text)
    payload["agent_type"] = "invariant-auditor"
    assert_allowed(run(root, "log_tool_use.py", payload))
    lines = log_lines(root)
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["tool"] == "Write"
    assert entry["agent"] == "invariant-auditor"
    assert entry["target"].endswith("a.py")
    assert secret_text not in lines[0]


def test_logger_appends_a_second_line_for_a_second_call(root):
    for _ in range(2):
        run(root, "log_tool_use.py", event("Bash", name="PostToolUse", command="ls"))
    assert len(log_lines(root)) == 2


def test_logger_cuts_long_commands_and_removes_secret_assignments(root):
    command = "API_TOKEN=abc123 run-thing " + "x" * 300 + "\nsecond line"
    run(root, "log_tool_use.py", event("Bash", name="PostToolUse", command=command))
    entry = json.loads(log_lines(root)[0])
    assert "abc123" not in entry["target"]
    assert "[redacted]" in entry["target"]
    assert len(entry["target"]) <= 100
    assert "second line" not in entry["target"]


def test_logger_failure_is_reported_with_exit_2(root):
    (root / ".claude" / "context" / "audit").write_text("a file where a folder should be")
    assert_blocked(run(root, "log_tool_use.py", event("Bash", name="PostToolUse", command="ls")), "audit trail")


# ------------------------------------------------------------------ settings


@pytest.fixture
def settings():
    return json.loads((KIT / ".claude" / "settings.json").read_text())


def hook_commands(settings, event_name):
    return [h for group in settings["hooks"][event_name] for h in group["hooks"]]


def test_settings_register_the_guards_before_tool_use_and_the_logger_after(settings):
    pre = " ".join(a for h in hook_commands(settings, "PreToolUse") for a in h["args"])
    post = " ".join(a for h in hook_commands(settings, "PostToolUse") for a in h["args"])
    assert "guard_paths.py" in pre and "guard_bash.py" in pre
    assert "log_tool_use.py" in post


def test_settings_make_the_guards_fail_closed_at_the_harness(settings):
    assert all(h["onFailure"] == "block" for h in hook_commands(settings, "PreToolUse"))


def test_settings_hook_scripts_exist(settings):
    for event_name in ("PreToolUse", "PostToolUse"):
        for h in hook_commands(settings, event_name):
            script = h["args"][0].replace("${CLAUDE_PROJECT_DIR}", str(KIT))
            assert Path(script).is_file(), script


def test_settings_deny_secret_reads_and_approval_writes(settings):
    deny = settings["permissions"]["deny"]
    for rule in ("Read(.env)", "Read(.env.*)", "Read(*.pem)", "Read(*.key)",
                 "Read(data/real/**)", "Edit(/.claude/context/approvals/**)"):
        assert rule in deny
    assert not any(rule.startswith("Write(") for rule in deny), "Write(path) rules match nothing"


def test_settings_deny_destructive_commands(settings):
    deny = settings["permissions"]["deny"]
    assert "Bash(git push --force*)" in deny
    assert "Bash(git reset --hard*)" in deny
    assert "Bash(rm -rf .)" in deny


def test_guard_json_protects_the_rulebook():
    config = json.loads((KIT / ".claude" / "guard.json").read_text())
    for path in ("CLAUDE.md", ".claude/settings.json", ".claude/settings.local.json",
                 ".claude/guard.json", ".claude/skills/invariants/SKILL.md"):
        assert path in config["protected_paths"]


def test_hooks_run_under_the_default_python3(root):
    python3 = shutil.which("python3")
    if python3 is None:
        pytest.skip("no python3 on PATH")
    result = run(root, "guard_paths.py", write_event(root, "CLAUDE.md"), interpreter=python3)
    assert_blocked(result, "INV-03")
    assert_allowed(run(root, "guard_paths.py", write_event(root, "src/app.py"), interpreter=python3))
