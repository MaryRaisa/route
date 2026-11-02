import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'airport.db')

def get_db_connection():
    """Returns a connection to the SQLite airport database with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_boarding_times(departure_time_str):
    """
    Computes boarding start time (40 mins prior) and gate closing time (20 mins prior)
    from a departure time string (e.g. '14:30').
    """
    try:
        parts = departure_time_str.strip().split(':')
        if len(parts) == 2:
            hour = int(parts[0])
            minute = int(parts[1])
            total_mins = hour * 60 + minute
            
            b_start_mins = (total_mins - 40) % (24 * 60)
            b_close_mins = (total_mins - 20) % (24 * 60)
            
            b_start = f"{b_start_mins // 60:02d}:{b_start_mins % 60:02d}"
            b_close = f"{b_close_mins // 60:02d}:{b_close_mins % 60:02d}"
            return b_start, b_close
    except Exception:
        pass
    return "40m before dep", "20m before dep"

def init_db():
    """Initializes database tables and creates schema."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin'
        )
    ''')

    # 2. locations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT UNIQUE NOT NULL,
            location_type TEXT NOT NULL,
            description TEXT,
            x_coordinate INTEGER NOT NULL,
            y_coordinate INTEGER NOT NULL
        )
    ''')

    # 3. paths/edges table for graph navigation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            distance INTEGER NOT NULL,
            direction_desc TEXT,
            FOREIGN KEY (source_id) REFERENCES locations (id) ON DELETE CASCADE,
            FOREIGN KEY (target_id) REFERENCES locations (id) ON DELETE CASCADE
        )
    ''')

    # 4. flights table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT UNIQUE NOT NULL,
            airline TEXT NOT NULL,
            destination_city TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            boarding_time TEXT,
            boarding_closes TEXT,
            checkin_counter TEXT NOT NULL,
            security_checkpoint TEXT NOT NULL,
            boarding_gate TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'On Time',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Migration check for existing databases
    cursor.execute("PRAGMA table_info(flights)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    if 'boarding_time' not in existing_cols:
        cursor.execute("ALTER TABLE flights ADD COLUMN boarding_time TEXT")
    if 'boarding_closes' not in existing_cols:
        cursor.execute("ALTER TABLE flights ADD COLUMN boarding_closes TEXT")

    # 5. qr_codes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER UNIQUE NOT NULL,
            qr_image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE
        )
    ''')

    # 6. navigation_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS navigation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT,
            source_location TEXT NOT NULL,
            destination_location TEXT NOT NULL,
            distance INTEGER NOT NULL,
            estimated_time REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def seed_initial_data():
    """Seeds the database with initial locations, walking graph paths, sample flights, and admin user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Seed Admin User
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123')
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       ('admin', hashed_pw, 'admin'))

    # Seed Locations
    initial_locations = [
        ("Main Entrance", "Entrance", "Terminal 2 Ground Floor Main Entrance & Drop-off Area", 100, 360),
        ("Info Desk", "Service", "Passenger Information, Special Assistance & Help Kiosk", 220, 360),
        ("Check-in Counter A", "Check-in", "Airline Check-in Island A (Rows 1-15)", 340, 240),
        ("Check-in Counter B", "Check-in", "Airline Check-in Island B (Rows 16-30)", 340, 480),
        ("Restroom A", "Restroom", "Restrooms & Baby Care near Entrance", 220, 180),
        ("Security Checkpoint 1", "Security", "Security Screening Zone 1 (Gates A Concourse)", 490, 250),
        ("Security Checkpoint 2", "Security", "Security Screening Zone 2 (Gates B Concourse)", 490, 470),
        ("Central Waiting Lounge", "Lounge", "Passenger Waiting Concourse & Duty Free Area", 660, 360),
        ("Food Court", "Amenities", "Dining Terrace, Cafes & Quick Bites", 660, 180),
        ("Restroom B", "Restroom", "Restrooms & Water Station near Concourse", 660, 530),
        ("Boarding Gate A1", "Gate", "Domestic Departure Gate A1", 860, 180),
        ("Boarding Gate A5", "Gate", "International Departure Gate A5", 860, 290),
        ("Boarding Gate B1", "Gate", "Departure Gate B1", 860, 430),
        ("Boarding Gate B5", "Gate", "Departure Gate B5", 860, 540),
        ("Baggage Claim", "Baggage", "Arrivals Baggage Carousels 1 to 4", 360, 620),
        ("Terminal Exit", "Exit", "Exit to Taxi Stand, Metro & Parking", 100, 620)
    ]

    for name, loc_type, desc, x, y in initial_locations:
        cursor.execute("SELECT id FROM locations WHERE location_name = ?", (name,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO locations (location_name, location_type, description, x_coordinate, y_coordinate)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, loc_type, desc, x, y))

    conn.commit()

    # Build Map of location_name -> ID
    cursor.execute("SELECT id, location_name FROM locations")
    loc_map = {row['location_name']: row['id'] for row in cursor.fetchall()}

    # Graph Edges (undirected walking paths with distance in meters)
    walking_paths = [
        ("Main Entrance", "Info Desk", 45, "Walk straight ahead towards Information Desk"),
        ("Info Desk", "Check-in Counter A", 55, "Head towards Check-in Island A on your left"),
        ("Info Desk", "Check-in Counter B", 55, "Head towards Check-in Island B on your right"),
        ("Info Desk", "Restroom A", 40, "Take the walkway towards Restrooms near Entrance"),
        ("Check-in Counter A", "Security Checkpoint 1", 70, "Proceed straight forward to Security Checkpoint 1"),
        ("Check-in Counter B", "Security Checkpoint 2", 70, "Proceed straight forward to Security Checkpoint 2"),
        ("Security Checkpoint 1", "Central Waiting Lounge", 80, "Pass through screening and enter Central Lounge"),
        ("Security Checkpoint 2", "Central Waiting Lounge", 80, "Pass through screening and enter Central Lounge"),
        ("Central Waiting Lounge", "Food Court", 60, "Take the escalator/concourse towards Food Court"),
        ("Central Waiting Lounge", "Restroom B", 50, "Walk south along the corridor towards Restrooms"),
        ("Central Waiting Lounge", "Boarding Gate A5", 85, "Follow Concourse A signs towards Gate A5"),
        ("Central Waiting Lounge", "Boarding Gate B1", 85, "Follow Concourse B signs towards Gate B1"),
        ("Food Court", "Boarding Gate A1", 75, "Follow corridor from Food Court towards Gate A1"),
        ("Boarding Gate A1", "Boarding Gate A5", 50, "Walk along Concourse A wing"),
        ("Boarding Gate B1", "Boarding Gate B5", 50, "Walk along Concourse B wing"),
        ("Restroom B", "Boarding Gate B5", 65, "Proceed along corridor towards Gate B5"),
        ("Check-in Counter B", "Baggage Claim", 80, "Take ground access path towards Baggage Claim"),
        ("Security Checkpoint 2", "Baggage Claim", 95, "Take connecting corridor towards Baggage Claim"),
        ("Baggage Claim", "Terminal Exit", 90, "Walk towards Terminal Exit and Ground Transportation")
    ]

    # Insert paths (both directions for undirected graph)
    cursor.execute("SELECT COUNT(*) as cnt FROM paths")
    if cursor.fetchone()['cnt'] == 0:
        for src, dst, dist, desc in walking_paths:
            if src in loc_map and dst in loc_map:
                s_id, d_id = loc_map[src], loc_map[dst]
                cursor.execute('''
                    INSERT INTO paths (source_id, target_id, distance, direction_desc)
                    VALUES (?, ?, ?, ?)
                ''', (s_id, d_id, dist, desc))
                # Add reverse edge
                cursor.execute('''
                    INSERT INTO paths (source_id, target_id, distance, direction_desc)
                    VALUES (?, ?, ?, ?)
                ''', (d_id, s_id, dist, f"Proceed towards {src}"))

    # Seed Sample Flights
    sample_flights = [
        ("AI202", "Air India", "London (LHR)", "14:30", "13:50", "14:10", "Check-in Counter A", "Security Checkpoint 1", "Boarding Gate A5", "On Time"),
        ("6E305", "IndiGo", "Dubai (DXB)", "15:45", "15:05", "15:25", "Check-in Counter B", "Security Checkpoint 2", "Boarding Gate B1", "Boarding"),
        ("UK819", "Vistara", "Singapore (SIN)", "16:15", "15:35", "15:55", "Check-in Counter A", "Security Checkpoint 1", "Boarding Gate A1", "Gate Changed"),
        ("EK501", "Emirates", "New York (JFK)", "17:00", "16:20", "16:40", "Check-in Counter B", "Security Checkpoint 2", "Boarding Gate B5", "On Time"),
        ("BA138", "British Airways", "Frankfurt (FRA)", "18:20", "17:40", "18:00", "Check-in Counter A", "Security Checkpoint 1", "Boarding Gate A5", "Delayed"),
        ("QP1102", "Akasa Air", "Mumbai (BOM)", "19:10", "18:30", "18:50", "Check-in Counter B", "Security Checkpoint 2", "Boarding Gate B1", "Scheduled")
    ]

    for f_num, airline, dest, dept, b_start, b_close, checkin, sec, gate, status in sample_flights:
        cursor.execute("SELECT id FROM flights WHERE flight_number = ?", (f_num,))
        row = cursor.fetchone()
        if not row:
            cursor.execute('''
                INSERT INTO flights (flight_number, airline, destination_city, departure_time,
                                     boarding_time, boarding_closes,
                                     checkin_counter, security_checkpoint, boarding_gate, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f_num, airline, dest, dept, b_start, b_close, checkin, sec, gate, status))
        else:
            # Update missing boarding details if row exists
            cursor.execute('''
                UPDATE flights 
                SET boarding_time = COALESCE(boarding_time, ?),
                    boarding_closes = COALESCE(boarding_closes, ?)
                WHERE id = ?
            ''', (b_start, b_close, row['id']))

    # Backfill any other custom flights that may have null boarding details
    cursor.execute("SELECT id, departure_time, boarding_time, boarding_closes FROM flights WHERE boarding_time IS NULL OR boarding_closes IS NULL")
    for r in cursor.fetchall():
        calc_start, calc_close = calculate_boarding_times(r['departure_time'])
        cursor.execute('''
            UPDATE flights
            SET boarding_time = COALESCE(boarding_time, ?),
                boarding_closes = COALESCE(boarding_closes, ?)
            WHERE id = ?
        ''', (calc_start, calc_close, r['id']))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    seed_initial_data()
    print("Airport database initialized and seeded successfully.")
