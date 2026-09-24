/**
 * Nilgiris Frame & Homewood Tea - Multi-Frame Campaign Configuration
 * 5 Curated Luxury Frames with exact canvas clipping geometry.
 */

const ALL_FRAMES = [
  {
    id: 'nilgiri-valley',
    aliases: ['nilgiri-tea'], // Backwards compatibility with existing URLs/QRs
    name: 'Nilgiris Valley',
    themeName: 'Lush Botanical Valley',
    category: 'Nature & Landscape',
    tag: 'Classic Reserve',
    badgeIcon: '🍃',
    clientId: 'sagar-nilgiri',
    clientName: 'Sagar Nilgiri Products',
    campaignTitle: 'A Moment from the Nilgiris',
    campaignSubtitle: 'Where Nature Feels Like Home',
    brandTagline: 'Nature Lives in Every Detail',
    locationText: 'Ooty Estate & Botanical Reserve',
    frameImage: 'frames/frame_1.png',
    thumbImage: 'frames/frame_1_thumb.png',
    theme: {
      primaryColor: '#0e1713',
      goldColor: '#e2be6c',
      darkBg: '#080d0b',
      accentColor: '#1a3026',
      textColor: '#faf7f0',
    },
    defaultHashtags: ['#SagarNilgiri', '#NilgiriMoments', '#NilgiriTea', '#OotyDiaries', '#PureNilgiris'],
    suggestedShareText: 'Preserving a timeless moment in the misty hills of the Nilgiris 🍃✨ #SagarNilgiri #NilgiriMoments',
    ctaText: 'Explore Nilgiri Reserve Blends →',
    ctaUrl: 'https://sagarnilgiri.example.com',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 85, y: 229, width: 908, height: 844, borderRadius: 0 },
      stageAreaPct: { left: 7.91, top: 16.93, width: 84.08, height: 62.50 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'homewood-heritage',
    aliases: [],
    name: 'Homewood Heritage',
    themeName: 'Artisan Wood & Reserve',
    category: 'Estate Heritage',
    tag: 'Artisan Wood',
    badgeIcon: '🪵',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Good Tea Brighter Days',
    campaignSubtitle: 'From The Nilgiris • In Every Cup',
    brandTagline: 'Where Nature Feels Like Home',
    locationText: 'Homewood Tea Factory & Gardens',
    frameImage: 'frames/frame_2.png',
    thumbImage: 'frames/frame_2_thumb.png',
    theme: {
      primaryColor: '#1a2218',
      goldColor: '#e8c574',
      darkBg: '#0a0e0a',
      accentColor: '#253d26',
      textColor: '#faf7f0',
    },
    defaultHashtags: ['#HomewoodTea', '#TheOriginal', '#GoodTeaBrighterDays', '#NilgiriHeritage', '#MountainTea'],
    suggestedShareText: 'Brewing warmth and timeless memories with Homewood Tea ☕🌿 #HomewoodTea #GoodTeaBrighterDays',
    ctaText: 'Discover Homewood Originals →',
    ctaUrl: 'https://homewoodtea.example.com',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 99, y: 185, width: 889, height: 868, borderRadius: 0 },
      stageAreaPct: { left: 9.18, top: 13.67, width: 82.32, height: 64.26 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'classic-gold',
    aliases: [],
    name: 'Classic Gold Seal',
    themeName: 'Imperial Gold Seal',
    category: 'Luxury Gold',
    tag: 'Gold Standard',
    badgeIcon: '✨',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Homewood Premium Blend',
    campaignSubtitle: 'Good Tea • Brighter Days',
    brandTagline: 'Premium Tea For A Better You',
    locationText: 'Nilgiri Mountain Private Reserve',
    frameImage: 'frames/frame_3.png',
    thumbImage: 'frames/frame_3_thumb.png',
    theme: {
      primaryColor: '#16130b',
      goldColor: '#f1d179',
      darkBg: '#0b0906',
      accentColor: '#453818',
      textColor: '#fffaf0',
    },
    defaultHashtags: ['#HomewoodTea', '#PremiumReserve', '#GoldStandard', '#NilgiriGold', '#TeaCulture'],
    suggestedShareText: 'Sipping the gold standard of mountain tea with Homewood ✨🫖 #HomewoodTea #NilgiriGold',
    ctaText: 'Shop Gold Reserve Blends →',
    ctaUrl: 'https://homewoodtea.example.com/reserve',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 112, y: 208, width: 857, height: 860, borderRadius: 0 },
      stageAreaPct: { left: 10.35, top: 15.43, width: 79.39, height: 63.74 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'homewood-moments',
    aliases: [],
    name: 'Moments Polaroid',
    themeName: 'Scrapbook Adventure',
    category: 'Travel & Scrapbook',
    tag: 'Polaroid Memories',
    badgeIcon: '📷',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Moments Like This',
    campaignSubtitle: 'Explore • Breathe • Sip • Repeat',
    brandTagline: 'Good Tea, Good Mood',
    locationText: 'Nilgiri High Country Trails',
    frameImage: 'frames/frame_4.png',
    thumbImage: 'frames/frame_4_thumb.png',
    theme: {
      primaryColor: '#1c1b17',
      goldColor: '#f5c65d',
      darkBg: '#0c0c0b',
      accentColor: '#3d3725',
      textColor: '#faf7f0',
    },
    defaultHashtags: ['#MomentsLikeThis', '#HomewoodTea', '#TeaTimeAnytime', '#NilgiriTrails', '#TravelMemories'],
    suggestedShareText: 'Explore, breathe, sip, repeat. Treasuring moments in the misty hills 🏔️📷 #MomentsLikeThis #HomewoodTea',
    ctaText: 'Plan Your Mountain Visit →',
    ctaUrl: 'https://homewoodtea.example.com/visit',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 123, y: 194, width: 821, height: 1089, borderRadius: 0 },
      stageAreaPct: { left: 11.43, top: 14.39, width: 75.98, height: 80.66 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
  {
    id: 'homewood-editorial',
    aliases: [],
    name: 'Minimalist Editorial',
    themeName: 'Nordic Editorial',
    category: 'Modern Magazine',
    tag: 'Botanical Living',
    badgeIcon: '⛰️',
    clientId: 'homewood-tea',
    clientName: 'Homewood Tea',
    campaignTitle: 'Nature Brews Happier Days',
    campaignSubtitle: 'Higher Places, Calmer Hearts',
    brandTagline: 'A Little Closer to Nature',
    locationText: 'The Nilgiris High Elevation Estate',
    frameImage: 'frames/frame_5.png',
    thumbImage: 'frames/frame_5_thumb.png',
    theme: {
      primaryColor: '#111b15',
      goldColor: '#d6caa6',
      darkBg: '#090d0b',
      accentColor: '#243a2c',
      textColor: '#f8f7f2',
    },
    defaultHashtags: ['#NilgirisEditorial', '#HomewoodTea', '#CalmerHearts', '#BotanicalLiving', '#QuietLuxury'],
    suggestedShareText: 'Higher places, calmer hearts. Nature brews happier days in the Nilgiris 🍃⛰️ #NilgirisEditorial #HomewoodTea',
    ctaText: 'Read the Mountain Journal →',
    ctaUrl: 'https://homewoodtea.example.com/journal',
    template: {
      canvas: { width: 1080, height: 1350 },
      photoArea: { x: 161, y: 129, width: 761, height: 921, borderRadius: 0 },
      stageAreaPct: { left: 14.94, top: 9.57, width: 70.51, height: 68.23 },
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

const STORAGE_KEY = 'nilgiri_frame_campaigns_v2';
const SELECTED_FRAME_STORAGE_KEY = 'nilgiri_active_frame_id_v2';

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
  // Check URL query params first: ?frame=, ?campaign=, ?q=, or path /q/<id>
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

  // Check localStorage for user's last selected frame
  try {
    const savedId = localStorage.getItem(SELECTED_FRAME_STORAGE_KEY);
    if (savedId) {
      const found = getFrameById(savedId);
      if (found) return found;
    }
  } catch (e) {}

  return ALL_FRAMES[0];
}
