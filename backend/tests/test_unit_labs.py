import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))

from app.main import app
from app.models.unit_labs import AGENT_LABS, DATA_LABS, SECURITY_LABS
from app.repositories import storage


class UnitLabTests(unittest.TestCase):
    def test_published_data_lab_is_closed_and_does_not_write_progress(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(storage, 'DB', Path(folder) / 'test.sqlite3'):
            before = storage.default_progress()
            with storage.transaction() as database:
                storage.write(database, 'progress', before)
            with TestClient(app, base_url='http://127.0.0.1', raise_server_exceptions=False) as client:
                detail = client.get('/api/v1/units/data-04/lab')
                self.assertEqual(detail.status_code, 200)
                payload = detail.json()
                self.assertNotIn('expected', payload)
                self.assertNotIn('answers', payload)
                self.assertEqual(payload['unit_id'], 'data-04')
                self.assertTrue(payload['questions'])
                answers = {}
                for question in payload['questions']:
                    alias = DATA_LABS['data-04'].get('aliases', {}).get(question['id'], question['id'])
                    answers[question['id']] = DATA_LABS['data-04']['expected'][alias]
                result = client.post('/api/v1/units/data-04/lab/run', json={'answers': answers}, headers={'X-Academy-Client': 'local'})
                self.assertEqual(result.status_code, 200)
                self.assertTrue(result.json()['correct'])
                self.assertEqual(client.get('/api/v1/progress').json(), before)

    def test_runner_rejects_unknown_units_and_unbounded_input(self):
        with TestClient(app, base_url='http://127.0.0.1', raise_server_exceptions=False) as client:
            self.assertEqual(client.get('/api/v1/units/security-01/lab').status_code, 200)
            headers = {'X-Academy-Client': 'local'}
            self.assertEqual(client.post('/api/v1/units/data-02/lab/run', json={'answers': {}, 'unexpected': True}, headers=headers).status_code, 422)
            response = client.post('/api/v1/units/data-02/lab/run', json={'answers': {'quotes-inner': '0'}}, headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json()['correct'])
            self.assertNotIn('4', response.text)

    def test_published_security_labs_are_closed_and_have_no_legacy_write(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(storage, 'DB', Path(folder) / 'test.sqlite3'):
            before = storage.default_progress()
            with storage.transaction() as database:
                storage.write(database, 'progress', before)
            with TestClient(app, base_url='http://127.0.0.1', raise_server_exceptions=False) as client:
                for unit_id in SECURITY_LABS:
                    with self.subTest(unit_id=unit_id):
                        detail = client.get(f'/api/v1/units/{unit_id}/lab')
                        self.assertEqual(detail.status_code, 200)
                        payload = detail.json()
                        self.assertNotIn('expected', payload)
                        answers = {
                            question['id']: SECURITY_LABS[unit_id]['expected'][SECURITY_LABS[unit_id].get('aliases', {}).get(question['id'], question['id'])]
                            for question in payload['questions']
                        }
                        result = client.post(f'/api/v1/units/{unit_id}/lab/run', json={'answers': answers}, headers={'X-Academy-Client': 'local'})
                        self.assertEqual(result.status_code, 200)
                        self.assertTrue(result.json()['correct'])
                self.assertEqual(client.get('/api/v1/progress').json(), before)

    def test_published_agent_labs_are_closed_and_have_no_legacy_write(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(storage, 'DB', Path(folder) / 'test.sqlite3'):
            before = storage.default_progress()
            with storage.transaction() as database:
                storage.write(database, 'progress', before)
            with TestClient(app, base_url='http://127.0.0.1', raise_server_exceptions=False) as client:
                for unit_id in AGENT_LABS:
                    with self.subTest(unit_id=unit_id):
                        detail = client.get(f'/api/v1/units/{unit_id}/lab')
                        self.assertEqual(detail.status_code, 200)
                        payload = detail.json()
                        self.assertNotIn('expected', payload)
                        answers = {
                            question['id']: AGENT_LABS[unit_id]['expected'][AGENT_LABS[unit_id].get('aliases', {}).get(question['id'], question['id'])]
                            for question in payload['questions']
                        }
                        result = client.post(f'/api/v1/units/{unit_id}/lab/run', json={'answers': answers}, headers={'X-Academy-Client': 'local'})
                        self.assertEqual(result.status_code, 200)
                        self.assertTrue(result.json()['correct'])
                self.assertEqual(client.get('/api/v1/progress').json(), before)


if __name__ == '__main__':
    unittest.main()
