const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PORT = process.env.PORT || 3001;
const PUBLIC_DIR = __dirname;

const MIME_TYPES = {
  '.html': 'text/html; charset=UTF-8',
  '.css': 'text/css; charset=UTF-8',
  '.js': 'application/javascript; charset=UTF-8',
  '.json': 'application/json; charset=UTF-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
};

// Retrieve prioritized network IPv4 addresses (Wi-Fi first)
function getNetworkIps() {
  const interfaces = os.networkInterfaces();
  const list = [];
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        const lower = name.toLowerCase();
        const isVirtual = lower.includes('virtual') || lower.includes('vbox') || lower.includes('vmware') || iface.address.startsWith('192.168.56.');
        const isWifi = lower.includes('wi-fi') || lower.includes('wireless') || lower.includes('wlan');
        list.push({ name, address: iface.address, isVirtual, isWifi });
      }
    }
  }

  // Sort Wi-Fi first, then physical Ethernet, then virtual
  list.sort((a, b) => {
    if (a.isWifi && !b.isWifi) return -1;
    if (!a.isWifi && b.isWifi) return 1;
    if (!a.isVirtual && b.isVirtual) return -1;
    if (a.isVirtual && !b.isVirtual) return 1;
    return 0;
  });

  return list;
}

const server = http.createServer((req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
  let pathname = parsedUrl.pathname;

  // SPA Route Rewrites
  if (pathname.startsWith('/q/') || pathname === '/' || pathname === '/index.html') {
    pathname = '/index.html';
  } else if (pathname === '/admin' || pathname === '/admin.html') {
    pathname = '/admin.html';
  }

  let filePath = path.join(PUBLIC_DIR, pathname);
  const resolvedPublicDir = path.resolve(PUBLIC_DIR).toLowerCase();
  const resolvedFilePath = path.resolve(filePath).toLowerCase();

  // Security check: ensure filePath is within PUBLIC_DIR
  if (!resolvedFilePath.startsWith(resolvedPublicDir)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('403 Forbidden');
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      // Fallback to index.html for client-side routing
      filePath = path.join(PUBLIC_DIR, 'index.html');
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    fs.readFile(filePath, (readErr, content) => {
      if (readErr) {
        console.error('Read error:', readErr, filePath);
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`500 Internal Server Error: ${readErr.message}`);
        return;
      }

      res.writeHead(200, {
        'Content-Type': contentType,
        'Cache-Control': 'no-cache',
        'Access-Control-Allow-Origin': '*',
      });
      res.end(content);
    });
  });
});

server.listen(PORT, '0.0.0.0', () => {
  const ips = getNetworkIps();
  const primaryIp = ips.length > 0 ? ips[0].address : 'localhost';

  console.log(`\n================================================================`);
  console.log(`🌿 Maple Connect - Pure HTML/CSS/JS Experience Running`);
  console.log(`================================================================`);
  console.log(`💻 Local Computer:     http://localhost:${PORT}`);
  console.log(`📱 Mobile (Wi-Fi):     http://${primaryIp}:${PORT}`);
  console.log(`----------------------------------------------------------------`);
  console.log(`🍃 Sagar Nilgiri Frame: http://${primaryIp}:${PORT}/q/nilgiri-tea`);
  console.log(`🍁 Maple Artisan Frame: http://${primaryIp}:${PORT}/q/maple-artisan`);
  console.log(`🌿 Highland Spice Frame: http://${primaryIp}:${PORT}/q/highland-spice`);
  console.log(`⚙️  Admin Studio:        http://${primaryIp}:${PORT}/admin`);
  console.log(`================================================================`);
  console.log(`📱 TO USE ON YOUR MOBILE PHONE:`);
  console.log(`1. Ensure your phone and PC are connected to the same Wi-Fi.`);
  console.log(`2. Open Safari or Chrome on your phone.`);
  console.log(`3. Type in the address: http://${primaryIp}:${PORT}`);
  console.log(`   (Or open http://localhost:${PORT} on your PC and click "📱 QR" to scan it straight off your monitor!)\n`);
});
