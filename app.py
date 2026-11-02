from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import os
import functools
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection, init_db, seed_initial_data, calculate_boarding_times
from navigation import (
    load_graph,
    generate_route_details,
    check_wrong_turn_and_reroute,
    get_text,
    get_location_display_name,
    TRANSLATIONS
)
from qr_generator import generate_location_qr, generate_all_qrcodes

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Ensure database and QR directories exist
init_db()
seed_initial_data()

# Template context processor to inject language helpers into all templates
@app.context_processor
def inject_localization():
    lang = session.get('lang', 'en')
    return {
        'current_lang': lang,
        'get_text': lambda key, **kwargs: get_text(key, lang=lang, **kwargs),
        'get_loc_name': lambda name: get_location_display_name(name, lang=lang),
        'all_translations': TRANSLATIONS.get(lang, TRANSLATIONS['en']),
        'available_langs': [
            {'code': 'en', 'label': 'English', 'flag': '🇬🇧'},
            {'code': 'ta', 'label': 'தமிழ் (Tamil)', 'flag': '🇮🇳'},
            {'code': 'hi', 'label': 'हिंदी (Hindi)', 'flag': '🇮🇳'}
        ]
    }

def login_required(view):
    """Admin authentication decorator."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'admin_user' not in session:
            flash('Please log in with admin credentials to access this area.', 'warning')
            return redirect(url_for('admin_login'))
        return view(**kwargs)
    return wrapped_view

# ==================== LANGUAGE SWITCHER ====================
@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['en', 'ta', 'hi']:
        session['lang'] = lang
    referer = request.headers.get('Referer')
    return redirect(referer or url_for('index'))

# ==================== PUBLIC PASSENGER ROUTES ====================
@app.route('/')
def index():
    """Home landing page."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights ORDER BY departure_time ASC LIMIT 6")
    flights = cursor.fetchall()
    cursor.execute("SELECT * FROM locations ORDER BY location_name ASC")
    locations = cursor.fetchall()
    conn.close()
    return render_template('index.html', flights=flights, locations=locations)

@app.route('/passenger')
def passenger_dashboard():
    """Passenger dashboard with flight tracking and quick facility navigation."""
    flight_num = request.args.get('flight', '').strip().upper()
    current_loc_id = request.args.get('loc_id', type=int)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations ORDER BY location_name ASC")
    locations = cursor.fetchall()

    cursor.execute("SELECT * FROM flights ORDER BY departure_time ASC")
    all_flights = cursor.fetchall()

    flight_info = None
    if flight_num:
        cursor.execute("SELECT * FROM flights WHERE flight_number = ?", (flight_num,))
        flight_info = cursor.fetchone()

    current_location = None
    if current_loc_id:
        cursor.execute("SELECT * FROM locations WHERE id = ?", (current_loc_id,))
        current_location = cursor.fetchone()

    conn.close()
    return render_template('passenger.html',
                           locations=locations,
                           all_flights=all_flights,
                           flight_info=flight_info,
                           flight_num=flight_num,
                           current_location=current_location)

@app.route('/scanner')
@app.route('/scan')
def qr_scanner():
    """QR Code scanner page with camera feed, file upload, and simulated quick checkpoints."""
    loc_id = request.args.get('loc_id', type=int)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, location_name, location_type FROM locations ORDER BY location_name ASC")
    locations = cursor.fetchall()
    conn.close()
    return render_template('scanner.html', locations=locations, scanned_loc_id=loc_id)

@app.route('/flight-search')
def flight_search():
    """Flight information search and departure schedule board."""
    query = request.args.get('q', '').strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()
    if query:
        cursor.execute('''
            SELECT * FROM flights
            WHERE flight_number LIKE ? OR airline LIKE ? OR destination_city LIKE ?
            ORDER BY departure_time ASC
        ''', (f"%{query}%", f"%{query}%", f"%{query}%"))
    else:
        cursor.execute("SELECT * FROM flights ORDER BY departure_time ASC")
    flights = cursor.fetchall()
    conn.close()
    return render_template('flight.html', flights=flights, query=query)

@app.route('/navigation')
def navigation_view():
    """Interactive airport map and turn-by-turn guidance page."""
    start_id = request.args.get('from', type=int)
    end_id = request.args.get('to', type=int)
    flight_num = request.args.get('flight', '').strip().upper()
    lang = session.get('lang', 'en')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, location_name, location_type, x_coordinate, y_coordinate, description FROM locations ORDER BY location_name ASC")
    locations = cursor.fetchall()

    flight_info = None
    if flight_num:
        cursor.execute("SELECT * FROM flights WHERE flight_number = ?", (flight_num,))
        flight_info = cursor.fetchone()

    conn.close()

    # If coordinates/IDs not provided, default to Main Entrance -> Central Lounge or Gate
    if not start_id and locations:
        start_id = locations[0]['id']
    if not end_id and len(locations) > 1:
        end_id = locations[7]['id'] if len(locations) > 7 else locations[1]['id']

    # Generate initial route
    route_data = generate_route_details(start_id, end_id, lang=lang)

    # Record into navigation_history
    if route_data.get('success'):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO navigation_history (flight_number, source_location, destination_location, distance, estimated_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                flight_num or 'N/A',
                route_data['start_node']['location_name'],
                route_data['end_node']['location_name'],
                route_data['total_distance'],
                route_data['estimated_time']
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving navigation history: {e}")

    return render_template('navigation.html',
                           locations=locations,
                           start_id=start_id,
                           end_id=end_id,
                           flight_info=flight_info,
                           flight_num=flight_num,
                           route_data=route_data)

# ==================== ADMIN AUTHENTICATION & DASHBOARD ====================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin staff login."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['admin_user'] = user['username']
            session['admin_role'] = user['role']
            flash('Successfully logged in to Airport Admin Portal.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_user', None)
    session.pop('admin_role', None)
    flash('You have been logged out of the Admin Portal.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard overview with statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as cnt FROM locations")
    total_locations = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM qr_codes")
    total_qrs = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM flights")
    total_flights = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM navigation_history")
    total_routes_navigated = cursor.fetchone()['cnt']

    cursor.execute("SELECT * FROM flights ORDER BY departure_time ASC")
    recent_flights = cursor.fetchall()

    cursor.execute('''
        SELECT nh.*, l1.location_name as src_name, l2.location_name as dst_name
        FROM navigation_history nh
        LEFT JOIN locations l1 ON nh.source_location = l1.location_name
        LEFT JOIN locations l2 ON nh.destination_location = l2.location_name
        ORDER BY nh.created_at DESC LIMIT 6
    ''')
    recent_activity = cursor.fetchall()

    conn.close()
    return render_template('admin_dashboard.html',
                           total_locations=total_locations,
                           total_qrs=total_qrs,
                           total_flights=total_flights,
                           total_routes_navigated=total_routes_navigated,
                           recent_flights=recent_flights,
                           recent_activity=recent_activity)

# ==================== ADMIN FLIGHT MANAGEMENT ====================
@app.route('/admin/flights')
@login_required
def manage_flights():
    """Flight management view."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights ORDER BY departure_time ASC")
    flights = cursor.fetchall()
    cursor.execute("SELECT location_name, location_type FROM locations ORDER BY location_name ASC")
    locations = cursor.fetchall()
    conn.close()
    return render_template('manage_flights.html', flights=flights, locations=locations)

@app.route('/admin/flights/add', methods=['POST'])
@login_required
def add_flight():
    flight_number = request.form.get('flight_number', '').strip().upper()
    airline = request.form.get('airline', '').strip()
    destination_city = request.form.get('destination_city', '').strip()
    departure_time = request.form.get('departure_time', '').strip()
    checkin_counter = request.form.get('checkin_counter', '').strip()
    security_checkpoint = request.form.get('security_checkpoint', '').strip()
    boarding_gate = request.form.get('boarding_gate', '').strip()
    boarding_time = request.form.get('boarding_time', '').strip()
    boarding_closes = request.form.get('boarding_closes', '').strip()
    status = request.form.get('status', 'On Time').strip()

    if not (flight_number and airline and destination_city and departure_time):
        flash('Please fill in all mandatory flight fields.', 'danger')
        return redirect(url_for('manage_flights'))

    # Auto-calculate boarding times if not explicitly provided
    if not boarding_time or not boarding_closes:
        calc_start, calc_close = calculate_boarding_times(departure_time)
        boarding_time = boarding_time or calc_start
        boarding_closes = boarding_closes or calc_close

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO flights (flight_number, airline, destination_city, departure_time,
                                 boarding_time, boarding_closes,
                                 checkin_counter, security_checkpoint, boarding_gate, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (flight_number, airline, destination_city, departure_time,
              boarding_time, boarding_closes,
              checkin_counter, security_checkpoint, boarding_gate, status))
        conn.commit()
        flash(f'Flight {flight_number} added successfully.', 'success')
    except Exception as e:
        flash(f'Error adding flight: {e}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('manage_flights'))

@app.route('/admin/flights/edit/<int:flight_id>', methods=['POST'])
@login_required
def edit_flight(flight_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    orig = cursor.fetchone()

    if not orig:
        conn.close()
        flash('Flight record not found.', 'danger')
        return redirect(url_for('manage_flights'))

    airline = request.form.get('airline', orig['airline']).strip()
    destination_city = request.form.get('destination_city', orig['destination_city']).strip()
    departure_time = request.form.get('departure_time', orig['departure_time']).strip()
    checkin_counter = request.form.get('checkin_counter', orig['checkin_counter']).strip()
    security_checkpoint = request.form.get('security_checkpoint', orig['security_checkpoint']).strip()
    boarding_gate = request.form.get('boarding_gate', orig['boarding_gate']).strip()
    boarding_time = request.form.get('boarding_time', orig['boarding_time'] or '').strip()
    boarding_closes = request.form.get('boarding_closes', orig['boarding_closes'] or '').strip()
    status = request.form.get('status', orig['status']).strip()

    # Recalculate boarding times if departure time changed and boarding times were left empty
    if not boarding_time or not boarding_closes:
        calc_start, calc_close = calculate_boarding_times(departure_time)
        boarding_time = boarding_time or calc_start
        boarding_closes = boarding_closes or calc_close

    # Detect Gate Change!
    if boarding_gate != orig['boarding_gate']:
        status = 'Gate Changed'
        flash(f'Gate Changed for Flight {orig["flight_number"]} from {orig["boarding_gate"]} to {boarding_gate}. Passengers will receive immediate live reroute alerts!', 'warning')

    cursor.execute('''
        UPDATE flights
        SET airline = ?, destination_city = ?, departure_time = ?,
            boarding_time = ?, boarding_closes = ?,
            checkin_counter = ?, security_checkpoint = ?, boarding_gate = ?,
            status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (airline, destination_city, departure_time,
          boarding_time, boarding_closes,
          checkin_counter, security_checkpoint, boarding_gate, status, flight_id))
    conn.commit()
    conn.close()

    flash(f'Flight {orig["flight_number"]} updated successfully.', 'success')
    return redirect(url_for('manage_flights'))

@app.route('/admin/flights/delete/<int:flight_id>', methods=['POST'])
@login_required
def delete_flight(flight_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flights WHERE id = ?", (flight_id,))
    conn.commit()
    conn.close()
    flash('Flight removed from active database.', 'info')
    return redirect(url_for('manage_flights'))

# ==================== ADMIN LOCATION & QR MANAGEMENT ====================
@app.route('/admin/locations')
@login_required
def manage_locations():
    """Airport locations and map coordinates management view."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.*, q.qr_image_path
        FROM locations l
        LEFT JOIN qr_codes q ON l.id = q.location_id
        ORDER BY l.location_name ASC
    ''')
    locations = cursor.fetchall()
    conn.close()
    return render_template('manage_locations.html', locations=locations)

@app.route('/admin/locations/add', methods=['POST'])
@login_required
def add_location():
    name = request.form.get('location_name', '').strip()
    loc_type = request.form.get('location_type', '').strip()
    desc = request.form.get('description', '').strip()
    x = request.form.get('x_coordinate', type=int) or 500
    y = request.form.get('y_coordinate', type=int) or 350

    if not name or not loc_type:
        flash('Location name and type are required.', 'danger')
        return redirect(url_for('manage_locations'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO locations (location_name, location_type, description, x_coordinate, y_coordinate)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, loc_type, desc, x, y))
        new_id = cursor.lastrowid
        conn.commit()

        # Automatically generate QR Code
        host_url = request.host_url.rstrip('/')
        qr_path = generate_location_qr(new_id, name, base_url=host_url)
        cursor.execute('''
            INSERT INTO qr_codes (location_id, qr_image_path)
            VALUES (?, ?)
        ''', (new_id, qr_path))
        conn.commit()

        flash(f'Airport location "{name}" added and QR code generated.', 'success')
    except Exception as e:
        flash(f'Error adding location: {e}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('manage_locations'))

@app.route('/admin/locations/edit/<int:loc_id>', methods=['POST'])
@login_required
def edit_location(loc_id):
    name = request.form.get('location_name', '').strip()
    loc_type = request.form.get('location_type', '').strip()
    desc = request.form.get('description', '').strip()
    x = request.form.get('x_coordinate', type=int)
    y = request.form.get('y_coordinate', type=int)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE locations
        SET location_name = ?, location_type = ?, description = ?,
            x_coordinate = ?, y_coordinate = ?
        WHERE id = ?
    ''', (name, loc_type, desc, x, y, loc_id))
    conn.commit()

    # Regenerate QR code
    host_url = request.host_url.rstrip('/')
    qr_path = generate_location_qr(loc_id, name, base_url=host_url)
    cursor.execute('''
        INSERT INTO qr_codes (location_id, qr_image_path)
        VALUES (?, ?)
        ON CONFLICT(location_id) DO UPDATE SET qr_image_path=excluded.qr_image_path
    ''', (loc_id, qr_path))
    conn.commit()
    conn.close()

    flash(f'Location "{name}" updated and QR refreshed.', 'success')
    return redirect(url_for('manage_locations'))

@app.route('/admin/locations/delete/<int:loc_id>', methods=['POST'])
@login_required
def delete_location(loc_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM locations WHERE id = ?", (loc_id,))
    cursor.execute("DELETE FROM paths WHERE source_id = ? OR target_id = ?", (loc_id, loc_id))
    cursor.execute("DELETE FROM qr_codes WHERE location_id = ?", (loc_id,))
    conn.commit()
    conn.close()
    flash('Location and associated paths removed.', 'info')
    return redirect(url_for('manage_locations'))

@app.route('/qrcodes')
@app.route('/admin/qrcodes')
def generate_qr_page():
    """QR Code showcase, generator, and download gallery."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.id, l.location_name, l.location_type, l.description, q.qr_image_path, q.created_at
        FROM locations l
        LEFT JOIN qr_codes q ON l.id = q.location_id
        ORDER BY l.id ASC
    ''')
    qrs = cursor.fetchall()
    conn.close()
    return render_template('generate_qr.html', qrs=qrs)

@app.route('/admin/qrcodes/regenerate-all', methods=['POST'])
@login_required
def regenerate_all_qrs():
    host_url = request.host_url.rstrip('/')
    generate_all_qrcodes(base_url=host_url)
    flash('All airport QR codes regenerated with current host URL.', 'success')
    return redirect(url_for('generate_qr_page'))

@app.route('/download/qr/<int:location_id>')
def download_qr(location_id):
    """Allows downloading the airport location QR code as PNG image."""
    filename = f"qr_location_{location_id}.png"
    filepath = os.path.join(os.path.dirname(__file__), 'static', 'qrcodes', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename)
    flash('QR image file not found. Please regenerate it.', 'warning')
    return redirect(url_for('generate_qr_page'))

# ==================== REST APIS FOR FRONTEND / AJAX ====================
@app.route('/api/locations')
def api_locations():
    """Returns list of all airport locations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, location_name, location_type, description, x_coordinate, y_coordinate FROM locations")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/paths')
def api_paths():
    """Returns all graph paths with node coordinates for map drawing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.source_id, p.target_id, p.distance, p.direction_desc,
               s.x_coordinate as x1, s.y_coordinate as y1, s.location_name as src_name,
               t.x_coordinate as x2, t.y_coordinate as y2, t.location_name as dst_name
        FROM paths p
        JOIN locations s ON p.source_id = s.id
        JOIN locations t ON p.target_id = t.id
        WHERE p.source_id < p.target_id
    ''')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/flight/<flight_number>')
def api_flight_details(flight_number):
    """Returns details for a flight number."""
    f_num = flight_number.strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE flight_number = ?", (f_num,))
    flight = cursor.fetchone()

    if not flight:
        conn.close()
        return jsonify({'success': False, 'message': 'Flight not found.'}), 404

    # Also resolve destination location IDs for Check-in, Security, Gate
    loc_names = [flight['checkin_counter'], flight['security_checkpoint'], flight['boarding_gate']]
    placeholders = ','.join('?' * len(loc_names))
    cursor.execute(f"SELECT id, location_name, x_coordinate, y_coordinate FROM locations WHERE location_name IN ({placeholders})", loc_names)
    loc_map = {r['location_name']: dict(r) for r in cursor.fetchall()}
    conn.close()

    data = dict(flight)
    if not data.get('boarding_time') or not data.get('boarding_closes'):
        calc_start, calc_close = calculate_boarding_times(data.get('departure_time', ''))
        data['boarding_time'] = data.get('boarding_time') or calc_start
        data['boarding_closes'] = data.get('boarding_closes') or calc_close
    data['checkin_loc'] = loc_map.get(flight['checkin_counter'])
    data['security_loc'] = loc_map.get(flight['security_checkpoint'])
    data['gate_loc'] = loc_map.get(flight['boarding_gate'])

    return jsonify({'success': True, 'flight': data})

@app.route('/api/navigate', methods=['POST'])
def api_navigate():
    """
    Computes shortest path using Dijkstra algorithm.
    Request JSON: { "start_id": 1, "end_id": 12, "lang": "en", "flight": "AI202" }
    """
    data = request.get_json(silent=True) or {}
    start_id = data.get('start_id')
    end_id = data.get('end_id')
    lang = data.get('lang') or session.get('lang', 'en')
    flight_num = data.get('flight')

    if not start_id or not end_id:
        return jsonify({'success': False, 'message': 'Source and destination required.'}), 400

    route_details = generate_route_details(int(start_id), int(end_id), lang=lang)

    # Save to history
    if route_details.get('success'):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO navigation_history (flight_number, source_location, destination_location, distance, estimated_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                flight_num or 'N/A',
                route_details['start_node']['location_name'],
                route_details['end_node']['location_name'],
                route_details['total_distance'],
                route_details['estimated_time']
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving history: {e}")

    return jsonify(route_details)

@app.route('/api/check-checkpoint', methods=['POST'])
def api_check_checkpoint():
    """
    Wrong-turn detection and automatic route correction.
    Request JSON: {
        "scanned_loc_id": 4,
        "planned_path_ids": [1, 2, 3, 6, 8, 12],
        "destination_id": 12,
        "lang": "en"
    }
    """
    data = request.get_json(silent=True) or {}
    scanned_id = data.get('scanned_loc_id')
    planned_path_ids = data.get('planned_path_ids', [])
    destination_id = data.get('destination_id')
    lang = data.get('lang') or session.get('lang', 'en')

    if not scanned_id or not destination_id:
        return jsonify({'success': False, 'message': 'Missing parameters.'}), 400

    result = check_wrong_turn_and_reroute(scanned_id, planned_path_ids, destination_id, lang=lang)
    return jsonify(result)

@app.route('/api/flight-updates/<flight_number>')
def api_flight_updates(flight_number):
    """Polls flight for status or gate changes in real-time."""
    f_num = flight_number.strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE flight_number = ?", (f_num,))
    flight = cursor.fetchone()
    conn.close()

    if not flight:
        return jsonify({'found': False})

    return jsonify({
        'found': True,
        'flight_number': flight['flight_number'],
        'boarding_gate': flight['boarding_gate'],
        'status': flight['status'],
        'checkin_counter': flight['checkin_counter'],
        'security_checkpoint': flight['security_checkpoint']
    })

@app.route('/favicon.ico')
def favicon():
    return ('', 204)

if __name__ == '__main__':
    import sys
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    print(f"Starting Smart QR Guide Airport on http://127.0.0.1:{port}")
    # debug=False ensures stable execution without watchdog reloading standard library files
    app.run(host='0.0.0.0', port=port, debug=False)
