"""Shared helpers for the guard hooks. Standard library only, Python 3.9 or later.

Every guard fails closed: any error in here ends in a block (exit code 2),
because Claude Code lets a tool call go ahead when a hook exits with any other
non-zero code.

Invariants served: INV-01, INV-02, INV-03 (see the invariants skill).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = ROOT / ".claude" / "guard.json"
LIST_KEYS = (
    "protected_paths", "real_data_paths", "blocked_hosts",
    "blocked_command_patterns", "secret_command_patterns",
)
STRING_KEYS = ("approvals_dir", "rule_changes_file")


def block(reason: str) -> None:
    """Print the reason on stderr and exit 2, which blocks the tool call."""
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
