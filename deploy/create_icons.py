#!/usr/bin/env python3
"""Generate PWA icons (192px, 512px) with HDD Network design."""
from PIL import Image, ImageDraw


def generate_icons():
    for size in (192, 512):
        img = Image.new('RGBA', (size, size), (30, 30, 46, 255))
        draw = ImageDraw.Draw(img)

        pad = size // 6
        icon_color = (220, 220, 220, 255)
        lw = max(2, size // 40)

        # HDD body
        draw.rectangle(
            [pad, pad + size // 8, size - pad, size - pad - size // 8],
            outline=icon_color, width=lw,
        )

        # LEDs
        led_y = pad + size // 4
        led_r = size // 16
        draw.ellipse([pad + size // 8 - led_r, led_y - led_r,
                       pad + size // 8 + led_r, led_y + led_r], fill=icon_color)
        draw.ellipse([pad + size // 5, led_y - led_r,
                       pad + size // 5 + led_r * 2, led_y + led_r], fill=icon_color)

        # Network lines
        mid_x = size // 2
        bot = size - pad - size // 8
        net_y = size - pad + size // 16
        draw.line([mid_x, bot, mid_x, net_y], fill=icon_color, width=lw)
        draw.line([pad + size // 6, net_y, size - pad - size // 6, net_y],
                  fill=icon_color, width=lw)

        img.save(f'front/static/icon-{size}.png', 'PNG')
        print(f'✅ icon-{size}.png generated')


if __name__ == '__main__':
    generate_icons()
