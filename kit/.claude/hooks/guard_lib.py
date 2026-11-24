"""Shared helpers for the guard hooks. Standard library only, Python 3.9 or later.

Every guard fails closed: any error in here ends in a block (exit code 2),
because Claude Code lets a tool call go ahead when a hook exits with any other
non-zero code. Every block is also written to the audit log, so a refused
attempt leaves a record. Writing the log is best effort and never changes the
outcome of a block.

Invariants served: INV-01, INV-02, INV-03 (see the invariants skill).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = ROOT / ".claude" / "guard.json"
LOG = ROOT / ".claude" / "context" / "audit" / "tool-log.jsonl"
LIST_KEYS = (
    "protected_paths", "real_data_paths", "blocked_hosts",
    "blocked_command_patterns", "secret_command_patterns",
)
STRING_KEYS = ("approvals_dir", "rule_changes_file")
SECRET_ASSIGNMENT = re.compile(r"(?i)\b(\w*(token|secret|password|passwd|key|auth)\w*)=\S+")
AUTH_HEADER = re.compile(r"(?i)\b(authorization|bearer)\b[:=]?\s*\S+(\s+\S+)?")
EVENT: dict = {}


def target_of(tool_input: dict) -> str:
    """Return a short description of what a tool call touched, never its contents.

    A file path is returned as given. For a command, the first line is cut to 100
    characters, with secret assignments and authorisation headers removed.
    """
    for name in ("file_path", "notebook_path", "path"):
        if isinstance(tool_input.get(name), str):
            return tool_input[name]
    command = tool_input.get("command")
    if isinstance(command, str) and command.strip():
        first_line = command.strip().splitlines()[0]
        first_line = SECRET_ASSIGNMENT.sub(r"\1=[redacted]", first_line)
        return AUTH_HEADER.sub("[redacted]", first_line)[:100]
    return ""


def append_log(extra: dict) -> None:
    """Append one JSON line about the current tool call to the audit log.

    The line holds the time, session, agent type, tool and target. It never holds
    file contents or command output. The audit folder is git-ignored.
    """
    tool_input = EVENT.get("tool_input")
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session": EVENT.get("session_id"),
        "agent": EVENT.get("agent_type"),
        "tool": EVENT.get("tool_name"),
        "target": target_of(tool_input if isinstance(tool_input, dict) else {}),
    }
    entry.update(extra)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as handle:
        handle.write(json.dumps(entry) + "\n")


def block(reason: str) -> None:
    """Record the attempt, print the reason on stderr and exit 2, which blocks the call."""
    try:
        append_log({"blocked": reason[:160]})
    except Exception:
        pass
    print("BLOCKED: " + reason, file=sys.stderr)
    sys.exit(2)


def read_event() -> dict:
    """Read the hook input from stdin. Anything unreadable blocks."""
    try:
        event = json.load(sys.stdin)
    except Exception:
        block("the hook input was not valid JSON, so the call cannot be checked (fail closed).")
    if not isinstance(event, dict):
        block("the hook input was not a JSON object (fail closed).")
    EVENT.update(event)
    return event


def load_config() -> dict:
    """Load guard.json. A missing, unreadable or malformed file blocks.

    The wrong type for a key, or an empty list of protected paths, would switch
    protection off without a sound, so both count as malformed.
    """
    try:
        config = json.loads(CONFIG_FILE.read_text())
        for key in LIST_KEYS:
            if not isinstance(config[key], list) or not all(isinstance(item, str) for item in config[key]):
                raise ValueError(key + " must be a list of strings")
        for key in STRING_KEYS:
            if not isinstance(config[key], str) or not config[key]:
                raise ValueError(key + " must be a non-empty string")
        if not config["protected_paths"]:
            raise ValueError("protected_paths must not be empty")
        return config
    except Exception as error:
        block("guard.json is missing, unreadable or incomplete (" + repr(error) + "). Restore it from version control (fail closed).")


def relative(path_text: str) -> str | None:
    """Return the path relative to the project root, lower-case, or None if outside it."""
    try:
        return Path(path_text).resolve().relative_to(ROOT).as_posix().lower()
    except ValueError:
        return None


def matches(rel: str, pattern: str) -> bool:
    """True if rel is the file named by pattern, or is under the directory it names."""
    p = pattern.lower().replace("\\", "/")
    if p.endswith("/**"):
        p = p[:-2]
    if p.endswith("/"):
        return rel.startswith(p) or rel == p.rstrip("/")
    return rel == p


def is_protected(rel: str, config: dict) -> bool:
    """True if rel is part of the rulebook."""
    return any(matches(rel, p) for p in config["protected_paths"])


def open_ids(text: str) -> set:
    """Return the ids of rule-change entries whose status line is 'open'.

    Fenced code blocks are ignored, so the format example is never an entry.
    """
    ids = set()
    text = re.sub(r"(?s)```.*?```", "", text)
    for chunk in re.split(r"(?m)^### ", text)[1:]:
        lines = chunk.splitlines()
        words = lines[0].split() if lines else []
        if words and any(line.strip().lower() == "- status: open" for line in lines):
            ids.add(words[0].rstrip(":"))
    return ids


def approved(rel: str, config: dict) -> bool:
    """True if a person has approved a change to rel.

    The approval is a file made by hand at <approvals_dir>/<id>.approved. It must
    name an approver and list the files it covers. The id must also be an open
    entry in the rule-changes file.
    """
    proposals = open_ids((ROOT / config["rule_changes_file"]).read_text())
    folder = ROOT / config["approvals_dir"]
    for approval in sorted(folder.glob("*.approved")):
        text = approval.read_text()
        who = re.search(r"(?mi)^approved by:\s*(\S.*)$", text)
        listed = re.search(r"(?mi)^files:\s*(.+)$", text)
        if approval.stem not in proposals or not who or not listed or who.group(1).startswith("<<"):
            continue
        if any(matches(rel, f.strip()) for f in listed.group(1).split(",") if f.strip()):
            return True
    return False
