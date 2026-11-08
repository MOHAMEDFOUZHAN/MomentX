/**
 * Nilgiris Frame & Homewood Tea - All-New 7 High-End Frames Configuration
 * Precision 1080x1350 canvas overlays with tailored Homewood Tea medallions.
 * 
 * Categories:
 * 1. Feminine / Aesthetic: 🌸 Rose Blossom & Berry
 * 2. Feminine / Aesthetic: 🌅 Golden Hour Blush
 * 3. Adventure & Rugged:   ⛰️ High Country Explorer
 * 4. Adventure & Bold:     ☕ Dark Roast Noir
 * 5. Universal Heritage:   🍃 Nilgiris Valley
 * 6. Luxury & VIP:         ✨ Classic Gold Seal
 * 7. Friends & Fun:        📷 Moments Polaroid
 */

const ALL_FRAMES = [
  {
    id: 'rose-blossom',
    aliases: ['pink', 'girls', 'floral'],
    name: 'Rose Blossom & Berry',
    themeName: 'Soft Blush & Botanical Floral',
    category: 'Feminine / Aesthetic',
    tag: 'Feminine Aesthetic',
    badgeIcon: '🌸',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Rose Blossom & Wild Berry',
    campaignSubtitle: 'Soft blush pink, wild rose petals & delicate gold calligraphy',
    brandTagline: 'Pure Mountain Infusion',
    locationText: 'Homewood Tea Gardens & Botanical Reserve',
    frameImage: 'new frames/frame_rose_blossom.png',
    thumbImage: 'new frames/frame_rose_blossom_thumb.png',
    theme: {
      primaryColor: '#8e3852',
      goldColor: '#dfb85b',
      darkBg: '#2a141d',
      accentColor: '#c27ba0',
      textColor: '#faf7f0',
    },
    defaultHashtags: ['#HomewoodTea', '#RoseBlossom', '#NilgiriMoments', '#AestheticTea', '#Nilgiris'],
    suggestedShareText: 'Sipping wild rose tea in the misty hills of the Nilgiris 🌸✨ #HomewoodTea #RoseBlossom',
    ctaText: 'Explore Floral Blends →',
    ctaUrl: 'https://homewoodtea.example.com',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 90, y: 185, width: 900, height: 875, borderRadius: 0 },
      stageAreaPct: { left: 8.33, top: 13.70, width: 83.33, height: 64.81 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'golden-hour',
    aliases: ['sunset', 'blush-sunset'],
    name: 'Golden Hour Blush',
    themeName: 'Sunset Peach & Radiant Gold',
    category: 'Feminine / Aesthetic',
    tag: 'Golden Hour',
    badgeIcon: '🌅',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Chasing Sunsets & Mountain Brews',
    campaignSubtitle: 'Warm peach & rose-gold gradient with glowing sunset mist',
    brandTagline: 'Higher Elevation • Warmer Memories',
    locationText: 'Homewood Tea Estate • 2,240M Altitude',
    frameImage: 'new frames/frame_golden_hour.png',
    thumbImage: 'new frames/frame_golden_hour_thumb.png',
    theme: {
      primaryColor: '#b85d43',
      goldColor: '#e5a93b',
      darkBg: '#2b160e',
      accentColor: '#f7c2a5',
      textColor: '#fffbf5',
    },
    defaultHashtags: ['#GoldenHour', '#HomewoodTea', '#NilgiriSunset', '#MountainBrews', '#Ooty'],
    suggestedShareText: 'Higher elevation, warmer memories. Chasing sunsets with Homewood Tea 🌅☕ #GoldenHour #HomewoodTea',
    ctaText: 'Discover Sunset Blends →',
    ctaUrl: 'https://homewoodtea.example.com',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 90, y: 185, width: 900, height: 875, borderRadius: 0 },
      stageAreaPct: { left: 8.33, top: 13.70, width: 83.33, height: 64.81 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'high-country',
    aliases: ['explorer', 'trekker', 'mountain'],
    name: 'High Country Explorer',
    themeName: 'Alpine Pine & Explorer Brass',
    category: 'Adventure & Rugged',
    tag: 'Mountain Explorer',
    badgeIcon: '⛰️',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Born to Roam • High Country',
    campaignSubtitle: 'Tactical forest green, topographic contours & rugged compass badge',
    brandTagline: 'Born to Roam • Peak Ridge Trails',
    locationText: 'Elevation: 2,637M • Nilgiris High Country Range',
    frameImage: 'new frames/frame_high_country.png',
    thumbImage: 'new frames/frame_high_country_thumb.png',
    theme: {
      primaryColor: '#0a1d13',
      goldColor: '#c99a3e',
      darkBg: '#09150d',
      accentColor: '#1b2320',
      textColor: '#f5f0e1',
    },
    defaultHashtags: ['#HighCountry', '#HomewoodTea', '#BornToRoam', '#NilgiriTrek', '#MountainExplorer'],
    suggestedShareText: 'Born to roam the high country. Trekking the misty Nilgiris peaks ⛰️🌲 #HighCountry #HomewoodTea',
    ctaText: 'View Alpine Trails & Blends →',
    ctaUrl: 'https://homewoodtea.example.com',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 90, y: 185, width: 900, height: 875, borderRadius: 0 },
      stageAreaPct: { left: 8.33, top: 13.70, width: 83.33, height: 64.81 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'dark-roast',
    aliases: ['noir', 'roast', 'industrial'],
    name: 'Dark Roast Noir',
    themeName: 'Matte Obsidian & Burnished Copper',
    category: 'Adventure & Bold',
    tag: 'Industrial Roast',
    badgeIcon: '☕',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Master Brewer Edition • Reserve Noir',
    campaignSubtitle: 'Sleek matte black & gunmetal bronze with bold factory seal',
    brandTagline: 'Bold • Smoky • Uncompromising',
    locationText: 'Homewood Factory Roast Room • Batch No. 07',
    frameImage: 'new frames/frame_dark_roast.png',
    thumbImage: 'new frames/frame_dark_roast_thumb.png',
    theme: {
      primaryColor: '#141719',
      goldColor: '#cd7f32',
      darkBg: '#0b0d0e',
      accentColor: '#2a2f35',
      textColor: '#faf5eb',
    },
    defaultHashtags: ['#DarkRoastNoir', '#HomewoodTea', '#MasterBrewer', '#BoldFlavors', '#FactoryReserve'],
    suggestedShareText: 'Bold, smoky, and uncompromising. Savoring the Master Brewer Reserve ☕🔥 #DarkRoastNoir #HomewoodTea',
    ctaText: 'Explore Dark Roasts →',
    ctaUrl: 'https://homewoodtea.example.com',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 90, y: 185, width: 900, height: 875, borderRadius: 0 },
      stageAreaPct: { left: 8.33, top: 13.70, width: 83.33, height: 64.81 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'nilgiri-valley',
    aliases: ['nilgiri-tea', 'valley', 'heritage'],
    name: 'Nilgiris Valley',
    themeName: 'British Colonial Tea Green & Gold Leaf',
    category: 'Universal Heritage',
    tag: 'Classic Heritage',
    badgeIcon: '🍃',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'The Nilgiris Valley Heritage',
    campaignSubtitle: 'Lush green tea gardens, mist & traditional imperial valley seal',
    brandTagline: 'Where Nature Feels Like Home',
    locationText: 'From Our Mountain Gardens To Your Cup • Ooty Estate',
    frameImage: 'new frames/frame_nilgiri_valley.png',
    thumbImage: 'new frames/frame_nilgiri_valley_thumb.png',
    theme: {
      primaryColor: '#0d2b1d',
      goldColor: '#d4af37',
      darkBg: '#091c13',
      accentColor: '#16432f',
      textColor: '#faf7f0',
    },
    defaultHashtags: ['#NilgirisValley', '#HomewoodTea', '#WhereNatureFeelsLikeHome', '#PureTea', '#OotyMoments'],
    suggestedShareText: 'Preserving a timeless moment in the misty Nilgiris hills 🍃✨ #NilgirisValley #HomewoodTea',
    ctaText: 'Discover Valley Blends →',
    ctaUrl: 'https://homewoodtea.example.com',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 90, y: 185, width: 900, height: 875, borderRadius: 0 },
      stageAreaPct: { left: 8.33, top: 13.70, width: 83.33, height: 64.81 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'classic-gold',
    aliases: ['gold-seal', 'vip', 'imperial'],
    name: 'Classic Gold Seal',
    themeName: '24K Imperial Gold & Royal Onyx',
    category: 'Luxury & VIP',
    tag: 'Imperial Gold',
    badgeIcon: '✨',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Homewood Imperial Reserve',
    campaignSubtitle: 'Imperial champagne gold borders with royal tea crest & crown finials',
    brandTagline: 'Premium Tea For A Better You',
    locationText: 'Grand Cru Harvest • Certified Estate Reserve',
    frameImage: 'new frames/frame_classic_gold.png',
    thumbImage: 'new frames/frame_classic_gold_thumb.png',
    theme: {
      primaryColor: '#16130b',
      goldColor: '#ffd700',
      darkBg: '#090805',
      accentColor: '#dfb743',
      textColor: '#fffdf5',
    },
    defaultHashtags: ['#ClassicGold', '#HomewoodTea', '#ImperialReserve', '#GoldStandard', '#LuxuryTea'],
    suggestedShareText: 'Sipping the gold standard of mountain tea with Homewood Imperial Reserve ✨🫖 #ClassicGold #HomewoodTea',
    ctaText: 'Shop Gold Reserve →',
    ctaUrl: 'https://homewoodtea.example.com',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 90, y: 185, width: 900, height: 875, borderRadius: 0 },
      stageAreaPct: { left: 8.33, top: 13.70, width: 83.33, height: 64.81 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'moments-polaroid',
    aliases: ['polaroid', 'scrapbook', 'friends'],
    name: 'Moments Polaroid',
    themeName: 'Warm Cardstock, Washi Tape & Stamp',
    category: 'Friends & Fun',
    tag: 'Polaroid Memories',
    badgeIcon: '📷',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Moments Like This Last Forever',
    campaignSubtitle: 'Retro travel scrapbook with gold washi tape, stamps & large photo window',
    brandTagline: 'Explore • Breathe • Sip • Repeat',
    locationText: 'Homewood Tea Factory • Nilgiris Travel Diary',
    frameImage: 'new frames/frame_moments_polaroid.png',
    thumbImage: 'new frames/frame_moments_polaroid_thumb.png',
    theme: {
      primaryColor: '#2d2a26',
      goldColor: '#e2be6c',
      darkBg: '#1a1816',
      accentColor: '#f4f1ea',
      textColor: '#2d2a26',
    },
    defaultHashtags: ['#MomentsLikeThis', '#HomewoodTea', '#PolaroidMemories', '#TravelDiary', '#OotyTrip'],
    suggestedShareText: 'Moments like this last forever... 📷✨ Exploring the Nilgiris with friends #MomentsLikeThis #HomewoodTea',
    ctaText: 'Plan Your Visit →',
    ctaUrl: 'https://homewoodtea.example.com',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 80, y: 125, width: 920, height: 920, borderRadius: 0 },
      stageAreaPct: { left: 7.41, top: 9.26, width: 85.19, height: 68.15 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
];

// Map into key-value map for quick lookup
const DEFAULT_CAMPAIGNS = {};
ALL_FRAMES.forEach(frame => {
  DEFAULT_CAMPAIGNS[frame.id] = frame;
  if (frame.aliases) {
    frame.aliases.forEach(alias => {
      DEFAULT_CAMPAIGNS[alias] = frame;
    });
  }
});

const STORAGE_KEY = 'nilgiri_frame_campaigns_v3';
const SELECTED_FRAME_STORAGE_KEY = 'nilgiri_active_frame_id_v3';

function getAllFrames() {
  return ALL_FRAMES;
}

function getFrameById(frameId) {
  if (!frameId) return ALL_FRAMES[0];
  const all = loadAllCampaigns();
  return all[frameId] || ALL_FRAMES.find(f => f.id === frameId || (f.aliases && f.aliases.includes(frameId))) || ALL_FRAMES[0];
}

function loadAllCampaigns() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      return { ...DEFAULT_CAMPAIGNS, ...parsed };
    }
  } catch (e) {
    console.warn('Could not read saved campaigns from localStorage:', e);
  }
  return { ...DEFAULT_CAMPAIGNS };
}

function saveCampaignConfig(campaignId, updatedConfig) {
  try {
    const all = loadAllCampaigns();
    all[campaignId] = updatedConfig;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
    return true;
  } catch (e) {
    console.error('Failed to save campaign:', e);
    return false;
  }
}

function resetCampaignsToDefault() {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(SELECTED_FRAME_STORAGE_KEY);
  return { ...DEFAULT_CAMPAIGNS };
}

function saveSelectedFrameId(id) {
  try {
    localStorage.setItem(SELECTED_FRAME_STORAGE_KEY, id);
  } catch (e) {}
}

function resolveCurrentCampaign() {
  const urlParams = new URLSearchParams(window.location.search);
  const paramId = urlParams.get('frame') || urlParams.get('campaign') || urlParams.get('q') || urlParams.get('code');
  if (paramId) {
    const found = getFrameById(paramId);
    if (found) return found;
  }

  const path = window.location.pathname.toLowerCase();
  if (path.startsWith('/q/')) {
    const pathId = path.replace('/q/', '').replace(/\/$/, '');
    const found = getFrameById(pathId);
    if (found) return found;
  }

  try {
    const savedId = localStorage.getItem(SELECTED_FRAME_STORAGE_KEY);
    if (savedId) {
      const found = getFrameById(savedId);
      if (found) return found;
    }
  } catch (e) {}

  return ALL_FRAMES[0];
}
