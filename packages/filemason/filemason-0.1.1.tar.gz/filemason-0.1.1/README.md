# FileMason

[![Python package](https://github.com/KarBryant/FileMason/actions/workflows/python-package.yml/badge.svg)](https://github.com/KarBryant/FileMason/actions/workflows/python-package.yml)

FileMason is a Python CLI that organizes files into configurable “buckets” (images, videos, documents, etc.) based on file extension. It is designed to be safe-by-default, observable, and testable.

## Key behavior

- **Dry-run by default**: preview the action plan before making changes.
- **Deterministic planning**: generates an ordered action plan (mkdir → move).
- **Structured run results**: returns a complete `RunResult` snapshot (read/classified/skipped/planned/executed/failed).
- **Collision-safe moves**: does not overwrite existing files at the destination.

## Quick start

```bash
pip install filemason

# Preview what would happen (dry-run)
filemason organize ~/Downloads

# Execute the plan
filemason organize ~/Downloads --no-dry

# Print the generated plan
filemason get-plan ~/Downloads
```

## Commands

### `filemason organize`

Organize files in a directory.

```bash
filemason organize [DIRECTORY] [--dry | --no-dry]
```

Notes:
- Defaults to the current directory (`.`).
- Dry-run is enabled by default.

### `filemason get-plan`

Show the action plan without performing any moves.

```bash
filemason get-plan [DIRECTORY]
```

### `filemason version`

Show the installed FileMason version.

```bash
filemason version
```

## How it works

FileMason runs a simple pipeline:

1. **Reader** scans the directory and produces `FileItem` objects (skipping hidden files, symlinks, and subdirectories).
2. **Classifier** assigns each file to a bucket using a fast extension → bucket lookup.
3. **Planner** converts classified files into an ordered `ActionPlan` (MKDIR then MOVE steps).
4. **Executor** performs the actions and reports successes/failures.
5. **Orchestrator** coordinates the entire workflow and returns a `RunResult`.

## Configuration

Buckets are defined in `config.toml`:

```toml
[buckets]
images = ["png", "jpeg", "jpg", "gif", "tiff", "tif", "webp", "bmp", "nef", "svg"]
videos = ["mp4", "mov", "mkv", "avi", "wmv", "flv", "m4v", "mpeg", "3gp"]
audio = ["mp3", "wav", "flac", "aac", "m4a", "ogg", "wma", "mid", "midi"]
documents = ["txt", "md", "pdf", "doc", "docx", "xlsx", "csv", "json", "xml", "html"]
archives = ["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "iso", "tar.gz", "tgz"]
models = ["obj", "fbx", "stl", "blend"]
```

Config validation includes:
- buckets cannot be empty
- extensions cannot appear in multiple buckets

## Project status

Current features:
- Reader / Classifier / Planner / Executor / Orchestrator services
- Typer CLI (`organize`, `get-plan`, `version`)
- Pydantic models (`FileItem`, `ActionStep`, `ActionPlan`, `RunResult`, `FailedAction`)
- CI (Black, Ruff, pytest + coverage threshold)

Planned (in progress):
- persisted run artifacts (JSON reports per run)
- undo support (based on recorded executed actions)

## Development

```bash
git clone https://github.com/KarBryant/FileMason.git
cd FileMason

python -m venv venv
source venv/bin/activate

pip install -e ".[dev]"
pytest -v
```

## Design notes

### Why invert the bucket config?
The classifier builds an inverted mapping at startup:

- From: `{ "images": ["png", "jpg"] }`
- To: `{ "png": "images", "jpg": "images" }`

This makes per-file classification O(1) for extension lookup.

### Why model failures explicitly?
Execution failures are captured as structured data (`FailedAction`) containing error type and message, instead of attempting to serialize raw Python exceptions.

## Requirements

- Python 3.11+

## License

MIT

## Author

Karson Bryant  
GitHub: [@KarBryant](https://github.com/KarBryant)
