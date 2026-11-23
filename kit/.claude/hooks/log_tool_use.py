#!/usr/bin/env python3
"""PostToolUse hook. Appends one JSON line per tool call to the audit log.

Rule served: the evidence behind INV-03 and INV-04. A reviewer can compare what
the log says was done with what the phase log says was done.

The log holds the time, session, agent type, tool name and a short target (a
file path, or the first line of a command cut to 100 characters with obvious
secret assignments removed). It never holds file contents or command output.
The folder .claude/context/audit/ is git-ignored.

If the log cannot be written the hook exits 2, so the failure is shown to Claude
and not hidden. The tool call itself has already happened by then.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone

from guard_lib import ROOT, block, read_event

LOG = ROOT / ".claude" / "context" / "audit" / "tool-log.jsonl"
SECRET_ASSIGNMENT = re.compile(r"(?i)\b(\w*(token|secret|password|passwd|key|auth)\w*)=\S+")


def target_of(tool_input: dict) -> str:
    """Return a short description of what the tool call touched, never its contents."""
    for name in ("file_path", "notebook_path", "path"):
        if isinstance(tool_input.get(name), str):
            return tool_input[name]
    command = tool_input.get("command")
    if isinstance(command, str) and command.strip():
        first_line = command.strip().splitlines()[0]
        return SECRET_ASSIGNMENT.sub(r"\1=[redacted]", first_line)[:100]
    return ""


def main() -> None:
    """Append one line describing the tool call."""
    event = read_event()
    tool_input = event.get("tool_input")
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session": event.get("session_id"),
        "agent": event.get("agent_type"),
        "tool": event.get("tool_name"),
        "target": target_of(tool_input if isinstance(tool_input, dict) else {}),
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as handle:
        handle.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        block("log_tool_use failed with " + repr(error) + ". The audit trail has a gap.")
    sys.exit(0)
