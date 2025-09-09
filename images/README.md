# Image Translation: Turkish to Italian Control Panel

This directory contains the implementation for translating a device front-panel image from Turkish to Italian while preserving the original layout and visual style.

## Quick Start

If you have the source image (image1.png or similar), run:

```bash
cd images
python3 translate_panel.py path/to/source/image.png
```

This will generate:
- `panel_it.png` - Final translated PNG
- `panel_it.svg` - Editable SVG with Italian labels
- Updated `panel_it_notes.md` with processing details

## Files

### Generated Outputs
- **panel_it.png** - High-resolution PNG at source resolution
- **panel_it.svg** - Editable SVG with correctly positioned Italian labels
- **panel_it_notes.md** - Documentation with translation notes and approximations

### Tools and Scripts
- **translate_panel.py** - Main translation script
- **create_demo_panel.py** - Creates demo Turkish control panel for testing

## Translation Mappings

The script includes all required Turkish → Italian translations:

### Control Elements
- `PRG ESC`, `SET` → **Not translated** (control keys)
- `RÖLESAN®`, `REV:01` → **Not translated** (brand/version)

### Status Indicators  
- `+ KAÇAK` → `+ Fuga`
- `AC ON` → `AC Acceso`
- `AŞIRI YÜK` → `Sovraccarico`
- `AKÜ KRİTİK` → `Batteria Critica`
- [Full mapping in panel_it_notes.md]

### System Labels
- `ASC ECOMAX DC BESLEME SİSTEMİ` → `Sistema di Alimentazione DC ASC ECOMAX`
- `OTOMATİK SİGORTA` → `Interruttore Automatico`
- [Complete list in translate_panel.py]

## Technical Features

- **Automatic font detection** and matching
- **Vector text conversion** for exact appearance preservation  
- **Layout preservation** - maintains original positioning and alignment
- **Multi-format support** - PNG, JPG, SVG inputs
- **Error handling** and detailed logging

## Requirements

```bash
# Install dependencies
pip3 install pillow opencv-python numpy matplotlib

# System tools (Ubuntu/Debian)
sudo apt install imagemagick inkscape
```

## Usage Examples

### Basic Translation
```bash
python3 translate_panel.py device_panel.png
```

### Create Demo Panel
```bash
python3 create_demo_panel.py
python3 translate_panel.py demo_panel_turkish.png
```

### Custom Output Directory
```bash
python3 translate_panel.py source.png --output-dir ./translated
```

## Notes

- The framework is ready but requires the actual source image (image1) to complete the translation
- Current implementation includes a complete demo workflow
- Text positioning will need manual adjustment for optimal results
- Font matching uses system fonts with fallback to outlines for exact appearance

## Troubleshooting

**Missing source image**: The problem statement references "image1" which was not found in the repository. Provide this image to complete the actual translation.

**Font issues**: If exact fonts are not available, text will be converted to vector outlines to preserve appearance.

**Positioning**: Fine-tune text coordinates in the generated SVG for pixel-perfect alignment.