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
    def test_published_data_lab_is_closed_and_records_only_its_guided_progress(self):
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
                after=client.get('/api/v1/progress').json()
                self.assertEqual({key:value for key,value in after.items() if key!='unit_progress'},{key:value for key,value in before.items() if key!='unit_progress'})
                self.assertEqual(after['unit_progress']['data-04'],{'lab_passed':True,'completed':False,'note':'','review':None})

    def test_runner_rejects_unknown_units_and_unbounded_input(self):
        with TestClient(app, base_url='http://127.0.0.1', raise_server_exceptions=False) as client:
            self.assertEqual(client.get('/api/v1/units/security-01/lab').status_code, 200)
            headers = {'X-Academy-Client': 'local'}
            self.assertEqual(client.post('/api/v1/units/data-02/lab/run', json={'answers': {}, 'unexpected': True}, headers=headers).status_code, 422)
            response = client.post('/api/v1/units/data-02/lab/run', json={'answers': {'quotes-inner': '0'}}, headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.json()['correct'])
            self.assertNotIn('4', response.text)

    def test_published_security_labs_are_closed_and_keep_legacy_namespaces_unchanged(self):
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
                after=client.get('/api/v1/progress').json()
                self.assertEqual({key:value for key,value in after.items() if key!='unit_progress'},{key:value for key,value in before.items() if key!='unit_progress'})
                self.assertEqual(set(after['unit_progress']),set(SECURITY_LABS))
                self.assertTrue(all(state['lab_passed'] and not state['completed'] for state in after['unit_progress'].values()))

    def test_published_agent_labs_are_closed_and_keep_legacy_namespaces_unchanged(self):
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
                after=client.get('/api/v1/progress').json()
                self.assertEqual({key:value for key,value in after.items() if key!='unit_progress'},{key:value for key,value in before.items() if key!='unit_progress'})
                self.assertEqual(set(after['unit_progress']),set(AGENT_LABS))
                self.assertTrue(all(state['lab_passed'] and not state['completed'] for state in after['unit_progress'].values()))

    def test_guided_unit_completion_review_and_backup_are_individual_and_legacy_safe(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(storage, 'DB', Path(folder) / 'test.sqlite3'):
            headers={'X-Academy-Client':'local'}
            with TestClient(app, base_url='http://127.0.0.1', raise_server_exceptions=False) as client:
                lab=client.get('/api/v1/units/data-01/lab').json()
                answers={question['id']:DATA_LABS['data-01']['expected'][DATA_LABS['data-01'].get('aliases',{}).get(question['id'],question['id'])] for question in lab['questions']}
                self.assertTrue(client.post('/api/v1/units/data-01/lab/run',json={'answers':answers},headers=headers).json()['correct'])
                self.assertEqual(client.post('/api/v1/units/data-01/complete',json={},headers=headers).status_code,422)
                note='Registrei as chaves, as relações e as restrições da fixture e conferi cada rejeição antes de concluir a prática.'
                saved=client.put('/api/v1/units/data-01/note',json={'text':note},headers=headers)
                self.assertEqual(saved.status_code,200)
                completed=client.post('/api/v1/units/data-01/complete',json={},headers=headers)
                self.assertEqual(completed.status_code,200)
                self.assertTrue(completed.json()['completed'])
                reviewed=client.post('/api/v1/units/data-01/review',json={'rating':'good'},headers=headers)
                self.assertEqual(reviewed.status_code,200)
                self.assertGreaterEqual(reviewed.json()['review']['interval'],1)
                backup=client.get('/api/v1/backup').json()
                self.assertEqual(backup['version'],2)
                self.assertEqual(backup['unit_progress']['data-01']['note'],note)
                self.assertEqual(client.get('/api/v1/progress').json()['completed'],[])


if __name__ == '__main__':
    unittest.main()
