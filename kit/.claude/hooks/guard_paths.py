#!/usr/bin/env python3
"""PreToolUse hook for Edit, Write and NotebookEdit. Exit 2 blocks the call.

Rules enforced:
  INV-01  No write under a real-data path.
  INV-03  The rulebook changes only through an approved rule change. The agent
          cannot create the approval, because it may not write to the approvals
          folder (this hook and a permission rule both stop it).

Fails closed: a missing or unreadable guard.json, an unreadable event, or any
unexpected error blocks the call.
"""
from __future__ import annotations

import sys

from guard_lib import approved, block, is_protected, load_config, matches, read_event, relative


def main() -> None:
    """Check the target path of a file edit against the guard configuration."""
    event = read_event()
    config = load_config()
    tool_input = event.get("tool_input")
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    raw = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(raw, str) or not raw:
        block("no file path was found in the tool input, so the write cannot be checked (fail closed).")
    rel = relative(raw)
    if rel is None:
        return
    if matches(rel, config["approvals_dir"]):
        block("INV-03: only a person may create files in the approvals folder. Propose the change with /rule-change and ask the owner to approve it by hand.")
    if any(matches(rel, p) for p in config["real_data_paths"]):
        block("INV-01: real data paths are never written to. Use synthetic records (see the synthetic-data skill).")
    if is_protected(rel, config) and not approved(rel, config):
        block("INV-03: " + rel + " is part of the rulebook and has no approved rule change. Run /rule-change to write a proposal, then wait for the owner to approve it.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        block("guard_paths failed with " + repr(error) + " (fail closed).")
    sys.exit(0)
