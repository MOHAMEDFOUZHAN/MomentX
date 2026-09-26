"""
Nilgiris Frame - Production Python Backend & Analytics Engine
Serves the web application and tracks visitor analytics, QR scans, and photo downloads.
Compatible with local execution and Vercel Serverless Functions.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, g

# Initialize Flask app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

# Database path (use /tmp on Vercel serverless to support writes)
if os.environ.get('VERCEL'):
    DB_PATH = '/tmp/analytics.db'
    seed_db = os.path.join(BASE_DIR, 'analytics.db')
    if os.path.exists(seed_db) and not os.path.exists(DB_PATH):
        try:
            import shutil
            shutil.copyfile(seed_db, DB_PATH)
        except Exception as e:
            print(f"Vercel DB seed notice: {e}")
else:
    DB_PATH = os.path.join(BASE_DIR, 'analytics.db')

# ---------------------------------------------------------------------------
# Database Management
# ---------------------------------------------------------------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Create database tables if they do not exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                campaign_id TEXT DEFAULT 'nilgiri-tea',
                device_type TEXT DEFAULT 'desktop',
                os_name TEXT DEFAULT 'unknown',
                browser TEXT DEFAULT 'unknown',
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                campaign_id TEXT DEFAULT 'nilgiri-tea',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_date ON events(created_at)')
        conn.commit()

# Initialize DB on module load
try:
    init_db()
except Exception as e:
    print(f"Database init notice: {e}")

# ---------------------------------------------------------------------------
# Device & Client Detection Helper
# ---------------------------------------------------------------------------
def parse_user_agent(ua_string):
    ua = (ua_string or '').lower()
    
    # Device Type
    if 'ipad' in ua or 'tablet' in ua:
        device = 'tablet'
    elif 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        device = 'mobile'
    else:
        device = 'desktop'
        
    # OS
    if 'iphone' in ua or 'ipad' in ua or 'ios' in ua:
        os_name = 'iOS'
    elif 'android' in ua:
        os_name = 'Android'
    elif 'windows' in ua:
        os_name = 'Windows'
    elif 'mac' in ua:
        os_name = 'macOS'
    elif 'linux' in ua:
        os_name = 'Linux'
    else:
        os_name = 'Other'
        
    # Browser
    if 'safari' in ua and 'chrome' not in ua:
        browser = 'Safari'
    elif 'chrome' in ua or 'crios' in ua:
        browser = 'Chrome'
    elif 'firefox' in ua:
        browser = 'Firefox'
    elif 'edg' in ua:
        browser = 'Edge'
    else:
        browser = 'Other'
        
    return device, os_name, browser

def get_wifi_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def generate_mobile_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=3,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='#081c15', back_color='#ffffff')
        qr_file = os.path.join(BASE_DIR, 'mobile-app-qr.png')
        img.save(qr_file)
        return True
    except Exception as e:
        print(f"QR generation notice: {e}")
        return False

# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------
@app.route('/api/network-info', methods=['GET'])
def get_network_info():
    """Return local Wi-Fi IP and URLs for mobile testing."""
    local_ip = get_wifi_ip()
    port = int(os.environ.get('PORT', 3001))
    mobile_url = f"http://{local_ip}:{port}"
    return jsonify({
        'status': 'ok',
        'local_ip': local_ip,
        'port': port,
        'mobile_url': mobile_url,
        'qr_image_url': '/mobile-app-qr.png'
    })

@app.route('/api/event', methods=['POST'])
def track_event():
    """Log an event (page_view, camera_open, photo_snap, photo_download, photo_share, cta_click)."""
    data = request.get_json(silent=True) or {}
    event_type = data.get('event_type', 'page_view')
    campaign_id = data.get('campaign_id', 'nilgiri-tea')
    
    ua_str = request.headers.get('User-Agent', '')
    device, os_name, browser = parse_user_agent(ua_str)
    ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_addr and ',' in ip_addr:
        ip_addr = ip_addr.split(',')[0].strip()
        
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO events (event_type, campaign_id, device_type, os_name, browser, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (event_type, campaign_id, device, os_name, browser, ip_addr, ua_str))
        db.commit()
        return jsonify({'status': 'ok', 'event_id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/lead', methods=['POST'])
def save_lead():
    """Save customer contact information for WhatsApp or promotions."""
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    campaign_id = data.get('campaign_id', 'nilgiri-tea')
    
    if not phone and not email:
        return jsonify({'status': 'error', 'message': 'Phone number or email required'}), 400
        
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO leads (name, phone, email, campaign_id)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, email, campaign_id))
        db.commit()
        return jsonify({'status': 'ok', 'lead_id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/analytics/stats', methods=['GET'])
def get_analytics_stats():
    """Return aggregated metrics, funnel data, and timeline charts."""
    timeframe = request.args.get('timeframe', 'all')  # 'today', '7d', '30d', 'all'
    
    date_filter = ""
    params = []
    if timeframe == 'today':
        date_filter = "WHERE created_at >= date('now', 'start of day')"
    elif timeframe == '7d':
        date_filter = "WHERE created_at >= date('now', '-7 days')"
    elif timeframe == '30d':
        date_filter = "WHERE created_at >= date('now', '-30 days')"

    try:
        db = get_db()
        cursor = db.cursor()
        
        # 1. Total counts by event type
        query = f'''
            SELECT event_type, COUNT(*) as count 
            FROM events {date_filter}
            GROUP BY event_type
        '''
        cursor.execute(query, params)
        rows = cursor.fetchall()
        counts = {r['event_type']: r['count'] for r in rows}
        
        visits = counts.get('page_view', 0)
        camera_opens = counts.get('camera_open', 0)
        snaps = counts.get('photo_snap', 0)
        downloads = counts.get('photo_download', 0)
        shares = counts.get('photo_share', 0)
        cta_clicks = counts.get('cta_click', 0)
        
        conversion_rate = round((downloads / visits * 100), 1) if visits > 0 else 0.0
        
        # 2. Funnel metrics
        funnel = [
            {'step': 'QR Scans / Visits', 'count': visits, 'pct': 100},
            {'step': 'Camera Opened', 'count': camera_opens, 'pct': round(camera_opens / visits * 100, 1) if visits else 0},
            {'step': 'Photos Snapped', 'count': snaps, 'pct': round(snaps / visits * 100, 1) if visits else 0},
            {'step': 'HD Downloads', 'count': downloads, 'pct': round(downloads / visits * 100, 1) if visits else 0},
            {'step': 'Social Shares', 'count': shares, 'pct': round(shares / visits * 100, 1) if visits else 0}
        ]
        
        # 3. Device & OS Breakdown
        cursor.execute(f'''
            SELECT device_type, COUNT(*) as count 
            FROM events {date_filter}
            GROUP BY device_type
        ''')
        device_breakdown = {r['device_type']: r['count'] for r in cursor.fetchall()}
        
        cursor.execute(f'''
            SELECT os_name, COUNT(*) as count 
            FROM events {date_filter}
            GROUP BY os_name
        ''')
        os_breakdown = {r['os_name']: r['count'] for r in cursor.fetchall()}
        
        # 4. Daily Activity Timeline (last 7 days)
        cursor.execute('''
            SELECT 
                strftime('%Y-%m-%d', created_at) as day,
                SUM(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) as visits,
                SUM(CASE WHEN event_type = 'photo_snap' THEN 1 ELSE 0 END) as snaps,
                SUM(CASE WHEN event_type = 'photo_download' THEN 1 ELSE 0 END) as downloads
            FROM events
            WHERE created_at >= date('now', '-6 days')
            GROUP BY day
            ORDER BY day ASC
        ''')
        daily_activity = [dict(r) for r in cursor.fetchall()]
        
        # Total leads
        cursor.execute('SELECT COUNT(*) as count FROM leads')
        leads_count = cursor.fetchone()['count']
        
        return jsonify({
            'status': 'ok',
            'summary': {
                'total_visits': visits,
                'camera_opens': camera_opens,
                'photos_snapped': snaps,
                'total_downloads': downloads,
                'total_shares': shares,
                'cta_clicks': cta_clicks,
                'conversion_rate': conversion_rate,
                'total_leads': leads_count
            },
            'funnel': funnel,
            'devices': device_breakdown,
            'operating_systems': os_breakdown,
            'timeline': daily_activity
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/analytics/recent', methods=['GET'])
def get_recent_events():
    """Return the most recent 40 events for the live log."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT id, event_type, campaign_id, device_type, os_name, browser, created_at
            FROM events
            ORDER BY id DESC
            LIMIT 40
        ''')
        events = [dict(r) for r in cursor.fetchall()]
        return jsonify({'status': 'ok', 'events': events})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/analytics/reset', methods=['POST'])
def reset_analytics():
    """Reset event and lead records (useful for fresh testing)."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM events')
        cursor.execute('DELETE FROM leads')
        db.commit()
        return jsonify({'status': 'ok', 'message': 'Analytics reset successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ---------------------------------------------------------------------------
# Static Web Page Routes
# ---------------------------------------------------------------------------
@app.route('/')
@app.route('/index.html')
@app.route('/q/<path:subpath>')
def serve_index(subpath=None):
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/admin')
@app.route('/admin.html')
def serve_admin():
    return send_from_directory(BASE_DIR, 'admin.html')

@app.route('/analytics')
@app.route('/analytics.html')
def serve_analytics():
    return send_from_directory(BASE_DIR, 'analytics.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(BASE_DIR, filename)

# ---------------------------------------------------------------------------
# Run Local Server
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    local_ip = get_wifi_ip()
    mobile_url = f"http://{local_ip}:{port}"
    generate_mobile_qr(mobile_url)
    
    print("\n" + "=" * 64)
    print("[*] Nilgiris Frame - Production Python Server Active")
    print("=" * 64)
    print(f"[*] Local Computer:      http://localhost:{port}")
    print(f"[*] Mobile (Wi-Fi):      {mobile_url}")
    print(f"[*] Mobile QR Image:     {mobile_url}/mobile-app-qr.png")
    print(f"[*] Analytics Dashboard: http://localhost:{port}/analytics")
    print(f"[*] Admin Studio:        http://localhost:{port}/admin")
    print("=" * 64 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)

