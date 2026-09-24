/**
 * Nilgiris Frame - High Resolution (1080x1350) Canvas Compositor Engine
 * Uses a real PNG template image as the overlay frame over the customer photo.
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

// Load an image from a URL / data URL and return an HTMLImageElement
function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error('Failed to load image: ' + src));
    img.src = src;
  });
}

// Master Canvas Compositor - uses the frame PNG as overlay
async function composeBrandedCanvas(capturedPhoto, campaign) {
  const width  = campaign.template.canvas.width  || 1080;
  const height = campaign.template.canvas.height || 1350;
  const { x, y, width: pw, height: ph } = campaign.template.photoArea;

  const canvas = document.createElement('canvas');
  canvas.width  = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Canvas 2D context not available');

  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';

  // LAYER 0: Dark base background (fills transparent parts of frame PNG)
  ctx.fillStyle = campaign.theme.darkBg || '#081c15';
  ctx.fillRect(0, 0, width, height);

  // LAYER 1: Customer photo clipped to the open area of the frame
  if (capturedPhoto && capturedPhoto.dataUrl) {
    const photoImg = await loadImage(capturedPhoto.dataUrl);

    ctx.save();
    // Clip to the photo window — no rounded radius since the frame PNG handles edges
    ctx.beginPath();
    ctx.rect(x, y, pw, ph);
    ctx.clip();

    const imgW = photoImg.naturalWidth  || photoImg.width;
    const imgH = photoImg.naturalHeight || photoImg.height;
    const photoAspect  = imgW / imgH;
    const targetAspect = pw  / ph;

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

  // LAYER 2: PNG Frame overlay — drawn on top of everything
  if (campaign.frameImage) {
    try {
      const frameImg = await loadImage(campaign.frameImage);
      // Draw the frame PNG to fill the entire canvas so it overlays perfectly
      ctx.drawImage(frameImg, 0, 0, width, height);
    } catch (e) {
      console.warn('Frame image could not be loaded, skipping overlay:', e);
    }
  }

  const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
  const blob    = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.95));

  return { canvas, dataUrl, blob, width, height };
}

// Export Transparent Frame PNG (for external use / admin preview)
async function exportTransparentFrame(campaign) {
  const width  = campaign.template.canvas.width  || 1080;
  const height = campaign.template.canvas.height || 1350;

  const canvas = document.createElement('canvas');
  canvas.width  = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Canvas 2D context not available');

  ctx.clearRect(0, 0, width, height);

  if (campaign.frameImage) {
    try {
      const frameImg = await loadImage(campaign.frameImage);
      ctx.drawImage(frameImg, 0, 0, width, height);
    } catch (e) {
      console.warn('Frame image could not be loaded:', e);
    }
  }

  const dataUrl = canvas.toDataURL('image/png');
  const blob    = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
  return { dataUrl, blob, canvas };
}
