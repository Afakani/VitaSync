"""Prueft die Beispieldateien in contracts/ gegen ihr Schema.

Aufruf:
    python scripts/validate_contracts.py              # prueft contracts/
    python scripts/validate_contracts.py <ordner>     # prueft einen anderen Baum

OpenAPI 3.1 verwendet JSON Schema 2020-12, deshalb validiert `jsonschema`
direkt gegen die Eintraege unter `components/schemas`.

Welche Datei gegen welches Schema geprueft wird, steht nicht hier, sondern im
Vertrag selbst: jedes Beispiel ist dort unter `examples:` mit `externalValue`
eingetragen. Ein Beispiel ohne Eintrag faellt damit auf, statt stillschweigend
ungeprueft zu bleiben.

Exit 1, sobald ein Beispiel nicht passt, ein Eintrag fehlt oder eine
referenzierte Datei nicht existiert. Kein Ersatz fuer einen vollstaendigen
OpenAPI-Validator: geprueft werden die Beispiele, nicht das Dokument selbst.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_BASE = "https://vitasync.local/contracts/"


def zeige(pfad: Path) -> str:
    """Pfad relativ zum Repo, falls moeglich - sonst absolut (Tests nutzen tmp-Ordner)."""
    return str(pfad.relative_to(ROOT)) if pfad.is_relative_to(ROOT) else str(pfad)


def finde_vertraege(basis: Path) -> list[Path]:
    """Alle handgepflegten OpenAPI-Entwuerfe unterhalb von `basis`."""
    return sorted(basis.rglob("*.openapi.yaml"))


def sammle_beispiele(spec: dict, vertrag: Path) -> list[tuple[Path, str]]:
    """Liefert (Beispieldatei, Schemaname) aus allen `examples`-Bloecken.

    Sucht rekursiv nach Stellen, die zugleich `schema` und `examples` tragen -
    also Request-Body und Antworten.
    """
    treffer: list[tuple[Path, str]] = []

    def gehe(knoten: object) -> None:
        if isinstance(knoten, dict):
            schema = knoten.get("schema")
            beispiele = knoten.get("examples")
            if isinstance(schema, dict) and isinstance(beispiele, dict):
                ref = schema.get("$ref", "")
                name = ref.rsplit("/", 1)[-1] if ref else ""
                for eintrag in beispiele.values():
                    if isinstance(eintrag, dict) and "externalValue" in eintrag:
                        pfad = (vertrag.parent / eintrag["externalValue"]).resolve()
                        treffer.append((pfad, name))
            for wert in knoten.values():
                gehe(wert)
        elif isinstance(knoten, list):
            for wert in knoten:
                gehe(wert)

    gehe(spec)
    return treffer


def pruefe_vertrag(vertrag: Path, probleme: list[str]) -> int:
    """Prueft alle Beispiele eines Vertrags. Gibt die Anzahl gepruefter Dateien zurueck."""
    spec = yaml.safe_load(vertrag.read_text(encoding="utf-8"))
    schemas = spec.get("components", {}).get("schemas", {})
    if not schemas:
        probleme.append(f"{zeige(vertrag)}: keine components/schemas gefunden")
        return 0

    # Der ganze Vertrag wird als Dokument registriert, damit '#/components/...'
    # innerhalb der Schemas aufloesbar bleibt.
    registry = Registry().with_resource(
        CONTRACT_BASE, Resource.from_contents(spec, default_specification=DRAFT202012)
    )

    beispiele = sammle_beispiele(spec, vertrag)
    if not beispiele:
        probleme.append(f"{zeige(vertrag)}: keine Beispiele mit externalValue eingetragen")

    eingetragen = {pfad for pfad, _ in beispiele}
    vorhanden = {p.resolve() for p in (vertrag.parent / "examples").glob("*.json")}
    for verwaist in sorted(vorhanden - eingetragen):
        probleme.append(
            f"{zeige(verwaist)}: liegt in examples/, ist im Vertrag aber "
            f"unter keinem 'externalValue' eingetragen und wird daher nicht geprueft"
        )

    geprueft = 0
    for pfad, schemaname in sorted(set(beispiele)):
        rel = zeige(pfad)
        if not pfad.is_file():
            probleme.append(f"{zeige(vertrag)}: Beispieldatei fehlt: {rel}")
            continue
        if schemaname not in schemas:
            probleme.append(f"{rel}: Schema '{schemaname}' gibt es im Vertrag nicht")
            continue
        try:
            daten = json.loads(pfad.read_text(encoding="utf-8"))
        except json.JSONDecodeError as fehler:
            probleme.append(f"{rel}: kein gueltiges JSON ({fehler})")
            continue

        validator = Draft202012Validator(
            {"$ref": f"{CONTRACT_BASE}#/components/schemas/{schemaname}"},
            registry=registry,
        )
        fehler_liste = sorted(validator.iter_errors(daten), key=lambda f: list(f.path))
        for fehler in fehler_liste:
            stelle = "/".join(str(teil) for teil in fehler.path) or "(Wurzel)"
            probleme.append(f"{rel} [{schemaname}] {stelle}: {fehler.message}")
        if not fehler_liste:
            print(f"ok   {rel} ({schemaname})")
        geprueft += 1
    return geprueft


def main(argv: list[str]) -> int:
    basis = Path(argv[1]).resolve() if len(argv) > 1 else ROOT / "contracts"
    if not basis.is_dir():
        print(f"Ordner nicht gefunden: {basis}")
        return 1

    vertraege = finde_vertraege(basis)
    if not vertraege:
        print(f"Keine *.openapi.yaml unter {basis} gefunden.")
        return 1

    probleme: list[str] = []
    gesamt = sum(pruefe_vertrag(vertrag, probleme) for vertrag in vertraege)

    for problem in probleme:
        print(f"FEHLER {problem}")
    if probleme:
        print(f"\n{gesamt} Beispiel(e) geprueft, {len(probleme)} Problem(e).")
        return 1
    print(f"\nPASS: {gesamt} Beispiel(e) in {len(vertraege)} Vertrag/Vertraegen gueltig.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
