import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_callout(doc, text, title="NOTE"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run_title = p.add_run(f"📌 {title}: ")
    run_title.bold = True
    run_title.font.color.rgb = RGBColor(11, 25, 44) # Navy
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(10.5)
    
    run_text = p.add_run(text)
    run_text.font.color.rgb = RGBColor(51, 65, 85)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(10.5)
    
    # Border
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="00A8FF"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_docx():
    doc = Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Set default style font
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)
    normal_style.paragraph_format.line_spacing = 1.2
    normal_style.paragraph_format.space_after = Pt(6)

    # ----------------- TITLE SECTION -----------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(6)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title_p.add_run("SMART QR GUIDE AIRPORT ✈️")
    r_title.bold = True
    r_title.font.size = Pt(26)
    r_title.font.color.rgb = RGBColor(11, 25, 44) # Navy
    
    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(10)
    r_sub = sub_p.add_run("Comprehensive System Architecture, Technical Implementation & Operational Working Guide")
    r_sub.font.size = Pt(13)
    r_sub.italic = True
    r_sub.font.color.rgb = RGBColor(0, 168, 255) # Aero Blue
    
    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_p.paragraph_format.space_after = Pt(24)
    r_meta = meta_p.add_run("Indoor Positioning • Dijkstra Graph Navigation • Trilingual Audio Guidance • Live Gate Rerouting\nDocument Version 2.0 | Full-Stack Web Application Technical Report")
    r_meta.font.size = Pt(9.5)
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    
    doc.add_heading("1. Executive Summary", level=1)
    doc.paragraphs[-1].paragraph_format.space_before = Pt(12)
    
    doc.add_paragraph(
        "Modern international and domestic airport terminals are massive, multi-level architectural structures designed to accommodate "
        "tens of millions of passengers annually. However, navigating through terminals remains one of the most stressful aspects of air travel. "
        "Traditional indoor navigation solutions suffer from significant technical limitations: Global Positioning System (GPS) signals cannot "
        "penetrate concrete and steel terminal roofs, while hardware-heavy solutions such as Bluetooth Low Energy (BLE) beacons or RFID readers "
        "incur massive capital expenditure, battery maintenance, and force passengers to download specialized native mobile applications."
    )
    
    doc.add_paragraph(
        "The SMART QR GUIDE AIRPORT project solves this problem through an elegant, infrastructure-light, zero-install web application. "
        "By placing standardized, high-contrast, branded QR codes at physical checkpoints across the terminal (entrances, check-in desks, security zones, "
        "lounges, gates, restrooms, and baggage claims), passengers simply scan any QR code using their standard smartphone camera. The system instantly "
        "identifies their precise physical location, retrieves flight itinerary details, calculates the mathematically optimal shortest walking path using "
        "Dijkstra's graph algorithm, renders an interactive SVG indoor map, provides turn-by-turn multilingual voice guidance (English, Tamil, Hindi), "
        "and automatically corrects wrong turns and gate changes in real time."
    )

    add_callout(doc, 
        "The core innovation lies in combining physical QR checkpoint anchoring with mathematical graph theory and client-side web technologies, "
        "providing centimeter-accurate indoor localization without requiring GPS, Bluetooth hardware, or native app installations.",
        "Key Value Proposition"
    )

    # ----------------- SECTION 2: PROBLEM STATEMENT & MOTIVATION -----------------
    doc.add_heading("2. Problem Statement & Motivation", level=1)
    
    doc.add_paragraph(
        "Navigating modern airport environments poses significant hurdles for diverse passenger demographics, especially first-time travelers, "
        "elderly passengers, and non-native language speakers. The specific challenges addressed by this system include:"
    )
    
    challenges = [
        ("Indoor GPS Blind Zones", "Satellite-based GPS signals degrade or completely vanish indoors, rendering Google Maps and Apple Maps ineffective inside airport concourses."),
        ("Physical Signage Limitations", "Static signs are often crowded, positioned high overhead, only available in limited languages, and cannot provide customized paths based on a passenger's individual flight status."),
        ("App Fatigue & Barrier to Entry", "Passengers are reluctant to download and configure a proprietary 100MB+ mobile app for a one-time transit through an airport."),
        ("Dynamic Airport Disruptions", "Flight gates frequently change at the last minute due to aircraft turnaround delays. Passengers already walking towards an outdated gate often miss auditory terminal announcements."),
        ("Language and Accessibility Barriers", "International airports cater to multilingual passengers. Lack of real-time audio guidance in local and regional languages creates confusion and missed flights.")
    ]
    
    for title, desc in challenges:
        p = doc.add_paragraph(style='List Bullet')
        r1 = p.add_run(f"{title}: ")
        r1.bold = True
        r1.font.color.rgb = RGBColor(11, 25, 44)
        p.add_run(desc)

    # ----------------- SECTION 3: SYSTEM ARCHITECTURE -----------------
    doc.add_heading("3. End-to-End System Architecture", level=1)
    
    doc.add_paragraph(
        "The application follows a clean, decoupled 3-tier client-server architecture built on Python Flask, SQLite, and modern web standards. "
        "The interaction between passenger devices, physical checkpoints, server endpoints, and administrative control is organized as follows:"
    )
    
    # Architecture Table
    arch_table = doc.add_table(rows=5, cols=3)
    arch_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Architecture Layer", "Primary Components & Technologies", "Responsibilities & Functions"]
    
    for i, h in enumerate(headers):
        cell = arch_table.cell(0, i)
        set_cell_background(cell, "0B192C")
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.size = Pt(10)
        
    arch_data = [
        ("Presentation Layer (Client-Side)", "HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, HTML5-QRCode, Web Speech Synthesis API, SVG Canvas", "Renders responsive passenger dashboard, accesses camera feed for live QR scanning, renders interactive dynamic vector indoor maps, plays multilingual voice guidance, and polls for gate changes."),
        ("Application & Logic Layer (Backend)", "Python 3.x, Flask Framework, Jinja2 Template Engine, Werkzeug Security, Priority Queue (heapq), Python qrcode & Pillow (PIL)", "Handles HTTP requests, session authentication, Dijkstra pathfinding calculations, wrong-turn rerouting logic, trilingual localization translation injection, and branded QR code image generation."),
        ("Data Persistence Layer (Database)", "SQLite 3 (database/airport.db), Relational Schema, ACID Transactions, Foreign Key Constraints", "Stores airport locations with (X,Y) coordinates, walkable hallway graph edges, real-time flight records, generated QR code image paths, user accounts, and navigational audit history logs."),
        ("Physical Hardware Layer (Terminal)", "Branded Airport QR Plaques / Posters, Smartphone Cameras (iOS & Android)", "Physical anchoring points distributed at entrance doors, ticketing desks, security checkpoints, concourses, gates, and baggage carousels. Scanned via standard device optical cameras.")
    ]
    
    for row_idx, data in enumerate(arch_data, start=1):
        for col_idx, text in enumerate(data):
            cell = arch_table.cell(row_idx, col_idx)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(text)
            run.font.size = Pt(9.5)
            if col_idx == 0:
                run.bold = True
                run.font.color.rgb = RGBColor(11, 25, 44)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ----------------- SECTION 4: STEP-BY-STEP WORKING WORKFLOW -----------------
    doc.add_heading("4. Comprehensive Operational Workflow (How It Works)", level=1)
    
    doc.add_paragraph(
        "The complete lifecycle of the Smart QR Guide Airport system is divided into four distinct phases: "
        "Physical Checkpoint Deployment, Passenger Journey Initiation, Active Graph Navigation, and Real-Time Event Handling."
    )
    
    doc.add_heading("Phase 1: Physical Checkpoint Deployment & QR Tagging", level=2)
    doc.add_paragraph(
        "1. Airport administrators map all key functional locations within the terminal in the Admin Portal (e.g., Main Entrance, Check-in Counter A, Security Checkpoint 1, Boarding Gate A5).\n"
        "2. For each location, administrators assign an (X, Y) coordinate representing its spatial position on the 1000x720 indoor floor plan canvas.\n"
        "3. The system's QR Engine (Python qrcode + Pillow) automatically synthesizes a high-resolution, branded airport QR code. "
        "The QR code payload contains a web URL embedding the checkpoint ID (e.g., http://<airport-domain>/scan?loc_id=1).\n"
        "4. These QR codes are printed and mounted on physical stands, pillars, and information kiosks at the corresponding airport locations."
    )
    
    doc.add_heading("Phase 2: Passenger Journey Initiation & Scanning", level=2)
    doc.add_paragraph(
        "1. When a passenger arrives at the terminal, they scan the nearest QR code using either their smartphone camera or the web app's built-in camera scanner (powered by Html5Qrcode).\n"
        "2. The scanned payload instantly resolves on the server, establishing the passenger's exact physical starting node without manual search.\n"
        "3. The passenger enters their flight number (e.g., 'AI202'). The backend retrieves the flight details: airline, destination, assigned check-in counter, security screening gate, and boarding gate.\n"
        "4. The Passenger Dashboard presents a customized, 3-stage milestone itinerary:\n"
        "   • Stage 1: Entrance / Current Position ➔ Assigned Check-in Counter\n"
        "   • Stage 2: Check-in Counter ➔ Security Screening Checkpoint\n"
        "   • Stage 3: Security Screening ➔ Boarding Gate\n"
        "   • Quick Facility Links: Immediate shortest-path routing to Restrooms, Food Court, or Baggage Claim."
    )

    doc.add_heading("Phase 3: Shortest Path Calculation & Interactive Guidance", level=2)
    doc.add_paragraph(
        "1. Upon selecting a destination milestone, the frontend issues an asynchronous POST request to /api/navigate with start_id, end_id, language, and flight_number.\n"
        "2. The Dijkstra Pathfinding Engine in navigation.py builds an in-memory weighted adjacency graph from the database paths table and determines the minimal walking distance path.\n"
        "3. The engine computes the total distance in metres and estimates walking time based on the standardized human airport walking velocity (~75 metres per minute).\n"
        "4. The backend constructs trilingual step-by-step turn directions ('Start from Main Entrance', 'Walk 85 metres towards Info Desk', 'Arrive at Boarding Gate A5').\n"
        "5. The interactive SVG floor plan visually draws the path: active hallway corridors glow in vibrant blue (#00A8FF), the starting point pulses with an animated radar circle, intermediate checkpoints appear as numbered nodes, and the destination displays a targeted map pin.\n"
        "6. If enabled, the HTML5 Web Speech Synthesis API vocalizes each turn-by-turn instruction in the passenger's selected language (English en-US, Tamil ta-IN, Hindi hi-IN)."
    )

    doc.add_heading("Phase 4: Wrong-Turn Detection & Live Gate Recalculation", level=2)
    doc.add_paragraph(
        "1. Wrong-Turn Detection: While walking, if a passenger scans another QR checkpoint along a corridor, the system checks whether the scanned location ID exists within the active planned path sequence.\n"
        "   • If the checkpoint is not on the route, a wrong-turn state is flagged.\n"
        "   • An audio-visual alert triggers: 'You have moved away from your planned route. A new route has been calculated.'\n"
        "   • The system seamlessly re-runs Dijkstra's algorithm using the newly scanned position as the new origin, immediately re-drawing the corrected path on the map.\n"
        "2. Live Gate Change Broadcasting: If airport operations modify a flight's gate in the Admin Portal (e.g., Gate A5 changed to Gate B1):\n"
        "   • The passenger's browser polls /api/flight-updates/<flight_number> periodically.\n"
        "   • Upon detecting a change, an emergency warning banner pops up, an audio voice announcement warns the passenger, and a single click automatically recalculates the route to the new gate."
    )

    # ----------------- SECTION 5: MATHEMATICAL & ALGORITHMIC FOUNDATION -----------------
    doc.add_heading("5. Mathematical & Algorithmic Foundation: Dijkstra Shortest Path", level=1)
    
    doc.add_paragraph(
        "Indoor airport navigation cannot rely on simple Euclidean (straight-line) distance because passengers must navigate along physical corridors, "
        "around walls, through designated security checkpoints, and across concourses. The terminal is therefore modeled as a weighted, undirected graph G = (V, E)."
    )
    
    doc.add_paragraph(
        "• Vertices (V): The set of discrete physical locations, checkpoints, intersections, and gates.\n"
        "• Edges (E): The walkable corridors connecting two adjacent locations, where each edge e = (u, v) has a non-negative weight w(u, v) representing actual walking distance in metres.\n"
        "• Min-Heap Priority Queue: The algorithm utilizes Python's heapq module to achieve optimal asymptotic time complexity of O((|V| + |E|) log |V|)."
    )
    
    add_callout(doc,
        "Walking Time Formula: Time (minutes) = max(1.0, round(Total Distance (m) / 75.0, 1))\n"
        "Average human indoor walking speed is approximately 1.25 to 1.3 m/s (~75 metres per minute). A lower bound of 1.0 minute is enforced for non-zero distances.",
        "Walking Duration Calibration"
    )

    # ----------------- SECTION 6: DETAILED TECHNOLOGY STACK -----------------
    doc.add_heading("6. Deep Dive into the Technology Stack", level=1)
    
    doc.add_paragraph(
        "Every layer of the Smart QR Guide Airport stack has been chosen for speed, zero-install accessibility, reliability, and ease of deployment. "
        "The complete technical composition is detailed below:"
    )

    tech_table = doc.add_table(rows=8, cols=3)
    tech_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tech_headers = ["Category", "Technology / Library", "Role & Technical Justification"]
    
    for i, h in enumerate(tech_headers):
        cell = tech_table.cell(0, i)
        set_cell_background(cell, "0B192C")
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.size = Pt(10)

    tech_data = [
        ("Backend Web Engine", "Python Flask 3.x", "Lightweight, WSGI-compliant micro-framework with negligible overhead. Handles REST APIs, Jinja2 template rendering, session cookies, and route dispatching."),
        ("Database & Storage", "SQLite 3", "Serverless, zero-configuration ACID relational database embedded directly in the application. Fast reads, zero network latency, and seamless portability across Windows and Linux environments."),
        ("QR Code Synthesis", "Python qrcode 8.x & Pillow (PIL)", "Generates high-contrast QR matrices with Error Correction Level H (allowing up to 30% damage recovery). Pillow composite canvas adds navy branding header, checkpoint ID, and typography."),
        ("Client QR Scanner", "html5-qrcode (JS Library)", "Cross-platform browser-based QR scanner using MediaDevices.getUserMedia(). Enables real-time camera scanning on iOS Safari, Android Chrome, and laptops without native apps."),
        ("Vector Indoor Mapping", "Dynamic SVG (Scalable Vector Graphics)", "Renders sharp, responsive architectural floor plans directly in the browser DOM. Allows dynamic CSS animations, glowing path strokes, pulsing radar markers, and interactive node tooltips without heavy WebGL engines."),
        ("Audio Voice Guidance", "HTML5 Web Speech Synthesis API", "Provides native, client-side text-to-speech synthesis without consuming external paid cloud TTS APIs. Maps to regional voice models: en-US, ta-IN, and hi-IN."),
        ("Styling & UI Design", "Vanilla CSS3, Bootstrap 5.3, Bootstrap Icons", "Aero-themed UI with deep navy (#0B192C), vibrant cyan accents (#00A8FF), glassmorphic cards, responsive flex layouts, and custom accessibility-focused contrast ratios.")
    ]

    for row_idx, data in enumerate(tech_data, start=1):
        for col_idx, text in enumerate(data):
            cell = tech_table.cell(row_idx, col_idx)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(text)
            run.font.size = Pt(9.5)
            if col_idx == 0:
                run.bold = True
                run.font.color.rgb = RGBColor(11, 25, 44)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ----------------- SECTION 7: DATABASE SCHEMA & RELATIONAL MODEL -----------------
    doc.add_heading("7. Database Schema & Data Models", level=1)
    
    doc.add_paragraph(
        "The relational database schema is designed in 3rd Normal Form (3NF) to ensure integrity, referential consistency, and rapid query response:"
    )
    
    schema_items = [
        ("users", "Stores administrative credentials. Fields: id (PK), username (UNIQUE), password_hash (Werkzeug pbkdf2:sha256), role ('admin')."),
        ("locations", "Defines all physical terminal nodes. Fields: id (PK), location_name (UNIQUE), location_type ('Entrance', 'Checkin', 'Security', 'Gate', 'Facility'), description, x_coordinate, y_coordinate."),
        ("paths", "Defines graph corridors/edges connecting nodes. Fields: id (PK), source_id (FK -> locations.id), target_id (FK -> locations.id), distance (metres), direction_desc (walkway notes)."),
        ("flights", "Stores dynamic flight departure schedule. Fields: id (PK), flight_number (UNIQUE), airline, destination_city, departure_time, checkin_counter, security_checkpoint, boarding_gate, status ('On Time', 'Delayed', 'Gate Changed'), updated_at."),
        ("qr_codes", "Maintains generated QR image references. Fields: id (PK), location_id (FK -> locations.id, UNIQUE), qr_image_path (static/qrcodes/qr_location_X.png), created_at."),
        ("navigation_history", "Audit logging table tracking passenger usage and route queries. Fields: id (PK), flight_number, source_location, destination_location, distance, estimated_time, created_at.")
    ]
    
    for tbl, desc in schema_items:
        p = doc.add_paragraph(style='List Bullet')
        r = p.add_run(f"Table '{tbl}': ")
        r.bold = True
        r.font.color.rgb = RGBColor(11, 25, 44)
        p.add_run(desc)

    # ----------------- SECTION 8: TRILINGUAL LOCALIZATION & ACCESSIBILITY -----------------
    doc.add_heading("8. Trilingual Localization & Accessibility", level=1)
    doc.add_paragraph(
        "To ensure accessibility for both domestic Indian passengers and international travelers, the application features an integrated, "
        "session-persistent translation engine supporting English (en), Tamil (ta), and Hindi (hi). "
        "The translation engine operates on three synchronized levels:\n"
        "1. UI Strings & System Controls: Navigation bars, buttons, milestone badges, and modal prompts.\n"
        "2. Terminal Location Names: All 16+ airport checkpoints are translated into native scripts (e.g., 'Main Entrance' -> 'முக்கிய நுழைவாயில்' -> 'मुख्य प्रवेश द्वार').\n"
        "3. Turn-by-Turn Dynamic Templates: Navigation instructions dynamically interpolate translated location names and calculated walking distances."
    )

    # ----------------- SECTION 9: ADMIN CONTROL & SECURITY -----------------
    doc.add_heading("9. Administration Portal, Security & Operations", level=1)
    doc.add_paragraph(
        "Airport staff access a dedicated management suite via /admin/login protected by cryptographic password hashing (pbkdf2:sha256) and session cookies. "
        "Key administrative functions include:\n"
        "• Operational Dashboard: Real-time statistics displaying total locations, active QR codes, scheduled flights, and total routes navigated.\n"
        "• Flight Schedule Management: Add, edit, or delete scheduled flights. Modifying a boarding gate automatically flags status as 'Gate Changed' and triggers passenger rerouting.\n"
        "• Location & Coordinate Mapper: Add new terminal checkpoints and set their (X,Y) indoor map coordinates. The system automatically creates a branded QR code.\n"
        "• QR Code Download Center: Printable gallery allowing staff to download high-resolution PNG badges for physical printing and installation."
    )

    # ----------------- SECTION 10: COMPARISON WITH ALTERNATIVE TECHNOLOGIES -----------------
    doc.add_heading("10. Comparison: Smart QR vs. Traditional Indoor Positioning", level=1)
    
    comp_table = doc.add_table(rows=5, cols=4)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    comp_headers = ["Evaluation Metric", "Smart QR Guide (This Project)", "BLE Beacons (Bluetooth)", "RFID Floor Tags"]
    
    for i, h in enumerate(comp_headers):
        cell = comp_table.cell(0, i)
        set_cell_background(cell, "0B192C")
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.size = Pt(10)

    comp_data = [
        ("Installation Cost", "Near Zero ($0 hardware, simple printouts)", "High ($20 - $50 per beacon, thousands required)", "Very High (requires specialized RFID floor readers)"),
        ("Maintenance & Power", "Zero maintenance, no batteries or power wiring", "High (battery replacements every 1-2 years)", "Moderate (reader maintenance, sensor wear)"),
        ("Passenger Barrier to Entry", "Zero install (works in standard web browser)", "High (requires custom native app & Bluetooth ON)", "Requires dedicated handheld terminal or tags"),
        ("Indoor Accuracy", "100% exact (physical checkpoint confirmation)", "Fluctuates (signal interference & multipath fading)", "Exact, but limited reading range")
    ]

    for row_idx, data in enumerate(comp_data, start=1):
        for col_idx, text in enumerate(data):
            cell = comp_table.cell(row_idx, col_idx)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(text)
            run.font.size = Pt(9.5)
            if col_idx == 0:
                run.bold = True
                run.font.color.rgb = RGBColor(11, 25, 44)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ----------------- SECTION 11: CONCLUSION -----------------
    doc.add_heading("11. Conclusion & Future Scope", level=1)
    doc.add_paragraph(
        "The SMART QR GUIDE AIRPORT project demonstrates that intelligent software architecture and mathematical optimization can overcome "
        "costly hardware barriers in indoor airport navigation. By combining physical QR checkpoints, graph theory (Dijkstra algorithm), "
        "vector SVG rendering, and browser-native voice synthesis, the system delivers a seamless, accessible passenger experience."
    )
    doc.add_paragraph(
        "Future enhancements may include integration with airport flight information display systems (AODB/FIDS) via WebSockets, "
        "Augmented Reality (AR) camera overlays for arrows projected onto physical corridors, and crowd-density congestion avoidance algorithms."
    )

    # Save document
    output_filename = "SMART_QR_AIRPORT_PROJECT_REPORT.docx"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == '__main__':
    build_docx()
