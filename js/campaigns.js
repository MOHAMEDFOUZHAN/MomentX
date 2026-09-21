/**
 * Nilgiris Frame - Campaign Configuration
 */

const DEFAULT_CAMPAIGNS = {
  'nilgiri-tea': {
    id: 'nilgiri-tea',
    clientId: 'sagar-nilgiri',
    clientName: 'Sagar Nilgiri Products',
    campaignTitle: 'A Moment from the Nilgiris',
    campaignSubtitle: 'I VISITED THE NILGIRIS',
    brandTagline: 'Nature Lives in Every Detail',
    locationText: 'Ooty Estate & Botanical Reserve',
    frameImage: 'nilgiris-frame.png',
    theme: {
      primaryColor: '#112e23',
      goldColor: '#d4af37',
      darkBg: '#081c15',
      accentColor: '#2d6a4f',
      textColor: '#fbf8f2',
    },
    defaultHashtags: ['#SagarNilgiri', '#NilgiriMoments', '#NilgiriTea', '#OotyDiaries', '#PureNilgiris'],
    suggestedShareText: 'Preserving a timeless moment in the misty hills of the Nilgiris 🍃✨ #SagarNilgiri #NilgiriMoments',
    ctaText: 'Explore Nilgiri Reserve Blends →',
    ctaUrl: 'https://sagarnilgiri.example.com',
    badgeIcon: '🍃',
    template: {
      canvas: { width: 1080, height: 1350 },
      // Photo area = the white open window in the Nilgiris frame PNG
      // Frame image is 683x855 native; scaled to 1080x1350
      // The white gap starts roughly at 17% from top and ends ~72% from top
      // Horizontally ~9% to 91%
      photoArea: { x: 90, y: 220, width: 900, height: 850, borderRadius: 0 },
      borderWidth: 0,
      framePadding: 28,
      styleVariant: 'image-overlay',
    },
  },
};

const STORAGE_KEY = 'nilgiri_frame_campaigns_v1';

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
  return { ...DEFAULT_CAMPAIGNS };
}

function resolveCurrentCampaign() {
  const campaigns = loadAllCampaigns();
  // Only one campaign — always return it
  return campaigns['nilgiri-tea'];
}
