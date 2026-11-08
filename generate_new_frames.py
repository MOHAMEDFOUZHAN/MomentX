"""
Nilgiris Frame - Master Generator for 7 High-End Souvenir Frames
Creates:
  1. Rose Blossom & Berry (Feminine / Soft Blush & Floral)
  2. Golden Hour Blush (Feminine / Sunset Peach & Gold)
  3. High Country Explorer (Adventure / Mountain & Compass)
  4. Dark Roast Noir (Adventure / Industrial Matte Carbon & Bronze)
  5. Nilgiris Valley (Universal / British Colonial Lush Tea & Emerald Gold)
  6. Classic Gold Seal (Luxury / 24K Royal Gold & Onyx)
  7. Moments Polaroid (Friends & Fun / Vintage Paper, Washi Tape & Stamp)

All frames:
  - 1080 x 1350 High-Definition Transparent PNG
  - Centered photo cutout window with transparent alpha
  - Custom themed Homewood Tea medallion logo
  - High-res matching 300 x 375 thumbnails
  - NO watermarks
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUTPUT_DIR = 'new frames'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# System Font Paths
FONT_GEORGIA_B = 'C:/Windows/Fonts/georgiab.ttf'
FONT_GEORGIA   = 'C:/Windows/Fonts/georgia.ttf'
FONT_GEORGIA_I = 'C:/Windows/Fonts/georgiai.ttf'
FONT_ARIAL_B   = 'C:/Windows/Fonts/arialbd.ttf'
FONT_ARIAL     = 'C:/Windows/Fonts/arial.ttf'
FONT_SCRIPT    = 'C:/Windows/Fonts/segoeprb.ttf'
FONT_SCRIPT_R  = 'C:/Windows/Fonts/segoepr.ttf'
FONT_CAMBRIA_B = 'C:/Windows/Fonts/cambriab.ttf'

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# ---------------------------------------------------------------------------
# Clean Logo Extraction & Luxury Medallion Generator
# ---------------------------------------------------------------------------
def get_clean_logo():
    src_path = r'C:/Users/fouzh/.gemini/antigravity/brain/0784bde3-2a57-442e-aeb3-2014d2ac91d5/.user_uploaded/media_1794154806845_b634fed9.png'
    im = Image.open(src_path)
    cx, cy, r_inner = 251.5, 246.0, 95.0
    d_inner = int(r_inner * 2)

    mask = Image.new('L', (d_inner * 4, d_inner * 4), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, d_inner * 4, d_inner * 4), fill=255)
    mask = mask.resize((d_inner, d_inner), Image.Resampling.LANCZOS)

    inner_crop = im.crop((int(cx - r_inner), int(cy - r_inner), int(cx + r_inner), int(cy + r_inner)))
    rgb = inner_crop.convert('RGB')
    arr = np.array(rgb, dtype=np.float32)

    diff_rg = np.abs(arr[:,:,0] - arr[:,:,1])
    diff_gb = np.abs(arr[:,:,1] - arr[:,:,2])
    is_gray_light = (arr[:,:,0] > 195) & (diff_rg < 22) & (diff_gb < 22)
    arr[is_gray_light] = 255

    cleaned_rgb = Image.fromarray(arr.astype(np.uint8))
    enh = ImageEnhance.Contrast(cleaned_rgb).enhance(1.22)
    enh_sharp = ImageEnhance.Sharpness(enh).enhance(1.4)

    out = enh_sharp.convert('RGBA')
    out.putalpha(mask)
    return out

CLEAN_LOGO = get_clean_logo()

def create_themed_medallion(style='gold', diameter=140):
    """
    Styles: 'rose_gold', 'sunset_brass', 'explorer_bronze', 'industrial_copper',
            'emerald_heritage', 'imperial_gold', 'vintage_stamp'
    """
    scale = 3
    d = diameter * scale
    canvas = Image.new('RGBA', (d + 80, d + 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    cx, cy = (d + 80) // 2, (d + 80) // 2
    r_outer = d // 2

    # Palettes for medals: (outer_rim, highlight_ring, accent_line, inner_disc)
    palettes = {
        'rose_gold': ((190, 110, 140, 255), (248, 205, 218, 255), (220, 150, 175, 255), (255, 252, 253, 255)),
        'sunset_brass': ((190, 120, 50, 255), (252, 220, 145, 255), (230, 160, 60, 255), (255, 250, 245, 255)),
        'explorer_bronze': ((60, 75, 65, 255), (200, 165, 95, 255), (140, 110, 55, 255), (248, 246, 240, 255)),
        'industrial_copper': ((30, 35, 38, 255), (205, 127, 50, 255), (184, 115, 51, 255), (245, 243, 240, 255)),
        'emerald_heritage': ((14, 45, 30, 255), (230, 195, 110, 255), (180, 140, 60, 255), (255, 254, 250, 255)),
        'imperial_gold': ((140, 105, 25, 255), (255, 225, 120, 255), (218, 175, 55, 255), (255, 255, 255, 255)),
        'vintage_stamp': ((180, 50, 50, 255), (245, 235, 220, 255), (190, 60, 60, 255), (252, 249, 244, 255)),
    }
    c_outer, c_high, c_acc, c_disc = palettes.get(style, palettes['imperial_gold'])

    # Drop shadow
    s_mask = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(s_mask)
    s_draw.ellipse((cx - r_outer + 8, cy - r_outer + 16, cx + r_outer + 8, cy + r_outer + 16), fill=(0, 0, 0, 160))
    s_mask = s_mask.filter(ImageFilter.GaussianBlur(16))
    canvas.paste(s_mask, (0, 0), s_mask)

    # Outer decorative teeth / gear / stars for special styles
    if style in ['industrial_copper', 'explorer_bronze']:
        num_notches = 24
        for i in range(num_notches):
            ang = (i / num_notches) * 2 * math.pi
            nx = cx + (r_outer + int(3 * scale)) * math.cos(ang)
            ny = cy + (r_outer + int(3 * scale)) * math.sin(ang)
            draw.ellipse((nx - 6, ny - 6, nx + 6, ny + 6), fill=c_high)

    # Outer ring
    draw.ellipse((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), fill=c_outer)

    # Highlight bevel ring
    r_high = r_outer - int(4 * scale)
    draw.ellipse((cx - r_high, cy - r_high, cx + r_high, cy + r_high), fill=c_high)

    # Middle stepped ring
    r_mid = r_outer - int(8 * scale)
    draw.ellipse((cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid), fill=c_outer)

    # Hairline ring
    r_acc = r_outer - int(12 * scale)
    draw.ellipse((cx - r_acc, cy - r_acc, cx + r_acc, cy + r_acc), fill=c_acc)

    # Inner disc
    r_disc_size = r_outer - int(14 * scale)
    draw.ellipse((cx - r_disc_size, cy - r_disc_size, cx + r_disc_size, cy + r_disc_size), fill=c_disc)

    # Place Homewood Tea clean logo inside disc
    logo_w = int(r_disc_size * 1.85)
    logo_h = int(r_disc_size * 1.85)
    logo_resized = CLEAN_LOGO.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    canvas.paste(logo_resized, (cx - logo_w // 2, cy - logo_h // 2), logo_resized)

    # Downscale for ultra-smooth antialiasing
    final = canvas.resize((diameter + 24, diameter + 24), Image.Resampling.LANCZOS)
    return final

# ---------------------------------------------------------------------------
# Helper Drawing Utilities
# ---------------------------------------------------------------------------
def draw_sparkle(draw, cx, cy, radius, color):
    """Draw a 4-point luxury star sparkle."""
    pts = [
        (cx, cy - radius),
        (cx + radius * 0.22, cy - radius * 0.22),
        (cx + radius, cy),
        (cx + radius * 0.22, cy + radius * 0.22),
        (cx, cy + radius),
        (cx - radius * 0.22, cy + radius * 0.22),
        (cx - radius, cy),
        (cx - radius * 0.22, cy - radius * 0.22)
    ]
    draw.polygon(pts, fill=color)

def draw_tea_leaf(draw, cx, cy, length, angle_deg, color):
    """Draw an aesthetic stylized tea leaf."""
    ang = math.radians(angle_deg)
    perp = ang + math.pi / 2
    w = length * 0.38
    tip_x = cx + length * math.cos(ang)
    tip_y = cy + length * math.sin(ang)
    c1_x = cx + (length * 0.45) * math.cos(ang) + w * math.cos(perp)
    c1_y = cy + (length * 0.45) * math.sin(ang) + w * math.sin(perp)
    c2_x = cx + (length * 0.45) * math.cos(ang) - w * math.cos(perp)
    c2_y = cy + (length * 0.45) * math.sin(ang) - w * math.sin(perp)
    pts = [(cx, cy), (c1_x, c1_y), (tip_x, tip_y), (c2_x, c2_y)]
    draw.polygon(pts, fill=color)
    draw.line([(cx, cy), (tip_x, tip_y)], fill=(255, 255, 255, 160), width=1)

def draw_corner_bracket(draw, x, y, size, thickness, color, flip_x=False, flip_y=False):
    """Draw luxury geometric corner brackets."""
    dx = -1 if flip_x else 1
    dy = -1 if flip_y else 1
    # Horizontal arm
    draw.line([(x, y), (x + size * dx, y)], fill=color, width=thickness)
    # Vertical arm
    draw.line([(x, y), (x, y + size * dy)], fill=color, width=thickness)

def cut_transparent_photo_window(canvas, x, y, w, h, inner_shadow=True):
    """Cuts out transparent window where customer photo will appear."""
    alpha = canvas.split()[3]
    alpha_arr = np.array(alpha)
    alpha_arr[y:y+h, x:x+w] = 0
    alpha_cut = Image.fromarray(alpha_arr, mode='L')
    canvas.putalpha(alpha_cut)

    if inner_shadow:
        # Subtle inner drop shadow for depth
        s_img = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(s_img)
        s_draw.rectangle([x, y, x + w, y + h], outline=(0, 0, 0, 110), width=3)
        s_draw.rectangle([x+1, y+1, x + w-1, y + h-1], outline=(0, 0, 0, 60), width=2)
        s_img = s_img.filter(ImageFilter.GaussianBlur(3))
        canvas.paste(s_img, (0, 0), s_img)

def save_frame_outputs(canvas, name, x, y, w, h):
    """Saves 1080x1350 frame PNG and 300x375 preview thumbnail with scenic backdrop."""
    png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    canvas.save(png_path, 'PNG', optimize=True)
    print(f"[OK] Saved frame: {png_path}")

    # Build representative thumbnail with soft placeholder image inside cutout
    thumb_canvas = Image.new('RGBA', (1080, 1350), (22, 28, 24, 255))
    t_draw = ImageDraw.Draw(thumb_canvas)

    # Pleasant gradient in photo area
    for i in range(h):
        ratio = i / float(h)
        r = int(35 + 40 * ratio)
        g = int(60 + 50 * ratio)
        b = int(50 + 35 * ratio)
        t_draw.line([(x, y + i), (x + w, y + i)], fill=(r, g, b, 255))

    # Tea leaf silhouette in photo area
    draw_tea_leaf(t_draw, x + w//2, y + h//2 - 20, 130, -45, (255, 255, 255, 45))
    draw_tea_leaf(t_draw, x + w//2, y + h//2 - 20, 110, 45, (255, 255, 255, 35))

    # Composite frame on top
    thumb_canvas.paste(canvas, (0, 0), canvas)

    # Downscale to 300x375
    thumb = thumb_canvas.resize((300, 375), Image.Resampling.LANCZOS)
    thumb_path = os.path.join(OUTPUT_DIR, f"{name}_thumb.png")
    thumb.save(thumb_path, 'PNG', optimize=True)
    print(f"[OK] Saved thumbnail: {thumb_path}")


# ===========================================================================
# 1. 🌸 ROSE BLOSSOM & BERRY (Feminine / Soft Blush & Floral)
# ===========================================================================
def build_frame_rose_blossom():
    name = 'frame_rose_blossom'
    w, h = 1080, 1350
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Outer border background (soft ballet slipper blush with rose-gold gradient)
    for i in range(h):
        t = i / float(h)
        # soft blush pink gradient
        r = int(253 - 10 * t)
        g = int(242 - 12 * t)
        b = int(246 - 8 * t)
        draw.line([(0, i), (w, i)], fill=(r, g, b, 255))

    # Photo Cutout Area
    px, py, pw, ph = 90, 185, 900, 875

    # Decorative inner mats & rose-gold foil keylines
    draw.rectangle([65, 65, w - 65, h - 65], outline=(225, 175, 195, 255), width=2)
    draw.rectangle([73, 73, w - 73, h - 73], outline=(215, 155, 180, 140), width=1)

    # Cutout window border: double gold/rose-gold foil
    draw.rectangle([px - 8, py - 8, px + pw + 8, py + ph + 8], outline=(235, 190, 130, 255), width=2)
    draw.rectangle([px - 4, py - 4, px + pw + 4, py + ph + 4], outline=(255, 255, 255, 255), width=3)
    draw.rectangle([px - 1, py - 1, px + pw + 1, py + ph + 1], outline=(190, 110, 145, 255), width=2)

    # Floral corner sprigs and petals
    corners = [
        (px - 4, py - 4, -45),
        (px + pw + 4, py - 4, -135),
        (px - 4, py + ph + 4, 45),
        (px + pw + 4, py + ph + 4, 135)
    ]
    for cx, cy, ang in corners:
        draw_tea_leaf(draw, cx, cy, 38, ang, (200, 120, 150, 230))
        draw_tea_leaf(draw, cx, cy, 30, ang - 35, (230, 160, 185, 210))
        draw_tea_leaf(draw, cx, cy, 30, ang + 35, (215, 175, 120, 210))
        draw_sparkle(draw, cx + 18 * math.cos(math.radians(ang)), cy + 18 * math.sin(math.radians(ang)), 8, (235, 195, 120, 255))

    # Top Header Typography
    f_sub = get_font(FONT_ARIAL_B, 20)
    f_title = get_font(FONT_GEORGIA_B, 42)
    f_sub2 = get_font(FONT_SCRIPT, 24)

    # Header tracking & text
    top_label = "HOMEWOOD TEA  •  BOTANICAL RESERVE"
    draw.text((w // 2, 95), top_label, font=f_sub, fill=(165, 85, 115, 255), anchor="mm")

    # Sparkle stars in top header
    draw_sparkle(draw, w // 2 - 250, 95, 9, (225, 175, 95, 255))
    draw_sparkle(draw, w // 2 + 250, 95, 9, (225, 175, 95, 255))

    title_text = "Rose Blossom & Wild Berry"
    draw.text((w // 2, 142), title_text, font=f_title, fill=(95, 32, 55, 255), anchor="mm")

    # Bottom Footer Typography & Medallion
    medal = create_themed_medallion('rose_gold', diameter=145)
    medal_x = (w - medal.width) // 2
    medal_y = 1075
    canvas.paste(medal, (medal_x, medal_y), medal)

    # Flanking botanical laurel leaf branches
    for sign in [-1, 1]:
        base_x = w // 2 + sign * 125
        base_y = medal_y + medal.height // 2
        for step in range(5):
            lx = base_x + sign * (step * 28)
            ly = base_y - int(math.sin(step * 0.45) * 22)
            draw_tea_leaf(draw, lx, ly, 24, 0 if sign > 0 else 180, (215, 150, 175, 230))
            draw_tea_leaf(draw, lx, ly, 18, 30 if sign > 0 else 150, (230, 185, 110, 210))

    f_quote = get_font(FONT_SCRIPT, 26)
    f_tag = get_font(FONT_GEORGIA_I, 21)

    draw.text((w // 2, 1245), "Pure Nilgiri Floral Infusion  •  Handcrafted Memories", font=f_quote, fill=(115, 45, 75, 255), anchor="mm")
    draw.text((w // 2, 1282), "ESTABLISHED IN THE HIGH BLUE MOUNTAINS  •  100% ORIGINAL", font=f_tag, fill=(165, 95, 125, 230), anchor="mm")

    # Cut out transparent photo window
    cut_transparent_photo_window(canvas, px, py, pw, ph)
    save_frame_outputs(canvas, name, px, py, pw, ph)


# ===========================================================================
# 2. 🌅 GOLDEN HOUR BLUSH (Feminine / Sunset Peach & Gold)
# ===========================================================================
def build_frame_golden_hour():
    name = 'frame_golden_hour'
    w, h = 1080, 1350
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Warm peach and apricot sunset glow
    for i in range(h):
        t = i / float(h)
        r = int(255 - 18 * t)
        g = int(240 - 28 * t)
        b = int(230 - 35 * t)
        draw.line([(0, i), (w, i)], fill=(r, g, b, 255))

    px, py, pw, ph = 90, 185, 900, 875

    # Double sunburst gold hairline framing
    draw.rectangle([65, 65, w - 65, h - 65], outline=(230, 175, 95, 255), width=2)
    draw.rectangle([74, 74, w - 74, h - 74], outline=(245, 205, 140, 150), width=1)

    # Inner cutout border: glowing sunset gold
    draw.rectangle([px - 8, py - 8, px + pw + 8, py + ph + 8], outline=(225, 155, 65, 255), width=2)
    draw.rectangle([px - 4, py - 4, px + pw + 4, py + ph + 4], outline=(255, 255, 255, 255), width=3)
    draw.rectangle([px - 1, py - 1, px + pw + 1, py + ph + 1], outline=(195, 105, 45, 255), width=2)

    # Corner sunburst flourishes
    corners = [(px - 4, py - 4), (px + pw + 4, py - 4), (px - 4, py + ph + 4), (px + pw + 4, py + ph + 4)]
    for cx, cy in corners:
        draw_sparkle(draw, cx, cy, 14, (245, 185, 80, 255))
        draw_sparkle(draw, cx, cy, 8, (255, 240, 190, 255))

    # Top Header
    f_sub = get_font(FONT_ARIAL_B, 20)
    f_title = get_font(FONT_GEORGIA_B, 40)
    f_script = get_font(FONT_SCRIPT, 26)

    draw.text((w // 2, 92), "NILGIRIS  GOLDEN  HOUR  COLLECTION", font=f_sub, fill=(185, 95, 45, 255), anchor="mm")
    draw_sparkle(draw, w // 2 - 275, 92, 9, (235, 170, 75, 255))
    draw_sparkle(draw, w // 2 + 275, 92, 9, (235, 170, 75, 255))

    draw.text((w // 2, 140), "Chasing Sunsets & Mountain Brews", font=f_script, fill=(145, 55, 25, 255), anchor="mm")

    # Bottom Footer Typography & Medallion
    medal = create_themed_medallion('sunset_brass', diameter=145)
    medal_x = (w - medal.width) // 2
    medal_y = 1075
    canvas.paste(medal, (medal_x, medal_y), medal)

    # Sunburst rays behind medallion
    for sign in [-1, 1]:
        base_x = w // 2 + sign * 125
        base_y = medal_y + medal.height // 2
        for step in range(5):
            lx = base_x + sign * (step * 28)
            draw_sparkle(draw, lx, base_y, 7 + step * 2, (235, 170, 75, 230))

    f_quote = get_font(FONT_GEORGIA_B, 24)
    f_tag = get_font(FONT_ARIAL, 18)

    draw.text((w // 2, 1245), "HIGHER ELEVATION  •  WARMER MEMORIES", font=f_quote, fill=(125, 48, 20, 255), anchor="mm")
    draw.text((w // 2, 1282), "ELEVATION 2,240M  •  HOMEWOOD TEA GARDENS, OOTY", font=f_tag, fill=(175, 95, 50, 230), anchor="mm")

    cut_transparent_photo_window(canvas, px, py, pw, ph)
    save_frame_outputs(canvas, name, px, py, pw, ph)


# ===========================================================================
# 3. ⛰️ HIGH COUNTRY EXPLORER (Adventure / Guys / Mountain Trekkers)
# ===========================================================================
def build_frame_high_country():
    name = 'frame_high_country'
    w, h = 1080, 1350
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Tactical alpine forest green & slate background
    for i in range(h):
        t = i / float(h)
        r = int(12 + 10 * t)
        g = int(28 + 15 * t)
        b = int(20 + 12 * t)
        draw.line([(0, i), (w, i)], fill=(r, g, b, 255))

    px, py, pw, ph = 90, 185, 900, 875

    # Topographic isolines motif across top & bottom
    for row_y in [105, 125, 1105, 1125]:
        draw.line([(60, row_y), (w - 60, row_y)], fill=(55, 85, 68, 120), width=1)

    # Explorer border with brass rivets
    draw.rectangle([65, 65, w - 65, h - 65], outline=(195, 155, 80, 240), width=2)
    draw.rectangle([74, 74, w - 74, h - 74], outline=(85, 120, 95, 150), width=1)

    # Corner brass rivets
    rivets = [(70, 70), (w - 70, 70), (70, h - 70), (w - 70, h - 70)]
    for rx, ry in rivets:
        draw.ellipse((rx - 7, ry - 7, rx + 7, ry + 7), fill=(215, 175, 95, 255), outline=(50, 40, 20, 255))

    # Inner cutout border: rugged alpine frame with corner brackets
    draw.rectangle([px - 8, py - 8, px + pw + 8, py + ph + 8], outline=(185, 145, 75, 255), width=2)
    draw.rectangle([px - 4, py - 4, px + pw + 4, py + ph + 4], outline=(22, 38, 28, 255), width=3)
    draw.rectangle([px - 1, py - 1, px + pw + 1, py + ph + 1], outline=(215, 175, 95, 255), width=2)

    # Heavy corner brackets
    draw_corner_bracket(draw, px - 6, py - 6, 45, 4, (225, 185, 105, 255))
    draw_corner_bracket(draw, px + pw + 6, py - 6, 45, 4, (225, 185, 105, 255), flip_x=True)
    draw_corner_bracket(draw, px - 6, py + ph + 6, 45, 4, (225, 185, 105, 255), flip_y=True)
    draw_corner_bracket(draw, px + pw + 6, py + ph + 6, 45, 4, (225, 185, 105, 255), flip_x=True, flip_y=True)

    # Top Header
    f_sub = get_font(FONT_ARIAL_B, 18)
    f_title = get_font(FONT_GEORGIA_B, 38)

    draw.text((w // 2, 92), "▲  NILGIRIS  MOUNTAIN  EXPEDITION  SERIES  ▲", font=f_sub, fill=(195, 160, 95, 255), anchor="mm")
    draw.text((w // 2, 138), "BORN TO ROAM  •  HIGH COUNTRY", font=f_title, fill=(245, 240, 225, 255), anchor="mm")

    # Bottom Footer Typography & Medallion
    medal = create_themed_medallion('explorer_bronze', diameter=145)
    medal_x = (w - medal.width) // 2
    medal_y = 1075
    canvas.paste(medal, (medal_x, medal_y), medal)

    # Compass points on sides
    f_compass = get_font(FONT_ARIAL_B, 22)
    draw.text((w // 2 - 120, medal_y + medal.height // 2), "◀ W", font=f_compass, fill=(195, 160, 95, 220), anchor="rm")
    draw.text((w // 2 + 120, medal_y + medal.height // 2), "E ▶", font=f_compass, fill=(195, 160, 95, 220), anchor="lm")

    f_quote = get_font(FONT_ARIAL_B, 22)
    f_tag = get_font(FONT_ARIAL, 18)

    draw.text((w // 2, 1245), "ELEVATION: 2,637M  •  PEAK RIDGE TRAILS", font=f_quote, fill=(235, 215, 165, 255), anchor="mm")
    draw.text((w // 2, 1282), "HOMEWOOD TEA FACTORY  •  ARTISAN ALPINE RESERVE", font=f_tag, fill=(160, 185, 170, 220), anchor="mm")

    cut_transparent_photo_window(canvas, px, py, pw, ph)
    save_frame_outputs(canvas, name, px, py, pw, ph)


# ===========================================================================
# 4. ☕ DARK ROAST NOIR (Adventure / Guys / Bold Industrial)
# ===========================================================================
def build_frame_dark_roast():
    name = 'frame_dark_roast'
    w, h = 1080, 1350
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Matte carbon obsidian background
    for i in range(h):
        t = i / float(h)
        r = int(14 + 10 * t)
        g = int(16 + 10 * t)
        b = int(19 + 10 * t)
        draw.line([(0, i), (w, i)], fill=(r, g, b, 255))

    px, py, pw, ph = 90, 185, 900, 875

    # Industrial burnt copper keylines
    draw.rectangle([65, 65, w - 65, h - 65], outline=(195, 115, 45, 240), width=2)
    draw.rectangle([74, 74, w - 74, h - 74], outline=(80, 85, 90, 150), width=1)

    # Industrial corner bolts
    bolts = [(70, 70), (w - 70, 70), (70, h - 70), (w - 70, h - 70)]
    for bx, by in bolts:
        draw.ellipse((bx - 8, by - 8, bx + 8, by + 8), fill=(205, 127, 50, 255), outline=(10, 10, 12, 255))

    # Inner cutout border: precision beveled industrial copper
    draw.rectangle([px - 8, py - 8, px + pw + 8, py + ph + 8], outline=(190, 110, 40, 255), width=2)
    draw.rectangle([px - 4, py - 4, px + pw + 4, py + ph + 4], outline=(28, 32, 36, 255), width=3)
    draw.rectangle([px - 1, py - 1, px + pw + 1, py + ph + 1], outline=(225, 140, 60, 255), width=2)

    # Chamfered corner accents
    draw_corner_bracket(draw, px - 6, py - 6, 40, 4, (215, 130, 50, 255))
    draw_corner_bracket(draw, px + pw + 6, py - 6, 40, 4, (215, 130, 50, 255), flip_x=True)
    draw_corner_bracket(draw, px - 6, py + ph + 6, 40, 4, (215, 130, 50, 255), flip_y=True)
    draw_corner_bracket(draw, px + pw + 6, py + ph + 6, 40, 4, (215, 130, 50, 255), flip_x=True, flip_y=True)

    # Top Header
    f_sub = get_font(FONT_ARIAL_B, 18)
    f_title = get_font(FONT_ARIAL_B, 38)

    draw.text((w // 2, 92), "HOMEWOOD  FACTORY  ROAST  •  RESERVE  NOIR", font=f_sub, fill=(210, 135, 60, 255), anchor="mm")
    draw.text((w // 2, 138), "MASTER BREWER EDITION", font=f_title, fill=(250, 245, 235, 255), anchor="mm")

    # Bottom Footer Typography & Medallion
    medal = create_themed_medallion('industrial_copper', diameter=145)
    medal_x = (w - medal.width) // 2
    medal_y = 1075
    canvas.paste(medal, (medal_x, medal_y), medal)

    # Mechanical technical rules flanking medallion
    for sign in [-1, 1]:
        base_x = w // 2 + sign * 125
        base_y = medal_y + medal.height // 2
        draw.line([(base_x, base_y), (base_x + sign * 180, base_y)], fill=(195, 115, 45, 220), width=2)
        draw.ellipse((base_x + sign * 180 - 4, base_y - 4, base_x + sign * 180 + 4, base_y + 4), fill=(215, 140, 65, 255))

    f_quote = get_font(FONT_ARIAL_B, 22)
    f_tag = get_font(FONT_ARIAL, 18)

    draw.text((w // 2, 1245), "BOLD  •  SMOKY  •  UNCOMPROMISING", font=f_quote, fill=(225, 145, 65, 255), anchor="mm")
    draw.text((w // 2, 1282), "BATCH NO. 07  •  FIRE-CURED NILGIRI LEAF  •  EST. 1935", font=f_tag, fill=(160, 165, 170, 220), anchor="mm")

    cut_transparent_photo_window(canvas, px, py, pw, ph)
    save_frame_outputs(canvas, name, px, py, pw, ph)


# ===========================================================================
# 5. 🍃 NILGIRIS VALLEY (Universal Heritage / Families & Nature)
# ===========================================================================
def build_frame_nilgiri_valley():
    name = 'frame_nilgiri_valley'
    w, h = 1080, 1350
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Deep British-colonial tea green background
    for i in range(h):
        t = i / float(h)
        r = int(10 + 8 * t)
        g = int(36 + 12 * t)
        b = int(24 + 10 * t)
        draw.line([(0, i), (w, i)], fill=(r, g, b, 255))

    px, py, pw, ph = 90, 185, 900, 875

    # 24K Gold foil keylines
    draw.rectangle([65, 65, w - 65, h - 65], outline=(215, 175, 80, 240), width=2)
    draw.rectangle([74, 74, w - 74, h - 74], outline=(150, 120, 55, 150), width=1)

    # Cutout border: gold leaf & forest green
    draw.rectangle([px - 8, py - 8, px + pw + 8, py + ph + 8], outline=(225, 185, 85, 255), width=2)
    draw.rectangle([px - 4, py - 4, px + pw + 4, py + ph + 4], outline=(14, 48, 32, 255), width=3)
    draw.rectangle([px - 1, py - 1, px + pw + 1, py + ph + 1], outline=(245, 215, 115, 255), width=2)

    # Tea leaf flourishes at 4 corners
    corners = [
        (px - 4, py - 4, -45),
        (px + pw + 4, py - 4, -135),
        (px - 4, py + ph + 4, 45),
        (px + pw + 4, py + ph + 4, 135)
    ]
    for cx, cy, ang in corners:
        draw_tea_leaf(draw, cx, cy, 42, ang, (235, 195, 95, 240))
        draw_tea_leaf(draw, cx, cy, 32, ang - 30, (140, 195, 150, 220))
        draw_tea_leaf(draw, cx, cy, 32, ang + 30, (140, 195, 150, 220))

    # Top Header
    f_sub = get_font(FONT_ARIAL_B, 18)
    f_title = get_font(FONT_GEORGIA_B, 42)

    draw.text((w // 2, 92), "THE  NILGIRIS  VALLEY  HERITAGE", font=f_sub, fill=(225, 185, 85, 255), anchor="mm")
    draw.text((w // 2, 138), "Where Nature Feels Like Home", font=f_title, fill=(255, 250, 240, 255), anchor="mm")

    # Bottom Footer Typography & Medallion
    medal = create_themed_medallion('emerald_heritage', diameter=145)
    medal_x = (w - medal.width) // 2
    medal_y = 1075
    canvas.paste(medal, (medal_x, medal_y), medal)

    # Flanking golden tea branch sprays
    for sign in [-1, 1]:
        base_x = w // 2 + sign * 125
        base_y = medal_y + medal.height // 2
        for step in range(5):
            lx = base_x + sign * (step * 28)
            draw_tea_leaf(draw, lx, base_y, 25, 0 if sign > 0 else 180, (235, 195, 95, 230))

    f_quote = get_font(FONT_GEORGIA_B, 24)
    f_tag = get_font(FONT_ARIAL, 18)

    draw.text((w // 2, 1245), "FROM OUR MOUNTAIN GARDENS TO YOUR CUP", font=f_quote, fill=(245, 215, 115, 255), anchor="mm")
    draw.text((w // 2, 1282), "BLUE MOUNTAIN ESTATE  •  OOTY  •  PURE NILGIRI TEA", font=f_tag, fill=(185, 210, 195, 220), anchor="mm")

    cut_transparent_photo_window(canvas, px, py, pw, ph)
    save_frame_outputs(canvas, name, px, py, pw, ph)


# ===========================================================================
# 6. ✨ CLASSIC GOLD SEAL (Luxury / VIP Souvenir)
# ===========================================================================
def build_frame_classic_gold():
    name = 'frame_classic_gold'
    w, h = 1080, 1350
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Rich imperial midnight onyx background
    for i in range(h):
        t = i / float(h)
        r = int(12 + 6 * t)
        g = int(14 + 6 * t)
        b = int(16 + 6 * t)
        draw.line([(0, i), (w, i)], fill=(r, g, b, 255))

    px, py, pw, ph = 90, 185, 900, 875

    # Double 24K gold foil keylines
    draw.rectangle([65, 65, w - 65, h - 65], outline=(235, 195, 80, 255), width=3)
    draw.rectangle([74, 74, w - 74, h - 74], outline=(180, 140, 50, 180), width=1)

    # Cutout border: luxury 3-tier gold molding
    draw.rectangle([px - 10, py - 10, px + pw + 10, py + ph + 10], outline=(175, 130, 40, 255), width=2)
    draw.rectangle([px - 6, py - 6, px + pw + 6, py + ph + 6], outline=(255, 225, 125, 255), width=3)
    draw.rectangle([px - 2, py - 2, px + pw + 2, py + ph + 2], outline=(195, 150, 50, 255), width=2)

    # Regal corner finials
    for cx, cy in [(px - 6, py - 6), (px + pw + 6, py - 6), (px - 6, py + ph + 6), (px + pw + 6, py + ph + 6)]:
        draw_sparkle(draw, cx, cy, 16, (255, 225, 120, 255))
        draw_sparkle(draw, cx, cy, 9, (255, 255, 255, 255))

    # Top Header
    f_sub = get_font(FONT_ARIAL_B, 18)
    f_title = get_font(FONT_GEORGIA_B, 42)

    draw.text((w // 2, 92), "★  HOMEWOOD  IMPERIAL  RESERVE  ★", font=f_sub, fill=(235, 195, 80, 255), anchor="mm")
    draw.text((w // 2, 138), "The Gold Standard of Mountain Tea", font=f_title, fill=(255, 255, 255, 255), anchor="mm")

    # Bottom Footer Typography & Medallion
    medal = create_themed_medallion('imperial_gold', diameter=145)
    medal_x = (w - medal.width) // 2
    medal_y = 1075
    canvas.paste(medal, (medal_x, medal_y), medal)

    # Imperial gold star bursts
    for sign in [-1, 1]:
        base_x = w // 2 + sign * 125
        base_y = medal_y + medal.height // 2
        for step in range(5):
            lx = base_x + sign * (step * 28)
            draw_sparkle(draw, lx, base_y, 7 + step * 2, (245, 205, 95, 230))

    f_quote = get_font(FONT_GEORGIA_B, 24)
    f_tag = get_font(FONT_ARIAL, 18)

    draw.text((w // 2, 1245), "PREMIUM TEA FOR A BETTER YOU", font=f_quote, fill=(255, 225, 120, 255), anchor="mm")
    draw.text((w // 2, 1282), "ESTATE RESERVE  •  GRAND CRU HARVEST  •  100% ORIGINAL", font=f_tag, fill=(205, 180, 125, 220), anchor="mm")

    cut_transparent_photo_window(canvas, px, py, pw, ph)
    save_frame_outputs(canvas, name, px, py, pw, ph)


# ===========================================================================
# 7. 📷 MOMENTS POLAROID (Friends & Fun / Scrapbook Memories)
# ===========================================================================
def build_frame_moments_polaroid():
    name = 'frame_moments_polaroid'
    w, h = 1080, 1350
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Warm vintage textured polaroid cardstock
    for i in range(h):
        t = i / float(h)
        r = int(252 - 4 * t)
        g = int(249 - 6 * t)
        b = int(244 - 8 * t)
        draw.line([(0, i), (w, i)], fill=(r, g, b, 255))

    # Polaroid Cutout: Large square window (ideal for big group photos)
    px, py, pw, ph = 80, 125, 920, 920

    # Delicate beveled polaroid cutout aperture
    draw.rectangle([px - 4, py - 4, px + pw + 4, py + ph + 4], outline=(230, 225, 215, 255), width=2)
    draw.rectangle([px - 1, py - 1, px + pw + 1, py + ph + 1], outline=(190, 180, 165, 255), width=2)

    # Tilted gold washi tape at top center
    tape_w, tape_h = 170, 44
    tape_x = (w - tape_w) // 2
    tape_y = 48
    draw.rectangle([tape_x, tape_y, tape_x + tape_w, tape_y + tape_h], fill=(230, 195, 110, 210), outline=(190, 150, 70, 240))
    # Washi tape subtle diagonal stripes
    for off in range(-20, tape_w + 20, 14):
        draw.line([(tape_x + off, tape_y), (tape_x + off + 15, tape_y + tape_h)], fill=(255, 235, 175, 140), width=3)

    # Bottom Polaroid Footer Margin
    # Stamp on right: "NILGIRIS HIGH COUNTRY • AIR MAIL"
    stamp_x, stamp_y = w - 170, 1155
    draw.ellipse((stamp_x - 48, stamp_y - 48, stamp_x + 48, stamp_y + 48), outline=(180, 60, 60, 200), width=2)
    draw.ellipse((stamp_x - 42, stamp_y - 42, stamp_x + 42, stamp_y + 42), outline=(180, 60, 60, 160), width=1)
    f_stamp = get_font(FONT_ARIAL_B, 13)
    draw.text((stamp_x, stamp_y - 12), "HOMEWOOD", font=f_stamp, fill=(180, 60, 60, 220), anchor="mm")
    draw.text((stamp_x, stamp_y + 10), "★ OOTY ★", font=f_stamp, fill=(180, 60, 60, 220), anchor="mm")

    # Center: Themed Medallion
    medal = create_themed_medallion('vintage_stamp', diameter=145)
    medal_x = 100
    medal_y = 1115
    canvas.paste(medal, (medal_x, medal_y), medal)

    # Handwritten script text in Polaroid bottom margin
    f_hand = get_font(FONT_SCRIPT, 36)
    f_sub = get_font(FONT_ARIAL_B, 19)

    draw.text((w // 2 + 35, 1135), "Moments like this last forever... ☕✨", font=f_hand, fill=(45, 42, 38, 255), anchor="mm")
    draw.text((w // 2 + 35, 1205), "EXPLORE  •  BREATHE  •  SIP  •  REPEAT", font=f_sub, fill=(160, 95, 45, 240), anchor="mm")
    draw.text((w // 2 + 35, 1245), "HOMEWOOD TEA FACTORY  •  TRAVEL DIARY SOUVENIR", font=get_font(FONT_ARIAL, 16), fill=(120, 115, 105, 230), anchor="mm")

    cut_transparent_photo_window(canvas, px, py, pw, ph)
    save_frame_outputs(canvas, name, px, py, pw, ph)


# ---------------------------------------------------------------------------
# Run Master Build
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 64)
    print("Generating 7 All-New High-End Souvenir Frames...")
    print("=" * 64)
    build_frame_rose_blossom()
    build_frame_golden_hour()
    build_frame_high_country()
    build_frame_dark_roast()
    build_frame_nilgiri_valley()
    build_frame_classic_gold()
    build_frame_moments_polaroid()
    print("=" * 64)
    print("All 7 frames and thumbnails generated in 'new frames/' successfully!")
    print("=" * 64)
