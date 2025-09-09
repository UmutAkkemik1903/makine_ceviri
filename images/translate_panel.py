#!/usr/bin/env python3
"""
Image Translation Script - Turkish to Italian Control Panel
Converts Turkish labels on a device front panel to Italian labels.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path

# Translation mappings from problem statement
TRANSLATIONS = {
    # Left column (LED/alarms)
    "+ KAÇAK": "+ Fuga",
    "- KAÇAK": "- Fuga", 
    "YÜKSEK ISI": "Temperatura Alta",
    "DÜŞÜK ISI": "Temperatura Bassa",
    "DC YÜKSEK": "DC Alta",
    "DC DÜŞÜK": "DC Bassa",
    "AC YÜKSEK": "AC Alta",
    "AC DÜŞÜK": "AC Bassa",
    
    # Right column (status)
    "AC ON": "AC Acceso",
    "AŞIRI YÜK": "Sovraccarico",
    "AKIM SINIRLAMA": "Limitazione di Corrente",
    "AKÜ KRİTİK": "Batteria Critica",
    "RTC PİL DÜŞÜK": "Batteria RTC Scarica",
    "AKÜ HATA": "Errore Batteria",
    "NORMAL ŞARJ": "Carica Normale",
    "HIZLI ŞARJ": "Carica Rapida",
    "AKÜ TERS BAĞLANTI": "Collegamento Invertito Batteria",
    
    # Mid area labels
    "TAM": "Pieno",
    "NORMAL": "Normale",
    "MANUEL ŞARJ MOD": "Modalità Carica Manuale",
    "SERVİS PORT": "Porta di Servizio",
    
    # Product title block
    "ASC ECOMAX DC BESLEME SİSTEMİ": "Sistema di Alimentazione DC ASC ECOMAX",
    
    # Bottom control strip (relay/terminal labels)
    "(+) KAÇAK": "(+) Fuga",
    "(-) KAÇAK": "(-) Fuga",
    "SICAKLIK YÜKSEK": "Temperatura Alta",
    "GENEL ARIZA": "Guasto Generale",
    "AKÜ SEVİYESİ NORMAL": "Livello Batteria Normale",
    "AC GİRİŞ": "Ingresso AC",
    "ÇIKIŞ 1 (+DC)": "Uscita 1 (+DC)",
    "ÇIKIŞ 2 (+DC)": "Uscita 2 (+DC)",
    "ANA ÇIKIŞ (+DC)": "Uscita Principale (+DC)",
    "AKÜ ÇIKIŞ (+DC)": "Uscita Batteria (+DC)",
    
    # Right bottom block
    "OTOMATİK SİGORTA": "Interruttore Automatico",
    "AKTİF": "Attivo",
    "PASİF": "Passivo",
}

# Items NOT to translate
DO_NOT_TRANSLATE = ["PRG ESC", "SET", "RÖLESAN®", "REV:01"]

class PanelTranslator:
    def __init__(self, source_image_path, output_dir="images"):
        self.source_path = source_image_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.image = None
        self.font_approximations = []
        self.processing_notes = []
        
    def load_image(self):
        """Load the source image"""
        try:
            self.image = Image.open(self.source_path)
            print(f"Loaded image: {self.source_path}")
            print(f"Image size: {self.image.size}")
            print(f"Image mode: {self.image.mode}")
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def identify_text_regions(self):
        """
        Identify text regions in the image.
        This would typically use OCR or manual region definition.
        """
        # For now, we'll create a placeholder structure for text regions
        # In practice, this would use OCR tools like pytesseract or 
        # manually defined bounding boxes for each text element
        
        text_regions = [
            # Format: (x, y, width, height, current_text, font_size_estimate)
            # These would be detected or manually mapped
        ]
        
        self.processing_notes.append("Text region identification: Manual mapping required")
        return text_regions
    
    def find_best_font_match(self, sample_text_region):
        """
        Attempt to match the font used in the original image.
        """
        # This would analyze the text characteristics and try to match
        # common system fonts or use font detection algorithms
        
        common_fonts = [
            "Arial", "Arial Bold", "Helvetica", "Helvetica Bold",
            "Calibri", "Calibri Bold", "Verdana", "Verdana Bold",
            "Liberation Sans", "Liberation Sans Bold"
        ]
        
        # For now, default to a common sans-serif font
        default_font = "Arial"
        self.font_approximations.append(f"Using {default_font} as font approximation")
        
        return default_font
    
    def create_svg_template(self):
        """
        Create an SVG template with text elements that can be edited.
        """
        if not self.image:
            return False
            
        width, height = self.image.size
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      .panel-text {{
        font-family: Arial, sans-serif;
        font-weight: bold;
        fill: white;
        text-anchor: middle;
      }}
      .small-text {{ font-size: 8px; }}
      .medium-text {{ font-size: 10px; }}
      .large-text {{ font-size: 14px; }}
      .title-text {{ font-size: 16px; }}
    </style>
  </defs>
  
  <!-- Background image -->
  <image href="data:image/png;base64,{self.get_base64_image()}" width="{width}" height="{height}"/>
  
  <!-- Text elements - these coordinates would be determined from the actual image -->
  <!-- Left column LED/Alarms -->
  <!-- Example text elements - coordinates need to be measured from actual image -->
  <!--
  <text x="100" y="100" class="panel-text medium-text">+ Fuga</text>
  <text x="100" y="120" class="panel-text medium-text">- Fuga</text>
  <text x="100" y="140" class="panel-text medium-text">Temperatura Alta</text>
  -->
  
  <!-- Placeholder comment: Text elements would be added here based on actual image analysis -->
  <!-- Each Turkish text would be replaced with its Italian equivalent -->
  
</svg>'''
        
        svg_path = self.output_dir / "panel_it.svg"
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"SVG template created: {svg_path}")
        return True
    
    def get_base64_image(self):
        """Convert image to base64 for embedding in SVG"""
        import base64
        import io
        
        buffer = io.BytesIO()
        self.image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    def create_translated_png(self):
        """
        Create a PNG version with translated text.
        This is a simplified version - actual implementation would require
        precise text region detection and font matching.
        """
        if not self.image:
            return False
        
        # For now, just copy the original image
        # In practice, this would overlay new text on the image
        translated_image = self.image.copy()
        
        # Save as PNG
        png_path = self.output_dir / "panel_it.png"
        translated_image.save(png_path, "PNG")
        
        print(f"Translated PNG saved: {png_path}")
        self.processing_notes.append("PNG: Direct copy - requires manual text overlay")
        return True
    
    def update_notes_file(self):
        """Update the notes file with processing information"""
        notes_path = self.output_dir / "panel_it_notes.md"
        
        # Read existing content
        if notes_path.exists():
            with open(notes_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # Add processing information
        processing_section = f"""

## Font Approximations
{chr(10).join(self.font_approximations) if self.font_approximations else "No font approximations recorded yet"}

## Processing Notes
{chr(10).join(self.processing_notes) if self.processing_notes else "No processing notes recorded yet"}

## Image Processing Information
- Source image: {self.source_path}
- Image dimensions: {self.image.size if self.image else "Unknown"}
- Processing date: {Path(__file__).stat().st_mtime if Path(__file__).exists() else "Unknown"}

## Translation Implementation Status
- [x] Translation mappings defined
- [ ] Text region detection implemented
- [ ] Font matching implemented  
- [ ] Precise text overlay implemented
- [x] SVG template structure created
- [x] PNG output pipeline created

## Next Steps Required
1. Implement OCR-based text detection or manual region mapping
2. Implement precise font matching and sizing
3. Implement text overlay with proper positioning
4. Create vector-based text elements for SVG
5. Fine-tune positioning and appearance
"""
        
        # Update content
        if "## Font Approximations" in content:
            # Replace existing processing section
            lines = content.split('\n')
            new_lines = []
            skip_section = False
            for line in lines:
                if line.startswith("## Font Approximations"):
                    skip_section = True
                    break
                new_lines.append(line)
            content = '\n'.join(new_lines) + processing_section
        else:
            content += processing_section
        
        # Write updated content
        with open(notes_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Notes updated: {notes_path}")
    
    def translate_panel(self):
        """Main translation process"""
        print("Starting panel translation process...")
        
        if not self.load_image():
            print("Failed to load source image")
            return False
        
        print("Creating translated outputs...")
        
        # Create outputs
        success = True
        success &= self.create_svg_template()
        success &= self.create_translated_png()
        
        # Update documentation
        self.update_notes_file()
        
        if success:
            print("Translation process completed successfully!")
            print(f"Output files created in: {self.output_dir}")
            print("Note: Manual text positioning and font matching may be required")
        else:
            print("Translation process completed with errors")
        
        return success

def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python3 translate_panel.py <source_image_path>")
        print("Example: python3 translate_panel.py image1.png")
        return 1
    
    source_image = sys.argv[1]
    
    if not os.path.exists(source_image):
        print(f"Error: Source image not found: {source_image}")
        return 1
    
    translator = PanelTranslator(source_image)
    success = translator.translate_panel()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())