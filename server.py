"""
Nilgiris Frame - Production Python Backend & Analytics Engine
Serves the web application and tracks visitor analytics, QR scans, and photo downloads.
Compatible with local execution and Vercel Serverless Functions.
"""

import os
import sys
import csv
import io
import json
import time
import hmac
import sqlite3
from datetime import datetime, timedelta, date
from functools import wraps
from urllib.parse import quote
from flask import Flask, request, jsonify, send_from_directory, g, redirect, session, Response

# Initialize Flask app.
# static_folder is deliberately disabled: every asset goes through the guarded
# catch-all route at the bottom of this file, so private files (analytics.db,
# server.py, requirements.txt, ...) can never be downloaded.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get('SECRET_KEY', 'nlg-maple-secret-2307')

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=bool(os.environ.get('VERCEL')),  # HTTPS-only in production
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)

# Admin credentials (override with env vars in production)
ADMIN_USER = os.environ.get('ADMIN_USER', 'fouzhan')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'mapleconnect2307')

if not os.environ.get('SECRET_KEY'):
    print('[security] SECRET_KEY is not set - using the built-in default. '
          'Set SECRET_KEY in the environment before deploying.')

# ---------------------------------------------------------------------------
# Auth & Static Asset Guards
# ---------------------------------------------------------------------------
# Only these file types may ever be served to the public.
PUBLIC_EXTENSIONS = {
    '.html', '.css', '.js', '.json',
    '.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif', '.ico',
    '.woff', '.woff2', '.ttf', '.otf',
}
# Defence in depth: never serve these even though they match an extension above.
BLOCKED_FILES = {'vercel.json'}


def is_public_asset(filename):
    """True only for real front-end assets, never for data or source files."""
    if not filename:
        return False
    normalized = filename.replace('\\', '/')
    if normalized.startswith('.') or '/.' in normalized:
        return False
    if '..' in normalized.split('/'):
        return False
    if normalized.lower() in BLOCKED_FILES:
        return False
    if '__pycache__' in normalized.lower():
        return False
    return os.path.splitext(normalized.lower())[1] in PUBLIC_EXTENSIONS


def constant_time_eq(value, expected):
    """Compare strings without leaking length/timing information."""
    return hmac.compare_digest(value.encode('utf-8'), expected.encode('utf-8'))


def login_required(view):
    """Hard gate for admin pages and analytics APIs, backed by the server session."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('admin_authenticated') is True:
            return view(*args, **kwargs)
        if request.path.startswith('/api/'):
            return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
        return redirect('/login?next=' + quote(request.path))
    return wrapped


def safe_next(target, default='/admin'):
    """Prevent open redirects - only our own admin pages are allowed."""
    if target and target.startswith('/') and not target.startswith('//'):
        if target.startswith(('/admin', '/analytics')):
            return target
    return default


# Simple in-memory brute-force throttle (per client IP)
LOGIN_WINDOW_SECONDS = 300
LOGIN_MAX_ATTEMPTS = 5
login_attempts = {}


def login_throttled(ip):
    now = time.time()
    recent = [t for t in login_attempts.get(ip, []) if now - t < LOGIN_WINDOW_SECONDS]
    login_attempts[ip] = recent
    return len(recent) >= LOGIN_MAX_ATTEMPTS


def record_login_failure(ip):
    login_attempts.setdefault(ip, []).append(time.time())

# Database path (ANALYTICS_DB overrides it; /tmp on Vercel serverless to support writes)
if os.environ.get('ANALYTICS_DB'):
    DB_PATH = os.environ['ANALYTICS_DB']
elif os.environ.get('VERCEL'):
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
@app.route('/api/login', methods=['POST'])
def api_login():
    """Verify credentials server-side and start an HttpOnly session cookie."""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr) or ''
    ip_addr = ip_addr.split(',')[0].strip()

    if login_throttled(ip_addr):
        return jsonify({'status': 'error', 'message': 'Too many attempts. Please try again in a few minutes.'}), 429

    user_ok = constant_time_eq(username, ADMIN_USER)
    pass_ok = constant_time_eq(password, ADMIN_PASS)

    if not (user_ok and pass_ok):
        record_login_failure(ip_addr)
        time.sleep(0.4)  # dampen rapid brute-force attempts
        return jsonify({'status': 'error', 'message': 'Invalid username or password.'}), 401

    login_attempts.pop(ip_addr, None)
    session.clear()
    session.permanent = True
    session['admin_authenticated'] = True
    session['admin_user'] = username
    return jsonify({'status': 'ok', 'redirect': safe_next(data.get('next'))})


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'ok'})


@app.route('/api/session', methods=['GET'])
def api_session():
    """Lets the login page skip the form when a valid session already exists."""
    return jsonify({'authenticated': session.get('admin_authenticated') is True})


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

# ---------------------------------------------------------------------------
# Reporting engine - daily / weekly scan reports for the owner
# ---------------------------------------------------------------------------
# created_at is stored in UTC (SQLite CURRENT_TIMESTAMP); reports group by the
# server's local calendar day so "scans per day" matches the booth's clock.
LOCAL_DAY = "date(created_at, 'localtime')"
REPORT_MAX_LEADS = 25


def resolve_report_range(key):
    """Translate a UI range key into concrete local calendar dates."""
    today = date.today()
    key = (key or '7d').strip().lower()
    if key == 'today':
        return key, 'Today', today, today
    if key == 'week':
        return key, 'This week', today - timedelta(days=today.weekday()), today
    if key == '30d':
        return key, 'Last 30 days', today - timedelta(days=29), today
    if key == '90d':
        return key, 'Last 90 days', today - timedelta(days=89), today
    if key == 'all':
        return key, 'All time', None, today
    return '7d', 'Last 7 days', today - timedelta(days=6), today


def _range_clause(start, end):
    if start is None:
        return '', []
    return f" AND {LOCAL_DAY} BETWEEN ? AND ?", [start.isoformat(), end.isoformat()]


def _int(value):
    return int(value or 0)


def _rate(part, whole):
    return round(part / whole * 100, 1) if whole else 0.0


def _summary_for(cursor, start, end, days):
    clause, params = _range_clause(start, end)
    cursor.execute(f'''
        SELECT
            SUM(event_type = 'page_view')      AS scans,
            SUM(event_type = 'camera_open')    AS camera_opens,
            SUM(event_type = 'photo_snap')     AS photos,
            SUM(event_type = 'photo_download') AS downloads,
            SUM(event_type = 'photo_share')    AS shares,
            SUM(event_type = 'cta_click')      AS cta_clicks,
            COUNT(DISTINCT CASE WHEN event_type = 'page_view'
                  THEN COALESCE(ip_address, '') || '|' || COALESCE(user_agent, '') END) AS unique_devices
        FROM events
        WHERE 1 = 1 {clause}
    ''', params)
    row = cursor.fetchone()
    cursor.execute(f"SELECT COUNT(*) AS c FROM leads WHERE 1 = 1 {clause}", params)
    leads = _int(cursor.fetchone()['c'])

    scans = _int(row['scans'])
    photos = _int(row['photos'])
    downloads = _int(row['downloads'])
    return {
        'scans': scans,
        'unique_devices': _int(row['unique_devices']),
        'camera_opens': _int(row['camera_opens']),
        'photos': photos,
        'downloads': downloads,
        'shares': _int(row['shares']),
        'cta_clicks': _int(row['cta_clicks']),
        'leads': leads,
        'scan_to_photo_pct': _rate(photos, scans),
        'photo_to_download_pct': _rate(downloads, photos),
        'scan_to_download_pct': _rate(downloads, scans),
        'avg_scans_per_day': round(scans / days, 1) if days else 0.0,
    }


def _breakdown(cursor, column, clause, params):
    """Count events grouped by one column (column is always a literal here)."""
    cursor.execute(
        f"SELECT {column} AS label, COUNT(*) AS count FROM events"
        f" WHERE 1 = 1 {clause} GROUP BY label ORDER BY count DESC", params)
    return {(row['label'] or 'Unknown'): row['count'] for row in cursor.fetchall()}


def build_report(range_key):
    """Full scan report: summary, previous period, daily, weekly and breakdowns."""
    range_key, label, start, end = resolve_report_range(range_key)
    db = get_db()
    cursor = db.cursor()

    if start is None:
        first = cursor.execute(f"SELECT MIN({LOCAL_DAY}) AS first FROM events").fetchone()
        start = date.fromisoformat(first['first']) if first and first['first'] else end
    days = (end - start).days + 1

    summary = _summary_for(cursor, start, end, days)
    clause, params = _range_clause(start, end)

    previous = None
    if range_key != 'all':
        previous_end = start - timedelta(days=1)
        previous_start = previous_end - timedelta(days=days - 1)
        previous = _summary_for(cursor, previous_start, previous_end, days)
        previous['start'] = previous_start.isoformat()
        previous['end'] = previous_end.isoformat()

    # Daily matrix: one row per event type per local day.
    cursor.execute(f'''
        SELECT {LOCAL_DAY} AS day, event_type, COUNT(*) AS count
        FROM events
        WHERE 1 = 1 {clause}
        GROUP BY day, event_type
    ''', params)
    by_day = {}
    for row in cursor.fetchall():
        by_day.setdefault(row['day'], {})[row['event_type']] = row['count']

    cursor.execute(f'''
        SELECT {LOCAL_DAY} AS day,
               COUNT(DISTINCT COALESCE(ip_address, '') || '|' || COALESCE(user_agent, '')) AS unique_devices
        FROM events
        WHERE event_type = 'page_view' {clause}
        GROUP BY day
    ''', params)
    unique_by_day = {row['day']: row['unique_devices'] for row in cursor.fetchall()}

    daily = []
    day = start
    while day <= end:
        iso = day.isoformat()
        counts = by_day.get(iso, {})
        daily.append({
            'date': iso,
            'weekday': day.strftime('%a'),
            'scans': counts.get('page_view', 0),
            'unique_devices': unique_by_day.get(iso, 0),
            'camera_opens': counts.get('camera_open', 0),
            'photos': counts.get('photo_snap', 0),
            'downloads': counts.get('photo_download', 0),
            'shares': counts.get('photo_share', 0),
        })
        day += timedelta(days=1)

    # Weekly buckets (ISO weeks, Monday start) from the daily series.
    weeks = {}
    for item in daily:
        current = date.fromisoformat(item['date'])
        week_start = current - timedelta(days=current.weekday())
        iso_year, iso_week, _ = current.isocalendar()
        week_key = f"{iso_year}-W{iso_week:02d}"
        bucket = weeks.setdefault(week_key, {
            'week': week_key,
            'start': week_start.isoformat(),
            'end': (week_start + timedelta(days=6)).isoformat(),
            'scans': 0,
            'photos': 0,
            'downloads': 0,
            'shares': 0,
            'days_in_range': 0,
        })
        bucket['days_in_range'] += 1
        for field in ('scans', 'photos', 'downloads', 'shares'):
            bucket[field] += item[field]
    weekly = []
    for bucket in sorted(weeks.values(), key=lambda w: w['start']):
        bucket['avg_scans_per_day'] = round(bucket['scans'] / bucket['days_in_range'], 1) if bucket['days_in_range'] else 0.0
        weekly.append(bucket)

    # Hour of day and day of week, based on scans only.
    cursor.execute(f'''
        SELECT CAST(strftime('%H', created_at, 'localtime') AS INTEGER) AS hour,
               COUNT(*) AS count
        FROM events
        WHERE event_type = 'page_view' {clause}
        GROUP BY hour
    ''', params)
    hour_counts = {row['hour']: row['count'] for row in cursor.fetchall()}
    hourly = [{'hour': hour, 'scans': hour_counts.get(hour, 0)} for hour in range(24)]

    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekday_counts = {name: 0 for name in weekday_names}
    for item in daily:
        weekday_counts[item['weekday']] += item['scans']
    weekdays = [{'weekday': name, 'scans': weekday_counts[name]} for name in weekday_names]

    # Per-frame performance.
    cursor.execute(f'''
        SELECT campaign_id,
               SUM(event_type = 'page_view')      AS scans,
               SUM(event_type = 'camera_open')    AS camera_opens,
               SUM(event_type = 'photo_snap')     AS photos,
               SUM(event_type = 'photo_download') AS downloads,
               SUM(event_type = 'photo_share')    AS shares
        FROM events
        WHERE 1 = 1 {clause}
        GROUP BY campaign_id
        ORDER BY scans DESC, downloads DESC
    ''', params)
    frames = []
    for row in cursor.fetchall():
        frame_scans = _int(row['scans'])
        frames.append({
            'id': row['campaign_id'] or 'unknown',
            'scans': frame_scans,
            'camera_opens': _int(row['camera_opens']),
            'photos': _int(row['photos']),
            'downloads': _int(row['downloads']),
            'shares': _int(row['shares']),
            'scan_to_download_pct': _rate(_int(row['downloads']), frame_scans),
        })

    busy = max(daily, key=lambda item: item['scans']) if daily else None
    if busy and busy['scans']:
        summary['busiest_day'] = {'date': busy['date'], 'weekday': busy['weekday'], 'scans': busy['scans']}
    else:
        summary['busiest_day'] = None

    peak = max(hourly, key=lambda item: item['scans']) if hourly else None
    summary['peak_hour'] = peak['hour'] if peak and peak['scans'] else None

    cursor.execute(f'''
        SELECT name, phone, email, campaign_id, created_at
        FROM leads
        WHERE 1 = 1 {clause}
        ORDER BY id DESC
        LIMIT {REPORT_MAX_LEADS}
    ''', params)
    leads = [dict(row) for row in cursor.fetchall()]

    return {
        'status': 'ok',
        'range': {
            'key': range_key,
            'label': label,
            'start': start.isoformat(),
            'end': end.isoformat(),
            'days': days,
        },
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'summary': summary,
        'previous': previous,
        'daily': daily,
        'weekly': weekly,
        'hourly': hourly,
        'weekdays': weekdays,
        'frames': frames,
        'funnel': [
            {'step': 'QR scans / visits', 'count': summary['scans'], 'pct': 100 if summary['scans'] else 0},
            {'step': 'Camera opened', 'count': summary['camera_opens'], 'pct': _rate(summary['camera_opens'], summary['scans'])},
            {'step': 'Photos snapped', 'count': summary['photos'], 'pct': _rate(summary['photos'], summary['scans'])},
            {'step': 'HD downloads', 'count': summary['downloads'], 'pct': _rate(summary['downloads'], summary['scans'])},
            {'step': 'Social shares', 'count': summary['shares'], 'pct': _rate(summary['shares'], summary['scans'])},
        ],
        'devices': _breakdown(cursor, 'device_type', clause, params),
        'operating_systems': _breakdown(cursor, 'os_name', clause, params),
        'browsers': _breakdown(cursor, 'browser', clause, params),
        'leads': leads,
    }


def build_report_csv(report):
    """Scan counts only: totals, one row per day and one row per week."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    meta = report['range']
    summary = report['summary']
    writer.writerow(['Nilgiris Frame - scan counts'])
    writer.writerow(['Range', meta['label']])
    writer.writerow(['From', meta['start']])
    writer.writerow(['To', meta['end']])
    writer.writerow(['Days', meta['days']])
    writer.writerow(['Generated', report['generated_at']])
    writer.writerow([])

    writer.writerow(['Total scans', summary['scans']])
    writer.writerow(['Average scans per day', summary['avg_scans_per_day']])
    writer.writerow([])

    writer.writerow(['Scans per day'])
    writer.writerow(['Date', 'Weekday', 'Scans'])
    for item in report['daily']:
        writer.writerow([item['date'], item['weekday'], item['scans']])
    writer.writerow([])

    writer.writerow(['Scans per week'])
    writer.writerow(['Week', 'Week start', 'Week end', 'Scans', 'Average scans per day'])
    for item in report['weekly']:
        writer.writerow([item['week'], item['start'], item['end'], item['scans'], item['avg_scans_per_day']])

    filename = f"nilgiris-scan-counts-{meta['key']}-{meta['end'].replace('-', '')}.csv"
    return filename, '\ufeff' + buffer.getvalue()


@app.route('/api/analytics/report', methods=['GET'])
@login_required
def get_analytics_report():
    """Full scan report for the dashboard (daily, weekly, frames, devices, leads)."""
    try:
        return jsonify(build_report(request.args.get('range', '7d')))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/analytics/report.csv', methods=['GET'])
@login_required
def download_analytics_report():
    """Download the same report as CSV (opens in Excel / Google Sheets)."""
    try:
        filename, payload = build_report_csv(build_report(request.args.get('range', '7d')))
        return Response(payload, content_type='text/csv; charset=utf-8', headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Cache-Control': 'no-store',
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/analytics/stats', methods=['GET'])
@login_required
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
@login_required
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
@login_required
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

@app.route('/login')
@app.route('/login.html')
def serve_login():
    """Public login page — no auth required."""
    return send_from_directory(BASE_DIR, 'login.html')

@app.route('/admin')
@app.route('/admin.html')
@login_required
def serve_admin():
    """Admin studio — gated by the server session."""
    return send_from_directory(BASE_DIR, 'admin.html')

@app.route('/analytics')
@app.route('/analytics.html')
@login_required
def serve_analytics():
    """Analytics dashboard — gated by the server session."""
    return send_from_directory(BASE_DIR, 'analytics.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve front-end assets only. Data, source and config files are never exposed."""
    if not is_public_asset(filename):
        return jsonify({'status': 'error', 'message': 'Not found'}), 404
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

