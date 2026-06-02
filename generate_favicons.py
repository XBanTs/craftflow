from PIL import Image
import os

# Load original favicon image (icon‑only part, ideally already cropped)
original = Image.open('static/images/favicon.png').convert('RGBA')

# Get dimensions and center‑crop a square
w, h = original.size
side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
right = left + side
bottom = top + side
icon = original.crop((left, top, right, bottom))

# Resize to standard sizes
sizes = {
    'favicon-16x16.png': (16, 16),
    'favicon-32x32.png': (32, 32),
    'apple-touch-icon.png': (180, 180),
    'android-chrome-192x192.png': (192, 192),
    'android-chrome-512x512.png': (512, 512),
}

for filename, size in sizes.items():
    resized = icon.resize(size, Image.LANCZOS)
    resized.save(f'static/images/{filename}')

# Multi‑size .ico
icon.resize((32, 32), Image.LANCZOS).save('static/images/favicon.ico', format='ICO')

print("All favicon files generated.")