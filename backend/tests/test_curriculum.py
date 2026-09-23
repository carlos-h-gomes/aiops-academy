import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'backend'))
sys.path.insert(0, str(ROOT/'scripts'))
from fastapi.testclient import TestClient
from app.main import app
from app.models.catalog import COURSE, LAB_MAP
from app.models.curriculum import read_metadata
from app.repositories import storage
from app.schemas.curriculum import Curriculum, validate_content_links
from author_curriculum import build_catalog, write_catalog


class CurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manuals = json.loads((ROOT/'backend/content/manuals.json').read_text(encoding='utf-8'))
        cls.catalog = build_catalog(COURSE, cls.manuals, LAB_MAP).model_dump()

    def test_catalog_stable_identity_available_and_planned_counts(self):
        value = Curriculum.model_validate(self.catalog)
        self.assertEqual([track.id for track in value.tracks], ['infra','data','security','agents'])
        available = [unit for unit in value.units if unit.status == 'available']
        legacy_available = [unit for unit in available if unit.lesson_day is not None]
        self.assertEqual([(unit.id,unit.lesson_day) for unit in legacy_available], [(f'infra-{day:02d}',day) for day in range(1,31)])
        self.assertEqual({unit.id for unit in available if unit.lesson_day is None}, {'data-01','data-02','data-03','data-04','data-05','data-06','security-01','security-02','security-03','security-04','security-05','security-06','agents-01','agents-02','agents-03','agents-04','agents-05','agents-06','agents-07','agents-08'})
        self.assertEqual(sum(unit.duration_minutes.essential for unit in legacy_available), 90*60)
        self.assertEqual(sum(unit.duration_minutes.complete for unit in legacy_available), 142*60)
        for track, count in [('data',6),('security',6),('agents',8)]:
            units = [unit for unit in value.units if unit.track_id == track]
            self.assertEqual(len(units), count)
            expected_available = {f'data-{order:02d}' for order in range(1,7)} if track == 'data' else ({f'security-{order:02d}' for order in range(1,7)} if track == 'security' else {f'agents-{order:02d}' for order in range(1,9)})
            self.assertTrue(all(unit.lesson_day is None and (unit.id in expected_available or unit.status=='planned') for unit in units))

    def test_graph_rejects_duplicates_dangling_references_and_cycles(self):
        cases = [
            lambda c: c['units'].append(copy.deepcopy(c['units'][0])),
            lambda c: c['tracks'].append(copy.deepcopy(c['tracks'][0])),
            lambda c: c['units'][0].update(track_id='unknown'),
            lambda c: c['units'][0].update(prerequisites=['unknown']),
            lambda c: c['units'][0].update(prerequisites=['infra-01']),
            lambda c: c['units'][0].update(prerequisites=['infra-02']),
            lambda c: c['units'][0].update(prerequisites=['data-01']),
            lambda c: c['units'][1].update(order=1),
            lambda c: c['units'][0].update(id='renumbered'),
            lambda c: c['tracks'][0]['guides'].append(copy.deepcopy(c['tracks'][0]['guides'][0])),
        ]
        for index, mutate in enumerate(cases):
            with self.subTest(case=index):
                bad=copy.deepcopy(self.catalog);mutate(bad)
                with self.assertRaises(ValueError):Curriculum.model_validate(bad)

    def test_readiness_translation_and_strict_input_validation(self):
        cases = [
            lambda c: c['units'][0].update(order=True),
            lambda c: c['units'][0].update(lesson_day='1'),
            lambda c: c['units'][0].update(sources=[]),
            lambda c: c['units'][0].update(practice=None),
            lambda c: c['units'][0]['duration_minutes'].update(essential=900),
            lambda c: c['units'][0]['sources'][0].update(url='javascript:inert'),
            lambda c: c['units'][0]['sources'][0].update(url='https://example.org/has space'),
            lambda c: c['units'][0]['sources'][0].update(url='https://fixture:inert@example.org'),
            lambda c: c['units'][0]['translations'][0].update(content_version='older'),
            lambda c: c['units'][0]['translations'][1].update(locale='pt-BR'),
            lambda c: c['units'][43].update(content_version=None),
            lambda c: c['units'][30].update(lesson_day=1),
            lambda c: c['units'][0].update(unexpected='value'),
        ]
        for index, mutate in enumerate(cases):
            with self.subTest(case=index):
                bad=copy.deepcopy(self.catalog);mutate(bad)
                with self.assertRaises(ValueError):Curriculum.model_validate(bad)

    def test_content_references_reject_stale_lessons_guides_and_labs(self):
        cases = [
            lambda c: c['units'][0].update(title='Stale title'),
            lambda c: c['units'][0]['practice'].update(lab_id='unknown'),
            lambda c: c['units'][0]['practice'].update(limitations='Untrue limitation'),
            lambda c: c['units'][0]['sources'][0].update(url='https://example.org/other'),
            lambda c: c['tracks'][0]['guides'][0].update(id='missing'),
        ]
        for index, mutate in enumerate(cases):
            with self.subTest(case=index):
                bad=copy.deepcopy(self.catalog);mutate(bad)
                with self.assertRaises(ValueError):validate_content_links(Curriculum.model_validate(bad),COURSE,self.manuals,LAB_MAP)

    def test_generation_is_reproducible_and_invalid_input_preserves_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'catalog.json'
            write_catalog(COURSE,self.manuals,LAB_MAP,target)
            before=target.read_bytes()
            self.assertEqual(before,(ROOT/'backend/content/curriculum.json').read_bytes())
            bad=copy.deepcopy(COURSE);bad['lessons'][0]['minutes']=True
            with self.assertRaises(ValueError):write_catalog(bad,self.manuals,LAB_MAP,target)
            self.assertEqual(target.read_bytes(),before)
            self.assertEqual(list(Path(folder).glob('*.tmp')),[])
        self.assertEqual(json.loads((ROOT/'schemas/curriculum.schema.json').read_text(encoding='utf-8')),Curriculum.model_json_schema())

    def test_bounded_metadata_reader(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'data.json';path.write_bytes(b' '*101)
            with self.assertRaises(ValueError):read_metadata(path,100)

    def test_read_only_api_preserves_legacy_progress_backup_and_course(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(storage,'DB',Path(folder)/'test.sqlite3'):
            previous=storage.default_progress()
            previous.update(settings={'start_date':'2035-12-15','daily_hours':0.75},notes={'1':'Evidência sintética de investigação.'},completed=[1],quizzes={'1':100},labs={'linux':True},reviews={'1':{'due':'2035-12-16','interval':1,'last_score':100}})
            with storage.transaction() as db:storage.write(db,'progress',previous)
            with TestClient(app,base_url='http://127.0.0.1',raise_server_exceptions=False) as client:
                backup=client.get('/api/v1/backup').json()
                course=client.get('/api/v1/course').json()
                response=client.get('/api/v1/curriculum')
                self.assertEqual(response.status_code,200)
                self.assertEqual(response.json(),self.catalog)
                self.assertNotIn('notes',response.json())
                self.assertTrue(all('quiz' not in unit and 'body' not in unit for unit in response.json()['units']))
                self.assertEqual(client.get('/api/v1/progress').json(),previous)
                self.assertEqual(client.get('/api/v1/backup').json(),backup)
                self.assertEqual(client.get('/api/v1/course').json(),course)
                self.assertEqual(client.post('/api/v1/complete/31',json={},headers={'X-Academy-Client':'local'}).status_code,422)
                self.assertEqual(client.get('/api/v1/progress').json(),previous)

    def test_catalog_error_is_safe_and_does_not_break_legacy_routes(self):
        with TestClient(app,base_url='http://127.0.0.1',raise_server_exceptions=False) as client:
            with patch('app.services.curriculum.load_curriculum',side_effect=RuntimeError('internal fixture path')):
                response=client.get('/api/v1/curriculum')
                self.assertEqual(response.status_code,500)
                self.assertNotIn('internal fixture path',response.text)
                self.assertEqual(client.get('/api/v1/course').status_code,200)


if __name__ == '__main__':unittest.main()
