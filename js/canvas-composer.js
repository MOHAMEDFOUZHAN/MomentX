/**
 * Maple Connect - High Resolution (1080x1350) Canvas Compositor Engine
 * Generates print-ready, high-resolution social framing for Instagram & mobile.
 */

// Draw rounded rectangle with cross-browser compatibility
function drawRoundedRect(ctx, x, y, width, height, radius) {
  ctx.beginPath();
  if (typeof ctx.roundRect === 'function') {
    ctx.roundRect(x, y, width, height, radius);
  } else {
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }
}

// Draw realistic botanical tea leaf
function drawLeafShape(ctx, x, y, angleRad, scale, fillColor, strokeColor) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angleRad);
  ctx.scale(scale, scale);

  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.bezierCurveTo(-24, -42, -22, -88, 0, -112);
  ctx.bezierCurveTo(22, -88, 24, -42, 0, 0);
  ctx.fillStyle = fillColor;
  ctx.fill();

  ctx.lineWidth = 2.5;
  ctx.strokeStyle = strokeColor;
  ctx.stroke();

  // Leaf central vein
  ctx.beginPath();
  ctx.moveTo(0, -4);
  ctx.quadraticCurveTo(2, -55, 0, -108);
  ctx.lineWidth = 1.8;
  ctx.strokeStyle = strokeColor;
  ctx.stroke();

  // Sub-veins
  ctx.beginPath();
  ctx.moveTo(0, -35); ctx.lineTo(-12, -50);
  ctx.moveTo(0, -55); ctx.lineTo(12, -70);
  ctx.moveTo(0, -75); ctx.lineTo(-10, -90);
  ctx.lineWidth = 1.2;
  ctx.stroke();

  ctx.restore();
}

// Corner botanical flourish
function drawBotanicalFlourish(ctx, cx, cy, scale, goldColor, accentColor) {
  ctx.save();
  ctx.translate(cx, cy);
  drawLeafShape(ctx, 0, 0, -0.42, scale, accentColor, goldColor);
  drawLeafShape(ctx, 0, 0, 0.42, scale * 0.9, accentColor, goldColor);
  drawLeafShape(ctx, 0, 0, 0.05, scale * 0.72, goldColor, '#fbf8f2');

  // Sparkle star
  ctx.fillStyle = goldColor;
  ctx.beginPath();
  ctx.arc(0, 8, 3, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

// Master Canvas Compositor
async function composeBrandedCanvas(capturedPhoto, campaign) {
  const width = campaign.template.canvas.width || 1080;
  const height = campaign.template.canvas.height || 1350;
  const { x, y, width: pw, height: ph, borderRadius } = campaign.template.photoArea;

  const darkBg = campaign.theme.darkBg || '#081c15';
  const primaryColor = campaign.theme.primaryColor || '#112e23';
  const goldColor = campaign.theme.goldColor || '#d4af37';
  const accentColor = campaign.theme.accentColor || '#2d6a4f';
  const textColor = campaign.theme.textColor || '#fbf8f2';

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Canvas 2D context not available');

  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';

  // Base background fill
  ctx.fillStyle = darkBg;
  ctx.fillRect(0, 0, width, height);

  // LAYER 1: Draw Customer Photo with User Transformations
  if (capturedPhoto && capturedPhoto.dataUrl) {
    const photoImg = new Image();
    await new Promise((resolve, reject) => {
      photoImg.onload = resolve;
      photoImg.onerror = reject;
      photoImg.src = capturedPhoto.dataUrl;
    });

    ctx.save();
    drawRoundedRect(ctx, x, y, pw, ph, borderRadius);
    ctx.clip();

    const imgW = photoImg.naturalWidth || photoImg.width;
    const imgH = photoImg.naturalHeight || photoImg.height;
    const photoAspect = imgW / imgH;
    const targetAspect = pw / ph;

    let dw, dh;
    if (photoAspect > targetAspect) {
      dh = ph;
      dw = ph * photoAspect;
    } else {
      dw = pw;
      dh = pw / photoAspect;
    }

    const scale = capturedPhoto.scale || 1.0;
    dw *= scale;
    dh *= scale;

    const dx = x + (pw - dw) / 2 + (capturedPhoto.offsetX || 0);
    const dy = y + (ph - dh) / 2 + (capturedPhoto.offsetY || 0);

    if (capturedPhoto.mirrored) {
      ctx.save();
      ctx.translate(x + pw, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(photoImg, x + pw - (dx + dw), dy, dw, dh);
      ctx.restore();
    } else {
      ctx.drawImage(photoImg, dx, dy, dw, dh);
    }

    ctx.restore();
  }

  // LAYER 2: Luxury Branded Cutout Overlay (even-odd transparent cutout)
  ctx.save();
  ctx.beginPath();
  ctx.rect(0, 0, width, height);
  drawRoundedRect(ctx, x, y, pw, ph, borderRadius);

  // Gradient fill for outer frame
  const bgGrad = ctx.createLinearGradient(0, 0, width, height);
  bgGrad.addColorStop(0, darkBg);
  bgGrad.addColorStop(0.35, primaryColor);
  bgGrad.addColorStop(0.7, darkBg);
  bgGrad.addColorStop(1, '#040d0a');
  ctx.fillStyle = bgGrad;
  ctx.fill('evenodd');

  // Outer frame perimeter borders
  const pad = campaign.template.framePadding || 28;
  ctx.lineWidth = 2.5;
  ctx.strokeStyle = goldColor;
  drawRoundedRect(ctx, pad, pad, width - pad * 2, height - pad * 2, 24);
  ctx.stroke();

  // Inset hairline border
  ctx.lineWidth = 1.0;
  ctx.strokeStyle = 'rgba(251, 248, 242, 0.25)';
  drawRoundedRect(ctx, pad + 6, pad + 6, width - (pad + 6) * 2, height - (pad + 6) * 2, 20);
  ctx.stroke();

  // Photo Cutout Gold Bevel & Glow
  ctx.lineWidth = 4.5;
  ctx.strokeStyle = goldColor;
  drawRoundedRect(ctx, x, y, pw, ph, borderRadius);
  ctx.stroke();

  // Photo Cutout Inner White Highlight
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
  drawRoundedRect(ctx, x + 4, y + 4, pw - 8, ph - 8, Math.max(0, borderRadius - 4));
  ctx.stroke();

  // Frame corner botanical flourishes
  drawBotanicalFlourish(ctx, x + 24, y + 24, 0.46, goldColor, accentColor);
  drawBotanicalFlourish(ctx, x + pw - 24, y + 24, 0.46, goldColor, accentColor);
  drawBotanicalFlourish(ctx, x + 24, y + ph - 24, 0.46, goldColor, accentColor);
  drawBotanicalFlourish(ctx, x + pw - 24, y + ph - 24, 0.46, goldColor, accentColor);

  // Center crest flourish above photo area
  drawBotanicalFlourish(ctx, width / 2, y - 20, 0.52, goldColor, accentColor);

  ctx.restore();

  // LAYER 3: Dynamic Typography & Branding
  // Top Client Name Badge
  ctx.save();
  ctx.font = "bold 22px 'Cinzel', Georgia, serif";
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const badgeText = `${campaign.badgeIcon || '✦'} ${campaign.clientName.toUpperCase()} ${campaign.badgeIcon || '✦'}`;
  const bMetric = ctx.measureText(badgeText);
  const bw = bMetric.width + 54;
  const bh = 46;
  const badgeY = 72;

  // Badge background pill
  ctx.fillStyle = 'rgba(8, 28, 21, 0.92)';
  drawRoundedRect(ctx, width / 2 - bw / 2, badgeY - bh / 2, bw, bh, 23);
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = goldColor;
  drawRoundedRect(ctx, width / 2 - bw / 2, badgeY - bh / 2, bw, bh, 23);
  ctx.stroke();

  // Badge text
  ctx.fillStyle = goldColor;
  ctx.fillText(badgeText, width / 2, badgeY);
  ctx.restore();

  // Campaign Title
  ctx.save();
  ctx.font = "bold 44px 'Playfair Display', Georgia, serif";
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.shadowColor = 'rgba(0, 0, 0, 0.7)';
  ctx.shadowBlur = 12;
  ctx.shadowOffsetY = 3;

  // Simulated gold metallic gradient
  const titleGrad = ctx.createLinearGradient(0, 130, 0, 175);
  titleGrad.addColorStop(0, '#ffffff');
  titleGrad.addColorStop(0.3, '#f9edd0');
  titleGrad.addColorStop(0.65, goldColor);
  titleGrad.addColorStop(1, '#9b760a');
  ctx.fillStyle = titleGrad;
  ctx.fillText(campaign.campaignTitle, width / 2, 150);
  ctx.restore();

  // Subtitle / Location Header
  ctx.save();
  ctx.font = "300 20px 'Outfit', sans-serif";
  ctx.textAlign = 'center';
  ctx.fillStyle = 'rgba(251, 248, 242, 0.85)';
  ctx.fillText(campaign.locationText || campaign.brandTagline, width / 2, 192);
  ctx.restore();

  // Bottom Subtitle Ribbon (Directly Below Photo)
  ctx.save();
  const subY = y + ph + 46;
  ctx.font = "bold 24px 'Cinzel', Georgia, serif";
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const subText = `✦ ${campaign.campaignSubtitle.toUpperCase()} ✦`;
  const sMetric = ctx.measureText(subText);
  const sw = sMetric.width + 60;
  const sh = 48;

  // Ribbon fill
  ctx.fillStyle = 'rgba(8, 28, 21, 0.9)';
  drawRoundedRect(ctx, width / 2 - sw / 2, subY - sh / 2, sw, sh, 24);
  ctx.fill();
  ctx.lineWidth = 1.8;
  ctx.strokeStyle = goldColor;
  drawRoundedRect(ctx, width / 2 - sw / 2, subY - sh / 2, sw, sh, 24);
  ctx.stroke();

  ctx.fillStyle = goldColor;
  ctx.fillText(subText, width / 2, subY);
  ctx.restore();

  // Bottom Tagline & Brand Verification
  ctx.save();
  const tagY = subY + 54;
  ctx.font = "400 24px 'Playfair Display', Georgia, serif";
  ctx.textAlign = 'center';
  ctx.fillStyle = textColor;
  ctx.fillText(`"${campaign.brandTagline}"`, width / 2, tagY);

  // Live Formatted Date & Certified Stamp
  const dateStr = new Intl.DateTimeFormat('en-US', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(new Date());

  ctx.font = "300 16px 'Outfit', sans-serif";
  ctx.fillStyle = 'rgba(251, 248, 242, 0.65)';
  ctx.fillText(`Recorded at Nilgiri Reserve • ${dateStr} • Authenticity Verified`, width / 2, tagY + 38);
  ctx.restore();

  const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
  const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.95));

  return {
    canvas,
    dataUrl,
    blob,
    width,
    height
  };
}

// Export Transparent Frame (PNG with alpha cutout for external use)
async function exportTransparentFrame(campaign) {
  const width = campaign.template.canvas.width || 1080;
  const height = campaign.template.canvas.height || 1350;
  const { x, y, width: pw, height: ph, borderRadius } = campaign.template.photoArea;

  const darkBg = campaign.theme.darkBg || '#081c15';
  const primaryColor = campaign.theme.primaryColor || '#112e23';
  const goldColor = campaign.theme.goldColor || '#d4af37';
  const accentColor = campaign.theme.accentColor || '#2d6a4f';

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Canvas 2D context not available');

  // Clear transparent canvas
  ctx.clearRect(0, 0, width, height);

  // Even-odd fill leaving photo cutout completely transparent
  ctx.beginPath();
  ctx.rect(0, 0, width, height);
  drawRoundedRect(ctx, x, y, pw, ph, borderRadius);

  const bgGrad = ctx.createLinearGradient(0, 0, width, height);
  bgGrad.addColorStop(0, darkBg);
  bgGrad.addColorStop(0.35, primaryColor);
  bgGrad.addColorStop(0.7, darkBg);
  bgGrad.addColorStop(1, '#040d0a');
  ctx.fillStyle = bgGrad;
  ctx.fill('evenodd');

  // Borders
  const pad = campaign.template.framePadding || 28;
  ctx.lineWidth = 3;
  ctx.strokeStyle = goldColor;
  drawRoundedRect(ctx, pad, pad, width - pad * 2, height - pad * 2, 24);
  ctx.stroke();

  ctx.lineWidth = 4.5;
  ctx.strokeStyle = goldColor;
  drawRoundedRect(ctx, x, y, pw, ph, borderRadius);
  ctx.stroke();

  // Corner botanicals
  drawBotanicalFlourish(ctx, x + 24, y + 24, 0.46, goldColor, accentColor);
  drawBotanicalFlourish(ctx, x + pw - 24, y + 24, 0.46, goldColor, accentColor);
  drawBotanicalFlourish(ctx, x + 24, y + ph - 24, 0.46, goldColor, accentColor);
  drawBotanicalFlourish(ctx, x + pw - 24, y + ph - 24, 0.46, goldColor, accentColor);
  drawBotanicalFlourish(ctx, width / 2, y - 20, 0.52, goldColor, accentColor);

  // Typography
  ctx.font = "bold 22px 'Cinzel', Georgia, serif";
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const badgeText = `${campaign.badgeIcon || '✦'} ${campaign.clientName.toUpperCase()} ${campaign.badgeIcon || '✦'}`;
  const bMetric = ctx.measureText(badgeText);
  const bw = bMetric.width + 54;
  const bh = 46;
  const badgeY = 72;
  ctx.fillStyle = 'rgba(8, 28, 21, 0.92)';
  drawRoundedRect(ctx, width / 2 - bw / 2, badgeY - bh / 2, bw, bh, 23);
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = goldColor;
  drawRoundedRect(ctx, width / 2 - bw / 2, badgeY - bh / 2, bw, bh, 23);
  ctx.stroke();
  ctx.fillStyle = goldColor;
  ctx.fillText(badgeText, width / 2, badgeY);

  ctx.font = "bold 44px 'Playfair Display', Georgia, serif";
  const titleGrad = ctx.createLinearGradient(0, 130, 0, 175);
  titleGrad.addColorStop(0, '#ffffff');
  titleGrad.addColorStop(0.3, '#f9edd0');
  titleGrad.addColorStop(0.65, goldColor);
  titleGrad.addColorStop(1, '#9b760a');
  ctx.fillStyle = titleGrad;
  ctx.fillText(campaign.campaignTitle, width / 2, 150);

  const subY = y + ph + 46;
  ctx.font = "bold 24px 'Cinzel', Georgia, serif";
  const subText = `✦ ${campaign.campaignSubtitle.toUpperCase()} ✦`;
  const sMetric = ctx.measureText(subText);
  const sw = sMetric.width + 60;
  const sh = 48;
  ctx.fillStyle = 'rgba(8, 28, 21, 0.9)';
  drawRoundedRect(ctx, width / 2 - sw / 2, subY - sh / 2, sw, sh, 24);
  ctx.fill();
  ctx.lineWidth = 1.8;
  ctx.strokeStyle = goldColor;
  drawRoundedRect(ctx, width / 2 - sw / 2, subY - sh / 2, sw, sh, 24);
  ctx.stroke();
  ctx.fillStyle = goldColor;
  ctx.fillText(subText, width / 2, subY);

  const dataUrl = canvas.toDataURL('image/png');
  const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
  return { dataUrl, blob, canvas };
}
