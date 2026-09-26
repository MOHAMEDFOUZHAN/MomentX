/**
 * Maple Connect - Main Application Controller
 * Connects UI Flow, Multi-Frame Selection, Camera Capture, Touch Photo Adjuster, and Compositor.
 */

(function () {
  // Application State
  let activeCampaign = resolveCurrentCampaign();
  let currentStep = 'portal'; // 'portal' | 'landing' | 'camera' | 'adjust' | 'compositing' | 'preview'
  let capturedPhoto = null;
  let compositeResult = null;

  // Adjuster state
  let adjustScale = 1.0;
  let adjustOffsetX = 0;
  let adjustOffsetY = 0;
  let adjustMirrored = false;
  let isDragging = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let initialOffsetX = 0;
  let initialOffsetY = 0;

  // Analytics Tracker (logs events to Python/Node backend)
  function trackEvent(eventType) {
    try {
      fetch('/api/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_type: eventType,
          campaign_id: activeCampaign ? activeCampaign.id : 'nilgiri-valley'
        })
      }).catch(() => {});
    } catch (e) {}
  }

  // DOM Elements
  const screenPortal = document.getElementById('screen-portal');
  const screenLanding = document.getElementById('screen-landing');
  const screenCamera = document.getElementById('screen-camera');
  const screenAdjust = document.getElementById('screen-adjust');
  const screenCompositing = document.getElementById('screen-compositing');
  const screenPreview = document.getElementById('screen-preview');

  const cameraVideo = document.getElementById('camera-video');
  const fileInput = document.getElementById('file-input');
  const cameraErrorBanner = document.getElementById('camera-error-banner');
  const cameraErrorText = document.getElementById('camera-error-text');

  const adjusterImg = document.getElementById('adjuster-img');
  const adjusterStage = document.getElementById('adjuster-stage');
  const adjusterOverlayImg = document.getElementById('adjuster-frame-overlay-img');
  const adjustFrameLabel = document.getElementById('adjust-frame-label');
  const zoomSlider = document.getElementById('zoom-slider');
  const zoomValText = document.getElementById('zoom-val-text');

  const landingTeaserImg = document.getElementById('landing-teaser-frame-img');
  const landingTeaserWindow = document.getElementById('landing-teaser-window');
  const landingFrameCounter = document.getElementById('landing-frame-counter');

  const finalCompositeImg = document.getElementById('final-composite-img');
  const shareModal = document.getElementById('share-modal');
  const qrModal = document.getElementById('qr-modal');
  const flashOverlay = document.getElementById('flash-overlay');

  // Screen Switcher
  function setStep(step) {
    currentStep = step;
    const screens = [screenPortal, screenLanding, screenCamera, screenAdjust, screenCompositing, screenPreview];
    screens.forEach(s => {
      if (s) s.classList.remove('active');
    });

    const target = {
      'portal': screenPortal,
      'landing': screenLanding,
      'camera': screenCamera,
      'adjust': screenAdjust,
      'compositing': screenCompositing,
      'preview': screenPreview
    }[step];

    if (target) {
      target.classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  // Set & Synchronize Active Frame
  function setActiveFrame(frameOrId, options = {}) {
    const frame = typeof frameOrId === 'string' ? getFrameById(frameOrId) : frameOrId;
    if (!frame) return;

    activeCampaign = frame;
    saveSelectedFrameId(frame.id);

    // Update Document & Brand Headers
    document.title = `${frame.name} | Nilgiris Branded Photo Experience`;

    const elements = {
      'brand-client-name': frame.clientName,
      'brand-campaign-title': frame.campaignTitle,
      'brand-tagline': frame.brandTagline,
      'brand-subtitle-badge': `✦ ${frame.campaignSubtitle.toUpperCase()} ✦`,
      'camera-client-label': `${frame.badgeIcon || '✦'} ${frame.name.toUpperCase()}`,
      'preview-title': frame.campaignTitle,
      'caption-text-preview': `${frame.suggestedShareText}\n\n${frame.defaultHashtags.join(' ')}`
    };

    for (const [id, val] of Object.entries(elements)) {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    }

    if (adjustFrameLabel) {
      adjustFrameLabel.textContent = frame.name;
    }

    const ctaLink = document.getElementById('cta-brand-link');
    if (ctaLink) {
      ctaLink.href = frame.ctaUrl;
      const ctaText = document.getElementById('cta-brand-text');
      if (ctaText) ctaText.textContent = frame.ctaText;
    }

    // Update Landing Teaser Frame
    if (landingTeaserImg && frame.frameImage) {
      landingTeaserImg.src = frame.frameImage;
    }

    // Update landing teaser window geometry
    if (landingTeaserWindow && frame.template && frame.template.stageAreaPct) {
      const pct = frame.template.stageAreaPct;
      landingTeaserWindow.style.left = `${pct.left}%`;
      landingTeaserWindow.style.top = `${pct.top}%`;
      landingTeaserWindow.style.width = `${pct.width}%`;
      landingTeaserWindow.style.height = `${pct.height}%`;
    }

    const allFrames = getAllFrames();
    const frameIndex = allFrames.findIndex(f => f.id === frame.id);
    if (landingFrameCounter && frameIndex >= 0) {
      landingFrameCounter.textContent = `Frame ${frameIndex + 1} of ${allFrames.length}`;
    }

    // Update Adjuster Stage & Overlay
    if (adjusterOverlayImg && frame.frameImage) {
      adjusterOverlayImg.src = frame.frameImage;
    }
    if (adjusterStage && frame.template && frame.template.stageAreaPct) {
      const pct = frame.template.stageAreaPct;
      adjusterStage.style.left = `${pct.left}%`;
      adjusterStage.style.top = `${pct.top}%`;
      adjusterStage.style.width = `${pct.width}%`;
      adjusterStage.style.height = `${pct.height}%`;
    }

    // Update Active CSS Classes across all selectors
    document.querySelectorAll('[data-frame-id]').forEach(el => {
      const fid = el.getAttribute('data-frame-id');
      const isMatch = (fid === frame.id) || (frame.aliases && frame.aliases.includes(fid));
      el.classList.toggle('active', isMatch);
    });

    // If switching from preview screen, trigger instant high-resolution re-compositing
    if (options.recomputePreview && currentStep === 'preview' && capturedPhoto) {
      runCompositor();
    }
  }

  // Populate Dynamic Multi-Frame Selectors in UI
  function renderAllFrameSelectors() {
    const frames = getAllFrames();

    // 1. Portal Frames Grid
    const portalGrid = document.getElementById('portal-frames-grid');
    if (portalGrid) {
      portalGrid.innerHTML = frames.map(f => `
        <div class="frame-card ${f.id === activeCampaign.id ? 'active' : ''}" data-frame-id="${f.id}">
          <div class="frame-card-badge">${f.badgeIcon || '✦'} ${f.tag || f.category}</div>
          <div class="frame-card-img-wrap">
            <img src="${f.thumbImage || f.frameImage}" alt="${f.name}" loading="lazy" />
          </div>
          <div class="frame-card-info">
            <h4 class="frame-card-title">${f.name}</h4>
            <p class="frame-card-sub">${f.campaignSubtitle}</p>
          </div>
          <div class="frame-card-actions">
            <button class="btn-gold" data-launch-frame="${f.id}" style="flex: 1; font-size: 0.85rem; padding: 0.75rem 0.9rem;">
              <span>📸 Launch Frame</span>
            </button>
            <button class="btn-secondary" data-show-qr="${f.id}" style="padding: 0.75rem 0.9rem;" title="Scan on Mobile">
              <span>📱 QR</span>
            </button>
          </div>
        </div>
      `).join('');
    }

    // 2. Landing Frame Carousel
    const landingCarousel = document.getElementById('landing-frame-carousel');
    if (landingCarousel) {
      landingCarousel.innerHTML = frames.map(f => `
        <div class="landing-frame-item ${f.id === activeCampaign.id ? 'active' : ''}" data-frame-id="${f.id}" data-select-frame="${f.id}">
          <div class="landing-frame-thumb">
            <img src="${f.thumbImage || f.frameImage}" alt="${f.name}" />
          </div>
          <div class="landing-frame-name">${f.name}</div>
          <div class="landing-frame-tag">${f.badgeIcon || '✦'} ${f.tag || 'Luxury'}</div>
        </div>
      `).join('');
    }

    // 3. Adjuster Frame Switcher Bar
    const adjustBar = document.getElementById('adjust-frame-bar');
    if (adjustBar) {
      adjustBar.innerHTML = frames.map(f => `
        <div class="adjust-frame-pill ${f.id === activeCampaign.id ? 'active' : ''}" data-frame-id="${f.id}" data-select-frame="${f.id}">
          <div class="adjust-frame-pill-thumb">
            <img src="${f.thumbImage || f.frameImage}" alt="${f.name}" />
          </div>
          <span>${f.badgeIcon || '✦'} ${f.name}</span>
        </div>
      `).join('');
    }

    // 4. Preview Screen Quick Re-frame Strip
    const previewStrip = document.getElementById('preview-frame-strip');
    if (previewStrip) {
      previewStrip.innerHTML = frames.map(f => `
        <div class="preview-frame-chip ${f.id === activeCampaign.id ? 'active' : ''}" data-frame-id="${f.id}" data-preview-switch-frame="${f.id}">
          <div class="preview-frame-chip-thumb">
            <img src="${f.thumbImage || f.frameImage}" alt="${f.name}" />
          </div>
          <span>${f.badgeIcon || '✦'} ${f.name}</span>
        </div>
      `).join('');
    }
  }

  // Visual Flash & Haptic Feedback
  function triggerShutterFlash() {
    if (flashOverlay) {
      flashOverlay.classList.add('flashing');
      setTimeout(() => flashOverlay.classList.remove('flashing'), 180);
    }
    if (typeof navigator !== 'undefined' && navigator.vibrate) {
      try { navigator.vibrate(40); } catch (e) {}
    }
  }

  // Camera Management
  async function launchCamera() {
    trackEvent('camera_open');
    setStep('camera');
    if (cameraErrorBanner) cameraErrorBanner.style.display = 'none';

    try {
      await cameraController.startStream(cameraVideo);
    } catch (err) {
      console.warn('Camera stream warning:', err.message);
      if (cameraErrorBanner && cameraErrorText) {
        cameraErrorText.textContent = err.message;
        cameraErrorBanner.style.display = 'flex';
      }
    }
  }

  // Proceed to Adjuster with captured photo
  function setupAdjuster(photo) {
    trackEvent('photo_snap');
    cameraController.stopStream();
    capturedPhoto = photo;
    adjustScale = 1.0;
    adjustOffsetX = 0;
    adjustOffsetY = 0;
    adjustMirrored = photo.mirrored || false;

    if (zoomSlider) zoomSlider.value = '1.0';
    if (zoomValText) zoomValText.textContent = '1.0x';

    adjusterImg.src = photo.dataUrl;
    updateAdjusterTransform();
    setStep('adjust');
  }

  // Update Photo Position & Zoom on the adjust screen
  function updateAdjusterTransform() {
    if (!adjusterImg) return;
    const mirrorScale = adjustMirrored ? -1 : 1;
    adjusterImg.style.transform = `translate(${adjustOffsetX}px, ${adjustOffsetY}px) scale(${adjustScale * mirrorScale}, ${adjustScale})`;
  }

  // Generate Final 1080x1350 High-Res Composite
  async function runCompositor() {
    setStep('compositing');
    try {
      // Add a slight micro-delay for smooth cinematic feedback
      await new Promise(r => setTimeout(r, 600));

      // Calculate exact scaling from adjuster stage to canvas photo area
      const stageRect = adjusterStage ? adjusterStage.getBoundingClientRect() : { width: 262, height: 242 };
      const stageW = stageRect.width || 262;
      const stageH = stageRect.height || 242;

      const photoArea = (activeCampaign.template && activeCampaign.template.photoArea) || { width: 908, height: 844 };
      const scaleFactorX = photoArea.width / stageW;
      const scaleFactorY = photoArea.height / stageH;

      const adjustedPhoto = {
        ...capturedPhoto,
        scale: adjustScale,
        offsetX: adjustOffsetX * scaleFactorX,
        offsetY: adjustOffsetY * scaleFactorY,
        mirrored: adjustMirrored
      };

      compositeResult = await composeBrandedCanvas(adjustedPhoto, activeCampaign);
      finalCompositeImg.src = compositeResult.dataUrl;
      setStep('preview');
    } catch (err) {
      console.error('Compositing error:', err);
      alert('Failed to compose photo: ' + err.message);
      setStep('adjust');
    }
  }

  // Setup Touch and Mouse Dragging for Photo Adjuster
  function setupDraggableAdjuster() {
    const dragTarget = document.getElementById('adjuster-frame-wrapper') || adjusterStage;
    if (!dragTarget) return;

    function handleStart(clientX, clientY) {
      isDragging = true;
      dragStartX = clientX;
      dragStartY = clientY;
      initialOffsetX = adjustOffsetX;
      initialOffsetY = adjustOffsetY;
      dragTarget.style.cursor = 'grabbing';
    }

    function handleMove(clientX, clientY) {
      if (!isDragging) return;
      adjustOffsetX = initialOffsetX + (clientX - dragStartX);
      adjustOffsetY = initialOffsetY + (clientY - dragStartY);
      updateAdjusterTransform();
    }

    function handleEnd() {
      isDragging = false;
      dragTarget.style.cursor = 'grab';
    }

    // Mouse events
    dragTarget.addEventListener('mousedown', (e) => {
      e.preventDefault();
      handleStart(e.clientX, e.clientY);
    });

    window.addEventListener('mousemove', (e) => {
      if (isDragging) handleMove(e.clientX, e.clientY);
    });
    window.addEventListener('mouseup', handleEnd);

    // Touch events (mobile)
    dragTarget.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        handleStart(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (isDragging && e.touches.length === 1) {
        handleMove(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });

    window.addEventListener('touchend', handleEnd);
  }

  // Flash status banner inside share modal
  function showShareStatus(text, duration = 3000) {
    const pill = document.getElementById('share-status-pill');
    if (!pill) return;
    pill.textContent = text;
    pill.style.display = 'block';
    setTimeout(() => {
      pill.style.display = 'none';
    }, duration);
  }

  // Trigger Native System Share Sheet (iOS / Android sheet with all installed apps)
  async function triggerNativeShare() {
    if (!compositeResult || !navigator.share) return false;

    const shareTitle = activeCampaign.campaignTitle || 'Nilgiris Frame';
    const shareText = `${activeCampaign.suggestedShareText}\n\n${(activeCampaign.defaultHashtags || []).join(' ')}`;

    // 1. Try sharing with the high-res 1080x1350 JPEG file
    if (compositeResult.blob) {
      try {
        const file = new File([compositeResult.blob], `${activeCampaign.id}-photo-1080x1350.jpg`, { type: 'image/jpeg' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({
            title: shareTitle,
            text: shareText,
            files: [file]
          });
          return true;
        }
      } catch (err) {
        if (err.name === 'AbortError') return true; // User tapped cancel
        console.warn('Native file share error:', err);
      }
    }

    // 2. Fallback: try sharing text & link
    try {
      await navigator.share({
        title: shareTitle,
        text: shareText,
        url: window.location.href
      });
      return true;
    } catch (err) {
      if (err.name === 'AbortError') return true;
      console.warn('Native text share error:', err);
    }

    return false;
  }

  // Open Share Hub Modal
  function openShareModal() {
    if (shareModal) {
      shareModal.classList.add('active');
    }
  }

  // Native Share Handler (attempts OS sheet or opens App Share Hub)
  async function handleShare() {
    if (!compositeResult) return;
    trackEvent('photo_share');

    // Attempt Native System Share Menu first (works when browser allows it)
    if (navigator.share) {
      const shared = await triggerNativeShare();
      if (shared) return;
    }

    // Otherwise, open the interactive Mobile App Share Hub Modal
    openShareModal();
  }

  // 1-Click Download of High-Res 1080x1350 JPEG
  function downloadPhoto(options = {}) {
    if (!compositeResult || !compositeResult.dataUrl) return;
    if (!options.silent) {
      trackEvent('photo_download');
    }
    const a = document.createElement('a');
    a.href = compositeResult.dataUrl;
    a.download = `${activeCampaign.id}-photo-1080x1350.jpg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // Mobile Origin Resolver (replaces localhost with actual LAN Wi-Fi IP for phones)
  let cachedMobileOrigin = null;

  async function resolveMobileOrigin() {
    if (cachedMobileOrigin) return cachedMobileOrigin;
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (!isLocal) {
      cachedMobileOrigin = window.location.origin;
      return cachedMobileOrigin;
    }
    try {
      const res = await fetch('/api/network-info');
      const data = await res.json();
      if (data && data.mobile_url) {
        cachedMobileOrigin = data.mobile_url;
        return cachedMobileOrigin;
      }
    } catch (e) {}
    // Fallback to detected Wi-Fi IP
    cachedMobileOrigin = `http://10.43.118.113:${window.location.port || '3001'}`;
    return cachedMobileOrigin;
  }

  // Display QR Code Modal for Scanning with Mobile
  async function openQrModal(frameId) {
    const origin = await resolveMobileOrigin();
    const frame = (frameId && frameId !== 'app') ? getFrameById(frameId) : null;
    const qrContainer = document.getElementById('qr-code-display');
    const qrLabel = document.getElementById('qr-modal-title');
    const qrSub = document.getElementById('qr-modal-sub');
    const qrDirectLink = document.getElementById('qr-direct-link');

    let targetUrl;
    if (frame) {
      if (qrLabel) qrLabel.textContent = `${frame.badgeIcon || '✦'} ${frame.name}`;
      if (qrSub) qrSub.textContent = `Scan with your phone to launch the ${frame.name} camera experience!`;
      targetUrl = `${origin}/q/${frame.id}`;
    } else {
      if (qrLabel) qrLabel.textContent = `📱 Open Nilgiris Frame Experience`;
      if (qrSub) qrSub.textContent = `Scan with your smartphone camera to operate the full touch photo app on your phone!`;
      targetUrl = `${origin}/`;
    }

    if (qrDirectLink) {
      qrDirectLink.href = targetUrl;
      qrDirectLink.textContent = targetUrl;
    }

    if (qrContainer && typeof QRCode !== 'undefined') {
      qrContainer.innerHTML = '';
      new QRCode(qrContainer, {
        text: targetUrl,
        width: 220,
        height: 220,
        colorDark: '#081c15',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
      });
    }

    if (qrModal) qrModal.classList.add('active');
  }

  // Wire Event Listeners
  function initEvents() {
    // Overall App QR Triggers
    const appQrBtns = ['btn-open-mobile-qr', 'btn-banner-scan-qr', 'btn-landing-phone-qr'];
    appQrBtns.forEach(id => {
      const btn = document.getElementById(id);
      if (btn) {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          if (id === 'btn-landing-phone-qr' && activeCampaign) {
            openQrModal(activeCampaign.id);
          } else {
            openQrModal(null);
          }
        });
      }
    });

    // Portal Launch Buttons
    document.addEventListener('click', (e) => {
      const launchBtn = e.target.closest('[data-launch-frame]');
      if (launchBtn) {
        e.preventDefault();
        const fId = launchBtn.getAttribute('data-launch-frame');
        setActiveFrame(fId);
        setStep('landing');
        return;
      }

      const qrBtn = e.target.closest('[data-show-qr]');
      if (qrBtn) {
        e.preventDefault();
        const fId = qrBtn.getAttribute('data-show-qr');
        openQrModal(fId);
        return;
      }

      // Frame selection on Landing or Adjuster
      const selectFrameItem = e.target.closest('[data-select-frame]');
      if (selectFrameItem) {
        e.preventDefault();
        const fId = selectFrameItem.getAttribute('data-select-frame');
        setActiveFrame(fId);
        return;
      }

      // Frame quick switch on Preview Screen
      const previewSwitchItem = e.target.closest('[data-preview-switch-frame]');
      if (previewSwitchItem) {
        e.preventDefault();
        const fId = previewSwitchItem.getAttribute('data-preview-switch-frame');
        setActiveFrame(fId, { recomputePreview: true });
        return;
      }
    });

    // Return to Portal Button
    const backToPortalBtn = document.getElementById('btn-back-to-portal');
    if (backToPortalBtn) {
      backToPortalBtn.addEventListener('click', () => {
        setStep('portal');
      });
    }

    // Landing Screen: Start Experience
    const startBtn = document.getElementById('btn-start-camera');
    if (startBtn) {
      startBtn.addEventListener('click', launchCamera);
    }

    // Viewfinder: Close / Back to Landing
    const closeCamBtn = document.getElementById('btn-close-camera');
    if (closeCamBtn) {
      closeCamBtn.addEventListener('click', () => {
        cameraController.stopStream();
        setStep('landing');
      });
    }

    // Viewfinder: Flip Front/Back Camera
    const flipCamBtn = document.getElementById('btn-flip-camera');
    if (flipCamBtn) {
      flipCamBtn.addEventListener('click', async () => {
        try {
          await cameraController.toggleFacingMode();
        } catch (e) {
          console.warn('Could not flip camera:', e);
        }
      });
    }

    // Viewfinder: Shutter Button Click
    const shutterBtn = document.getElementById('btn-shutter');
    if (shutterBtn) {
      shutterBtn.addEventListener('click', () => {
        triggerShutterFlash();
        const frame = cameraController.captureFrame();
        if (frame) {
          setupAdjuster(frame);
        } else {
          fileInput?.click();
        }
      });
    }

    // File Upload input & trigger buttons
    document.querySelectorAll('[data-action="upload-photo"]').forEach(btn => {
      btn.addEventListener('click', () => fileInput?.click());
    });

    if (fileInput) {
      fileInput.addEventListener('change', async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        try {
          const photo = await cameraController.loadFromFile(file);
          setupAdjuster(photo);
        } catch (err) {
          alert('Error loading photo: ' + err.message);
        }
        fileInput.value = '';
      });
    }

    // Demo Visitor Portrait Button
    document.querySelectorAll('[data-action="sample-portrait"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const sample = cameraController.createSamplePortrait();
        if (sample) setupAdjuster(sample);
      });
    });

    // Adjuster: Zoom Slider
    if (zoomSlider) {
      zoomSlider.addEventListener('input', (e) => {
        adjustScale = parseFloat(e.target.value);
        if (zoomValText) zoomValText.textContent = `${adjustScale.toFixed(1)}x`;
        updateAdjusterTransform();
      });
    }

    // Adjuster: Mirror Flip
    const mirrorBtn = document.getElementById('btn-mirror-photo');
    if (mirrorBtn) {
      mirrorBtn.addEventListener('click', () => {
        adjustMirrored = !adjustMirrored;
        updateAdjusterTransform();
      });
    }

    // Adjuster: Retake Photo
    const retakeBtn = document.getElementById('btn-retake-photo');
    if (retakeBtn) {
      retakeBtn.addEventListener('click', launchCamera);
    }

    // Adjuster: Confirm & Frame
    const confirmBtn = document.getElementById('btn-confirm-adjust');
    if (confirmBtn) {
      confirmBtn.addEventListener('click', runCompositor);
    }

    // Preview: Download HD
    const downloadBtn = document.getElementById('btn-download-hd');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', downloadPhoto);
    }

    // Preview: Share Button
    const shareBtn = document.getElementById('btn-share');
    if (shareBtn) {
      shareBtn.addEventListener('click', handleShare);
    }

    // Preview: Take Another Photo
    const newPhotoBtn = document.getElementById('btn-take-another');
    if (newPhotoBtn) {
      newPhotoBtn.addEventListener('click', launchCamera);
    }

    // Share Modal: Copy Caption
    const copyCaptionBtn = document.getElementById('btn-copy-caption');
    if (copyCaptionBtn) {
      copyCaptionBtn.addEventListener('click', () => {
        const caption = `${activeCampaign.suggestedShareText}\n\n${activeCampaign.defaultHashtags.join(' ')}`;
        navigator.clipboard.writeText(caption).then(() => {
          copyCaptionBtn.textContent = '✓ Caption Copied!';
          setTimeout(() => { copyCaptionBtn.textContent = 'Copy Instagram Caption'; }, 2000);
        });
      });
    }

    // QR Modal: Copy Link
    const copyQrLinkBtn = document.getElementById('btn-copy-qr-link');
    if (copyQrLinkBtn) {
      copyQrLinkBtn.addEventListener('click', () => {
        const linkEl = document.getElementById('qr-direct-link');
        const url = linkEl ? linkEl.href : window.location.href;
        navigator.clipboard.writeText(url).then(() => {
          copyQrLinkBtn.innerHTML = '<span>✓ Link Copied to Clipboard!</span>';
          setTimeout(() => { copyQrLinkBtn.innerHTML = '<span>📋 Copy Mobile Link</span>'; }, 2000);
        });
      });
    }

    // Share Modal: System Share Sheet Button
    const sysShareBtn = document.getElementById('btn-trigger-system-share');
    if (sysShareBtn) {
      sysShareBtn.addEventListener('click', async () => {
        if (navigator.share) {
          const success = await triggerNativeShare();
          if (success) return;
        }
        showShareStatus('✦ Tap WhatsApp or Instagram below to share directly!');
      });
    }

    // Share Modal: Save Photo to Device
    const modalDlBtn = document.getElementById('btn-modal-download-hd');
    if (modalDlBtn) {
      modalDlBtn.addEventListener('click', () => {
        downloadPhoto();
        showShareStatus('✓ 1080×1350 Photo saved to your device gallery!');
      });
    }

    // Share App 1: WhatsApp
    const waBtn = document.getElementById('share-btn-whatsapp');
    if (waBtn) {
      waBtn.addEventListener('click', (e) => {
        e.preventDefault();
        downloadPhoto({ silent: true });
        const caption = `${activeCampaign.suggestedShareText}\n\n${(activeCampaign.defaultHashtags || []).join(' ')}`;
        navigator.clipboard?.writeText(caption);
        showShareStatus('✓ Photo saved! Opening WhatsApp...');
        const waUrl = `whatsapp://send?text=${encodeURIComponent(caption)}`;
        window.location.href = waUrl;
        setTimeout(() => {
          window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(caption)}`, '_blank');
        }, 1200);
      });
    }

    // Share App 2: Instagram
    const igBtn = document.getElementById('share-btn-instagram');
    if (igBtn) {
      igBtn.addEventListener('click', (e) => {
        e.preventDefault();
        downloadPhoto({ silent: true });
        const caption = `${activeCampaign.suggestedShareText}\n\n${(activeCampaign.defaultHashtags || []).join(' ')}`;
        navigator.clipboard?.writeText(caption);
        showShareStatus('✓ Caption copied & Photo saved! Opening Instagram...');
        window.location.href = 'instagram://app';
        setTimeout(() => {
          window.open('https://www.instagram.com', '_blank');
        }, 1200);
      });
    }

    // Share App 3: Telegram
    const tgBtn = document.getElementById('share-btn-telegram');
    if (tgBtn) {
      tgBtn.addEventListener('click', (e) => {
        e.preventDefault();
        downloadPhoto({ silent: true });
        const caption = `${activeCampaign.suggestedShareText}\n\n${(activeCampaign.defaultHashtags || []).join(' ')}`;
        navigator.clipboard?.writeText(caption);
        showShareStatus('✓ Photo saved! Opening Telegram...');
        window.location.href = `tg://msg?text=${encodeURIComponent(caption)}`;
        setTimeout(() => {
          window.open(`https://t.me/share/url?text=${encodeURIComponent(caption)}`, '_blank');
        }, 1200);
      });
    }

    // Share App 4: Messages / SMS
    const smsBtn = document.getElementById('share-btn-sms');
    if (smsBtn) {
      smsBtn.addEventListener('click', (e) => {
        e.preventDefault();
        downloadPhoto({ silent: true });
        const text = `${activeCampaign.suggestedShareText} ${(activeCampaign.defaultHashtags || []).join(' ')}`;
        showShareStatus('✓ Photo saved! Opening Messages...');
        window.location.href = `sms:?&body=${encodeURIComponent(text)}`;
      });
    }

    // Share App 5: Twitter / X
    const twBtn = document.getElementById('share-btn-twitter');
    if (twBtn) {
      twBtn.addEventListener('click', (e) => {
        e.preventDefault();
        downloadPhoto({ silent: true });
        const text = `${activeCampaign.suggestedShareText}\n\n${(activeCampaign.defaultHashtags || []).join(' ')}`;
        showShareStatus('✓ Opening X / Twitter...');
        window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank');
      });
    }

    // Share App 6: Facebook
    const fbBtn = document.getElementById('share-btn-facebook');
    if (fbBtn) {
      fbBtn.addEventListener('click', (e) => {
        e.preventDefault();
        downloadPhoto({ silent: true });
        showShareStatus('✓ Opening Facebook...');
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.origin)}`, '_blank');
      });
    }

    // Modals Close
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
      btn.addEventListener('click', () => {
        if (shareModal) shareModal.classList.remove('active');
        if (qrModal) qrModal.classList.remove('active');
      });
    });

    // Initialize Draggable Adjuster
    setupDraggableAdjuster();
  }

  // Initialize Application
  function init() {
    trackEvent('page_view');

    // Populate frame selectors
    renderAllFrameSelectors();

    // Set active frame state & theme
    setActiveFrame(activeCampaign);

    // If URL contains a campaign/frame path (e.g. /q/classic-gold) or ?frame=, start at that frame's landing page
    const path = window.location.pathname.toLowerCase();
    const query = new URLSearchParams(window.location.search);
    if (path.startsWith('/q/') || query.has('frame') || query.has('q') || query.has('code') || query.has('campaign')) {
      setStep('landing');
    } else {
      setStep('portal');
    }

    initEvents();
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
