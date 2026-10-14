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
KNOWLEDGE_FIELDS = ["id", "titel", "status", "sprache", "version", "herausgeber",
                    "quelle", "reviewer", "review_datum"]
# 'testfreigabe' ist eine befristete Ausnahme aus D10 (Testlauf).
KNOWLEDGE_STATUS = {"entwurf", "testfreigabe", "geprueft"}
KNOWLEDGE_LANGUAGES = {"de", "en"}
# Kategorien, ohne die weder Notfallhinweis noch Fallback funktionieren.
KNOWLEDGE_REQUIRED_REVIEWED = {"knowledge/rules", "knowledge/care_paths"}
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


def check_knowledge(problems, warnings):
    for rel_dir in KNOWLEDGE_DIRS:
        reviewed = 0
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
            if status not in KNOWLEDGE_STATUS:
                allowed = " or ".join(repr(s) for s in sorted(KNOWLEDGE_STATUS))
                problems.append(f"{rel}: status must be {allowed}")
            if status == "geprueft":
                reviewed += 1
                for field in ("quelle", "herausgeber", "reviewer", "review_datum"):
                    if not meta.get(field) or meta[field].startswith("<"):
                        problems.append(f"{rel}: 'geprueft' requires '{field}'")
            if status == "testfreigabe":
                # D10: erlaubt, aber nicht fachlich geprueft - sichtbar halten.
                warnings.append(f"{rel}: status 'testfreigabe' - not reviewed, "
                                f"loaded only with APP_ENV=development (D10)")

            language = meta.get("sprache")
            if language not in KNOWLEDGE_LANGUAGES:
                allowed = " or ".join(repr(s) for s in sorted(KNOWLEDGE_LANGUAGES))
                problems.append(f"{rel}: 'sprache' must be {allowed}")
            # Dateiname traegt die Sprache: <name>.<sprache>.md
            suffixes = file.name.split(".")
            if len(suffixes) != 3 or suffixes[-1] != "md":
                problems.append(f"{rel}: file name must be '<name>.<sprache>.md'")
            elif language and suffixes[1] != language:
                problems.append(f"{rel}: file name says '{suffixes[1]}', "
                                f"front matter says '{language}'")

            version = meta.get("version", "")
            if not re.fullmatch(r"[1-9]\d*", version or ""):
                problems.append(f"{rel}: 'version' must be a whole number >= 1")

        if not reviewed and rel_dir in KNOWLEDGE_REQUIRED_REVIEWED:
            warnings.append(f"{rel_dir}: no entry with status 'geprueft' - "
                            f"the category is not usable yet (TEST-001 B8)")


def check_decisions(problems):
    """Prueft Kopfdaten der Entscheidungen und den Abgleich mit der Statustabelle."""
    listed = {}
    index = ROOT / "docs/decisions/README.md"
    if index.is_file():
        for ident, status in re.findall(
            r"\|\s*\[(D\d+)\]\([^)]+\)\s*\|[^|]*\|\s*([a-z]+)\s*\|",
            index.read_text(encoding="utf-8"),
        ):
            listed[ident] = status

    seen = set()
    for file in sorted((ROOT / "docs/decisions").glob("D[0-9]*.md")):
        rel = file.relative_to(ROOT)
        meta = frontmatter(file.read_text(encoding="utf-8")) or {}
        status = meta.get("status")
        if status not in DECISION_STATUS:
            problems.append(f"{rel}: invalid status {status!r}")
        if status == "bestaetigt" and not (meta.get("bestaetigt_von") and meta.get("bestaetigt_am")):
            problems.append(f"{rel}: 'bestaetigt' requires bestaetigt_von and bestaetigt_am")

        ident = meta.get("id") or file.name.split("-")[0]
        seen.add(ident)
        # TEST-001 B8: Tabelle und Kopfdaten duerfen nicht auseinanderlaufen.
        if ident not in listed:
            problems.append(f"{rel}: not listed in docs/decisions/README.md")
        elif listed[ident] != status:
            problems.append(f"{rel}: status {status!r} but README.md says "
                            f"{listed[ident]!r}")

    for ident in sorted(set(listed) - seen):
        problems.append(f"docs/decisions/README.md: lists {ident}, but no such file")


def check():
    """Gibt (problems, warnings) zurueck. Nur problems setzen den Exit-Code."""
    fix = "--fix" in sys.argv
    problems = []
    warnings = []
    for name in REQUIRED_FILES:
        if not (ROOT / name).is_file():
            problems.append(f"missing required file: {name}")
    for name in FORBIDDEN_ROOT_DIRS:
        if (ROOT / name).exists():
            problems.append(f"forbidden root folder: {name}/ (see AGENTS.md)")
    check_agent_files(problems, fix)
    check_links(problems)
    check_knowledge(problems, warnings)
    check_decisions(problems)
    return problems, warnings


if __name__ == "__main__":
    findings, notes = check()
    for finding in findings:
        print(f"FEHLER  {finding}")
    for note in notes:
        print(f"WARNUNG {note}")
    if findings:
        sys.exit(1)
    summary = "PASS: structure, agent files, links, knowledge metadata, decisions."
    if notes:
        summary += f" {len(notes)} Warnung(en), kein Fehler."
    print(summary)
