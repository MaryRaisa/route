import heapq
from database import get_db_connection

# Comprehensive Multilingual Dictionary for UI, Locations, and Navigation
TRANSLATIONS = {
    'en': {
        'app_title': 'SMART QR GUIDE AIRPORT',
        'subtitle': 'Airport Navigation & Passenger Guidance System',
        'welcome': 'Welcome to Smart Airport Navigation',
        'home': 'Home',
        'passenger_dash': 'Passenger Dashboard',
        'qr_scanner': 'QR Scanner',
        'flight_search': 'Flight Search',
        'airport_map': 'Airport Map',
        'admin_login': 'Admin Login',
        'admin_panel': 'Admin Dashboard',
        'logout': 'Logout',
        'language': 'Language',
        'select_language': 'Select Language',
        'current_location': 'Current Location',
        'destination': 'Destination',
        'distance': 'Distance',
        'walking_time': 'Estimated Walking Time',
        'metres': 'metres',
        'minutes': 'mins',
        'seconds': 'sec',
        'steps': 'Step-by-Step Directions',
        'start_navigation': 'Start Navigation',
        'recalculate_route': 'Recalculate Route',
        'voice_guidance': 'Voice Guidance',
        'listen_directions': 'Read Aloud',
        'pause': 'Pause',
        'resume': 'Resume',
        'stop': 'Stop',
        'flight_number': 'Flight Number',
        'passenger_name': 'Passenger Name',
        'enter_flight': 'Enter Flight Number (e.g. AI202)',
        'scan_qr_prompt': 'Scan Airport QR Code',
        'manual_location_prompt': 'Or Choose Location Manually',
        'checkin_counter': 'Check-in Counter',
        'security_checkpoint': 'Security Checkpoint',
        'boarding_gate': 'Boarding Gate',
        'boarding_time': 'Boarding Starts',
        'boarding_closes': 'Gate Closes',
        'boarding_closing_details': 'Boarding Closing Details',
        'gate_closing_notice': 'Gate closes 20 mins prior to departure',
        'flight_status': 'Flight Status',
        'airline': 'Airline',
        'departure': 'Departure',
        'destination_city': 'Destination City',
        'navigate_to_checkin': 'Navigate to Check-in Counter',
        'navigate_to_security': 'Navigate to Security Checkpoint',
        'navigate_to_gate': 'Navigate to Boarding Gate',
        'facilities': 'Airport Facilities',
        'wrong_turn_warning': 'You have moved away from your planned route. A new route has been calculated.',
        'gate_changed_alert': 'Attention! The boarding gate for flight {flight} has changed to {gate}. A new route has been updated.',
        'arrived_destination': 'You have reached your destination: {dest}!',
        'simulate_checkpoint': 'Simulate Scan Checkpoint',
        'simulate_wrong_turn': 'Simulate Wrong Turn',
        'next_step': 'Next Step',
        'locations': {
            'Main Entrance': 'Main Entrance',
            'Info Desk': 'Information Desk',
            'Check-in Counter A': 'Check-in Counter A',
            'Check-in Counter B': 'Check-in Counter B',
            'Restroom A': 'Restroom A (Near Entrance)',
            'Security Checkpoint 1': 'Security Checkpoint 1 (Concourse A)',
            'Security Checkpoint 2': 'Security Checkpoint 2 (Concourse B)',
            'Central Waiting Lounge': 'Central Waiting Lounge & Duty Free',
            'Food Court': 'Food Court & Cafes',
            'Restroom B': 'Restroom B (Concourse)',
            'Boarding Gate A1': 'Boarding Gate A1',
            'Boarding Gate A5': 'Boarding Gate A5',
            'Boarding Gate B1': 'Boarding Gate B1',
            'Boarding Gate B5': 'Boarding Gate B5',
            'Baggage Claim': 'Baggage Claim Carousels',
            'Terminal Exit': 'Terminal Exit & Ground Transport'
        },
        'step_templates': {
            'start': 'Start from {source}.',
            'walk': 'Walk {dist} metres towards {target}.',
            'arrive': 'You have arrived at your destination: {target}.'
        }
    },
    'ta': {
        'app_title': 'ஸ்மார்ட் கியூஆர் வழிகாட்டி விமான நிலையம்',
        'subtitle': 'விமான நிலைய வழிசெலுத்தல் மற்றும் பயணிகள் வழிகாட்டி அமைப்பு',
        'welcome': 'ஸ்மார்ட் விமான நிலைய வழிசெலுத்தலுக்கு வரவேற்கிறோம்',
        'home': 'முகப்பு',
        'passenger_dash': 'பயணிகள் டாஷ்போர்டு',
        'qr_scanner': 'QR ஸ்கேனர்',
        'flight_search': 'விமானத் தேடல்',
        'airport_map': 'விமான நிலைய வரைபடம்',
        'admin_login': 'நிர்வாகி உள்நுழைவு',
        'admin_panel': 'நிர்வாக குழு',
        'logout': 'வெளியேறு',
        'language': 'மொழி',
        'select_language': 'மொழியைத் தேர்ந்தெடுக்கவும்',
        'current_location': 'தற்போதைய இடம்',
        'destination': 'சேருமிடம்',
        'distance': 'தூரம்',
        'walking_time': 'தோராயமான நடை நேரம்',
        'metres': 'மீட்டர்கள்',
        'minutes': 'நிமிடங்கள்',
        'seconds': 'வினாடிகள்',
        'steps': 'படிப்படியான வழிகாட்டுதல்',
        'start_navigation': 'வழிசெலுத்தலைத் தொடங்கு',
        'recalculate_route': 'பாதையை மீண்டும் கணக்கிடு',
        'voice_guidance': 'குரல் வழிகாட்டுதல்',
        'listen_directions': 'குரலில் கேளுங்கள்',
        'pause': 'இடைநிறுத்து',
        'resume': 'மீண்டும் தொடங்கு',
        'stop': 'நிறுத்து',
        'flight_number': 'விமான எண்',
        'passenger_name': 'பயணி பெயர்',
        'enter_flight': 'விமான எண்ணை உள்ளிடவும் (எ.கா. AI202)',
        'scan_qr_prompt': 'QR குறியீட்டை ஸ்கேன் செய்யவும்',
        'manual_location_prompt': 'அல்லது இடத்தை நேரடியாக தேர்ந்தெடுக்கவும்',
        'checkin_counter': 'செக்-இன் கவுண்டர்',
        'security_checkpoint': 'பாதுகாப்பு சோதனை சாவடி',
        'boarding_gate': 'போர்டிங் கேட்',
        'boarding_time': 'போர்டிங் தொடங்கும் நேரம்',
        'boarding_closes': 'கேட் மூடும் நேரம்',
        'boarding_closing_details': 'போர்டிங் நிறைவு விவரங்கள்',
        'gate_closing_notice': 'புறப்படுவதற்கு 20 நிமிடங்களுக்கு முன் கேட் மூடப்படும்',
        'flight_status': 'விமான நிலை',
        'airline': 'விமான நிறுவனம்',
        'departure': 'புறப்படும் நேரம்',
        'destination_city': 'சேரும் நகரம்',
        'navigate_to_checkin': 'செக்-இன் கவுண்டருக்கு செல்லவும்',
        'navigate_to_security': 'பாதுகாப்பு சோதனைக்கு செல்லவும்',
        'navigate_to_gate': 'போர்டிங் கேட்-க்கு செல்லவும்',
        'facilities': 'விமான நிலைய வசதிகள்',
        'wrong_turn_warning': 'நீங்கள் திட்டமிடப்பட்ட பாதையிலிருந்து விலகிவிட்டீர்கள். புதிய பாதை கணக்கிடப்பட்டுள்ளது.',
        'gate_changed_alert': 'கவனம்! விமானம் {flight} க்கான போர்டிங் கேட் {gate} ஆக மாற்றப்பட்டுள்ளது. புதிய பாதை புதுப்பிக்கப்பட்டது.',
        'arrived_destination': 'நீங்கள் உங்கள் சேருமிடத்தை அடைந்துவிட்டீர்கள்: {dest}!',
        'simulate_checkpoint': 'அடுத்த சோதனைச் சாவடியை உருவகப்படுத்து',
        'simulate_wrong_turn': 'தவறான திருப்பத்தை உருவகப்படுத்து',
        'next_step': 'அடுத்த படி',
        'locations': {
            'Main Entrance': 'முக்கிய நுழைவாயில்',
            'Info Desk': 'தகவல் மற்றும் உதவி மையம்',
            'Check-in Counter A': 'செக்-இன் கவுண்டர் ஏ',
            'Check-in Counter B': 'செக்-இன் கவுண்டர் பி',
            'Restroom A': 'ஓய்வறை ஏ (நுழைவு அருகே)',
            'Security Checkpoint 1': 'பாதுகாப்பு சோதனை சாவடி 1',
            'Security Checkpoint 2': 'பாதுகாப்பு சோதனை சாவடி 2',
            'Central Waiting Lounge': 'மத்திய காத்திருப்பு கூடம்',
            'Food Court': 'உணவு கூடம் & சிற்றுண்டி',
            'Restroom B': 'ஓய்வறை பி (கேட் அருகே)',
            'Boarding Gate A1': 'போர்டிங் கேட் ஏ1',
            'Boarding Gate A5': 'போர்டிங் கேட் ஏ5',
            'Boarding Gate B1': 'போர்டிங் கேட் பி1',
            'Boarding Gate B5': 'போர்டிங் கேட் பி5',
            'Baggage Claim': 'சாமான்கள் பெறும் பகுதி',
            'Terminal Exit': 'முனைய வெளியேறும் வழி'
        },
        'step_templates': {
            'start': '{source} இலிருந்து தொடங்கவும்.',
            'walk': '{dist} மீட்டர் நேராக {target} நோக்கி செல்லவும்.',
            'arrive': 'நீங்கள் உங்கள் சேருமிடமான {target} ஐ அடைந்துவிட்டீர்கள்.'
        }
    },
    'hi': {
        'app_title': 'स्मार्ट क्यूआर गाइड एयरपोर्ट',
        'subtitle': 'स्मार्ट एयरपोर्ट नेविगेशन और यात्री मार्गदर्शन प्रणाली',
        'welcome': 'स्मार्ट एयरपोर्ट नेविगेशन में आपका स्वागत है',
        'home': 'होम',
        'passenger_dash': 'यात्री डैशबोर्ड',
        'qr_scanner': 'क्यूआर स्कैनर',
        'flight_search': 'उड़ान खोज',
        'airport_map': 'हवाई अड्डा मानचित्र',
        'admin_login': 'व्यवस्थापक लॉगिन',
        'admin_panel': 'व्यवस्थापक डैशबोर्ड',
        'logout': 'लॉगआउट',
        'language': 'भाषा',
        'select_language': 'भाषा चुनें',
        'current_location': 'वर्तमान स्थान',
        'destination': 'गंतव्य',
        'distance': 'दूरी',
        'walking_time': 'अनुमानित पैदल समय',
        'metres': 'मीटर',
        'minutes': 'मिनट',
        'seconds': 'सेकंड',
        'steps': 'कदम-दर-कदम निर्देश',
        'start_navigation': 'नेविगेशन शुरू करें',
        'recalculate_route': 'मार्ग की पुनर्गणना करें',
        'voice_guidance': 'ध्वनि मार्गदर्शन',
        'listen_directions': 'आवाज़ में सुनें',
        'pause': 'रोकें',
        'resume': 'पुनः शुरू करें',
        'stop': 'बंद करें',
        'flight_number': 'उड़ान संख्या',
        'passenger_name': 'यात्री का नाम',
        'enter_flight': 'उड़ान संख्या दर्ज करें (उदा. AI202)',
        'scan_qr_prompt': 'एयरपोर्ट क्यूआर कोड स्कैन करें',
        'manual_location_prompt': 'या सीधे स्थान चुनें',
        'checkin_counter': 'चेक-इन काउंटर',
        'security_checkpoint': 'सुरक्षा जांच चौकी',
        'boarding_gate': 'बोर्डिंग गेट',
        'boarding_time': 'बोर्डिंग प्रारंभ',
        'boarding_closes': 'गेट बंद होने का समय',
        'boarding_closing_details': 'बोर्डिंग समापन विवरण',
        'gate_closing_notice': 'प्रस्थान से 20 मिनट पहले गेट बंद हो जाएगा',
        'flight_status': 'उड़ान स्थिति',
        'airline': 'एयरलाइन',
        'departure': 'प्रस्थान समय',
        'destination_city': 'गंतव्य शहर',
        'navigate_to_checkin': 'चेक-इन काउंटर पर जाएं',
        'navigate_to_security': 'सुरक्षा जांच पर जाएं',
        'navigate_to_gate': 'बोर्डिंग गेट पर जाएं',
        'facilities': 'हवाई अड्डा सुविधाएं',
        'wrong_turn_warning': 'आप अपने नियोजित मार्ग से भटक गए हैं। एक नया मार्ग निर्धारित किया गया है।',
        'gate_changed_alert': 'ध्यान दें! उड़ान {flight} के लिए बोर्डिंग गेट बदलकर {gate} कर दिया गया है। नया मार्ग अपडेट कर दिया गया है।',
        'arrived_destination': 'आप अपने गंतव्य {dest} पर पहुँच चुके हैं!',
        'simulate_checkpoint': 'चेकपॉइंट स्कैन अनुकरण करें',
        'simulate_wrong_turn': 'गलत मोड़ का अनुकरण करें',
        'next_step': 'अगला कदम',
        'locations': {
            'Main Entrance': 'मुख्य प्रवेश द्वार',
            'Info Desk': 'सूचना एवं सहायता केंद्र',
            'Check-in Counter A': 'चेक-इन काउंटर ए',
            'Check-in Counter B': 'चेक-इन काउंटर बी',
            'Restroom A': 'विश्राम गृह ए (प्रवेश द्वार के पास)',
            'Security Checkpoint 1': 'सुरक्षा जांच चौकी 1',
            'Security Checkpoint 2': 'सुरक्षा जांच चौकी 2',
            'Central Waiting Lounge': 'केंद्रीय प्रतीक्षालय',
            'Food Court': 'फूड कोर्ट और कैफे',
            'Restroom B': 'विश्राम गृह बी (गेट के पास)',
            'Boarding Gate A1': 'बोर्डिंग गेट ए1',
            'Boarding Gate A5': 'बोर्डिंग गेट ए5',
            'Boarding Gate B1': 'बोर्डिंग गेट बी1',
            'Boarding Gate B5': 'बोर्डिंग गेट बी5',
            'Baggage Claim': 'सामान दावा क्षेत्र',
            'Terminal Exit': 'टर्मिनल निकास द्वार'
        },
        'step_templates': {
            'start': '{source} से शुरू करें।',
            'walk': '{dist} मीटर सीधे {target} की ओर चलें।',
            'arrive': 'आप अपने गंतव्य {target} पर पहुँच गए हैं।'
        }
    }
}

def get_text(key, lang='en', **kwargs):
    """Retrieves localized text with fallback to English."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    val = lang_dict.get(key, TRANSLATIONS['en'].get(key, key))
    if isinstance(val, str) and kwargs:
        return val.format(**kwargs)
    return val

def get_location_display_name(loc_name, lang='en'):
    """Translates an airport location name."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    loc_translations = lang_dict.get('locations', {})
    return loc_translations.get(loc_name, loc_name)

def load_graph():
    """
    Builds adjacency graph from database locations and paths.
    Returns: (graph, locations_dict)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Load all locations
    cursor.execute("SELECT id, location_name, location_type, description, x_coordinate, y_coordinate FROM locations")
    locations = {row['id']: dict(row) for row in cursor.fetchall()}

    # Initialize graph
    graph = {loc_id: [] for loc_id in locations}

    # Load paths
    cursor.execute("SELECT source_id, target_id, distance, direction_desc FROM paths")
    for row in cursor.fetchall():
        s_id, t_id, dist, desc = row['source_id'], row['target_id'], row['distance'], row['direction_desc']
        if s_id in graph and t_id in graph:
            graph[s_id].append({
                'target': t_id,
                'distance': dist,
                'desc': desc
            })

    conn.close()
    return graph, locations

def dijkstra_shortest_path(start_id, end_id):
    """
    Calculates shortest path using Dijkstra algorithm.
    Returns: (path_ids, total_distance, estimated_minutes)
    """
    if start_id == end_id:
        return [start_id], 0, 0.0

    graph, _ = load_graph()
    if start_id not in graph or end_id not in graph:
        return [], 0, 0.0

    distances = {node: float('inf') for node in graph}
    distances[start_id] = 0
    previous = {node: None for node in graph}
    pq = [(0, start_id)]

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_dist > distances[current_node]:
            continue

        if current_node == end_id:
            break

        for edge in graph[current_node]:
            neighbor = edge['target']
            weight = edge['distance']
            distance = current_dist + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    # Reconstruct path
    path = []
    curr = end_id
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()

    if not path or path[0] != start_id:
        return [], 0, 0.0

    total_dist = distances[end_id]
    # Average airport walking pace: 75 metres per minute (~1.25 m/s)
    estimated_mins = round(total_dist / 75.0, 1)
    if estimated_mins < 1.0 and total_dist > 0:
        estimated_mins = 1.0

    return path, total_dist, estimated_mins

def generate_route_details(start_id, end_id, lang='en'):
    """
    Generates rich route details including:
    - Path node details (coordinates, type, names)
    - Multilingual step-by-step turn-by-turn instructions
    - Voice guidance strings
    - Distance and estimated walking duration
    """
    graph, locations = load_graph()
    path_ids, total_distance, estimated_mins = dijkstra_shortest_path(start_id, end_id)

    if not path_ids:
        return {
            'success': False,
            'message': 'No route found between selected points.',
            'path': [],
            'steps': [],
            'total_distance': 0,
            'estimated_time': 0
        }

    path_nodes = [locations[nid] for nid in path_ids]

    steps = []
    voice_script = []

    # Step 1: Start
    start_loc_name = get_location_display_name(locations[start_id]['location_name'], lang)
    start_step_txt = get_text('step_templates', lang)['start'].format(source=start_loc_name)
    steps.append({
        'step_number': 1,
        'from_id': start_id,
        'to_id': start_id,
        'instruction': start_step_txt,
        'distance': 0,
        'icon': 'bi-geo-alt-fill'
    })
    voice_script.append(start_step_txt)

    # Step 2 to N: Walk between consecutive nodes
    for i in range(len(path_ids) - 1):
        u = path_ids[i]
        v = path_ids[i+1]
        u_name = get_location_display_name(locations[u]['location_name'], lang)
        v_name = get_location_display_name(locations[v]['location_name'], lang)

        # Find edge distance
        dist = 50
        for edge in graph[u]:
            if edge['target'] == v:
                dist = edge['distance']
                break

        walk_txt = get_text('step_templates', lang)['walk'].format(dist=dist, target=v_name)
        steps.append({
            'step_number': i + 2,
            'from_id': u,
            'to_id': v,
            'instruction': walk_txt,
            'distance': dist,
            'icon': 'bi-arrow-right-circle-fill'
        })
        voice_script.append(walk_txt)

    # Final Arrival Step
    dest_name = get_location_display_name(locations[end_id]['location_name'], lang)
    arrive_txt = get_text('step_templates', lang)['arrive'].format(target=dest_name)
    steps.append({
        'step_number': len(steps) + 1,
        'from_id': end_id,
        'to_id': end_id,
        'instruction': arrive_txt,
        'distance': 0,
        'icon': 'bi-check-circle-fill'
    })
    voice_script.append(arrive_txt)

    return {
        'success': True,
        'start_node': locations[start_id],
        'end_node': locations[end_id],
        'start_display_name': start_loc_name,
        'end_display_name': dest_name,
        'path_ids': path_ids,
        'path_nodes': path_nodes,
        'steps': steps,
        'voice_text': " ".join(voice_script),
        'total_distance': total_distance,
        'estimated_time': estimated_mins,
        'is_wrong_turn': False
    }

def check_wrong_turn_and_reroute(scanned_loc_id, planned_path_ids, destination_id, lang='en'):
    """
    Checks if a scanned checkpoint deviates from the expected route.
    If deviated, automatically recalculates new shortest route from scanned location.
    """
    scanned_loc_id = int(scanned_loc_id)
    destination_id = int(destination_id)

    # If already reached destination
    if scanned_loc_id == destination_id:
        details = generate_route_details(scanned_loc_id, destination_id, lang)
        details['status'] = 'ARRIVED'
        details['is_wrong_turn'] = False
        return details

    # If scanned location is in remaining path
    if scanned_loc_id in planned_path_ids:
        # User is advancing correctly on planned path
        idx = planned_path_ids.index(scanned_loc_id)
        # Recalculate remaining path from current checkpoint to destination
        details = generate_route_details(scanned_loc_id, destination_id, lang)
        details['status'] = 'ON_TRACK'
        details['is_wrong_turn'] = False
        details['remaining_path_ids'] = planned_path_ids[idx:]
        return details
    else:
        # Passenger made a wrong turn!
        details = generate_route_details(scanned_loc_id, destination_id, lang)
        details['status'] = 'WRONG_TURN'
        details['is_wrong_turn'] = True
        details['warning_message'] = get_text('wrong_turn_warning', lang)
        return details
