#!/usr/bin/env python3
"""
Create a demo control panel image for testing the translation script
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_demo_panel():
    """Create a demo control panel image with Turkish text"""
    
    # Create a panel-like image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='#2C3E50')
    draw = ImageDraw.Draw(image)
    
    # Try to use a system font, fallback to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 16)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 12)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 10)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Panel background
    draw.rectangle([50, 50, width-50, height-50], fill='#34495E', outline='#BDC3C7', width=2)
    
    # Title area
    draw.rectangle([70, 70, width-70, 120], fill='#2980B9', outline='#3498DB', width=1)
    draw.text((width//2, 95), "ASC ECOMAX DC BESLEME SİSTEMİ", font=font_large, fill='white', anchor='mm')
    
    # Left column - LED indicators
    left_x = 100
    start_y = 150
    spacing = 30
    
    led_texts = [
        "+ KAÇAK",
        "- KAÇAK", 
        "YÜKSEK ISI",
        "DÜŞÜK ISI",
        "DC YÜKSEK",
        "DC DÜŞÜK",
        "AC YÜKSEK",
        "AC DÜŞÜK"
    ]
    
    for i, text in enumerate(led_texts):
        y = start_y + i * spacing
        # LED circle
        draw.ellipse([left_x-15, y-8, left_x-5, y+2], fill='red', outline='darkred')
        # Text
        draw.text((left_x, y), text, font=font_small, fill='white')
    
    # Right column - Status indicators  
    right_x = 500
    right_texts = [
        "AC ON",
        "AŞIRI YÜK",
        "AKIM SINIRLAMA", 
        "AKÜ KRİTİK",
        "RTC PİL DÜŞÜK",
        "AKÜ HATA",
        "NORMAL ŞARJ",
        "HIZLI ŞARJ"
    ]
    
    for i, text in enumerate(right_texts):
        y = start_y + i * spacing
        # LED circle
        draw.ellipse([right_x-15, y-8, right_x-5, y+2], fill='green', outline='darkgreen')
        # Text
        draw.text((right_x, y), text, font=font_small, fill='white')
    
    # Middle section
    mid_y = 380
    draw.text((200, mid_y), "TAM", font=font_medium, fill='white')
    draw.text((300, mid_y), "NORMAL", font=font_medium, fill='white')
    draw.text((450, mid_y), "MANUEL ŞARJ MOD", font=font_medium, fill='white')
    
    # Service port
    draw.text((350, mid_y + 30), "SERVİS PORT", font=font_small, fill='white')
    
    # Bottom section - terminals
    bottom_y = 480
    terminal_texts = [
        "(+) KAÇAK", "(-) KAÇAK", "SICAKLIK YÜKSEK", "DC YÜKSEK", "DC DÜŞÜK",
        "AC ON", "GENEL ARIZA", "AKÜ SEVİYESİ NORMAL"
    ]
    
    x_pos = 80
    for text in terminal_texts[:4]:
        draw.text((x_pos, bottom_y), text, font=font_small, fill='white')
        x_pos += 120
    
    x_pos = 80
    for text in terminal_texts[4:]:
        draw.text((x_pos, bottom_y + 20), text, font=font_small, fill='white')
        x_pos += 150
    
    # Bottom right section
    draw.text((600, bottom_y + 40), "OTOMATİK SİGORTA", font=font_small, fill='white')
    draw.text((620, bottom_y + 55), "AKTİF", font=font_small, fill='green')
    draw.text((680, bottom_y + 55), "PASİF", font=font_small, fill='red')
    
    # Control buttons (not to be translated)
    draw.rectangle([650, 200, 720, 230], fill='#E74C3C', outline='darkred')
    draw.text((685, 215), "PRG ESC", font=font_small, fill='white', anchor='mm')
    
    draw.rectangle([650, 240, 720, 270], fill='#27AE60', outline='darkgreen') 
    draw.text((685, 255), "SET", font=font_small, fill='white', anchor='mm')
    
    # Brand mark
    draw.text((650, 300), "RÖLESAN®", font=font_medium, fill='white')
    draw.text((650, 320), "REV:01", font=font_small, fill='white')
    
    return image

def main():
    """Create demo panel image"""
    print("Creating demo panel image...")
    
    image = create_demo_panel()
    
    # Save the demo image
    demo_path = "demo_panel_turkish.png"
    image.save(demo_path)
    
    print(f"Demo panel created: {demo_path}")
    print("This image contains Turkish text that can be translated to Italian using the translate_panel.py script")
    
    return demo_path

if __name__ == "__main__":
    main()