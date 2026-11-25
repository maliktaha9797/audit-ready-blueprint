"""Mutate-to-red proof for the kit's and the demo's detection tests (invariant INV-06).

For each mutation: break one thing in one kit file, run the test file that is
meant to catch it, expect at least one failure, then restore the file byte for
byte. A mutation that leaves the tests green means a detection cannot fail,
which is a finding.

Run from the repository root:  python scripts/mutate_kit.py
Standard library only. It rewrites files under kit/ for a few seconds each, so
do not run it while another process is editing them.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
LIB = "kit/.claude/hooks/guard_lib.py"
PATHS = "kit/.claude/hooks/guard_paths.py"
BASH = "kit/.claude/hooks/guard_bash.py"
HOOKS = "tests/test_hooks.py"
STRUCTURE = "tests/test_kit_structure.py"
LEDGER = "demo/supplier_demo/ledger.py"
OUTBOUND = "demo/supplier_demo/outbound.py"
RULES = "demo/supplier_demo/rules.py"
CODE_RULES = "tests/test_demo_code_rules.py"
EXAMPLE = "tests/test_example.py"
CHECK = "scripts/check_rulebook.py"
CHECK_TESTS = "tests/test_check_rulebook.py"

# (name, file to break, text to find, replacement, test file that must go red)
MUTATIONS = [
    ("block exits 1 instead of 2", LIB, "sys.exit(2)", "sys.exit(1)", HOOKS),
    ("approved() always true", LIB, "def approved(rel: str, config: dict) -> bool:\n", "def approved(rel: str, config: dict) -> bool:\n    return True\n", HOOKS),
    ("matches() is case sensitive", LIB, 'p = pattern.lower().replace("\\\\", "/")', 'p = pattern.replace("\\\\", "/")', HOOKS),
    ("open_ids no longer ignores code fences", LIB, 'text = re.sub(r"(?s)```.*?```", "", text)', "pass", HOOKS),
    ("approval scope ignored", LIB, "if any(matches(rel, f.strip()) for f in listed.group(1).split(\",\") if f.strip()):", "if True:", HOOKS),
    ("approver name not required", LIB, ' or who.group(1).startswith("<<")', "", HOOKS),
    ("empty protected_paths allowed", LIB, 'if not config["protected_paths"]:', "if False:", HOOKS),
    ("approvals folder not guarded", PATHS, 'if matches(rel, config["approvals_dir"]):', "if False:", HOOKS),
    ("real data path not guarded", PATHS, 'if any(matches(rel, p) for p in config["real_data_paths"]):', "if False:", HOOKS),
    ("missing path allowed", PATHS, 'if not isinstance(raw, str) or not raw:\n        block(', 'if not isinstance(raw, str) or not raw:\n        return\n        block(', HOOKS),
    ("bash write check removed", BASH, "if WRITERS.search(command):", "if False:", HOOKS),
    ("secret patterns ignored", BASH, 'for pattern in config["secret_command_patterns"]:', "for pattern in []:", HOOKS),
    ("auditor is given an edit tool", "kit/.claude/agents/invariant-auditor.md", "tools: Read, Grep, Glob, Bash\n", "tools: Read, Grep, Glob, Bash, Edit\n", STRUCTURE),
    ("a command can be started by Claude", "kit/.claude/skills/gate/SKILL.md", "disable-model-invocation: true\n", "", STRUCTURE),
    ("a skill name differs from its folder", "kit/.claude/skills/regress/SKILL.md", "name: regress\n", "name: regres\n", STRUCTURE),
    ("an undefined invariant id is cited", "kit/CLAUDE.md", "(INV-08)", "(INV-99)", STRUCTURE),
    ("an agent is missing from CLAUDE.md", "kit/CLAUDE.md", "| `red-team` |", "| `red-team-x` |", STRUCTURE),
    ("a count of invariants is written in prose", "kit/CLAUDE.md", "- Let code decide", "- Follow the 12 invariants.\n- Let code decide", STRUCTURE),
    ("the summary exceeds its cap", "kit/.claude/context/summary.md", "## Links", "\n" * 130 + "## Links", STRUCTURE),
    ("the phase-owner template gets frontmatter", "kit/.claude/agents/_phase-owner.template.md", "<!-- What it is: a template", "---\nname: t\ndescription: t\n---\n<!-- What it is: a template", STRUCTURE),
    ("a slot file is missing from the kit README", "kit/README.md", "`.claude/context/acceptance.md`", "`.claude/context/acceptance-x.md`", STRUCTURE),
    ("ledger stops checking the content hash", LEDGER, 'if hash_entry(entry) != entry.get("hash"):', "if False:", "tests/test_ledger.py"),
    ("ledger stops checking the chain", LEDGER, 'if entry.get("prev_hash") != previous:', "if False:", "tests/test_ledger.py"),
    ("ledger accepts an entry with no actor", LEDGER, 'for required in ("actor", "policy_version"):', "for required in ():", "tests/test_ledger.py"),
    ("ledger gains a way to overwrite the file", LEDGER, 'with open(path, "a") as handle:', 'with open(path, "w") as handle:', "tests/test_ledger.py"),
    ("outbound ignores the mode", OUTBOUND, 'if config["mode"] != "live":', "if False:", "tests/test_outbound.py"),
    ("outbound ignores the allowlist", OUTBOUND, "if recipient not in allowlist:", "if False:", "tests/test_outbound.py"),
    ("outbound treats a missing mode as live", OUTBOUND, 'if "mode" not in config:', 'if "mode" not in config and False:', "tests/test_outbound.py"),
    ("outbound sends before it records", OUTBOUND, '        ledger.append(ledger_path, entry)\n        OUTBOX.append({"recipient": recipient, "message": message})\n', '        OUTBOX.append({"recipient": recipient, "message": message})\n        ledger.append(ledger_path, entry)\n', "tests/test_outbound.py"),
    ("rules ignore a failing rule", RULES, "if not rule_passed:", "if False:", "tests/test_rules.py"),
    ("rules accept any proposal when the rule passes", RULES, "elif proposed_status not in ALLOWED_PROPOSALS:", "elif False:", "tests/test_rules.py"),
    ("rules accept two empty registration numbers", RULES, 'if clean_number(given) == "":', "if False:", "tests/test_rules.py"),
    ("demo gains a class", RULES, "def clean_number(number: str) -> str:", "class Helper:\n    pass\n\n\ndef clean_number(number: str) -> str:", CODE_RULES),
    ("demo function loses its return type", RULES, "def clean_number(number: str) -> str:", "def clean_number(number: str):", CODE_RULES),
    ("demo docstring stops naming its invariant", RULES, "Serves INV-07: the rule compares", "The rule compares", CODE_RULES),
    ("demo gains a filtered comprehension", OUTBOUND, "OUTBOX: list[dict] = []", "OUTBOX: list[dict] = [{} for item in range(0) if item]", CODE_RULES),
    ("demo imports a package outside the standard library", LEDGER, "import hashlib\n", "import hashlib\nimport requests\n", CODE_RULES),
    ("demo module grows past the length limit", RULES, "POLICY_VERSION =", "\n" * 120 + "POLICY_VERSION =", CODE_RULES),
    ("a slot is left in the example", "example/CLAUDE.md", "## Overview", "## <<FILL: overview>>", EXAMPLE),
    ("a covered register row cites a test that does not exist", "example/register.csv", "test_editing_an_entry_is_detected,covered", "test_editing_an_entry_is_detected_x,covered", EXAMPLE),
    ("the example cites an undefined invariant", "example/CLAUDE.md", "(INV-16)", "(INV-99)", EXAMPLE),
    ("a not-verifiable criterion is ticked", "example/context/phases/phase-0.md", "- [ ] One supplier's file cannot read another's", "- [x] One supplier's file cannot read another's", EXAMPLE),
    ("the example pass bar is signed", "example/acceptance.md", "Signed by:\nDate:", "Signed by: A Person\nDate:", EXAMPLE),
    ("a trail file loses its illustrative notice", "example/context/summary.md", "> Illustrative trail:", "> Trail:", EXAMPLE),
    ("a ticked slice loses its label", "example/context/phases/phase-0.md", "test_append_then_verify_passes`. Label: executed.", "test_append_then_verify_passes`.", EXAMPLE),
    ("the check script ignores banned terms", CHECK, "if pattern.search(name) or pattern.search(text):", "if False:", CHECK_TESTS),
    ("short banned terms match inside words", CHECK, "if len(term) <= 4:", "if False:", CHECK_TESTS),
    ("the check script allows em dashes", CHECK, "for name, text in texts.items() if EM_DASH in text]", "for name, text in texts.items() if False]", CHECK_TESTS),
    ("the check script allows prose counts", CHECK, 'match = PROSE_COUNT.search(text) if name.endswith(".md") else None', "match = None", CHECK_TESTS),
    ("the check script allows unknown commands", CHECK, "if ref not in commands and ref not in BUILT_IN_COMMANDS:", "if False:", CHECK_TESTS),
    ("the check script allows undefined invariant ids", CHECK, "if cited not in allowed:", "if False:", CHECK_TESTS),
    ("the check script allows missing test ids", CHECK, "if names is None or test not in names:", "if False:", CHECK_TESTS),
    ("the check script allows broken links", CHECK, 'if clean and not (base / clean.lstrip("/")).exists():', "if False:", CHECK_TESTS),
    ("the check script ignores the summary cap", CHECK, "and len(text.splitlines()) > SUMMARY_CAP]", "and False]", CHECK_TESTS),
    ("the check script allows slots anywhere", CHECK, '        if match:\n            found.append(finding("slots"', '        if False:\n            found.append(finding("slots"', CHECK_TESTS),
    ("the check script exits zero on failure", CHECK, "return 1 if failures else 0", "return 0", CHECK_TESTS),
    ("the history check is ignored", CHECK, "history = check_history(root, terms)", "history = []", CHECK_TESTS),
    ("strict history no longer fails", CHECK, "        if strict_history:\n            failures += history", "        if False:\n            failures += history", CHECK_TESTS),
    ("the prose-count pattern misses the 'of the' form", CHECK, "of\\s+(?:the|these|those|our|its)", "of\\s+(?:xx)", CHECK_TESTS),
    ("the shell guard ignores blocked hosts", BASH, 'if not host.startswith("<<") and host.lower() in lowered:', "if False:", HOOKS),
    ("the shell guard ignores real-data paths", BASH, '        if strip_glob(path) in lowered:\n            block("INV-01', '        if False:\n            block("INV-01', HOOKS),
    ("the shell guard ignores blocked command patterns", BASH, '        if re.search(pattern, command, re.I):\n            block("this command matches', '        if False:\n            block("this command matches', HOOKS),
    ("the shell guard misses a short name after cd", BASH, 'last = whole.rsplit("/", 1)[-1]', "last = whole", HOOKS),
    ("the path guard skips the protected-file check", PATHS, "if is_protected(rel, config) and not approved(rel, config):", "if False:", HOOKS),
    ("a block is no longer logged", LIB, 'append_log({"blocked": reason[:160]})', "pass", HOOKS),
    ("the logger writes nothing", "kit/.claude/hooks/log_tool_use.py", "    append_log({})\n", "    pass\n", HOOKS),
    ("authorisation headers are not redacted", LIB, 'return AUTH_HEADER.sub("[redacted]", first_line)[:100]', "return first_line[:100]", HOOKS),
    ("the guards stop failing closed at the harness", "kit/.claude/settings.json", '"onFailure": "block"', '"onFailure": "continue"', HOOKS),
    ("the settings stop denying .env reads", "kit/.claude/settings.json", '      "Read(.env)",\n', "", HOOKS),
    ("guard.json stops protecting the workflow files", "kit/.claude/guard.json", '    ".claude/workflow-docs/**",\n', "", HOOKS),
    ("guard.json stops blocking environment dumps", "kit/.claude/guard.json", '    "\\\\b(export\\\\s+-p|declare\\\\s+-[a-z]*[xp])\\\\b",\n', "", HOOKS),
    ("the rule reads the document text", RULES, "rule_passed = registration_matches(supplier, registry_record)", 'rule_passed = registration_matches(supplier, registry_record) and "ignore" not in str(supplier.get("document_text", ""))', "tests/test_rules.py"),
    ("the register check goes back to substring matching", "kit/.claude/skills/scenario-register/SKILL.md", 'and row["fixture_id"] not in collected:', 'and row["fixture_id"] not in "\\n".join(collected):', STRUCTURE),
    ("the proof-and-label check forgets one label", "kit/.claude/skills/invariants/SKILL.md", ' + match($0,/Proof: .+ Label: read[.]/)', "", STRUCTURE),
    ("the PowerShell matcher is dropped from the settings", "kit/.claude/settings.json", '"matcher": "Bash|PowerShell"', '"matcher": "Bash"', HOOKS),
    ("the ask rule for a plain push is dropped", "kit/.claude/settings.json", '"Bash(git push *)"', '"Bash(git push x)"', HOOKS),
    ("a hook script path in the settings is wrong", "kit/.claude/settings.json", "guard_paths.py", "guard_pathz.py", HOOKS),
    ("the hard-reset deny rule is dropped", "kit/.claude/settings.json", '      "Bash(git reset --hard*)",\n', "", HOOKS),
    ("the wildcard env deny rule is dropped", "kit/.claude/settings.json", '      "Read(*.env)",\n', "", HOOKS),
    ("tee is not recognised as a writer", BASH, "(tee|mv|", "(mv|", HOOKS),
    ("curl is not recognised as a writer", BASH, "|curl|wget|", "|wget|", HOOKS),
    ("PowerShell cmdlets are not recognised as writers", BASH, "(set|add|out|new|remove|move|copy|rename|clear)-(content|item|itemproperty)", "(zzz)-(content)", HOOKS),
    ("short names always trigger", BASH, "    if not short_names:\n        return [whole]\n", "", HOOKS),
    ("short names never trigger after a cd", BASH, "short = bool(CHANGES_DIRECTORY.search(command))", "short = False", HOOKS),
    ("secret file names with a prefix are not matched", "kit/.claude/guard.json", "])[\\\\w.*-]*\\\\.env", "])\\\\.env", HOOKS),
    ("a bare set is not treated as an environment dump", "kit/.claude/guard.json", "(env|set)", "(env)", HOOKS),
    ("strict mode passes without a banned list", CHECK, "        if strict_history:\n            failures.append(", "        if False:\n            failures.append(", CHECK_TESTS),
    ("number words stop at twelve", CHECK, "|dozen|score|hundred)", ")", CHECK_TESTS),
    ("only the fill marker counts as a placeholder", CHECK, 'PLACEHOLDER = re.compile(r"<<(?!OWNER)[A-Z]{3,}")', 'PLACEHOLDER = re.compile(r"<<FILL")', CHECK_TESTS),
    ("the committer is not scanned in history", CHECK, "%an%n%ae%n%cn%n%ce%n%B", "%an%n%ae%n%B", CHECK_TESTS),
    ("the log records the whole command, not its first line", LIB, "first_line = command.strip().splitlines()[0]", "first_line = command.strip()", HOOKS),
    ("the proof check ignores the stories", CHECK, '"example/", "stories/")', '"example/")', CHECK_TESTS),
]


def main() -> int:
    """Return the number of mutations that failed to turn their tests red."""
    bad = 0
    for name, relative, old, new, test_file in MUTATIONS:
        path = ROOT / relative
        original = path.read_bytes()
        text = original.decode()
        if old not in text:
            print("SETUP ERROR: text not found for mutation: " + name)
            bad += 1
            continue
        try:
            path.write_text(text.replace(old, new, 1))
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-q", "-x", "--no-header", "-p", "no:cacheprovider"],
                cwd=ROOT, capture_output=True, text=True,
            )
        finally:
            path.write_bytes(original)
        red = result.returncode != 0
        first = next((line for line in result.stdout.splitlines() if line.startswith("FAILED")), "")
        print(("RED (good)         " if red else "STILL GREEN (bad)  ") + name + "  " + first[:100])
        bad += 0 if red else 1
    print("mutations that stayed green or failed setup: " + str(bad))
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
