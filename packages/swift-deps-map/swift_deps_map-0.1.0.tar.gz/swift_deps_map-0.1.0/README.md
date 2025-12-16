# swift-deps-map

Lightweight Swift file-level dependency mapper that scans a source tree for symbol definitions/references and reports cross-file edges. Generates human-readable summaries plus optional graph/JSON exports for visualization.

## Features
- Default root is the current working directory for drop-in use on any Swift repo.
- Supports focus prefixes for zooming into specific folders.
- Exports graphs in Mermaid, Graphviz DOT, or Cytoscape JSON.
- Optional JSON report with symbols and edges for further processing.
- `--max-files` guard to avoid runaway scans on very large projects.
- Proper exit codes with errors sent to stderr for automation friendliness.

## Quick start
From PyPI (after publishing):
```
uvx swift-deps-map --help
uvx swift-deps-map --root /path/to/src --graph-format mermaid --graph-output deps.mmd
```

Local, without publishing (run at repo root):
```
uvx --from . swift-deps-map --root . --graph-format cytoscape --graph-output deps.cyto.json
```

You can also call the module directly:
```
python -m swift_deps_map --help
```

## CLI options
- `--root PATH` (default: `.`) Root directory to scan.
- `--focus PREFIX...` Limit printed focus sections to matching relative paths.
- `--limit N` Max rows per focus section (default: 20).
- `--max-files N` Abort if more than N Swift files are detected (0 disables).
- `--json PATH` Write the JSON report to PATH.
- `--graph-format {mermaid,dot,cytoscape}` Choose graph export format.
- `--graph-output PATH` Write graph output to PATH (stdout if omitted).
- `--include-viewer` When using `--graph-format cytoscape` with `--graph-output`, also drop `cyto_viewer.html` beside the JSON so you can open it directly.
- `--version` Show the CLI version.

## Outputs
- **Console summary:** Total Swift files, unique symbols, duplicate symbol hints, and feature-level edges.
- **Graph exports:** Mermaid/DOT snippets or Cytoscape JSON for visual viewers.
- **JSON report:** Includes `root`, `focus`, `dependencies`, and per-file `defines`/`references`.

## Development
- Requires Python 3.9+.
- Install/iterate locally: `uvx --from . swift-deps-map --help` or `python -m swift_deps_map --help`.
- Package data includes `cyto_viewer.html` for Cytoscape visualization if you want an offline viewer.

## License
Apache-2.0. See `LICENSE`.

