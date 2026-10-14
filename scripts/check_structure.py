"""Check repository structure, agent files, links and knowledge metadata.

Standard library only. Read-only unless --fix is given, which only creates or
normalizes CLAUDE.md stubs next to existing AGENTS.md files.
Exit status 1 means at least one problem was found.

Not an application test and not a medical validation.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CLAUDE_STUB = "@AGENTS.md\n"
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", "build"}

# Directories that must always carry their own AGENTS.md.
REQUIRED_MODULES = [
    "apps/web",
    "apps/api",
    "apps/api/src/vitasync/api",
    "apps/api/src/vitasync/features",
    "apps/api/src/vitasync/core",
    "apps/api/src/vitasync/security",
    "apps/api/src/vitasync/adapters/llm",
    "apps/api/src/vitasync/adapters/fhir",
    "apps/api/src/vitasync/adapters/db",
    "apps/api/migrations",
    "contracts",
    "knowledge",
    "evals",
    "data/synthetic",
    "infra",
]
# Every direct subfolder of these directories is a module and needs AGENTS.md.
MODULE_PARENTS = ["apps/api/src/vitasync/features"]
REQUIRED_FILES = ["AGENTS.md", "CLAUDE.md", "README.md", "docs/Start.md",
                  "docs/decisions/README.md"]
FORBIDDEN_ROOT_DIRS = ["src", "backend", "frontend", "utils"]
KNOWLEDGE_DIRS = ["knowledge/topics", "knowledge/rules", "knowledge/care_paths"]
KNOWLEDGE_FIELDS = ["id", "titel", "status", "quelle", "reviewer", "review_datum"]
DECISION_STATUS = {"offen", "empfohlen", "bestaetigt", "ersetzt"}


def walk(pattern):
    for path in ROOT.rglob(pattern):
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


def frontmatter(text):
    """Return simple 'key: value' pairs from a leading --- block, or None."""
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def check_agent_files(problems, fix):
    for rel in REQUIRED_MODULES:
        if not (ROOT / rel / "AGENTS.md").is_file():
            problems.append(f"{rel}: missing AGENTS.md")
    for parent in MODULE_PARENTS:
        base = ROOT / parent
        if base.is_dir():
            for sub in sorted(p for p in base.iterdir() if p.is_dir()):
                if sub.name.startswith((".", "_")):
                    continue
                if not (sub / "AGENTS.md").is_file():
                    problems.append(f"{sub.relative_to(ROOT)}: module without AGENTS.md")
    for agents in walk("AGENTS.md"):
        if agents.parent == ROOT:
            continue  # root CLAUDE.md has its own content
        claude = agents.parent / "CLAUDE.md"
        current = claude.read_text(encoding="utf-8") if claude.is_file() else None
        if current != CLAUDE_STUB:
            if fix:
                claude.write_text(CLAUDE_STUB, encoding="utf-8")
                print(f"fixed: {claude.relative_to(ROOT)}")
            else:
                problems.append(f"{claude.relative_to(ROOT)}: must contain exactly '@AGENTS.md' (run --fix)")
    for claude in walk("CLAUDE.md"):
        if not (claude.parent / "AGENTS.md").is_file():
            problems.append(f"{claude.relative_to(ROOT)}: CLAUDE.md without AGENTS.md")


def check_links(problems):
    vault = {p.stem: p for p in (ROOT / "docs").rglob("*.md")}
    for file in walk("*.md"):
        text = re.sub(r"```.*?```", "", file.read_text(encoding="utf-8"), flags=re.S)
        rel = file.relative_to(ROOT)
        for link in re.findall(r"\[\[([^\]]+)\]\]", text):
            target = link.split("|")[0].split("#")[0].strip()
            if target and target not in vault:
                problems.append(f"{rel}: missing wiki target {target}")
        for link in re.findall(r"\]\(([^)\s]+)\)", text):
            if "://" in link or link.startswith(("#", "mailto:")):
                continue
            target = link.split("#")[0]
            if target and not (file.parent / target).exists():
                problems.append(f"{rel}: missing link target {target}")


def check_knowledge(problems):
    for rel_dir in KNOWLEDGE_DIRS:
        for file in sorted((ROOT / rel_dir).glob("*.md")):
            rel = file.relative_to(ROOT)
            meta = frontmatter(file.read_text(encoding="utf-8"))
            if meta is None:
                problems.append(f"{rel}: missing front matter")
                continue
            for field in KNOWLEDGE_FIELDS:
                if field not in meta:
                    problems.append(f"{rel}: missing field '{field}'")
            status = meta.get("status")
            if status not in {"entwurf", "geprueft"}:
                problems.append(f"{rel}: status must be 'entwurf' or 'geprueft'")
            if status == "geprueft":
                for field in ("quelle", "reviewer", "review_datum"):
                    if not meta.get(field) or meta[field].startswith("<"):
                        problems.append(f"{rel}: 'geprueft' requires '{field}'")


def check_decisions(problems):
    for file in sorted((ROOT / "docs/decisions").glob("D[0-9]*.md")):
        rel = file.relative_to(ROOT)
        meta = frontmatter(file.read_text(encoding="utf-8")) or {}
        if meta.get("status") not in DECISION_STATUS:
            problems.append(f"{rel}: invalid status {meta.get('status')!r}")
        if meta.get("status") == "bestaetigt" and not (meta.get("bestaetigt_von") and meta.get("bestaetigt_am")):
            problems.append(f"{rel}: 'bestaetigt' requires bestaetigt_von and bestaetigt_am")


def check():
    fix = "--fix" in sys.argv
    problems = []
    for name in REQUIRED_FILES:
        if not (ROOT / name).is_file():
            problems.append(f"missing required file: {name}")
    for name in FORBIDDEN_ROOT_DIRS:
        if (ROOT / name).exists():
            problems.append(f"forbidden root folder: {name}/ (see AGENTS.md)")
    check_agent_files(problems, fix)
    check_links(problems)
    check_knowledge(problems)
    check_decisions(problems)
    return problems


if __name__ == "__main__":
    findings = check()
    for finding in findings:
        print(finding)
    if findings:
        sys.exit(1)
    print("PASS: structure, agent files, links, knowledge metadata, decisions.")
