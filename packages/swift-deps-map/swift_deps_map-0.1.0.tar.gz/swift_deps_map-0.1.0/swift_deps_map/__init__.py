#!/usr/bin/env python3
"""
Lightweight Swift file-level dependency mapper.

What it does:
- Scans Swift files under a root directory (default: current directory).
- Detects locally defined symbols (class/struct/enum/protocol/actor/extension).
- Finds cross-file references by matching symbol names against other files.
- Emits a plain-text report and optional JSON payload describing dependencies.

Example usage:
    swift-deps-map --root ./Sources --graph-format mermaid --graph-output deps.mmd
    swift-deps-map --json deps.json --focus Views/LoginViews Services/Authentication
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

__version__ = "0.1.0"
DEFAULT_ROOT = Path(".")
DEFAULT_MAX_FILES = 0


SYMBOL_DEF_RE = re.compile(
    r"\b(?:class|struct|enum|protocol|actor|extension)\s+([A-Z][A-Za-z0-9_]*)"
)
SYMBOL_TOKEN_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\b")

BUILTIN_SYMBOLS: set[str] = {
    # Swift / Foundation primitives
    "String",
    "Int",
    "Double",
    "Float",
    "Bool",
    "Data",
    "Date",
    "URL",
    "UUID",
    "Array",
    "Dictionary",
    "Set",
    "Optional",
    "Result",
    "Never",
    "Any",
    "AnyObject",
    "CGFloat",
    # Common framework types that should not be treated as project edges
    "Color",
    "Image",
    "View",
    "Task",
    "DispatchQueue",
    "UserDefaults",
    "NotificationCenter",
    "UIScreen",
    "UIApplication",
    "Scene",
    "ScenePhase",
    "CGRect",
    "CGSize",
    "CGPoint",
}


@dataclass
class FileSymbols:
    """Symbols defined and referenced in a single file."""

    path: Path
    defines: set[str] = field(default_factory=set)
    references: set[str] = field(default_factory=set)


def discover_swift_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.swift") if p.is_file())


def parse_defined_symbols(text: str) -> set[str]:
    return set(SYMBOL_DEF_RE.findall(text))


def parse_referenced_symbols(text: str) -> set[str]:
    return set(SYMBOL_TOKEN_RE.findall(text))


def build_symbol_index(files: Iterable[Path]) -> tuple[dict[str, Path], dict[str, list[Path]], dict[Path, FileSymbols]]:
    symbol_to_file: dict[str, Path] = {}
    collisions: dict[str, list[Path]] = defaultdict(list)
    file_data: dict[Path, FileSymbols] = {}

    for path in files:
        contents = path.read_text(encoding="utf-8", errors="ignore")
        defined = {s for s in parse_defined_symbols(contents) if s not in BUILTIN_SYMBOLS}
        referenced = parse_referenced_symbols(contents)
        file_data[path] = FileSymbols(path=path, defines=defined, references=referenced)

        for symbol in defined:
            if symbol in symbol_to_file:
                # Track duplicates without overwriting the first hit
                collisions[symbol].append(path)
            else:
                symbol_to_file[symbol] = path

    return symbol_to_file, collisions, file_data


def build_dependencies(
    symbol_to_file: Mapping[str, Path], file_data: Mapping[Path, FileSymbols]
) -> dict[Path, set[Path]]:
    dependencies: dict[Path, set[Path]] = defaultdict(set)

    for path, data in file_data.items():
        for symbol in data.references:
            target = symbol_to_file.get(symbol)
            if not target:
                continue
            if target == path:
                # Skip self references
                continue
            dependencies[path].add(target)

    return dependencies


def group_key(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    parts = rel.parts
    if not parts:
        return "."
    # Use first two segments when available to reflect feature folders
    if len(parts) >= 2:
        return str(Path(parts[0]) / parts[1])
    return str(Path(parts[0]))


def filter_prefixes(paths: Iterable[Path], prefixes: Sequence[str], root: Path) -> list[Path]:
    if not prefixes:
        return list(paths)
    normalized = [p.strip("/").lower() for p in prefixes]
    filtered: list[Path] = []
    for p in paths:
        rel = str(p.relative_to(root)).lower()
        if any(rel.startswith(prefix) for prefix in normalized):
            filtered.append(p)
    return filtered


def serialize_report(
    root: Path,
    dependencies: Mapping[Path, set[Path]],
    file_data: Mapping[Path, FileSymbols],
    focus: Sequence[str],
) -> dict:
    # Convert paths to strings for JSON
    deps_json = {
        str(path.relative_to(root)): sorted(str(t.relative_to(root)) for t in targets)
        for path, targets in dependencies.items()
    }
    files_json = {
        str(path.relative_to(root)): {
            "defines": sorted(data.defines),
            "references": sorted(data.references),
        }
        for path, data in file_data.items()
    }
    return {
        "root": str(root),
        "focus": focus,
        "dependencies": deps_json,
        "files": files_json,
    }


def normalize_graph_edges(
    dependencies: Mapping[Path, set[Path]], root: Path
) -> tuple[list[str], list[tuple[str, str]]]:
    """Flatten dependency sets into sorted node and edge lists."""
    nodes: set[str] = set()
    edges: list[tuple[str, str]] = []

    for src, targets in dependencies.items():
        rel_src = str(src.relative_to(root))
        nodes.add(rel_src)
        for tgt in targets:
            rel_tgt = str(tgt.relative_to(root))
            nodes.add(rel_tgt)
            edges.append((rel_src, rel_tgt))

    return sorted(nodes), sorted(edges)


def render_mermaid(nodes: Sequence[str], edges: Sequence[tuple[str, str]]) -> str:
    lines = ["flowchart LR"]
    for src, tgt in edges:
        lines.append(f'  "{src}" --> "{tgt}"')
    return "\n".join(lines)


def render_graphviz(nodes: Sequence[str], edges: Sequence[tuple[str, str]]) -> str:
    lines = ["digraph Dependencies {", "  rankdir=LR;", "  node [shape=box];"]
    for node in nodes:
        lines.append(f'  "{node}";')
    for src, tgt in edges:
        lines.append(f'  "{src}" -> "{tgt}";')
    lines.append("}")
    return "\n".join(lines)


def render_cytoscape(nodes: Sequence[str], edges: Sequence[tuple[str, str]]) -> str:
    payload = {
        "elements": {
            "nodes": [{"data": {"id": node, "label": node}} for node in nodes],
            "edges": [
                {"data": {"id": f"e{idx}", "source": src, "target": tgt}}
                for idx, (src, tgt) in enumerate(edges)
            ],
        }
    }
    return json.dumps(payload, indent=2)


def render_graph(format_name: str, nodes: Sequence[str], edges: Sequence[tuple[str, str]]) -> str:
    if format_name == "mermaid":
        return render_mermaid(nodes, edges)
    if format_name == "dot":
        return render_graphviz(nodes, edges)
    if format_name == "cytoscape":
        return render_cytoscape(nodes, edges)
    raise ValueError(f"Unsupported graph format: {format_name}")


def print_focus_section(
    root: Path,
    focus_paths: list[Path],
    dependencies: Mapping[Path, set[Path]],
    inverse_deps: Mapping[Path, set[Path]],
    limit: int,
) -> None:
    for focus_path in focus_paths:
        rel_focus = focus_path.relative_to(root)
        print(f"\n=== Focus: {rel_focus} ===")
        outgoing = sorted(dependencies.get(focus_path, []))
        incoming = sorted(inverse_deps.get(focus_path, []))

        if not outgoing and not incoming:
            print("No dependencies found.")
            continue

        if outgoing:
            print(f"Outgoing ({len(outgoing)}):")
            for target in outgoing[:limit]:
                print(f"  -> {target.relative_to(root)}")
            if len(outgoing) > limit:
                print(f"  ... +{len(outgoing) - limit} more")
        else:
            print("Outgoing: none")

        if incoming:
            print(f"Incoming ({len(incoming)}):")
            for source in incoming[:limit]:
                print(f"  <- {source.relative_to(root)}")
            if len(incoming) > limit:
                print(f"  ... +{len(incoming) - limit} more")
        else:
            print("Incoming: none")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map Swift file dependencies by symbol usage.")
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Root directory to scan (default: current working directory).",
    )
    parser.add_argument(
        "--focus",
        nargs="*",
        default=[],
        help="Optional path prefixes (relative to root) to highlight, e.g. Views/LoginViews",
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        default=None,
        help="Optional path to write JSON output.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum rows to print per section (default: 20).",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help="Abort if more than N Swift files are found (0 disables the limit).",
    )
    parser.add_argument(
        "--graph-format",
        choices=["mermaid", "dot", "cytoscape"],
        help="Optional graph export format for web viewers (Mermaid, Graphviz, Cytoscape).",
    )
    parser.add_argument(
        "--graph-output",
        type=Path,
        default=None,
        help="Path to write the exported graph. Defaults to stdout when omitted.",
    )
    parser.add_argument(
        "--include-viewer",
        action="store_true",
        help="When using --graph-format cytoscape and --graph-output, also copy a bundled HTML viewer beside the graph.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    if not root.exists():
        print(f"Root not found: {root}", file=sys.stderr)
        return 1

    swift_files = discover_swift_files(root)
    if args.max_files and len(swift_files) > args.max_files:
        print(
            f"Found {len(swift_files)} Swift files, exceeding --max-files={args.max_files}. "
            "Aborting to avoid long runtimes.",
            file=sys.stderr,
        )
        return 1

    symbol_to_file, collisions, file_data = build_symbol_index(swift_files)
    dependencies = build_dependencies(symbol_to_file, file_data)

    inverse_deps: dict[Path, set[Path]] = defaultdict(set)
    for source, targets in dependencies.items():
        for target in targets:
            inverse_deps[target].add(source)

    print(f"Scanned {len(swift_files)} Swift files under {root}.")
    print(f"Discovered {len(symbol_to_file)} unique symbols.")
    if collisions:
        collision_count = sum(len(v) for v in collisions.values())
        print(f"Note: {collision_count} duplicate symbol definitions detected.")

    focus_paths = filter_prefixes(swift_files, args.focus, root)

    # Aggregate by feature folder for a quick overview
    group_outgoing: dict[str, set[str]] = defaultdict(set)
    for src, targets in dependencies.items():
        g_src = group_key(src, root)
        for tgt in targets:
            g_tgt = group_key(tgt, root)
            if g_src != g_tgt:
                group_outgoing[g_src].add(g_tgt)

    if group_outgoing:
        print("\n=== Feature-Level Edges (source -> target groups) ===")
        for grp in sorted(group_outgoing):
            targets = sorted(group_outgoing[grp])
            print(f"{grp} -> {', '.join(targets)}")

    if args.focus:
        print_focus_section(root, focus_paths, dependencies, inverse_deps, args.limit)

    if args.graph_format:
        nodes, edges = normalize_graph_edges(dependencies, root)
        graph_payload = render_graph(args.graph_format, nodes, edges)
        if args.graph_output:
            try:
                args.graph_output.parent.mkdir(parents=True, exist_ok=True)
                args.graph_output.write_text(graph_payload, encoding="utf-8")
                if args.graph_format == "cytoscape" and args.include_viewer:
                    viewer_src = Path(__file__).with_name("cyto_viewer.html")
                    viewer_dst = args.graph_output.parent / "cyto_viewer.html"
                    viewer_dst.write_text(viewer_src.read_text(encoding="utf-8"), encoding="utf-8")
            except OSError as exc:
                print(f"Failed to write graph output: {exc}", file=sys.stderr)
                return 1
            print(f"\nGraph ({args.graph_format}) written to {args.graph_output}")
            if args.graph_format == "cytoscape" and args.include_viewer:
                print(f"Viewer written to {viewer_dst}")
        else:
            print(f"\n=== {args.graph_format.upper()} Graph ===")
            print(graph_payload)

    if args.json_path:
        payload = serialize_report(root, dependencies, file_data, args.focus)
        try:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            print(f"Failed to write JSON output: {exc}", file=sys.stderr)
            return 1
        print(f"\nJSON written to {args.json_path}")

    return 0


def main() -> int:
    try:
        return run(parse_args())
    except KeyboardInterrupt:
        print("Interrupted by user.", file=sys.stderr)
        return 130
    except Exception as exc:  # pragma: no cover - defensive guard for CLI use
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

