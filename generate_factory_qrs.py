"""
Generate Ultra High-Resolution and Vector QR Codes for Nilgiris Valley
Target URL: https://moment-x-seven.vercel.app/
Purpose: Factory display, standees, banners, acrylic boards, flex printing.
"""

import os
import qrcode
import qrcode.image.svg
from PIL import Image, ImageDraw, ImageFont

TARGET_URL = "https://moment-x-seven.vercel.app/"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"Target URL: {TARGET_URL}")
print(f"Generating assets into: {OUTPUT_DIR}")

# 1. Pure Vector SVG (Infinite Resolution for Large Format Factory Banners)
svg_factory = qrcode.image.svg.SvgPathImage
svg_qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
    image_factory=svg_factory
)
svg_qr.add_data(TARGET_URL)
svg_qr.make(fit=True)
svg_img = svg_qr.make_image(attrib={'class': 'nilgiris-factory-qr'})
svg_path = os.path.join(OUTPUT_DIR, "nilgiris_factory_qr_vector.svg")
svg_img.save(svg_path)
print(f"[OK] Vector SVG saved: {svg_path}")

# 2. Ultra 4K Crisp High-Contrast PNG (4000 x 4000 px, 300 DPI)
qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=75,
    border=4
)
qr.add_data(TARGET_URL)
qr.make(fit=True)

# Generate standard black on white
base_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
# Resize exactly to 4000x4000 with high-quality resampling
img_4k = base_img.resize((4000, 4000), Image.Resampling.NEAREST)
png_4k_path = os.path.join(OUTPUT_DIR, "nilgiris_factory_qr_4k.png")
img_4k.save(png_4k_path, dpi=(300, 300), optimize=True)
print(f"[OK] 4K High-Res PNG saved: {png_4k_path} ({img_4k.size})")

# 3. Transparent High-Res PNG (4000 x 4000 px) for flex/overlay designers
qr_rgba = base_img.convert("RGBA")
datas = qr_rgba.getdata()
new_data = []
for item in datas:
    # If pixel is white/near white, make it transparent
    if item[0] > 200 and item[1] > 200 and item[2] > 200:
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append((8, 28, 21, 255)) # Deep Nilgiris Forest Black
qr_rgba.putdata(new_data)
img_trans = qr_rgba.resize((4000, 4000), Image.Resampling.NEAREST)
trans_path = os.path.join(OUTPUT_DIR, "nilgiris_factory_qr_transparent.png")
img_trans.save(trans_path, dpi=(300, 300), optimize=True)
print(f"[OK] Transparent PNG saved: {trans_path}")

# 4. Luxury Branded QR Code (Deep Forest Green & Champagne Gold with Nilgiris Badge)
# Use level H error correction to safely allow center logo emblem
branded_base = qr.make_image(fill_color="#081c15", back_color="#faf7f0").convert("RGBA")
branded_4k = branded_base.resize((4000, 4000), Image.Resampling.NEAREST)
draw = ImageDraw.Draw(branded_4k)

# Add a stylish luxury center emblem
center_x = 2000
center_y = 2000
badge_radius = 420  # ~21% of width, easily covered by 30% Level H ECC

# Outer gold glow & border
draw.ellipse([center_x - badge_radius - 20, center_y - badge_radius - 20, 
              center_x + badge_radius + 20, center_y + badge_radius + 20], 
             fill="#e2be6c")
# Forest green circle
draw.ellipse([center_x - badge_radius, center_y - badge_radius, 
              center_x + badge_radius, center_y + badge_radius], 
             fill="#081c15")
# Inner gold ring
draw.ellipse([center_x - badge_radius + 25, center_y - badge_radius + 25, 
              center_x + badge_radius - 25, center_y + badge_radius - 25], 
             outline="#e2be6c", width=12)

# Center Emblem with Homewood Tea Brand Logo
logo_file = os.path.join(OUTPUT_DIR, "homewood_clean_logo.png")
if os.path.exists(logo_file):
    # Pure white / ivory inner core
    core_r = badge_radius - 20
    draw.ellipse([center_x - core_r, center_y - core_r, center_x + core_r, center_y + core_r], fill="#ffffff")
    draw.ellipse([center_x - core_r + 15, center_y - core_r + 15, center_x + core_r - 15, center_y + core_r - 15], outline="#e2be6c", width=6)
    
    logo_img = Image.open(logo_file).convert("RGBA")
    target_w = int((core_r * 2) * 0.88)
    target_h = int(target_w * (logo_img.height / logo_img.width))
    logo_resized = logo_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Gold star
    try:
        font_star = ImageFont.truetype("arialbd.ttf", 85)
    except Exception:
        font_star = ImageFont.load_default()
    draw.text((center_x, center_y - int(core_r * 0.45)), "✦", fill="#e2be6c", font=font_star, anchor="mm")
    
    # Paste logo in center
    branded_4k.paste(logo_resized, (center_x - target_w // 2, center_y - target_h // 2 + 20), logo_resized)
else:
    # Fallback to text
    draw.text((center_x, center_y), "HOMEWOOD TEA", fill="#ffffff", anchor="mm")

branded_path = os.path.join(OUTPUT_DIR, "nilgiris_factory_qr_branded.png")
branded_4k.save(branded_path, dpi=(300, 300), optimize=True)
print(f"[OK] Branded 4K PNG saved: {branded_path}")

# 5. Also update mobile-app-qr.png in workspace root for direct usage
small_qr = base_img.resize((500, 500), Image.Resampling.LANCZOS)
mobile_path = os.path.join(OUTPUT_DIR, "mobile-app-qr.png")
small_qr.save(mobile_path)
print(f"[OK] mobile-app-qr.png updated: {mobile_path}")

print("All QR codes generated successfully!")
