#!/usr/bin/env python3
"""Generate favicon.ico from HDD Network icon."""
from PIL import Image, ImageDraw


def generate_favicon():
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    c = (220, 220, 220, 255)
    lw = 3

    # HDD body
    draw.rectangle([16, 20, 48, 44], outline=c, width=lw)

    # LEDs
    draw.ellipse([20, 26, 26, 32], fill=c)
    draw.ellipse([29, 26, 35, 32], fill=c)

    # Network lines
    draw.line([32, 44, 32, 52], fill=c, width=lw)
    draw.line([20, 52, 44, 52], fill=c, width=lw)
    draw.line([20, 52, 20, 56], fill=c, width=lw)
    draw.line([32, 52, 32, 56], fill=c, width=lw)
    draw.line([44, 52, 44, 56], fill=c, width=lw)

    img.save('front/static/favicon.ico', format='ICO',
             sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print('✅ favicon.ico generated')


if __name__ == '__main__':
    generate_favicon()
