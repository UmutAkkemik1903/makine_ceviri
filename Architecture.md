# Architecture

This repository currently has three working areas: the Python file translator, the Python image translation tools, and the new Rust archive module.

## Root

- `README.md`: project entry point.
- `Architecture.md`: folder responsibilities and module interaction map.
- `TechStack.md`: technologies and package versions used by the project.
- `TODO.md`: implementation phases and pending work.

## `frontend/`

Desktop translation UI built with Python and CustomTkinter. It scans loose text-like files, previews original content, sends text to DeepL through `deepl_client.py`, and stores translated output in memory before export.

## `images/`

Image translation helpers for panel-style images. These scripts are independent from the archive pipeline.

## `archive_module/`

Rust MVP module for Unreal archive handling. The module is intentionally separate from `frontend/` because `.pak` files are binary archives and must not be treated as plain text.

### Internal Layers

- `src/controllers/archive_controller.rs`: orchestration entry point for archive scanning.
- `src/interfaces/archive_parser.rs`: `ArsivAyrisitirici` contract for archive parsers.
- `src/models/`: data models for archive type, archive entries, scan output, and `.pak` options.
- `src/services/detect_pak_signature.rs`: checks the requested Unreal data marker.
- `src/services/list_pak_entries.rs`: placeholder for future VFS index parsing without full extraction.
- `src/services/create_mod_folder_plan.rs`: computes the safe `~mods` output location.
- `src/services/unreal_pak_parser.rs`: Unreal `.pak` parser implementation behind the interface.

### Planned Interaction

1. Rust archive module detects and lists translatable internal files.
2. The translation layer targets extracted `.locres` or other supported text resources.
3. The archive layer writes translated files into a mod-priority folder instead of replacing original archives.
