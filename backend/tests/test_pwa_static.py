import sys
from pathlib import Path
import unittest

from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'backend'))

from app.main import app


class PwaStaticTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app,base_url='http://127.0.0.1')

    def test_manifest_and_service_worker_are_exposed_from_the_built_interface(self):
        manifest = self.client.get('/manifest.webmanifest')
        self.assertEqual(manifest.status_code, 200)
        self.assertEqual(manifest.headers['content-type'].split(';')[0], 'application/manifest+json')
        self.assertEqual(manifest.json()['start_url'], '/')
        self.assertEqual(manifest.json()['display'], 'standalone')

        worker = self.client.get('/sw.js')
        self.assertEqual(worker.status_code, 200)
        self.assertIn('application/javascript', worker.headers['content-type'])
        self.assertIn("const CACHE_NAME='aiops-academy-pwa-v2'", worker.text)


if __name__ == '__main__':
    unittest.main()
