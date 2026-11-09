"""
Process All 9 Uploaded AI Frames:
1. Resize to 1080x1350 (standard 4:5 souvenir ratio).
2. Segment and make center photo window 100% transparent.
3. Tastefully integrate the Homewood Tea logo medallion onto the lower frame border.
4. Measure exact cutout bounding boxes and stage percentages.
5. Create matching 300x375 preview thumbnails with scenic backdrop.
6. Export exact campaign configuration for js/campaigns.js.
"""

import os
import json
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from scipy import ndimage

INPUT_DIR = 'new frames'
OUTPUT_DIR = 'new frames'

# Load clean base logo
src_logo_path = r'C:/Users/fouzh/.gemini/antigravity/brain/0784bde3-2a57-442e-aeb3-2014d2ac91d5/.user_uploaded/media_1794154806845_b634fed9.png'
im_logo = Image.open(src_logo_path)
cx, cy, r_inner = 251.5, 246.0, 95.0
d_inner = int(r_inner * 2)

mask = Image.new('L', (d_inner * 4, d_inner * 4), 0)
d = ImageDraw.Draw(mask)
d.ellipse((0, 0, d_inner * 4, d_inner * 4), fill=255)
mask = mask.resize((d_inner, d_inner), Image.Resampling.LANCZOS)

inner_crop = im_logo.crop((int(cx - r_inner), int(cy - r_inner), int(cx + r_inner), int(cy + r_inner)))
rgb = inner_crop.convert('RGB')
arr = np.array(rgb, dtype=np.float32)

diff_rg = np.abs(arr[:,:,0] - arr[:,:,1])
diff_gb = np.abs(arr[:,:,1] - arr[:,:,2])
is_gray_light = (arr[:,:,0] > 195) & (diff_rg < 22) & (diff_gb < 22)
arr[is_gray_light] = 255

cleaned_rgb = Image.fromarray(arr.astype(np.uint8))
enh = ImageEnhance.Contrast(cleaned_rgb).enhance(1.22)
enh_sharp = ImageEnhance.Sharpness(enh).enhance(1.4)
CLEAN_LOGO = enh_sharp.convert('RGBA')
CLEAN_LOGO.putalpha(mask)

def create_themed_medallion(style='gold', diameter=125):
    scale = 3
    d = diameter * scale
    canvas = Image.new('RGBA', (d + 60, d + 60), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    cx, cy = (d + 60) // 2, (d + 60) // 2
    r_outer = d // 2

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
    s_draw.ellipse((cx - r_outer + 6, cy - r_outer + 12, cx + r_outer + 6, cy + r_outer + 12), fill=(0, 0, 0, 140))
    s_mask = s_mask.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(s_mask, (0, 0), s_mask)

    # Outer ring
    draw.ellipse((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), fill=c_outer)
    # Highlight bevel ring
    r_high = r_outer - int(3 * scale)
    draw.ellipse((cx - r_high, cy - r_high, cx + r_high, cy + r_high), fill=c_high)
    # Middle stepped ring
    r_mid = r_outer - int(6 * scale)
    draw.ellipse((cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid), fill=c_outer)
    # Hairline ring
    r_acc = r_outer - int(9 * scale)
    draw.ellipse((cx - r_acc, cy - r_acc, cx + r_acc, cy + r_acc), fill=c_acc)
    # Inner porcelain disc
    r_disc_size = r_outer - int(11 * scale)
    draw.ellipse((cx - r_disc_size, cy - r_disc_size, cx + r_disc_size, cy + r_disc_size), fill=c_disc)

    # Place Homewood Tea logo
    logo_w = int(r_disc_size * 1.85)
    logo_resized = CLEAN_LOGO.resize((logo_w, logo_w), Image.Resampling.LANCZOS)
    canvas.paste(logo_resized, (cx - logo_w // 2, cy - logo_w // 2), logo_resized)

    return canvas.resize((diameter + 20, diameter + 20), Image.Resampling.LANCZOS)

FRAME_DEFS = [
    {
        'raw_filename': 'Homewood Tea Rose Garden Frame.png',
        'id': 'rose-garden',
        'name': 'Rose Garden Blush',
        'category': 'Feminine / Aesthetic',
        'badgeIcon': '🌸',
        'tag': 'Rose & Botanicals',
        'themeName': 'Soft Blush Pink & Wild Rose',
        'campaignTitle': 'Rose Garden & Wild Petals',
        'campaignSubtitle': 'Soft blush pink, wild rose petals and delicate gold leaf',
        'style': 'rose_gold',
        'primaryColor': '#8e3852',
        'goldColor': '#dfb85b',
        'darkBg': '#2a141d',
        'accentColor': '#c27ba0',
        'textColor': '#faf7f0',
        'hashtags': ['#HomewoodTea', '#RoseGarden', '#NilgiriMoments', '#AestheticTea', '#Nilgiris'],
        'shareText': 'Sipping wild rose tea in the misty hills of the Nilgiris 🌸✨ #HomewoodTea #RoseGarden'
    },
    {
        'raw_filename': 'Homewood Tea Sunset Frame.png',
        'id': 'sunset-glow',
        'name': 'Golden Sunset Glow',
        'category': 'Feminine / Aesthetic',
        'badgeIcon': '🌅',
        'tag': 'Golden Hour',
        'themeName': 'Warm Peach & Sunset Gold',
        'campaignTitle': 'Chasing Sunsets & Mountain Brews',
        'campaignSubtitle': 'Warm peach & rose-gold gradient with glowing mountain mist',
        'style': 'sunset_brass',
        'primaryColor': '#b85d43',
        'goldColor': '#e5a93b',
        'darkBg': '#2b160e',
        'accentColor': '#f7c2a5',
        'textColor': '#fffbf5',
        'hashtags': ['#GoldenHour', '#HomewoodTea', '#NilgiriSunset', '#MountainBrews', '#Ooty'],
        'shareText': 'Higher elevation, warmer memories. Chasing sunsets with Homewood Tea 🌅☕ #GoldenHour #HomewoodTea'
    },
    {
        'raw_filename': 'Lavender Tea Garden Photo Frame.png',
        'id': 'lavender-serenity',
        'name': 'Lavender Tea Garden',
        'category': 'Feminine / Aesthetic',
        'badgeIcon': '🪻',
        'tag': 'Floral Serenity',
        'themeName': 'Pastel Lavender & Lilac Mist',
        'campaignTitle': 'Lavender Fields & Mountain Serenity',
        'campaignSubtitle': 'Delicate purple blossoms, serene lavender mist and tea flora',
        'style': 'rose_gold',
        'primaryColor': '#6b4c7d',
        'goldColor': '#d8b4e2',
        'darkBg': '#1d1324',
        'accentColor': '#9b72b0',
        'textColor': '#faf6fc',
        'hashtags': ['#LavenderTea', '#HomewoodTea', '#PurpleSerenity', '#NilgiriGardens', '#OotyFlora'],
        'shareText': 'Basking in the gentle lavender breeze at Homewood Tea Gardens 🪻🍃 #LavenderTea #HomewoodTea'
    },
    {
        'raw_filename': 'High Country Tea Explorer Frame.png',
        'id': 'high-country',
        'name': 'High Country Explorer',
        'category': 'Adventure & Rugged',
        'badgeIcon': '⛰️',
        'tag': 'Mountain Explorer',
        'themeName': 'Alpine Forest Pine & Brass',
        'campaignTitle': 'Born to Roam • High Country',
        'campaignSubtitle': 'Tactical forest green, topographic contours & rugged compass badge',
        'style': 'explorer_bronze',
        'primaryColor': '#0a1d13',
        'goldColor': '#c99a3e',
        'darkBg': '#09150d',
        'accentColor': '#1b2320',
        'textColor': '#f5f0e1',
        'hashtags': ['#HighCountry', '#HomewoodTea', '#BornToRoam', '#NilgiriTrek', '#MountainExplorer'],
        'shareText': 'Born to roam the high country. Trekking the misty Nilgiris peaks ⛰️🌲 #HighCountry #HomewoodTea'
    },
    {
        'raw_filename': 'Nilgiris Explorer Tea Adventure Frame.png',
        'id': 'nilgiris-adventure',
        'name': 'Nilgiris Trail Adventure',
        'category': 'Adventure & Rugged',
        'badgeIcon': '🧭',
        'tag': 'Peak Expedition',
        'themeName': 'Summit Ridge & Antique Compass',
        'campaignTitle': 'Nilgiris Mountain Trail Adventure',
        'campaignSubtitle': 'Mountain ridge silhouettes, trail compass and vintage expedition styling',
        'style': 'explorer_bronze',
        'primaryColor': '#18241e',
        'goldColor': '#d4a34b',
        'darkBg': '#0d1410',
        'accentColor': '#2a3d33',
        'textColor': '#f7f4ea',
        'hashtags': ['#NilgiriTrail', '#HomewoodTea', '#PeakAdventure', '#MountainTrek', '#BornWild'],
        'shareText': 'Every trail leads to extraordinary views and great tea 🧭⛰️ #NilgiriTrail #HomewoodTea'
    },
    {
        'raw_filename': 'Dark Roast Noir Tea Frame.png',
        'id': 'dark-roast',
        'name': 'Dark Roast Noir',
        'category': 'Adventure & Bold',
        'badgeIcon': '☕',
        'tag': 'Industrial Roast',
        'themeName': 'Matte Carbon Obsidian & Copper',
        'campaignTitle': 'Master Brewer Edition • Reserve Noir',
        'campaignSubtitle': 'Sleek matte black & gunmetal bronze with bold factory roast seal',
        'style': 'industrial_copper',
        'primaryColor': '#141719',
        'goldColor': '#cd7f32',
        'darkBg': '#0b0d0e',
        'accentColor': '#2a2f35',
        'textColor': '#faf5eb',
        'hashtags': ['#DarkRoastNoir', '#HomewoodTea', '#MasterBrewer', '#BoldFlavors', '#FactoryReserve'],
        'shareText': 'Bold, smoky, and uncompromising. Savoring the Master Brewer Reserve ☕🔥 #DarkRoastNoir #HomewoodTea'
    },
    {
        'raw_filename': 'Nilgiris Valley Tea Frame.png',
        'id': 'nilgiris-valley',
        'name': 'Nilgiris Valley Heritage',
        'category': 'Universal Heritage',
        'badgeIcon': '🍃',
        'tag': 'Classic Estate',
        'themeName': 'British Colonial Tea Green & Gold Leaf',
        'campaignTitle': 'The Nilgiris Valley Heritage',
        'campaignSubtitle': 'Lush green tea gardens, mist and traditional imperial valley seal',
        'style': 'emerald_heritage',
        'primaryColor': '#0d2b1d',
        'goldColor': '#d4af37',
        'darkBg': '#091c13',
        'accentColor': '#16432f',
        'textColor': '#faf7f0',
        'hashtags': ['#NilgirisValley', '#HomewoodTea', '#WhereNatureFeelsLikeHome', '#PureTea', '#OotyMoments'],
        'shareText': 'Preserving a timeless moment in the misty Nilgiris hills 🍃✨ #NilgirisValley #HomewoodTea'
    },
    {
        'raw_filename': 'Homewood Tea Nilgiris Heritage Frame.png',
        'id': 'classic-heritage',
        'name': 'Imperial Gold Heritage',
        'category': 'Luxury & VIP',
        'badgeIcon': '✨',
        'tag': 'Imperial Gold',
        'themeName': '24K Imperial Gold & Royal Velvet',
        'campaignTitle': 'Homewood Imperial Reserve',
        'campaignSubtitle': 'Imperial champagne gold borders with royal tea crest and crown finials',
        'style': 'imperial_gold',
        'primaryColor': '#16130b',
        'goldColor': '#ffd700',
        'darkBg': '#090805',
        'accentColor': '#dfb743',
        'textColor': '#fffdf5',
        'hashtags': ['#ClassicGold', '#HomewoodTea', '#ImperialReserve', '#GoldStandard', '#LuxuryTea'],
        'shareText': 'Sipping the gold standard of mountain tea with Homewood Imperial Reserve ✨🫖 #ClassicGold #HomewoodTea'
    },
    {
        'raw_filename': 'Homewood Tea Nilgiris Scrapbook Frame.png',
        'id': 'moments-scrapbook',
        'name': 'Moments Scrapbook Polaroid',
        'category': 'Friends & Fun',
        'badgeIcon': '📷',
        'tag': 'Travel Polaroid',
        'themeName': 'Fine Art Cardstock & Postal Stamp',
        'campaignTitle': 'Moments Like This Last Forever',
        'campaignSubtitle': 'Retro travel scrapbook with gold washi tape, stamps & wide photo window',
        'style': 'vintage_stamp',
        'primaryColor': '#2d2a26',
        'goldColor': '#e2be6c',
        'darkBg': '#1a1816',
        'accentColor': '#f4f1ea',
        'textColor': '#2d2a26',
        'hashtags': ['#MomentsLikeThis', '#HomewoodTea', '#PolaroidMemories', '#TravelDiary', '#OotyTrip'],
        'shareText': 'Moments like this last forever... 📷✨ Exploring the Nilgiris with friends #MomentsLikeThis #HomewoodTea'
    }
]

campaigns_config = []

print("=" * 64)
print("Processing 9 All-New Frames...")
print("=" * 64)

for defn in FRAME_DEFS:
    raw_path = os.path.join(INPUT_DIR, defn['raw_filename'])
    if not os.path.exists(raw_path):
        print(f"Error: {raw_path} not found!")
        continue

    im = Image.open(raw_path).convert('RGB')
    orig_w, orig_h = im.size

    # Resize to exact standard 1080 x 1350
    target_w, target_h = 1080, 1350
    im_scaled = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    arr = np.array(im_scaled)

    # Detect white cutout window from center (using int32 to avoid uint8 overflow)
    r = arr[:, :, 0].astype(np.int32)
    g = arr[:, :, 1].astype(np.int32)
    b = arr[:, :, 2].astype(np.int32)
    is_white = (r >= 238) & (g >= 238) & (b >= 238) & (np.abs(r - g) < 16) & (np.abs(g - b) < 16)

    labels, num = ndimage.label(is_white)
    counts = np.bincount(labels.ravel())
    counts[0] = 0  # Ignore non-white background
    largest_label = counts.argmax()
    cutout_mask = (labels == largest_label)

    # Bounding box of cutout
    y_idx, x_idx = np.where(cutout_mask)
    if len(y_idx) == 0:
        # Fallback to standard 80% box
        px, py, pw, ph = 90, 160, 900, 920
    else:
        px = int(x_idx.min())
        py = int(y_idx.min())
        pw = int(x_idx.max() - px + 1)
        ph = int(y_idx.max() - py + 1)

    # Create Alpha Channel
    alpha = np.ones((target_h, target_w), dtype=np.uint8) * 255
    alpha[cutout_mask] = 0

    rgba = Image.fromarray(arr).convert('RGBA')
    rgba.putalpha(Image.fromarray(alpha, mode='L'))

    # Stamp Homewood Tea Medallion Seal onto bottom border
    medal = create_themed_medallion(defn['style'], diameter=122)
    medal_x = (target_w - medal.width) // 2
    # Place at bottom border center
    medal_y = target_h - medal.height - 20

    # Paste medallion with alpha
    rgba.paste(medal, (medal_x, medal_y), medal)

    # Save final transparent frame PNG
    out_frame_filename = f"frame_{defn['id']}.png"
    out_frame_path = os.path.join(OUTPUT_DIR, out_frame_filename)
    rgba.save(out_frame_path, 'PNG', optimize=True)

    # Create 300x375 preview thumbnail with pleasant tea landscape placeholder
    thumb_canvas = Image.new('RGBA', (target_w, target_h), (20, 26, 22, 255))
    t_draw = ImageDraw.Draw(thumb_canvas)
    # Gradient in cutout
    for i in range(ph):
        ratio = i / float(ph)
        r = int(30 + 45 * ratio)
        g = int(55 + 50 * ratio)
        b = int(45 + 35 * ratio)
        t_draw.line([(px, py + i), (px + pw, py + i)], fill=(r, g, b, 255))

    thumb_canvas.paste(rgba, (0, 0), rgba)
    thumb = thumb_canvas.resize((300, 375), Image.Resampling.LANCZOS)
    out_thumb_filename = f"frame_{defn['id']}_thumb.png"
    out_thumb_path = os.path.join(OUTPUT_DIR, out_thumb_filename)
    thumb.save(out_thumb_path, 'PNG', optimize=True)

    # Compute percentages for web stage
    stage_left = round((px / float(target_w)) * 100, 2)
    stage_top = round((py / float(target_h)) * 100, 2)
    stage_width = round((pw / float(target_w)) * 100, 2)
    stage_height = round((ph / float(target_h)) * 100, 2)

    campaigns_config.append({
        'id': defn['id'],
        'aliases': [defn['raw_filename'].replace('.png', '').lower().replace(' ', '-')],
        'name': defn['name'],
        'themeName': defn['themeName'],
        'category': defn['category'],
        'tag': defn['tag'],
        'badgeIcon': defn['badgeIcon'],
        'clientId': 'homewood-tea',
        'clientName': 'Homewood Tea',
        'campaignTitle': defn['campaignTitle'],
        'campaignSubtitle': defn['campaignSubtitle'],
        'brandTagline': 'Where Nature Feels Like Home',
        'locationText': 'Homewood Tea Factory & Gardens • Ooty, Nilgiris',
        'frameImage': f"new frames/{out_frame_filename}",
        'thumbImage': f"new frames/{out_thumb_filename}",
        'theme': {
            'primaryColor': defn['primaryColor'],
            'goldColor': defn['goldColor'],
            'darkBg': defn['darkBg'],
            'accentColor': defn['accentColor'],
            'textColor': defn['textColor'],
        },
        'defaultHashtags': defn['hashtags'],
        'suggestedShareText': defn['shareText'],
        'ctaText': 'Explore Homewood Tea Blends →',
        'ctaUrl': 'https://homewoodtea.example.com',
        'template': {
            'canvas': {'width': target_w, 'height': target_h},
            'photoArea': {'x': px, 'y': py, 'width': pw, 'height': ph, 'borderRadius': 0},
            'stageAreaPct': {
                'left': stage_left,
                'top': stage_top,
                'width': stage_width,
                'height': stage_height
            },
            'borderWidth': 0,
            'framePadding': 28,
            'styleVariant': 'image-overlay',
        }
    })

    print(f"[OK] Processed {defn['name']}: cutout=[x={px}, y={py}, w={pw}, h={ph}], saved to {out_frame_filename}")

with open('new frames/campaigns_data.json', 'w', encoding='utf-8') as f:
    json.dump(campaigns_config, f, indent=2)

print("=" * 64)
print("Successfully generated all 9 frames and campaigns_data.json!")
print("=" * 64)
