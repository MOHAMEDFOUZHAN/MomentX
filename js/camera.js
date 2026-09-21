/**
 * Maple Connect - Camera and Media Capture Controller
 * Seamlessly handles Live Stream Camera, Native Device Capture fallback, and Demo Portraits.
 */

class CameraController {
  constructor() {
    this.stream = null;
    this.facingMode = 'user'; // 'user' (selfie) or 'environment' (scenic/back)
    this.videoElement = null;
    this.isSupported = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  // Start or switch live camera stream
  async startStream(videoEl, mode = this.facingMode) {
    this.videoElement = videoEl;
    this.facingMode = mode;
    this.stopStream();

    if (!this.isSupported) {
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      let errMsg = 'Camera access is not supported by your browser in this connection.';
      if (isMobile && location.protocol !== 'https:' && location.hostname !== 'localhost') {
        errMsg = 'Mobile browsers require HTTPS for live viewfinder streaming. Tap "Take Photo with Camera" below to use your native camera!';
      }
      throw new Error(errMsg);
    }

    try {
      const constraints = {
        video: {
          facingMode: { ideal: mode },
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: false
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.stream = stream;

      if (this.videoElement) {
        this.videoElement.srcObject = stream;
        // Flip selfie camera horizontally for natural mirror feel
        this.videoElement.style.transform = mode === 'user' ? 'scaleX(-1)' : 'scaleX(1)';
        await this.videoElement.play();
      }

      return stream;
    } catch (err) {
      console.warn('Camera streaming failed:', err);
      let message = 'Could not access camera.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        message = 'Camera permission was denied. Please allow camera permissions or upload an existing photo.';
      } else if (err.name === 'NotFoundError') {
        message = 'No camera found on this device. You can upload a photo or use the sample visitor photo.';
      } else {
        message = err.message || 'Camera is currently unavailable.';
      }
      throw new Error(message);
    }
  }

  // Switch between front and back camera
  async toggleFacingMode() {
    const nextMode = this.facingMode === 'user' ? 'environment' : 'user';
    if (this.videoElement) {
      return await this.startStream(this.videoElement, nextMode);
    }
    this.facingMode = nextMode;
    return null;
  }

  // Stop all active video tracks
  stopStream() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.videoElement) {
      this.videoElement.srcObject = null;
    }
  }

  // Capture current frame from live video
  captureFrame() {
    if (!this.videoElement) return null;

    const video = this.videoElement;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 1080;
    canvas.height = video.videoHeight || 1350;

    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.95);

    return {
      dataUrl,
      width: canvas.width,
      height: canvas.height,
      rotation: 0,
      scale: 1.0,
      offsetX: 0,
      offsetY: 0,
      mirrored: this.facingMode === 'user'
    };
  }

  // Process uploaded image file
  async loadFromFile(file) {
    return new Promise((resolve, reject) => {
      if (!file) return reject(new Error('No file selected'));

      const reader = new FileReader();
      reader.onload = (event) => {
        const dataUrl = event.target.result;
        const img = new Image();
        img.onload = () => {
          resolve({
            dataUrl,
            width: img.naturalWidth || img.width,
            height: img.naturalHeight || img.height,
            rotation: 0,
            scale: 1.0,
            offsetX: 0,
            offsetY: 0,
            mirrored: false
          });
        };
        img.onerror = () => reject(new Error('Failed to load image file'));
        img.src = dataUrl;
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  }

  // Generate a realistic, picturesque visitor portrait canvas for instant demo & offline testing
  createSamplePortrait() {
    const canvas = document.createElement('canvas');
    canvas.width = 1080;
    canvas.height = 1350;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    // Atmospheric mountain sky
    const sky = ctx.createLinearGradient(0, 0, 0, 800);
    sky.addColorStop(0, '#6d8fa8');
    sky.addColorStop(0.4, '#b4c7d9');
    sky.addColorStop(1, '#e4eae4');
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, 1080, 800);

    // Misty Nilgiri Blue Mountains
    ctx.fillStyle = '#41617a';
    ctx.beginPath();
    ctx.moveTo(0, 540);
    ctx.bezierCurveTo(240, 420, 480, 560, 780, 430);
    ctx.bezierCurveTo(940, 370, 1040, 470, 1080, 450);
    ctx.lineTo(1080, 1350);
    ctx.lineTo(0, 1350);
    ctx.closePath();
    ctx.fill();

    // Terraced Tea Plantations
    ctx.fillStyle = '#245a42';
    ctx.beginPath();
    ctx.moveTo(0, 670);
    ctx.bezierCurveTo(280, 570, 620, 710, 1080, 610);
    ctx.lineTo(1080, 1350);
    ctx.lineTo(0, 1350);
    ctx.closePath();
    ctx.fill();

    // Tea Bush Contours
    ctx.strokeStyle = '#143828';
    ctx.lineWidth = 14;
    for (let r = 700; r < 1250; r += 65) {
      ctx.beginPath();
      ctx.moveTo(0, r);
      ctx.bezierCurveTo(340, r - 35, 760, r + 45, 1080, r);
      ctx.stroke();
    }

    // Visitor Portrait Silhouette
    // Face & Neck
    ctx.fillStyle = '#fce9dc';
    ctx.beginPath();
    ctx.ellipse(540, 580, 165, 205, 0, 0, Math.PI * 2);
    ctx.fill();

    // Hair
    ctx.fillStyle = '#261b17';
    ctx.beginPath();
    ctx.arc(540, 530, 185, Math.PI, 0);
    ctx.bezierCurveTo(745, 580, 725, 740, 685, 770);
    ctx.lineTo(395, 770);
    ctx.bezierCurveTo(355, 740, 335, 580, 355, 530);
    ctx.fill();

    // Stylish Sunglasses
    ctx.fillStyle = '#1c1917';
    ctx.fillRect(415, 550, 105, 62);
    ctx.fillRect(560, 550, 105, 62);
    ctx.lineWidth = 5.5;
    ctx.strokeStyle = '#d4af37';
    ctx.strokeRect(415, 550, 105, 62);
    ctx.strokeRect(560, 550, 105, 62);
    ctx.beginPath();
    ctx.moveTo(520, 578);
    ctx.lineTo(560, 578);
    ctx.stroke();

    // Warm Smile
    ctx.beginPath();
    ctx.arc(540, 665, 48, 0.15 * Math.PI, 0.85 * Math.PI);
    ctx.lineWidth = 6;
    ctx.strokeStyle = '#c25852';
    ctx.stroke();

    // Coat / Shoulders
    ctx.fillStyle = '#0e261d';
    ctx.beginPath();
    ctx.ellipse(540, 1060, 410, 330, 0, 0, Math.PI * 2);
    ctx.fill();

    // Gold Cashmere Scarf
    ctx.fillStyle = '#d4af37';
    ctx.beginPath();
    ctx.ellipse(540, 785, 185, 80, 0, 0, Math.PI * 2);
    ctx.fill();

    const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
    return {
      dataUrl,
      width: 1080,
      height: 1350,
      rotation: 0,
      scale: 1.0,
      offsetX: 0,
      offsetY: 0,
      mirrored: false
    };
  }
}

const cameraController = new CameraController();
