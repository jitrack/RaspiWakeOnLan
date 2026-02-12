#!/usr/bin/env python3
"""
Generate PWA icons for NAS Control application
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with the specified size"""
    # Dark background color (Catppuccin Mocha)
    bg_color = '#262640'
    # Light blue text color
    text_color = '#89dceb'
    
    # Create image
    img = Image.new('RGB', (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a larger font
    try:
        font_size = size // 4
        font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf', font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw text
    text = "NAS"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save the image
    filepath = os.path.join('static', filename)
    img.save(filepath, 'PNG')
    print(f"✓ Created {filepath}")

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Generate icons
    create_icon(192, 'icon-192.png')
    create_icon(512, 'icon-512.png')
    
    print("\nPWA icons created successfully!")
    print("Your app is now ready for installation on phones and tablets.")
