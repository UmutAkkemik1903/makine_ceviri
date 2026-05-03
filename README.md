# makine_ceviri

Machine translation workspace for loose text files, image panels, and archive-aware game localization research.

## Modules

- `frontend/`: Python desktop translator for loose text-like files.
- `images/`: Python tooling for translated panel image outputs.
- `archive_module/`: Rust MVP module for Unreal `.pak` archive detection and future VFS parsing.

## Rust Archive Module

Run the current archive detector with:

```bash
cd archive_module
cargo run -- path/to/file.pak
```

The module accepts a user-provided AES key as an optional second argument for future encrypted-index parsing. It does not brute-force keys.
