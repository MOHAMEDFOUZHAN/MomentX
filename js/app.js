/**
 * Maple Connect - Main Application Controller
 * Connects UI Flow, Camera Capture, Touch Photo Adjuster, and Compositor.
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
  const zoomSlider = document.getElementById('zoom-slider');
  const zoomValText = document.getElementById('zoom-val-text');

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

  // Populate Active Campaign Data into DOM
  function updateCampaignTheme(camp) {
    activeCampaign = camp;
    document.title = `${camp.clientName} | QR Branded Photo Experience`;

    // Dynamic brand elements
    const elements = {
      'brand-client-name': camp.clientName,
      'brand-campaign-title': camp.campaignTitle,
      'brand-tagline': camp.brandTagline,
      'brand-subtitle-badge': `✦ ${camp.campaignSubtitle} ✦`,
      'camera-client-label': camp.clientName.toUpperCase(),
      'preview-title': camp.campaignTitle,
      'caption-text-preview': `${camp.suggestedShareText}\n\n${camp.defaultHashtags.join(' ')}`
    };

    for (const [id, val] of Object.entries(elements)) {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    }

    const ctaLink = document.getElementById('cta-brand-link');
    if (ctaLink) {
      ctaLink.href = camp.ctaUrl;
      const ctaText = document.getElementById('cta-brand-text');
      if (ctaText) ctaText.textContent = camp.ctaText;
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

      const adjustedPhoto = {
        ...capturedPhoto,
        scale: adjustScale,
        offsetX: adjustOffsetX * (1080 / 340), // scale relative to adjuster canvas
        offsetY: adjustOffsetY * (1350 / 425),
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
    if (!adjusterStage) return;

    function handleStart(clientX, clientY) {
      isDragging = true;
      dragStartX = clientX;
      dragStartY = clientY;
      initialOffsetX = adjustOffsetX;
      initialOffsetY = adjustOffsetY;
    }

    function handleMove(clientX, clientY) {
      if (!isDragging) return;
      adjustOffsetX = initialOffsetX + (clientX - dragStartX);
      adjustOffsetY = initialOffsetY + (clientY - dragStartY);
      updateAdjusterTransform();
    }

    function handleEnd() {
      isDragging = false;
    }

    // Mouse events
    adjusterStage.addEventListener('mousedown', (e) => {
      e.preventDefault();
      handleStart(e.clientX, e.clientY);
    });
    window.addEventListener('mousemove', (e) => {
      if (isDragging) handleMove(e.clientX, e.clientY);
    });
    window.addEventListener('mouseup', handleEnd);

    // Touch events (mobile)
    adjusterStage.addEventListener('touchstart', (e) => {
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

  // Native Share or Instagram Modal
  async function handleShare() {
    if (!compositeResult) return;

    // Check if Web Share API with files is supported
    if (navigator.share && compositeResult.blob) {
      try {
        const file = new File([compositeResult.blob], `${activeCampaign.id}-moment.jpg`, { type: 'image/jpeg' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          await navigator.share({
            title: activeCampaign.campaignTitle,
            text: `${activeCampaign.suggestedShareText}\n${activeCampaign.defaultHashtags.join(' ')}`,
            files: [file]
          });
          return;
        }
      } catch (e) {
        if (e.name !== 'AbortError') {
          console.log('Native share error, falling back to modal:', e);
        } else {
          return;
        }
      }
    }

    // Fallback: Open Instagram Share Guidance Modal
    if (shareModal) shareModal.classList.add('active');
  }

  // 1-Click Download of High-Res 1080x1350 JPEG
  function downloadPhoto() {
    if (!compositeResult || !compositeResult.dataUrl) return;
    const a = document.createElement('a');
    a.href = compositeResult.dataUrl;
    a.download = `${activeCampaign.id}-photo-1080x1350.jpg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // Display QR Code Modal for Scanning with Mobile
  function openQrModal(campaignId) {
    const campaigns = loadAllCampaigns();
    const camp = campaigns[campaignId] || activeCampaign;
    const qrContainer = document.getElementById('qr-code-display');
    const qrLabel = document.getElementById('qr-modal-title');
    const qrSub = document.getElementById('qr-modal-sub');
    const qrDirectLink = document.getElementById('qr-direct-link');

    if (qrLabel) qrLabel.textContent = camp.clientName;
    if (qrSub) qrSub.textContent = camp.campaignTitle;

    // Determine target URL for mobile phone
    // If running on localhost, suggest using current origin or Wi-Fi IP
    const targetUrl = `${window.location.origin}/q/${camp.id}`;
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
    // Portal Launch Buttons
    document.querySelectorAll('[data-launch-campaign]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const campKey = btn.getAttribute('data-launch-campaign');
        const campaigns = loadAllCampaigns();
        if (campaigns[campKey]) {
          updateCampaignTheme(campaigns[campKey]);
          setStep('landing');
        }
      });
    });

    // Portal QR Code Show Buttons
    document.querySelectorAll('[data-show-qr]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const campKey = btn.getAttribute('data-show-qr');
        openQrModal(campKey);
      });
    });

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
          // If video isn't active, open file input
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

    // Preview: New Photo
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
    updateCampaignTheme(activeCampaign);

    // If URL contains a campaign path (e.g. /q/nilgiri-tea) or ?q=, start at that campaign's landing page
    const path = window.location.pathname.toLowerCase();
    const query = new URLSearchParams(window.location.search);
    if (path.startsWith('/q/') || query.has('q') || query.has('code') || query.has('campaign')) {
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
