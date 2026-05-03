# TODO

## Phase 1: Archive Skeleton

- [x] Create Rust archive module crate.
- [x] Add parser interface for archive readers.
- [x] Add Unreal marker detection service.
- [x] Add safe `~mods` folder planning service.
- [x] Document architecture and tech stack.

## Phase 2: Unreal VFS Reader

- [ ] Parse Unreal `.pak` footer and version metadata.
- [ ] Read encrypted indexes with a user-provided AES key.
- [ ] List internal `.locres` and `.uasset` candidates without full archive extraction.

## Phase 3: Localization Pipeline

- [ ] Add `.locres` binary parser.
- [ ] Preserve string identifiers and binary offsets during translation export.
- [ ] Connect archive candidates to the DeepL batching layer.

## Phase 4: Patch Output

- [ ] Generate mod-priority output in `~mods`.
- [ ] Add delta patch metadata.
- [ ] Add optional Zstandard and LZ4 support.
