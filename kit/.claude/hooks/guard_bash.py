#!/usr/bin/env python3
"""PreToolUse hook for Bash and PowerShell. Exit 2 blocks the call.

Rules enforced:
  INV-01  No command that mentions a real-data path or a blocked production host.
  INV-02  No command that reads a secret file or prints a secret-looking variable,
          or that dumps the environment in the common ways (printenv, env, export -p,
          declare -x, /proc/*/environ, os.environ).
  INV-03  No shell command that writes to a protected file or to the approvals
          folder without an approved rule change. This is a text check against a
          fixed list of write-like commands (WRITERS). It is deliberately
          conservative: it can block a harmless command that mentions a protected
          file next to a write-like word, and it does not know every program that
          can write a file. Use the Read tool to read such a file.

Limit: a determined user with shell access can get around text matching. This
hook raises the cost of breaking a rule and leaves evidence. It is not a
security boundary.

Fails closed on a bad guard.json, a bad event or any unexpected error.
"""
from __future__ import annotations

import re
import sys

from guard_lib import approved, block, load_config, read_event

WRITERS = re.compile(
    r"(>|\b(tee|mv|cp|rm|touch|truncate|ln|dd|install|sed|awk|perl|python3?|node|ruby|php|ed|vim?|nano"
    r"|curl|wget|rsync|tar|unzip|patch)\b"
    r"|\bgit\s+(checkout|restore|apply|reset|stash|am|merge|rebase|cherry-pick|pull)\b"
    r"|\b(set|add|out|new|remove|move|copy|rename|clear)-(content|item|itemproperty)\b|\bout-file\b)",
    re.I,
)
CHANGES_DIRECTORY = re.compile(r"\b(cd|pushd|set-location)\b", re.I)


def strip_glob(pattern: str) -> str:
    """Turn a path pattern such as '.claude/hooks/**' into the text '.claude/hooks'."""
    return pattern.lower().replace("\\", "/").rstrip("*").rstrip("/")


def triggers(pattern: str, short_names: bool) -> list:
    """Return the texts that show a command names a protected path.

    The whole path always. When the command also changes directory, the last part
    as well: 'settings.json' for a file, 'approvals/' for a folder. A command that
    moves into a folder and then names a file by its short name would otherwise
    slip past. The short name is used only then, because on its own it would block
    ordinary commands that happen to name a file called settings.json somewhere else.
    """
    whole = strip_glob(pattern)
    if not short_names:
        return [whole]
    last = whole.rsplit("/", 1)[-1]
    if pattern.endswith(("/**", "/")):
        last += "/"
    return [whole, last]


def main() -> None:
    """Check a shell command against the guard configuration."""
    event = read_event()
    config = load_config()
    tool_input = event.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not command.strip():
        block("no command was found in the tool input, so it cannot be checked (fail closed).")
    lowered = command.lower().replace("\\", "/")
    for host in config["blocked_hosts"]:
        if not host.startswith("<<") and host.lower() in lowered:
            block("INV-01: the command mentions the blocked host " + host + ". Production systems are never touched during the build.")
    for path in config["real_data_paths"]:
        if strip_glob(path) in lowered:
            block("INV-01: the command mentions the real-data path " + path + ". Use synthetic records instead.")
    for pattern in config["blocked_command_patterns"]:
        if re.search(pattern, command, re.I):
            block("this command matches the blocked pattern " + pattern + ". Ask the owner to run it by hand if it is really needed.")
    for pattern in config["secret_command_patterns"]:
        if re.search(pattern, command, re.I):
            block("INV-02: the command reads a secret file or dumps the environment. Secrets are never readable by the agent.")
    if WRITERS.search(command):
        short = bool(CHANGES_DIRECTORY.search(command))
        if any(text in lowered for text in triggers(config["approvals_dir"], short)):
            block("INV-03: only a person may create files in the approvals folder.")
        for path in config["protected_paths"]:
            if any(text in lowered for text in triggers(path, short)) and not approved(strip_glob(path), config):
                block("INV-03: the command appears to write to the rulebook file " + path + " with no approved rule change. Run /rule-change.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:
        block("guard_bash failed with " + repr(error) + " (fail closed).")
    sys.exit(0)
