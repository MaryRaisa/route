# SMART QR GUIDE AIRPORT ✈️
### A Smart QR-Based Airport Navigation & Passenger Guidance System

🌐 **Live Deployed Application (Render):** [https://smart-qr-airport.onrender.com](https://smart-qr-airport.onrender.com)  
*(Backup PythonAnywhere: [https://maryraisap.pythonanywhere.com/](https://maryraisap.pythonanywhere.com/))*

A complete full-stack web application designed for modern airport terminals. The system enables passengers to navigate seamlessly from terminal entrance to boarding gate using QR codes scanned via their smartphones, with interactive indoor maps, Dijkstra shortest-path calculations, multilingual guidance (English, Tamil, Hindi), voice directions, gate change notifications, and automatic wrong-turn route correction.

---

## 🌟 Key Features

1. **Passenger Dashboard & Itinerary Planning**
   - Personalized flight-specific guidance (`AI202`, `6E305`, `UK819`, `EK501`, etc.).
   - 3-step sequential journey: **Check-in Counter ➡️ Security Screening ➡️ Boarding Gate**.
   - Immediate facility finder for Restrooms, Food Court, Waiting Lounge, and Baggage Claim.

2. **Airport QR Code Generation & Scanning**
   - High-resolution, airport-branded QR code generator using Python `qrcode` and `Pillow`.
   - Real-time device camera scanning powered by `Html5Qrcode` with reticle overlay.
   - Camera fallback with manual location selection and 1-click demonstration simulation buttons.

3. **Graph-Based Indoor Navigation (Dijkstra Algorithm)**
   - Terminal locations modeled as graph nodes and walking corridors as weighted edges.
   - Computes the shortest walking distance (in metres) and estimated walking time (in minutes).
   - Dynamic SVG terminal floor plan with highlighted paths, pulsing origin markers, and target pins.

4. **Trilingual Multilingual Guidance**
   - **English (EN)**
   - **தமிழ் - Tamil (TA)**
   - **हिंदी - Hindi (HI)**
   - Instant language switching across all turn-by-turn directions, banners, buttons, and facility names.

5. **Audio Voice Guidance (Web Speech API)**
   - Spoken turn-by-turn audio directions in English (`en-US`), Tamil (`ta-IN`), and Hindi (`hi-IN`).
   - Interactive Play, Pause, Resume, and Stop audio controls.

6. **Wrong-Turn Detection & Automatic Rerouting**
   - Indoor tracking via QR checkpoint scanning.
   - When a passenger scans a checkpoint outside the planned route, the system alerts:
     * *English:* "You have moved away from your planned route. A new route has been calculated."
     * *Tamil:* "நீங்கள் திட்டமிடப்பட்ட பாதையிலிருந்து விலகிவிட்டீர்கள். புதிய பாதை கணக்கிடப்பட்டுள்ளது."
     * *Hindi:* "आप अपने नियोजित मार्ग से भटक गए हैं। एक नया मार्ग निर्धारित किया गया है।"
   - Automatically recalculates and animates the new shortest path from the scanned checkpoint.

7. **Live Gate Change Updates**
   - Airport admin can change flight boarding gates in real-time.
   - Active passengers receive an immediate live audio-visual notification banner.
   - 1-click automatic route recalculation to the newly assigned gate.

8. **Admin Operations & CRUD Management**
   - Secure staff login portal (`admin` / `admin123`).
   - Complete flight management: Add, edit, delete, and modify gate assignments.
   - Location & terminal checkpoint management with (X, Y) coordinate mapping.
   - Printable QR Code gallery with individual PNG downloads.

---

## 🏗️ Technology Stack

- **Backend:** Python Flask 3.x
- **Database:** SQLite 3 (`database/airport.db`)
- **QR Engine:** Python `qrcode 8.x` & `Pillow`
- **Frontend:** HTML5, CSS3, JavaScript (ES6), Bootstrap 5.3, Bootstrap Icons
- **Indoor Mapping:** Interactive SVG Floor Plan Canvas & Graph Visualizer
- **Voice Synthesis:** HTML5 Web Speech Synthesis API
- **QR Scanner:** `html5-qrcode` JavaScript library

---

## 📁 Project Folder Structure

```
smart_qr_airport/
│
├── app.py                     # Main Flask web application and REST API endpoints
├── database.py                # Database connection, SQLite schema, and seeding
├── navigation.py              # Dijkstra shortest-path engine and translations
├── qr_generator.py            # Branded airport QR code generator
├── requirements.txt           # Python dependencies
│
├── database/
│   └── airport.db             # SQLite database storing users, flights, locations, paths
│
├── static/
│   ├── css/
│   │   └── style.css          # Airport design system (Navy/White/Aero Blue)
│   ├── js/
│   │   └── script.js          # SVG map rendering, voice synthesis, live polling
│   └── qrcodes/               # Generated high-resolution location QR PNGs
│
├── templates/
│   ├── base.html              # Shared layout, navbar, language selector & footer
│   ├── index.html             # Home landing page with hero search & map preview
│   ├── passenger.html         # Passenger dashboard with flight milestones
│   ├── scanner.html           # Live camera scanner and checkpoint simulator
│   ├── flight.html            # Flight search and departure schedule board
│   ├── navigation.html        # Interactive Dijkstra map, voice & wrong-turn simulator
│   ├── admin_login.html       # Staff login portal
│   ├── admin_dashboard.html   # Metrics, flight operations & audit logs
│   ├── manage_flights.html    # Add/Edit flights & gate change broadcaster
│   ├── manage_locations.html  # Location coordinates and QR linking
│   └── generate_qr.html       # Printable QR code gallery and download center
│
└── README.md                  # Complete documentation and execution guide
```

---

## 🚀 Installation & Running on Windows

### Step 1: Open Terminal / PowerShell
Navigate to the project directory:
```powershell
cd c:\Users\Lenovo\OneDrive\Desktop\rfid
```

### Step 2: Install Required Python Packages
```powershell
pip install -r requirements.txt
```

### Step 3: Initialize Database & Generate QR Codes
*(Note: Initialized automatically on first start, but you can run directly):*
```powershell
python database.py
python qr_generator.py
```

### Step 4: Start the Flask Application
```powershell
python app.py
```

### Step 5: Open in Your Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔐 Demonstration Credentials & Sample Data

### Admin Login Credentials:
- **URL:** `http://127.0.0.1:5000/admin/login`
- **Username:** `admin`
- **Password:** `admin123`

### Sample Flight Numbers for Testing:
| Flight Number | Airline | Destination | Dep Time | Boarding Starts | Gate Closes | Check-in | Security | Boarding Gate | Status |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **AI202** | Air India | London (LHR) | 14:30 | 13:50 | 14:10 | Check-in Counter A | Security Checkpoint 1 | Boarding Gate A5 | On Time |
| **6E305** | IndiGo | Dubai (DXB) | 15:45 | 15:05 | 15:25 | Check-in Counter B | Security Checkpoint 2 | Boarding Gate B1 | Boarding |
| **UK819** | Vistara | Singapore (SIN) | 16:15 | 15:35 | 15:55 | Check-in Counter A | Security Checkpoint 1 | Boarding Gate A1 | Gate Changed |
| **EK501** | Emirates | New York (JFK) | 17:00 | 16:20 | 16:40 | Check-in Counter B | Security Checkpoint 2 | Boarding Gate B5 | On Time |
| **BA138** | British Airways | Frankfurt (FRA) | 18:20 | 17:40 | 18:00 | Check-in Counter A | Security Checkpoint 1 | Boarding Gate A5 | Delayed |
| **QP1102** | Akasa Air | Mumbai (BOM) | 19:10 | 18:30 | 18:50 | Check-in Counter B | Security Checkpoint 2 | Boarding Gate B1 | Scheduled |

---

## 🧪 How to Demonstrate for Mini-Project Evaluation

1. **Home Page & Passenger Search:**
   - Go to `http://127.0.0.1:5000`.
   - Enter flight `AI202` and click **Guide Me**.
   - Notice the passenger dashboard displays Check-in Counter A, Security Zone 1, and Gate A5.

2. **Dijkstra Shortest Path Navigation:**
   - Click **Full Journey Navigation** or visit `http://127.0.0.1:5000/navigation?flight=AI202`.
   - Watch the animated cyan path calculated by Dijkstra's algorithm.
   - Check total distance (e.g. `280 metres`) and walking time (`3.7 mins`).

3. **Multilingual & Voice Guidance:**
   - Click the language selector at the top right to switch between **English**, **தமிழ் (Tamil)**, and **हिंदी (Hindi)**.
   - Click **Read Aloud** to test browser speech synthesis in the chosen language.

4. **Wrong-Turn Detection Simulation:**
   - Under the map in the Navigation page, locate the **Evaluator Checkpoint & Wrong-Turn Simulator**.
   - Click **Force Wrong Turn**.
   - The red alert banner appears immediately in your chosen language: *"You have moved away from your planned route. A new route has been calculated."*
   - The Dijkstra algorithm automatically recalculates the route from the deviated checkpoint!

5. **Live Gate Change Test:**
   - In a second tab, log into Admin (`/admin/login`).
   - Go to **Manage Flights**, edit `AI202`, and change gate from `Boarding Gate A5` to `Boarding Gate B5`.
   - In the passenger navigation tab, a real-time gate change alert banner appears with 1-click rerouting.

6. **QR Code Generation & Camera Scanning:**
   - Visit `/admin/qrcodes` to view and download high-resolution PNG badges.
   - Visit `/scanner` to test camera scanning or 1-click test simulation.

---

## 📄 License
Academic & Educational Project - Open Source under MIT License.
