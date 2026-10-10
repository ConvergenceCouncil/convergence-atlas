import re
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / 'globe.html').read_text()

class GlobeTests(unittest.TestCase):
    def test_status_visible_when_menu_closed(self):
        self.assertIn('id="load-status"', HTML)
        self.assertIn('role="status"', HTML)

    def test_all_location_sources(self):
        for source in ['ancient-relic-cities.geojson', 'tourist-attractions.geojson', 'tourist-attractions-expansion.geojson']:
            self.assertIn(source, HTML)
        self.assertIn('Promise.allSettled', HTML)

    def test_search_and_camera_controls_available(self):
        self.assertIn('id="location-search"', HTML)
        self.assertNotIn('id="engine-controls" hidden', HTML)

    def test_mobile_budget_and_timeouts(self):
        self.assertIn("applyQuality(mobile?'balanced':'high')", HTML)
        self.assertIn('cacheBytes', HTML)
        self.assertIn('maximumCacheOverflowBytes', HTML)
        self.assertIn('withTimeout', HTML)

if __name__ == '__main__': unittest.main()
