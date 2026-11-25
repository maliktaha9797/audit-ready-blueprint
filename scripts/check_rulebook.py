"""Check the repository for rulebook drift and for things that must not be published.

Run from the repository root:  python scripts/check_rulebook.py [--strict-history]
Standard library only. Exit code 0 means every check passed. Exit code 1 means at
least one failed. Warnings (owner stubs still to write) never change the exit code.

Checks:
  banned-terms         no term from the banned list appears in any file but the list
  history              no term from the banned list appears in a commit's author,
                       committer or message, or in a branch or tag name
  em-dash              no em dash in any text file
  prose-count          no "<number> invariants" or "<number> rules" in any Markdown file
  reference-integrity  every agent, skill, command and workflow named under kit/ exists,
                       and every INV id used is defined in the relevant invariants table
  proof-integrity      every test id cited in any Markdown file exists in tests/
  links                every relative Markdown link resolves
  size-cap             every summary.md is within its line cap
  slots                no unfilled slot marker outside kit/ and templates/

The history check reports a warning by default, because only the repository owner
can rewrite authorship. Pass --strict-history to make it a failure, and do so before
publishing. Strict mode also fails if there is no banned list to check against, so a
missing list cannot look like a clean history. A warning never prints the term, only which entry of the list matched.

The banned list is read from scripts/banned_terms.txt, which is git-ignored. If that
file is absent the list is read from the BANNED_TERMS environment variable, one term
per line. If neither exists the banned-terms check is skipped, with a warning.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".py", ".json", ".txt", ".csv", ".toml", ".yml", ".yaml"}
TEXT_NAMES = {"LICENSE", ".gitignore"}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}
BANNED_FILES = {"scripts/banned_terms.txt"}
SUMMARY_CAP = 120
EM_DASH = chr(0x2014)
PLACEHOLDER = re.compile(r"<<(?!OWNER)[A-Z]{3,}")
OWNER_MARKERS = ("<!-- " + "OWNER:", "<<" + "OWNER:")
NUMBER_WORDS = (r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
                r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|dozen|score|hundred)")
PROSE_COUNT = re.compile(
    r"\b" + NUMBER_WORDS + r"\s+(?:of\s+(?:the|these|those|our|its)\s+(?:[\w'\u2019-]+\s+){0,2})?(invariants|rules)\b",
    re.I,
)
FENCE = re.compile(r"(?s)```.*?```")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
TEST_ID = re.compile(r"tests/(\w+)\.py::(\w+)")
INV_ID = re.compile(r"INV-\d+")
INV_ROW = re.compile(r"(?m)^\| (INV-\d+) \|")
BUILT_IN_COMMANDS = {"hooks", "permissions", "status"}


def list_files(root: Path) -> list[str]:
    """Return the repository's files as relative paths. Uses git when available."""
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root, capture_output=True, text=True,
        )
        if result.returncode == 0:
            return [name for name in result.stdout.splitlines() if (root / name).is_file()]
    found = []
    for folder, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            found.append(Path(folder, name).relative_to(root).as_posix())
    return sorted(found)


def read_texts(root: Path, files: list[str]) -> dict[str, str]:
    """Return the text of every text file, keyed by relative path."""
    texts = {}
    for name in files:
        path = Path(name)
        if path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES:
            try:
                texts[name] = (root / name).read_text()
            except UnicodeDecodeError:
                continue
    return texts


def finding(check: str, where: str, message: str) -> dict:
    """Build one finding."""
    return {"check": check, "where": where, "message": message}


def line_of(text: str, index: int) -> int:
    """Return the 1-based line number of a character index."""
    return text.count("\n", 0, index) + 1


def load_banned_terms(root: Path, env: dict) -> list[str] | None:
    """Return the banned terms, or None if no list exists in the file or the environment."""
    path = root / "scripts" / "banned_terms.txt"
    if path.is_file():
        text = path.read_text()
    elif env.get("BANNED_TERMS"):
        text = env["BANNED_TERMS"]
    else:
        return None
    return [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]


def term_pattern(term: str) -> re.Pattern:
    """A term of four characters or fewer matches whole words only. A longer one matches anywhere."""
    escaped = re.escape(term)
    if len(term) <= 4:
        return re.compile(r"(?<![A-Za-z0-9_])" + escaped + r"(?![A-Za-z0-9_])", re.I)
    return re.compile(escaped, re.I)


def check_banned_terms(texts: dict, terms: list[str]) -> list[dict]:
    """No banned term appears in any text, or in any file name, other than the list itself."""
    patterns = [term_pattern(term) for term in terms]
    found = []
    for name, text in texts.items():
        if name in BANNED_FILES:
            continue
        for number, pattern in enumerate(patterns, 1):
            if pattern.search(name) or pattern.search(text):
                found.append(finding("banned-terms", name, "matches entry " + str(number) + " of the banned list"))
    return found


def history_blocks(root: Path) -> list[tuple[str, str]] | None:
    """Return (short hash, text) for each commit, or None if this is not a git repository.

    The text is the author and committer names and emails, the message, and the names
    of the branches and tags that point at the commit.
    """
    if not (root / ".git").exists():
        return None
    fmt = "%h%x1f%an%n%ae%n%cn%n%ce%n%B%n%D%x1e"
    result = subprocess.run(["git", "log", "--all", "--format=" + fmt], cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    blocks = []
    for chunk in result.stdout.split("\x1e"):
        if "\x1f" in chunk:
            short, text = chunk.strip().split("\x1f", 1)
            blocks.append((short, text))
    return blocks


def check_history(root: Path, terms: list[str]) -> list[dict]:
    """No banned term in any commit's author, committer, message or ref names. Never prints the term."""
    patterns = [term_pattern(term) for term in terms]
    found = []
    for short, text in history_blocks(root) or []:
        for number, pattern in enumerate(patterns, 1):
            if pattern.search(text):
                found.append(finding("history", "commit " + short, "matches entry " + str(number) + " of the banned list"))
    return found


def check_em_dashes(texts: dict) -> list[dict]:
    """No em dash in any text file."""
    return [finding("em-dash", name + ":" + str(line_of(text, text.index(EM_DASH))), "contains an em dash")
            for name, text in texts.items() if EM_DASH in text]


def check_prose_counts(texts: dict) -> list[dict]:
    """No count of invariants or rules written in prose. Counts drift. The table is the only source."""
    found = []
    for name, text in texts.items():
        match = PROSE_COUNT.search(text) if name.endswith(".md") else None
        if match:
            found.append(finding("prose-count", name + ":" + str(line_of(text, match.start())), "writes a count: " + match.group(0)))
    return found


def invariant_ids(text: str) -> set:
    """The ids defined as rows in an invariants table."""
    return set(INV_ROW.findall(text))


def table_names(text: str, heading: str) -> list[str]:
    """Backticked names in the first column of the table under a '## heading'."""
    section = re.search(r"(?ms)^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", text)
    names = []
    for line in (section.group(1).splitlines() if section else []):
        cells = line.split("|")
        if line.startswith("|") and len(cells) > 2:
            match = re.fullmatch(r"`/?([\w-]+)(?: [^`]*)?`", cells[1].strip())
            if match:
                names.append(match.group(1))
    return names


def check_references(root: Path, texts: dict) -> list[dict]:
    """Everything named under kit/ exists, and every invariant id is defined where it should be."""
    found = []
    kit = root / "kit" / ".claude"
    kit_table = texts.get("kit/.claude/skills/invariants/SKILL.md", "")
    example_table = texts.get("example/invariants.md", "")
    kit_ids, example_ids = invariant_ids(kit_table), invariant_ids(example_table)
    commands = {p.name for p in (kit / "skills").glob("*") if "disable-model-invocation: true" in
                texts.get("kit/.claude/skills/" + p.name + "/SKILL.md", "")} if kit.exists() else set()
    for name, text in texts.items():
        if name.startswith("kit/") and name.endswith(".md"):
            plain = FENCE.sub("", text)
            for ref in re.findall(r"\.claude/workflow-docs/([\w-]+)\.md", plain):
                if not (kit / "workflow-docs" / (ref + ".md")).is_file():
                    found.append(finding("reference-integrity", name, "names a workflow that does not exist: " + ref))
            for ref in re.findall(r"\.claude/skills/([\w-]+)/SKILL\.md", plain):
                if not (kit / "skills" / ref / "SKILL.md").is_file():
                    found.append(finding("reference-integrity", name, "names a skill that does not exist: " + ref))
            for ref in re.findall(r"\.claude/agents/([\w.-]+\.md)", plain):
                if not (kit / "agents" / ref).is_file():
                    found.append(finding("reference-integrity", name, "names an agent that does not exist: " + ref))
            for ref in re.findall(r"`/([a-z][a-z-]*)(?: [^`]*)?`", plain):
                if ref not in commands and ref not in BUILT_IN_COMMANDS:
                    found.append(finding("reference-integrity", name, "names a command that does not exist: /" + ref))
        if name == "kit/CLAUDE.md":
            for heading, kind, base in (("Agents", "agent", kit / "agents"), ("Skills", "skill", kit / "skills"), ("Commands", "command", kit / "skills")):
                for ref in table_names(text, heading):
                    target = base / (ref + ".md") if kind == "agent" else base / ref / "SKILL.md"
                    if not target.is_file():
                        found.append(finding("reference-integrity", name, "table names a " + kind + " that does not exist: " + ref))
        if name.startswith("kit/.claude/agents/") and name.endswith(".md") and text.startswith("---"):
            block = re.search(r"(?m)^skills:\n((?:  - .*\n)+)", text)
            for ref in (re.findall(r"- (\S+)", block.group(1)) if block else []):
                if not (kit / "skills" / ref / "SKILL.md").is_file():
                    found.append(finding("reference-integrity", name, "preloads a skill that does not exist: " + ref))
        if Path(name).suffix in {".md", ".py", ".json", ".csv"} and not name.startswith(("scripts/", "tests/")):
            allowed = kit_ids if name.startswith("kit/") else example_ids if name.startswith("example/") else kit_ids | example_ids
            for cited in sorted(set(INV_ID.findall(text))):
                if cited not in allowed:
                    found.append(finding("reference-integrity", name, "cites " + cited + ", which no invariants table defines for this file"))
    return found


def test_names_in(root: Path, module: str) -> set | None:
    """The names of the test functions in tests/<module>.py, or None if the file is missing."""
    path = root / "tests" / (module + ".py")
    if not path.is_file():
        return None
    tree = ast.parse(path.read_text())
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


PROOF_SCOPES = ("README.md", "CASE-STUDY.md", "BUILD-REPORT.md", "docs/", "demo/", "example/", "stories/")


def check_proof_ids(root: Path, texts: dict) -> list[dict]:
    """Every test id cited as proof in the README, case study, build report, docs, demo, example or stories exists in tests/.

    The kit and the templates are not checked: their test ids are generic samples.
    """
    found = []
    for name, text in texts.items():
        if not name.endswith(".md") or not name.startswith(PROOF_SCOPES):
            continue
        for module, test in sorted(set(TEST_ID.findall(text))):
            names = test_names_in(root, module)
            if names is None or test not in names:
                found.append(finding("proof-integrity", name, "cites tests/" + module + ".py::" + test + ", which does not exist"))
    return found


def check_links(root: Path, texts: dict) -> list[dict]:
    """Every relative Markdown link resolves to a file or folder."""
    found = []
    for name, text in texts.items():
        if not name.endswith(".md"):
            continue
        for target in LINK.findall(FENCE.sub("", text)):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#")[0].split("?")[0]
            base = root if clean.startswith("/") else (root / name).parent
            if clean and not (base / clean.lstrip("/")).exists():
                found.append(finding("links", name, "link does not resolve: " + target))
    return found


def check_size_caps(texts: dict) -> list[dict]:
    """Every summary.md is within its line cap."""
    return [finding("size-cap", name, "has " + str(len(text.splitlines())) + " lines, over the cap of " + str(SUMMARY_CAP))
            for name, text in texts.items() if Path(name).name == "summary.md" and len(text.splitlines()) > SUMMARY_CAP]


def check_slots(texts: dict) -> list[dict]:
    """No unfilled slot or placeholder outside kit/ and templates/. Python files may name the marker.

    A slot is two opening angle brackets and a capitalised word, such as the fill marker.
    The owner marker is not a slot: it is counted separately as a publication checklist.
    """
    found = []
    for name, text in texts.items():
        if name.startswith(("kit/", "templates/")) or name.endswith(".py"):
            continue
        match = PLACEHOLDER.search(text)
        if match:
            found.append(finding("slots", name + ":" + str(line_of(text, match.start())), "has an unfilled slot or placeholder"))
    return found


def owner_stubs(texts: dict) -> list[str]:
    """Where an owner stub is still to be written, as 'file:line' strings."""
    places = []
    for name, text in texts.items():
        if name.endswith(".py"):
            continue
        for marker in OWNER_MARKERS:
            for match in re.finditer(re.escape(marker), text):
                places.append(name + ":" + str(line_of(text, match.start())))
    return places


def run_checks(root: Path, env: dict, strict_history: bool = False) -> tuple[list[dict], list[str], list[str]]:
    """Run every check. Return the failures, the warnings and the owner stubs.

    A history finding is a warning unless strict_history is true, because only the
    repository owner can rewrite authorship.
    """
    texts = read_texts(root, list_files(root))
    failures, warnings = [], []
    terms = load_banned_terms(root, env)
    if terms is None:
        warnings.append("banned-terms check skipped: no scripts/banned_terms.txt and no BANNED_TERMS variable")
        if strict_history:
            failures.append(finding("banned-terms", "scripts/banned_terms.txt", "strict mode needs the banned list: add the file or set BANNED_TERMS"))
    else:
        failures += check_banned_terms(texts, terms)
        history = check_history(root, terms)
        if strict_history:
            failures += history
        else:
            warnings += ["history: " + item["where"] + " " + item["message"] + ". Rewrite history before publishing, then run with --strict-history." for item in history]
    failures += check_em_dashes(texts) + check_prose_counts(texts) + check_references(root, texts)
    failures += check_proof_ids(root, texts) + check_links(root, texts) + check_size_caps(texts) + check_slots(texts)
    return failures, warnings, owner_stubs(texts)


def main(argv: list[str]) -> int:
    """Run the checks, print the result, and return the exit code."""
    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else Path(__file__).resolve().parents[1]
    failures, warnings, stubs = run_checks(root, dict(os.environ), strict_history="--strict-history" in argv)
    for item in failures:
        print("FAIL [" + item["check"] + "] " + item["where"] + ": " + item["message"])
    for warning in warnings:
        print("WARN " + warning)
    if stubs:
        print("OWNER STUBS still to write, a publication checklist:")
        for place in stubs:
            print("  - " + place)
    print("check_rulebook: " + ("FAILED" if failures else "passed") + ", " + str(len(failures)) + " failure(s), " + str(len(stubs)) + " owner stub(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
