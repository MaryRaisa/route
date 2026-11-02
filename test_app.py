import unittest
import json
from app import app
from database import get_db_connection, init_db, seed_initial_data
from navigation import dijkstra_shortest_path, generate_route_details, check_wrong_turn_and_reroute

class SmartQRAirportTestCase(unittest.TestCase):
    def setUp(self):
        init_db()
        seed_initial_data()
        self.app = app.test_client()
        self.app.testing = True

    def test_database_seeded(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as cnt FROM locations")
        loc_count = c.fetchone()['cnt']
        c.execute("SELECT COUNT(*) as cnt FROM flights")
        flight_count = c.fetchone()['cnt']
        c.execute("SELECT COUNT(*) as cnt FROM paths")
        path_count = c.fetchone()['cnt']
        conn.close()

        self.assertGreaterEqual(loc_count, 12, "Should have at least 12 airport locations")
        self.assertGreaterEqual(flight_count, 5, "Should have sample flights")
        self.assertGreaterEqual(path_count, 15, "Should have graph paths")

    def test_dijkstra_shortest_path(self):
        # Path from Main Entrance (1) to Boarding Gate A5 (12)
        path, dist, mins = dijkstra_shortest_path(1, 12)
        self.assertTrue(len(path) > 1, "Path should contain multiple nodes")
        self.assertEqual(path[0], 1, "Start node should be 1")
        self.assertEqual(path[-1], 12, "End node should be 12")
        self.assertGreater(dist, 0, "Distance should be positive")
        self.assertGreater(mins, 0, "Walking time should be positive")

    def test_multilingual_route_generation(self):
        # English
        en_route = generate_route_details(1, 12, lang='en')
        self.assertTrue(en_route['success'])
        self.assertIn("Main Entrance", en_route['steps'][0]['instruction'])

        # Tamil
        ta_route = generate_route_details(1, 12, lang='ta')
        self.assertTrue(ta_route['success'])
        self.assertIn("முக்கிய நுழைவாயில்", ta_route['steps'][0]['instruction'])

        # Hindi
        hi_route = generate_route_details(1, 12, lang='hi')
        self.assertTrue(hi_route['success'])
        self.assertIn("मुख्य प्रवेश द्वार", hi_route['steps'][0]['instruction'])

    def test_wrong_turn_detection(self):
        # Planned path from Entrance (1) to Gate A5 (12)
        path, _, _ = dijkstra_shortest_path(1, 12)
        # Checkpoint: Baggage Claim (15), which is not on this path
        result = check_wrong_turn_and_reroute(15, path, 12, lang='en')
        self.assertTrue(result['is_wrong_turn'], "Should detect wrong turn")
        self.assertEqual(result['status'], 'WRONG_TURN')
        self.assertIn("away from your planned route", result['warning_message'])
        self.assertEqual(result['path_ids'][0], 15, "New path should start from deviated node")
        self.assertEqual(result['path_ids'][-1], 12, "New path should still reach target destination")

    def test_pages_render(self):
        # Home
        res = self.app.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'SMART QR GUIDE AIRPORT', res.data)

        # Passenger Dashboard
        res = self.app.get('/passenger?flight=AI202')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'AI202', res.data)

        # QR Scanner
        res = self.app.get('/scanner')
        self.assertEqual(res.status_code, 200)

        # Flight Search
        res = self.app.get('/flight-search')
        self.assertEqual(res.status_code, 200)

        # Navigation
        res = self.app.get('/navigation?from=1&to=12')
        self.assertEqual(res.status_code, 200)

    def test_api_endpoints(self):
        # Locations API
        res = self.app.get('/api/locations')
        self.assertEqual(res.status_code, 200)
        locations = json.loads(res.data)
        self.assertIsInstance(locations, list)

        # Flight API
        res = self.app.get('/api/flight/AI202')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['flight']['flight_number'], 'AI202')
        self.assertIn('boarding_time', data['flight'])
        self.assertIn('boarding_closes', data['flight'])
        self.assertEqual(data['flight']['boarding_time'], '13:50')
        self.assertEqual(data['flight']['boarding_closes'], '14:10')

        # Navigate API
        res = self.app.post('/api/navigate', 
                            data=json.dumps({'start_id': 1, 'end_id': 11, 'lang': 'en'}),
                            content_type='application/json')
        self.assertEqual(res.status_code, 200)
        nav_data = json.loads(res.data)
        self.assertTrue(nav_data['success'])

    def test_boarding_closing_calculation(self):
        from database import calculate_boarding_times
        # 14:30 -> starts 13:50, closes 14:10
        start, close = calculate_boarding_times("14:30")
        self.assertEqual(start, "13:50")
        self.assertEqual(close, "14:10")

        # Past midnight check: 00:20 -> starts 23:40, closes 00:00
        start2, close2 = calculate_boarding_times("00:20")
        self.assertEqual(start2, "23:40")
        self.assertEqual(close2, "00:00")

if __name__ == '__main__':
    unittest.main()
