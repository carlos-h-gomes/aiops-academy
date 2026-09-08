import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch
from datetime import date

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.main import app
from app.repositories import storage
from app.models.catalog import LESSONS,LAB_MAP
from app.services import learning

HEADERS={'X-Academy-Client':'local'}
class AcademyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.original=storage.DB;storage.DB=Path(self.tmp.name)/'test.sqlite3'
        self.client=TestClient(app,base_url='http://127.0.0.1',raise_server_exceptions=False)
    def tearDown(self):self.client.close();storage.DB=self.original;self.tmp.cleanup()
    def post(self,path,body=None):return self.client.post('/api/v1'+path,json=body or {},headers=HEADERS)
    def start(self,id):return self.post('/labs/'+id+'/start').json()['id']
    def run_lab(self,id,sid,source='',action='',check=False):return self.post('/labs/'+id+'/run',dict(session_id=sid,source=source,action=action,check=check))
    def test_first_access_date_is_saved_across_days(self):
        with patch('app.repositories.storage.date') as calendar:
            calendar.today.return_value=date(2028,2,29)
            first=self.client.get('/api/v1/progress').json()
            self.assertEqual(first['settings']['start_date'],'2028-02-29')
            calendar.today.return_value=date(2028,3,1)
            second=self.client.get('/api/v1/progress').json()
            self.assertEqual(second,first)
    def test_existing_v1_progress_and_calendar_survive_upgrade(self):
        previous=storage.default_progress()
        previous['settings']={'start_date':'2026-09-05','daily_hours':3}
        previous['notes']={'1':'Evidência sintética existente; a atualização deve preservar este texto.'}
        with storage.transaction() as db:storage.write(db,'progress',previous)
        with patch('app.repositories.storage.date') as calendar:
            calendar.today.return_value=date(2035,1,1)
            self.assertEqual(self.client.get('/api/v1/progress').json(),previous)
        backup=self.client.get('/api/v1/backup').json()
        response=self.client.put('/api/v1/settings',json={'start_date':'2035-12-15','daily_hours':5},headers=HEADERS)
        self.assertEqual(response.status_code,200)
        self.assertEqual(self.post('/restore',{**backup,'confirm':True}).status_code,200)
        self.assertEqual(self.client.get('/api/v1/progress').json(),previous)
    def test_calendar_rejects_unsupported_bounds(self):
        for start in ('1999-12-31','2101-01-01','2035-02-30'):
            response=self.client.put('/api/v1/settings',json={'start_date':start,'daily_hours':5},headers=HEADERS)
            self.assertEqual(response.status_code,422)
    def test_flexible_hours_backup_and_existing_notes(self):
        self.assertEqual(self.client.get('/api/v1/progress').json()['settings']['daily_hours'],1)
        seed=storage.default_progress()
        seed.update(notes={'1':'Nota sintética preservada.'},completed=[1],quizzes={'1':100},labs={'linux':True},reviews={'1':{'due':'2035-12-16','interval':1,'last_score':100}})
        with storage.transaction() as db:storage.write(db,'progress',seed)
        for hours in (0.5,0.75,1,1.5,2,3,5):
            response=self.client.put('/api/v1/settings',json={'start_date':'2035-12-15','daily_hours':hours},headers=HEADERS)
            self.assertEqual(response.status_code,200)
            backup=self.client.get('/api/v1/backup').json()
            self.assertEqual(backup['settings']['daily_hours'],hours)
            for key in ('notes','completed','quizzes','labs','reviews'):
                self.assertEqual(backup[key],seed[key])
            self.client.put('/api/v1/settings',json={'start_date':'2040-01-01','daily_hours':3},headers=HEADERS)
            before_restore=learning.backup()
            self.assertEqual(self.post('/restore',{**backup,'confirm':True}).status_code,200)
            self.assertEqual(learning.backup(),backup)
            self.assertEqual(self.post('/restore/undo').status_code,200)
            self.assertEqual(learning.backup(),before_restore)
    def test_invalid_hours_do_not_mutate_progress(self):
        before=self.client.get('/api/v1/progress').json()
        for hours in (True,False,'1',None,[],{},0,-1,0.25,4,25):
            response=self.client.put('/api/v1/settings',json={'start_date':'2035-12-15','daily_hours':hours},headers=HEADERS)
            self.assertEqual(response.status_code,422)
        self.assertEqual(self.client.get('/api/v1/progress').json(),before)
    def test_invalid_backup_hours_preserve_state_and_undo_point(self):
        original=learning.backup()
        learning.save_note(1,'Estado sintético antes de restaurar.')
        undo_target=learning.backup()
        self.assertEqual(self.post('/restore',{**original,'confirm':True}).status_code,200)
        for hours in (True,False,'1',None,0,4):
            invalid={**original,'settings':{'start_date':'2035-12-15','daily_hours':hours},'confirm':True}
            self.assertEqual(self.post('/restore',invalid).status_code,422)
            self.assertEqual(learning.backup(),original)
        self.assertEqual(self.post('/restore/undo').status_code,200)
        self.assertEqual(learning.backup(),undo_target)
    def test_catalog_30_days_60_questions_and_priorities(self):
        r=self.client.get('/api/v1/course');self.assertEqual(r.status_code,200);c=r.json()
        self.assertEqual(len(c['lessons']),30);self.assertEqual(sum(len(l['quiz']) for l in c['lessons']),60)
        self.assertEqual(len(c['labs']),11)
        self.assertNotIn('answer',c['lessons'][0]['quiz'][0]);self.assertNotIn('solution',c['labs'][0])
        self.assertIn('GCP',str(c));self.assertIn('OpenSearch',str(c));self.assertIn('Dynatrace',str(c))
    def test_no_completion_without_evidence_and_assessment(self):
        self.assertEqual(self.post('/complete/1').status_code,422)
        self.assertEqual(storage.progress()['completed'],[])
    def test_quiz_wrong_answers_schedule_review(self):
        q=LESSONS[1]['quiz'];r=self.post('/quiz/1',{'answers':[(x['answer']+1)%3 for x in q]})
        self.assertEqual(r.json()['score'],0);self.assertIn('1',storage.progress()['reviews'])
    def test_complete_valid_learning_journey_and_persist(self):
        sid=self.start('linux')
        for command in ['df -h','journalctl -u quotes','metrics','rotate-logs','status']:
            r=self.run_lab('linux',sid,command);self.assertEqual(r.status_code,200)
        self.assertTrue(r.json()['passed'])
        self.post('/quiz/1',dict(answers=[q['answer'] for q in LESSONS[1]['quiz']]))
        note='Evidência sintética: observei disco 96%, erros de escrita e taxa 22%. Rotação limitada recuperou a API; confirmei métricas e documentei limites.'
        self.assertEqual(self.client.put('/api/v1/notes/1',json={'text':note},headers=HEADERS).status_code,200)
        self.assertEqual(self.post('/complete/1').status_code,200)
        self.client.close();self.client=TestClient(app,base_url='http://127.0.0.1')
        p=self.client.get('/api/v1/progress').json();self.assertIn(1,p['completed']);self.assertEqual(p['notes']['1'],note)
    def test_ansible_check_does_not_apply_and_second_run_converges(self):
        sid=self.start('ansible');source=LAB_MAP['ansible']['solution']
        r=self.run_lab('ansible',sid,source,check=True).json();self.assertFalse(r['passed']);self.assertEqual(r['state']['hosts'][0]['packages'],[])
        r=self.run_lab('ansible',sid,source).json();self.assertFalse(r['passed']);self.assertEqual(r['changes'],4)
        r=self.run_lab('ansible',sid,source).json();self.assertTrue(r['passed']);self.assertEqual(r['changes'],0)
    def test_wrong_platform_is_failure_not_success(self):
        sid=self.start('ansible');source=LAB_MAP['ansible']['solution'].replace('hosts: webservers','hosts: windows')
        r=self.run_lab('ansible',sid,source).json();self.assertEqual(r['failed'],1);self.assertFalse(r['passed'])
    def test_yaml_alias_tag_and_unknown_options_fail_closed(self):
        sid=self.start('ansible')
        for source in ['- &a {hosts: webservers, tasks: [*a]}','!!python/object/apply:os.system [echo inert]','- hosts: webservers\n  tasks:\n    - shell: echo inert',LAB_MAP['ansible']['solution']+'      when: false\n']:
            self.assertEqual(self.run_lab('ansible',sid,source).status_code,422)
        self.assertFalse(storage.progress()['labs'])
    def test_session_cannot_cross_lab(self):
        self.assertEqual(self.run_lab('ansible',self.start('linux'),LAB_MAP['ansible']['solution']).status_code,422)
    def test_all_non_terminal_reference_solutions(self):
        for id in ['ansible-windows','dql','opensearch','slo','events','workflow','anomaly','rag']:
            with self.subTest(lab=id):
                sid=self.start(id);r=self.run_lab(id,sid,LAB_MAP[id]['solution'])
                if id.startswith('ansible'):r=self.run_lab(id,sid,LAB_MAP[id]['solution'])
                self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['passed'],r.text)
    def test_dql_is_executed_not_keyword_match(self):
        sid=self.start('dql')
        valid='fetch logs | filter loglevel == "INFO" | summarize total = count(), by:{service.name}'
        r=self.run_lab('dql',sid,valid);self.assertEqual(r.status_code,200);self.assertFalse(r.json()['passed'])
        alternate='fetch logs | filter loglevel != "INFO" | filter loglevel != "WARN" | summarize total=count(), by: {service.name}'
        self.assertTrue(self.run_lab('dql',sid,alternate).json()['passed'])
        self.assertEqual(self.run_lab('dql',sid,'fetch logs | execute anything').status_code,422)
    def test_no_nan_bool_numeric_or_extra_keys(self):
        sid=self.start('slo')
        for source in ['{"allowed_errors":NaN}','{"allowed_errors":1000,"excess_errors":400,"burn_rate":20,"extra":1}']:
            self.assertEqual(self.run_lab('slo',sid,source).status_code,422)
        q={'allowed_errors':1000,'excess_errors':400,'burn_rate':True}
        self.assertFalse(self.run_lab('slo',sid,json.dumps(q)).json()['passed'])
    def test_incident_requires_approval_and_verification(self):
        sid=self.start('incident');r=self.run_lab('incident',sid,action='rollback').json();self.assertFalse(r['state']['fixed'])
        for a in ['metrics','logs','changes','communicate','approve','rollback','verify','close']:r=self.run_lab('incident',sid,action=a).json()
        self.assertTrue(r['passed']);self.assertTrue(r['state']['closed'])
    def test_exam_deadline_and_idempotent_submission(self):
        exam=self.post('/exams/final/start').json();self.assertEqual(len(exam['questions']),30)
        self.assertNotIn('answer',exam['questions'][0])
        with patch.object(learning.time,'time',return_value=exam['expires']+1):
            r=self.post('/exams/'+exam['id']+'/submit',dict(answers=[0]*30)).json()
        self.assertTrue(r['expired']);self.assertFalse(r['passed'])
        self.assertEqual(r,self.post('/exams/'+exam['id']+'/submit',dict(answers=[1]*30)).json())
    def test_backup_restore_roundtrip_and_undo(self):
        learning.save_note(2,'Primeira evidência '+('sintética '*10));before=learning.backup()
        learning.save_note(2,'Segunda evidência '+('diferente '*10));second=learning.backup()
        self.assertEqual(self.post('/restore',{**before,'confirm':True}).status_code,200)
        self.assertEqual(learning.backup(),before)
        self.assertEqual(self.post('/restore/undo').status_code,200);self.assertEqual(learning.backup(),second)
    def test_invalid_backup_atomic_and_confirmation_required(self):
        before=learning.backup();invalid={**before,'notes':{'31':'não existe'},'confirm':True}
        self.assertEqual(self.post('/restore',invalid).status_code,422);self.assertEqual(learning.backup(),before)
        self.assertEqual(self.post('/restore',{**before,'confirm':False}).status_code,422)
    def test_body_host_origin_and_headers(self):
        self.assertEqual(self.client.get('/api/v1/progress',headers={'Host':'evil.example'}).status_code,403)
        self.assertEqual(self.client.get('/api/v1/progress',headers={'Origin':'https://evil.example'}).status_code,403)
        self.assertEqual(self.client.post('/api/v1/complete/1',json={}).status_code,403)
        self.assertEqual(self.client.post('/api/v1/complete/1',content='x'*800001,headers={**HEADERS,'Content-Type':'application/json'}).status_code,413)
        self.assertEqual(self.client.post('/api/v1/complete/1',content='x',headers={**HEADERS,'Content-Type':'text/plain'}).status_code,415)
    def test_sources_and_db_not_served(self):
        for path in ['/data/academy.sqlite3','/backend/app/main.py','/assets/../../data/academy.sqlite3','/_qa/audit.html']:
            self.assertEqual(self.client.get(path).status_code,404)
        self.assertIn("frame-ancestors 'none'",self.client.get('/api/v1/health').headers['content-security-policy'])
    def test_quiz_unknown_day_incomplete_answers_and_note_limit(self):
        self.assertEqual(self.post('/quiz/31',{'answers':[0,0]}).status_code,422)
        self.assertEqual(self.post('/quiz/1',{'answers':[0]}).status_code,422)
        self.assertEqual(self.client.put('/api/v1/notes/1',json={'text':'a'*12001},headers=HEADERS).status_code,422)
    def test_review_card_and_schedule(self):
        self.assertIn('explanation',self.client.get('/api/v1/reviews/1/card').json())
        self.assertEqual(self.post('/reviews/1',{'rating':'easy'}).status_code,200)
        self.assertEqual(storage.progress()['reviews']['1']['interval'],3)
    def test_no_fake_python_or_shell_execution(self):
        sid=self.start('linux');self.assertEqual(self.run_lab('linux',sid,'python -c "print(1)"').status_code,422)
        self.assertEqual(self.run_lab('linux',sid,'rm -rf /').status_code,422)

if __name__=='__main__':unittest.main(verbosity=2)
