#!/usr/bin/env python3
"""PostToolUse hook. Appends one JSON line per successful tool call to the audit log.

Rule served: the evidence behind INV-03 and INV-04. A reviewer can compare what
the log says was done with what the phase log says was done.

Claude Code runs this hook only after a tool call succeeds. A call that a guard
blocks never reaches it, so the guards write their own line, marked "blocked",
before they exit. Together the two give a record of what was done and what was
refused.

The line holds the time, session, agent type, tool name and a short target (a
file path, or the first line of a command cut to 100 characters with obvious
secrets removed). It never holds file contents or command output. The folder
.claude/context/audit/ is git-ignored.

If the log cannot be written the hook exits 2, so the failure is shown to Claude
and not hidden. The tool call itself has already happened by then.
"""
from __future__ import annotations

import sys

from guard_lib import append_log, block, read_event


def main() -> None:
    """Append one line describing the tool call."""
    read_event()
    append_log({})


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        block("log_tool_use failed with " + repr(error) + ". The audit trail has a gap.")
    sys.exit(0)
