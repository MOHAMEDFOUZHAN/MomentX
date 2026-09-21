/**
 * Maple Connect - Admin & Template Studio Controller
 */

(function () {
  let campaigns = loadAllCampaigns();
  let selectedCampaignKey = 'nilgiri-tea';
  let activeTab = 'template';
  let currentPreviewCanvas = null;

  // DOM Elements
  const selectCampaign = document.getElementById('select-campaign');
  const previewImg = document.getElementById('admin-preview-img');
  const previewLoading = document.getElementById('admin-preview-loading');

  // Sliders
  const inputX = document.getElementById('input-x');
  const inputY = document.getElementById('input-y');
  const inputW = document.getElementById('input-w');
  const inputH = document.getElementById('input-h');
  const inputR = document.getElementById('input-r');

  const valX = document.getElementById('val-x');
  const valY = document.getElementById('val-y');
  const valW = document.getElementById('val-w');
  const valH = document.getElementById('val-h');
  const valR = document.getElementById('val-r');

  // QR Elements
  const qrContainer = document.getElementById('admin-qr-container');
  const inputQrUrl = document.getElementById('admin-qr-url');
  const btnDownloadQr = document.getElementById('btn-download-qr');

  // JSON Elements
  const jsonTextarea = document.getElementById('json-campaign-text');

  // Switch Tab
  function setTab(tab) {
    activeTab = tab;
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === tab);
    });

    document.querySelectorAll('.admin-tab-content').forEach(content => {
      content.style.display = content.getAttribute('data-tab-content') === tab ? 'block' : 'none';
    });

    if (tab === 'qrcodes') updateAdminQr();
    if (tab === 'json') updateJsonViewer();
  }

  // Populate Sliders from Active Campaign
  function syncSlidersFromCampaign() {
    const camp = campaigns[selectedCampaignKey];
    const pa = camp.template.photoArea;

    inputX.value = pa.x; valX.textContent = `${pa.x}px`;
    inputY.value = pa.y; valY.textContent = `${pa.y}px`;
    inputW.value = pa.width; valW.textContent = `${pa.width}px`;
    inputH.value = pa.height; valH.textContent = `${pa.height}px`;
    inputR.value = pa.borderRadius; valR.textContent = `${pa.borderRadius}px`;

    // Also update QR url field
    if (inputQrUrl) {
      inputQrUrl.value = `${window.location.origin}/q/${camp.id}`;
    }
  }

  // Render Template Live Preview
  async function renderLivePreview() {
    const camp = campaigns[selectedCampaignKey];
    previewLoading.style.display = 'flex';

    // Create a mock demo portrait for preview
    const sampleCanvas = document.createElement('canvas');
    sampleCanvas.width = 1080;
    sampleCanvas.height = 1350;
    const sctx = sampleCanvas.getContext('2d');

    // Gradient backdrop
    const grad = sctx.createLinearGradient(0, 0, 1080, 1350);
    grad.addColorStop(0, '#2d4a53');
    grad.addColorStop(0.5, '#4f776a');
    grad.addColorStop(1, '#1b3228');
    sctx.fillStyle = grad;
    sctx.fillRect(0, 0, 1080, 1350);

    // Visitor silhouette
    sctx.fillStyle = '#fceade';
    sctx.beginPath();
    sctx.ellipse(540, 580, 160, 200, 0, 0, Math.PI * 2);
    sctx.fill();

    sctx.fillStyle = '#261b17';
    sctx.beginPath();
    sctx.arc(540, 530, 180, Math.PI, 0);
    sctx.bezierCurveTo(740, 580, 720, 730, 680, 760);
    sctx.lineTo(400, 760);
    sctx.bezierCurveTo(360, 730, 340, 580, 360, 530);
    sctx.fill();

    // Visitor Label
    sctx.fillStyle = 'rgba(8, 28, 21, 0.75)';
    sctx.font = 'bold 34px sans-serif';
    sctx.textAlign = 'center';
    sctx.fillText('Sample Visitor Portrait', 540, 600);

    const sampleDataUrl = sampleCanvas.toDataURL('image/jpeg');
    const captured = {
      dataUrl: sampleDataUrl,
      width: 1080,
      height: 1350,
      scale: 1.0,
      offsetX: 0,
      offsetY: 0,
      mirrored: false
    };

    try {
      const result = await composeBrandedCanvas(captured, camp);
      currentPreviewCanvas = result.canvas;
      previewImg.src = result.dataUrl;
    } catch (e) {
      console.error('Preview error:', e);
    } finally {
      previewLoading.style.display = 'none';
    }
  }

  // Update Template Photo Area from Sliders
  function handleSliderChange() {
    const camp = campaigns[selectedCampaignKey];
    camp.template.photoArea = {
      x: parseInt(inputX.value, 10),
      y: parseInt(inputY.value, 10),
      width: parseInt(inputW.value, 10),
      height: parseInt(inputH.value, 10),
      borderRadius: parseInt(inputR.value, 10)
    };

    valX.textContent = `${camp.template.photoArea.x}px`;
    valY.textContent = `${camp.template.photoArea.y}px`;
    valW.textContent = `${camp.template.photoArea.width}px`;
    valH.textContent = `${camp.template.photoArea.height}px`;
    valR.textContent = `${camp.template.photoArea.borderRadius}px`;

    renderLivePreview();
  }

  // Update Admin QR Code
  function updateAdminQr() {
    if (!qrContainer || typeof QRCode === 'undefined') return;
    const url = inputQrUrl.value || `${window.location.origin}/q/${selectedCampaignKey}`;

    qrContainer.innerHTML = '';
    new QRCode(qrContainer, {
      text: url,
      width: 256,
      height: 256,
      colorDark: '#081c15',
      colorLight: '#ffffff',
      correctLevel: QRCode.CorrectLevel.H
    });
  }

  // Download Generated QR Code as PNG
  function downloadQrPng() {
    const canvas = qrContainer.querySelector('canvas');
    if (!canvas) return;
    const a = document.createElement('a');
    a.href = canvas.toDataURL('image/png');
    a.download = `qrcode-${selectedCampaignKey}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // Download Transparent Frame PNG
  async function downloadTransparentFramePng() {
    const camp = campaigns[selectedCampaignKey];
    try {
      const res = await exportTransparentFrame(camp);
      const a = document.createElement('a');
      a.href = res.dataUrl;
      a.download = `frame-${selectedCampaignKey}-transparent.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (e) {
      alert('Error exporting frame: ' + e.message);
    }
  }

  // Update JSON Viewer
  function updateJsonViewer() {
    if (jsonTextarea) {
      jsonTextarea.value = JSON.stringify(campaigns[selectedCampaignKey], null, 2);
    }
  }

  // Save changes to localStorage
  function saveCurrentConfig() {
    saveCampaignConfig(selectedCampaignKey, campaigns[selectedCampaignKey]);
    const statusMsg = document.getElementById('save-status-msg');
    if (statusMsg) {
      statusMsg.textContent = '✓ Template saved successfully to LocalStorage!';
      setTimeout(() => { statusMsg.textContent = ''; }, 3000);
    }
  }

  // Reset to Defaults
  function resetDefaults() {
    if (confirm('Reset all templates to original factory presets?')) {
      campaigns = resetCampaignsToDefault();
      syncSlidersFromCampaign();
      renderLivePreview();
      updateJsonViewer();
    }
  }

  // Event Listeners
  function initEvents() {
    // Campaign Selector
    selectCampaign.addEventListener('change', (e) => {
      selectedCampaignKey = e.target.value;
      syncSlidersFromCampaign();
      renderLivePreview();
      if (activeTab === 'qrcodes') updateAdminQr();
      if (activeTab === 'json') updateJsonViewer();
    });

    // Tab buttons
    document.querySelectorAll('.admin-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        setTab(btn.getAttribute('data-tab'));
      });
    });

    // Slider inputs
    [inputX, inputY, inputW, inputH, inputR].forEach(slider => {
      slider.addEventListener('input', handleSliderChange);
    });

    // QR controls
    if (inputQrUrl) inputQrUrl.addEventListener('input', updateAdminQr);
    if (btnDownloadQr) btnDownloadQr.addEventListener('click', downloadQrPng);

    // Save & Reset Buttons
    document.getElementById('btn-save-template')?.addEventListener('click', saveCurrentConfig);
    document.getElementById('btn-reset-defaults')?.addEventListener('click', resetDefaults);
    document.getElementById('btn-export-frame')?.addEventListener('click', downloadTransparentFramePng);

    // JSON Copy Button
    document.getElementById('btn-copy-json')?.addEventListener('click', () => {
      if (jsonTextarea) {
        navigator.clipboard.writeText(jsonTextarea.value).then(() => {
          alert('Campaign JSON copied to clipboard!');
        });
      }
    });
  }

  // Initialize
  function init() {
    syncSlidersFromCampaign();
    renderLivePreview();
    initEvents();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
