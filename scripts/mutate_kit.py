"""Mutate-to-red proof for the kit's detection tests (invariant INV-06).

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
