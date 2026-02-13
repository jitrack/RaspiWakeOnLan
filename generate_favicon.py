#!/usr/bin/env python3
"""
Script pour générer un favicon.ico avec l'icône HDD Network (comme dans la navbar)
"""
from PIL import Image, ImageDraw
import os

def generate_favicon():
    """Génère favicon.ico avec l'icône HDD network"""
    
    favicon_path = 'static/favicon.ico'
    
    try:
        # Créer une image 64x64 avec fond transparent
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Couleur de l'icône (blanc/gris clair comme dans Bootstrap)
        icon_color = (220, 220, 220, 255)
        line_width = 3
        
        # Dessiner le disque dur (rectangle principal)
        # Partie supérieure du HDD
        draw.rectangle([16, 20, 48, 44], outline=icon_color, width=line_width)
        
        # LED/indicateur sur le HDD
        draw.ellipse([20, 26, 26, 32], fill=icon_color)
        draw.ellipse([29, 26, 35, 32], fill=icon_color)
        
        # Dessiner les connexions réseau (lignes en bas)
        # Ligne centrale
        draw.line([32, 44, 32, 52], fill=icon_color, width=line_width)
        
        # Branches réseau (comme un hub)
        draw.line([20, 52, 44, 52], fill=icon_color, width=line_width)
        draw.line([20, 52, 20, 56], fill=icon_color, width=line_width)
        draw.line([32, 52, 32, 56], fill=icon_color, width=line_width)
        draw.line([44, 52, 44, 56], fill=icon_color, width=line_width)
        
        # Créer aussi les versions PNG pour le manifest PWA
        img_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
        img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        
        # Sauvegarder en PNG
        img_192.save('static/icon-192.png', 'PNG')
        img_512.save('static/icon-512.png', 'PNG')
        print(f"✅ Icônes PNG générées: icon-192.png, icon-512.png")
        
        # Sauvegarder le favicon avec plusieurs tailles
        img.save(
            favicon_path,
            format='ICO',
            sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
        )
        
        print(f"✅ Favicon généré avec succès: {favicon_path}")
        print("🎨 Icône: HDD Network (comme dans la navbar)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return False

if __name__ == '__main__':
    generate_favicon()
