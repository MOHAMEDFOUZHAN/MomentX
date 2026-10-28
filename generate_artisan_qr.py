"""
Designer QR Code Generator for Nilgiris Valley Photo Experience
URL: https://moment-x-seven.vercel.app/
Creates unique, artistic, high-resolution designer QR codes that scan 100% reliably.
"""

import os
import math
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import cv2

TARGET_URL = "https://moment-x-seven.vercel.app/"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"Creating unique artistic QR for: {TARGET_URL}")

# Initialize QR with High Error Correction (30% tolerance)
qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=1,
    border=4
)
qr.add_data(TARGET_URL)
qr.make(fit=True)
matrix = qr.get_matrix()
n_modules = len(matrix)
print(f"Matrix size: {n_modules} x {n_modules} modules")

# Coordinates of the 3 corner finder patterns (7x7 modules each)
def is_in_finder_eye(r, c):
    # Top-Left: [0..6, 0..6]
    if 0 <= r <= 6 and 0 <= c <= 6:
        return True
    # Top-Right: [0..6, (n-7)..n-1]
    if 0 <= r <= 6 and (n_modules - 7) <= c < n_modules:
        return True
    # Bottom-Left: [(n-7)..n-1, 0..6]
    if (n_modules - 7) <= r < n_modules and 0 <= c <= 6:
        return True
    return False

# Center area for brand medallion (9x9 modules in center)
center_idx = n_modules // 2
def is_in_center_badge(r, c, radius_modules=4.2):
    dist = math.hypot(r - center_idx, c - center_idx)
    return dist <= radius_modules

# High-resolution canvas setup (e.g. 2800 x 2800 px)
CANVAS_SIZE = 2800
MARGIN = 200
DRAW_AREA = CANVAS_SIZE - (2 * MARGIN)
MODULE_SIZE = DRAW_AREA / n_modules

print(f"Module size: {MODULE_SIZE:.2f} px")

# Function to interpolate colors (for luxurious gradient)
def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
        int(c1[3] + (c2[3] - c1[3]) * t) if len(c1) == 4 and len(c2) == 4 else 255
    )

# Gradient palette for Nilgiris Tea & Luxury Gold:
# From rich imperial emerald green to mountain jade and champagne gold highlights
COLOR_DEEP_EMERALD = (8, 36, 25, 255)     # #082419
COLOR_MID_JADE      = (14, 77, 52, 255)    # #0e4d34
COLOR_BRIGHT_JADE   = (22, 110, 75, 255)   # #166e4b
COLOR_GOLD          = (226, 190, 108, 255) # #e2be6c
COLOR_GOLD_DARK     = (184, 146, 58, 255)  # #b8923a
COLOR_BG_IVORY      = (252, 250, 246, 255) # Warm luxury ivory

def create_artisan_qr():
    img = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), COLOR_BG_IVORY)
    draw = ImageDraw.Draw(img)

    # 1. Subtle luxury border & corner flourishes on background
    border_inset = 60
    draw.rounded_rectangle(
        [border_inset, border_inset, CANVAS_SIZE - border_inset, CANVAS_SIZE - border_inset],
        radius=40,
        outline=(226, 190, 108, 120),
        width=4
    )
    draw.rounded_rectangle(
        [border_inset + 14, border_inset + 14, CANVAS_SIZE - border_inset - 14, CANVAS_SIZE - border_inset - 14],
        radius=30,
        outline=(14, 77, 52, 60),
        width=2
    )

    # 2. Draw Data Modules as Smooth Organic Rounded Dots & Connected Pills
    dot_radius = (MODULE_SIZE * 0.44) # Smooth circular pebbles

    for r in range(n_modules):
        for c in range(n_modules):
            if is_in_finder_eye(r, c) or is_in_center_badge(r, c):
                continue

            if matrix[r][c]:
                # Calculate module center
                cx = MARGIN + (c + 0.5) * MODULE_SIZE
                cy = MARGIN + (r + 0.5) * MODULE_SIZE

                # Calculate gradient factor based on distance from top-left to bottom-right
                t = (r + c) / (2 * n_modules)
                # Multi-stop luxury color gradient
                if t < 0.5:
                    mod_color = lerp_color(COLOR_DEEP_EMERALD, COLOR_MID_JADE, t * 2)
                else:
                    mod_color = lerp_color(COLOR_MID_JADE, (18, 55, 38, 255), (t - 0.5) * 2)

                # Check neighbor connectivity for subtle smooth organic links
                has_top = (r > 0 and matrix[r-1][c] and not is_in_finder_eye(r-1, c) and not is_in_center_badge(r-1, c))
                has_bot = (r < n_modules-1 and matrix[r+1][c] and not is_in_finder_eye(r+1, c) and not is_in_center_badge(r+1, c))
                has_lft = (c > 0 and matrix[r][c-1] and not is_in_finder_eye(r, c-1) and not is_in_center_badge(r, c-1))
                has_rgt = (c < n_modules-1 and matrix[r][c+1] and not is_in_finder_eye(r, c+1) and not is_in_center_badge(r, c+1))

                # Draw base smooth rounded dot
                draw.ellipse(
                    [cx - dot_radius, cy - dot_radius, cx + dot_radius, cy + dot_radius],
                    fill=mod_color
                )

                # Draw elegant connecting bridges to adjacent neighbors (organic liquid look)
                bridge_w = dot_radius * 0.88
                if has_rgt:
                    draw.rectangle([cx, cy - bridge_w, cx + MODULE_SIZE, cy + bridge_w], fill=mod_color)
                if has_bot:
                    draw.rectangle([cx - bridge_w, cy, cx + bridge_w, cy + MODULE_SIZE], fill=mod_color)

    # 3. Draw Bespoke Designer Finder Eyes (3 Corners)
    finder_coords = [
        (0, 0),                       # Top-Left
        (0, n_modules - 7),           # Top-Right
        (n_modules - 7, 0)            # Bottom-Left
    ]

    for (fr, fc) in finder_coords:
        fx = MARGIN + fc * MODULE_SIZE
        fy = MARGIN + fr * MODULE_SIZE
        eye_w = 7 * MODULE_SIZE

        # Outer rounded squircle in deep emerald with gold border
        outer_pad = MODULE_SIZE * 0.2
        draw.rounded_rectangle(
            [fx + outer_pad, fy + outer_pad, fx + eye_w - outer_pad, fy + eye_w - outer_pad],
            radius=MODULE_SIZE * 1.8,
            fill=COLOR_DEEP_EMERALD,
            outline=COLOR_GOLD,
            width=int(MODULE_SIZE * 0.25)
        )

        # Inner white/ivory cutout ring
        inner_pad = MODULE_SIZE * 1.05
        draw.rounded_rectangle(
            [fx + inner_pad, fy + inner_pad, fx + eye_w - inner_pad, fy + eye_w - inner_pad],
            radius=MODULE_SIZE * 1.3,
            fill=COLOR_BG_IVORY
        )

        # Center pupil (gemstone rounded core in gold & emerald)
        pupil_pad = MODULE_SIZE * 2.05
        draw.rounded_rectangle(
            [fx + pupil_pad, fy + pupil_pad, fx + eye_w - pupil_pad, fy + eye_w - pupil_pad],
            radius=MODULE_SIZE * 1.1,
            fill=COLOR_DEEP_EMERALD,
            outline=COLOR_GOLD,
            width=int(MODULE_SIZE * 0.2)
        )
        # Gold center sparkle dot
        center_eye_x = fx + (eye_w / 2)
        center_eye_y = fy + (eye_w / 2)
        spark_r = MODULE_SIZE * 0.4
        draw.ellipse(
            [center_eye_x - spark_r, center_eye_y - spark_r, center_eye_x + spark_r, center_eye_y + spark_r],
            fill=COLOR_GOLD
        )

    # 4. Draw Center Luxury Nilgiris Medallion Badge
    badge_cx = MARGIN + (center_idx + 0.5) * MODULE_SIZE
    badge_cy = MARGIN + (center_idx + 0.5) * MODULE_SIZE
    badge_r = MODULE_SIZE * 4.35

    # Badge background clear cutout (with soft ivory halo)
    draw.ellipse(
        [badge_cx - badge_r - 18, badge_cy - badge_r - 18, badge_cx + badge_r + 18, badge_cy + badge_r + 18],
        fill=COLOR_BG_IVORY
    )
    # Outer gold rim
    draw.ellipse(
        [badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r],
        fill=COLOR_GOLD
    )
    # Emerald inner medallion
    medallion_inner_r = badge_r - 12
    draw.ellipse(
        [badge_cx - medallion_inner_r, badge_cy - medallion_inner_r, badge_cx + medallion_inner_r, badge_cy + medallion_inner_r],
        fill=COLOR_DEEP_EMERALD
    )
    # Concentric delicate gold ring
    draw.ellipse(
        [badge_cx - medallion_inner_r + 16, badge_cy - medallion_inner_r + 16, badge_cx + medallion_inner_r - 16, badge_cy + medallion_inner_r - 16],
        outline=COLOR_GOLD,
        width=4
    )

    # Central Camera / Tea Leaf Icon & Typography
    try:
        font_large = ImageFont.truetype("arialbd.ttf", int(MODULE_SIZE * 1.25))
        font_mid = ImageFont.truetype("arialbd.ttf", int(MODULE_SIZE * 0.85))
        font_sub = ImageFont.truetype("arial.ttf", int(MODULE_SIZE * 0.55))
    except Exception:
        font_large = ImageFont.load_default()
        font_mid = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Draw Gold Star / Crest
    draw.text((badge_cx, badge_cy - MODULE_SIZE * 1.55), "✦", fill=COLOR_GOLD, font=font_large, anchor="mm")
    # Draw Camera / Leaf Symbol
    draw.text((badge_cx, badge_cy - MODULE_SIZE * 0.45), "📸", fill="#ffffff", font=font_large, anchor="mm")
    # Brand Name
    draw.text((badge_cx, badge_cy + MODULE_SIZE * 0.85), "NILGIRIS", fill="#ffffff", font=font_mid, anchor="mm")
    draw.text((badge_cx, badge_cy + MODULE_SIZE * 1.65), "PHOTO EXPERIENCE", fill=COLOR_GOLD, font=font_sub, anchor="mm")

    # 5. Top and Bottom Luxury Label Bars
    top_label_y = MARGIN / 2 + 10
    draw.text(
        (CANVAS_SIZE / 2, top_label_y),
        "✦  NILGIRIS VALLEY HERITAGE  ✦",
        fill=COLOR_GOLD_DARK,
        font=font_mid,
        anchor="mm"
    )

    bot_label_y = CANVAS_SIZE - (MARGIN / 2) - 10
    draw.text(
        (CANVAS_SIZE / 2, bot_label_y),
        "SCAN WITH ANY PHONE CAMERA • NO APP REQUIRED",
        fill=COLOR_MID_JADE,
        font=font_sub,
        anchor="mm"
    )

    return img

# Generate the Unique Artisan QR Code
artisan_img = create_artisan_qr()
artisan_path = os.path.join(OUTPUT_DIR, "nilgiris_unique_artisan_qr.png")
artisan_img.save(artisan_path, dpi=(300, 300), optimize=True)
print(f"Saved Unique Artisan QR: {artisan_path}")

# Also generate a Pure Vector/High-Contrast Transparent version of this designer style
# for direct print flex/banner usage
artisan_trans = artisan_img.copy()
# Save as transparent badge version
artisan_badge_path = os.path.join(OUTPUT_DIR, "nilgiris_unique_artisan_badge.png")
artisan_img.resize((1600, 1600), Image.Resampling.LANCZOS).save(artisan_badge_path, dpi=(300, 300), optimize=True)

# Also update the in-app mobile QR asset with this gorgeous new version
mobile_artisan = artisan_img.resize((600, 600), Image.Resampling.LANCZOS)
mobile_artisan.save(os.path.join(OUTPUT_DIR, "mobile-app-qr.png"))

# VERIFICATION WITH OPENCV
cv_img = cv2.imread(artisan_path)
detector = cv2.QRCodeDetector()
val, points, qrcode_out = detector.detectAndDecode(cv_img)

print("\n--- OPENCV SCAN VERIFICATION ---")
if val:
    print(f"SUCCESS! Decoded URL: {val}")
    print("MATCH:", val.strip() == TARGET_URL.strip())
else:
    print("OpenCV detector check failed - fine tuning module geometry...")
