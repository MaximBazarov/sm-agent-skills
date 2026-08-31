#!/usr/bin/env python3
"""Render swift symbolgraph-extract JSON as a Markdown API surface.

Called by generate-api-surface.sh. Output is sorted so that regenerating an
unchanged library produces a byte-identical file.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

# Rendered in this order, so a reader meets the protocols before their conformers.
KIND_ORDER = [
    ("swift.protocol", "Protocols"),
    ("swift.class", "Classes"),
    ("swift.struct", "Structs"),
    ("swift.enum", "Enums"),
    ("swift.func.op", "Operators"),
]
MEMBER_KIND_LABEL = {
    "swift.init": "init",
    "swift.method": "method",
    "swift.type.method": "static method",
    "swift.property": "property",
    "swift.type.property": "static property",
    "swift.enum.case": "case",
    "swift.associatedtype": "associatedtype",
}


def declaration(symbol):
    return "".join(f["spelling"] for f in symbol.get("declarationFragments", []))


def summary(symbol):
    """First paragraph of the doc comment, as one line."""
    lines = [line["text"] for line in symbol.get("docComment", {}).get("lines", [])]
    paragraph = []
    for line in lines:
        if not line.strip():
            break
        paragraph.append(line.strip())
    return " ".join(paragraph)


def readable_usr(precise):
    """Recover a plain name from a mangled USR for a symbol outside this module.

    Swift mangles names length-prefixed, so `s:s8SendableP` carries `Sendable`.
    Only the trailing component is wanted: it is the type being named.
    """
    tail = precise.split(":")[-1]
    names, i = [], 0
    while i < len(tail):
        if tail[i].isdigit():
            j = i
            while j < len(tail) and tail[j].isdigit():
                j += 1
            length = int(tail[i:j])
            names.append(tail[j:j + length])
            i = j + length
        else:
            i += 1
    return names[-1] if names else tail


def load(paths):
    symbols, relationships = {}, []
    for path in paths:
        graph = json.loads(Path(path).read_text())
        for symbol in graph["symbols"]:
            symbols[symbol["identifier"]["precise"]] = symbol
        relationships.extend(graph["relationships"])
    return symbols, relationships


def render(module_name, graph_paths, out):
    symbols, relationships = load(graph_paths)

    members = defaultdict(list)
    conformances = defaultdict(list)
    requirements = set()
    defaulted = set()
    for rel in relationships:
        if rel["kind"] == "memberOf":
            members[rel["target"]].append(rel["source"])
        elif rel["kind"] == "conformsTo":
            conformances[rel["source"]].append(rel["target"])
        elif rel["kind"] == "requirementOf":
            # A protocol requirement hangs off its protocol by this edge, not memberOf.
            members[rel["target"]].append(rel["source"])
            requirements.add(rel["source"])
        elif rel["kind"] == "defaultImplementationOf":
            defaulted.add(rel["target"])

    def type_name(precise):
        symbol = symbols.get(precise)
        if symbol:
            return ".".join(symbol["pathComponents"])
        return readable_usr(precise)

    out.append(f"## {module_name}")
    out.append("")

    top_level = [s for s in symbols.values() if len(s["pathComponents"]) == 1]
    for kind, heading in KIND_ORDER:
        group = sorted(
            (s for s in top_level if s["kind"]["identifier"] == kind),
            key=lambda s: s["names"]["title"],
        )
        if not group:
            continue
        out.append(f"### {heading}")
        out.append("")
        for symbol in group:
            render_type(symbol, out, symbols, members, conformances, requirements, defaulted, type_name)


def render_type(symbol, out, symbols, members, conformances, requirements, defaulted, type_name):
    precise = symbol["identifier"]["precise"]
    out.append(f"#### {symbol['names']['title']}")
    out.append("")
    out.append("```swift")
    out.append(declaration(symbol))
    out.append("```")
    out.append("")

    text = summary(symbol)
    if text:
        out.append(text)
        out.append("")

    conforms = sorted({type_name(t) for t in conformances.get(precise, [])})
    if conforms:
        out.append(f"Conforms to: {', '.join(f'`{c}`' for c in conforms)}.")
        out.append("")

    own = [symbols[m] for m in members.get(precise, []) if m in symbols]
    if not own:
        return

    def sort_key(member):
        kinds = [k for k, _ in enumerate(MEMBER_KIND_LABEL)]
        order = list(MEMBER_KIND_LABEL).index(member["kind"]["identifier"]) \
            if member["kind"]["identifier"] in MEMBER_KIND_LABEL else len(kinds)
        return (order, declaration(member))

    out.append("```swift")
    for member in sorted(own, key=sort_key):
        line = declaration(member)
        marks = []
        if member["identifier"]["precise"] in requirements:
            marks.append("requirement")
        if member["identifier"]["precise"] in defaulted:
            marks.append("has default")
        out.append(f"{line}{'  // ' + ', '.join(marks) if marks else ''}")
    out.append("```")
    out.append("")


def main():
    release, anchor, generated_by = sys.argv[1], sys.argv[2], sys.argv[3]
    groups = sys.argv[4:]  # module=path[,path] ...

    out = [
        "# StateManagement public API surface",
        "",
        "<!-- GENERATED. Do not edit. Regenerate with scripts/generate-api-surface.sh -->",
        "",
        f"- **Library release**: `{release}`",
        f"- **Anchor commit**: `{anchor}`",
        f"- **Generated by**: {generated_by}",
        "",
        "This is the whole public surface at that anchor, and nothing else: no advice, no examples,"
        " no judgement. The skills hold the judgement and name no symbols, so this file is the only"
        " place a signature appears.",
        "",
        "Check the anchor above against your `Package.resolved` before trusting a signature. On a"
        " mismatch, regenerate against your own resolved version and prefer that copy.",
        "",
        "A `// requirement` comment marks a protocol requirement you must implement;"
        " `// has default` marks one the library already implements for you.",
        "",
    ]

    for group in groups:
        module_name, paths = group.split("=", 1)
        render(module_name, paths.split(","), out)

    sys.stdout.write("\n".join(out).rstrip() + "\n")


if __name__ == "__main__":
    main()
