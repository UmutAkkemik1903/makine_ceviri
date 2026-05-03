# Archive Module

Rust-based MVP module for detecting Unreal Engine `.pak` archives before the translation pipeline touches binary content.

## Run

```bash
cargo run -- path/to/file.pak
```

Optional AES key input is accepted as the second argument for future encrypted-index parsing:

```bash
cargo run -- path/to/file.pak YOUR_AES_KEY
```

## Current Scope

- Detects the requested Unreal data marker: `5B 44 41 54 41 5D`.
- Exposes an `ArsivAyrisitirici` parser interface.
- Keeps VFS entry listing as a dedicated service layer placeholder.
- Plans safe `~mods` output instead of replacing original archives.

## Safety Boundary

This module accepts user-provided AES keys only. It does not brute-force keys or bypass protected content.
