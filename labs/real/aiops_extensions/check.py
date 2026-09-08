"""Offline checks by topic; --solution checks the reference instead of the learner file."""
import argparse
import importlib
import unittest

class Checks(unittest.TestCase):
    def test_correlation(self):
        events=[dict(id='a',env='prod',service='api',minute=1),dict(id='a',env='prod',service='api',minute=2),dict(id='b',env='prod',service='api',minute=4),dict(id='a',env='test',service='api',minute=1)]
        self.assertEqual(code.correlate(events),{('prod','api',0):2,('test','api',0):1})
        self.assertEqual(code.correlate(events+[dict(id='c',env='prod',service='api',minute=5)])[('prod','api',1)],1)
    def test_correlation_boundaries(self):
        self.assertEqual(code.correlate([]),{})
        with self.assertRaises(ValueError):code.correlate([dict(id='a',env='p',service='s',minute=-1)])
    def test_capacity(self):
        self.assertEqual(code.replicas(2400,500,.6,1),9)
        self.assertEqual(code.replicas(2401,500,.6,1),10)
        self.assertEqual(code.replicas(0,500,.6,1),1)
    def test_capacity_boundaries(self):
        for args in [(1,0,.6,1),(1,500,0,1),(1,500,1.1,1),(1,500,.6,-1)]:
            with self.assertRaises(ValueError):code.replicas(*args)
    def test_seasonal(self):
        self.assertEqual(code.seasonal([100,105,95],130),dict(baseline=100.0,deviation_pct=30.0,flag=True))
        self.assertFalse(code.seasonal([100,105,95],120)['flag'])
        self.assertTrue(code.seasonal([100,105,95],60)['flag'])
    def test_seasonal_boundaries(self):
        for values in ([1,2],[0,2,3],[1,2,float('nan')]):
            with self.assertRaises(ValueError):code.seasonal(values,10)
    def test_mlops(self):
        self.assertEqual(code.model_triage(.01,.12,.94,.93,1000),'inspect_data')
        self.assertEqual(code.model_triage(.01,.01,.94,.84,1000),'review_model')
        self.assertEqual(code.model_triage(.01,.12,.94,.84,40),'insufficient_evidence')
        self.assertEqual(code.model_triage(.01,.06,.94,.94,500),'inspect_data')
        self.assertEqual(code.model_triage(.01,.01,.94,.94,500),'monitor')
    def test_mlops_boundaries(self):
        with self.assertRaises(ValueError):code.model_triage(-.1,0,.9,.9,500)
        with self.assertRaises(ValueError):code.model_triage(0,0,.9,.9,True)
    def test_agents(self):
        cases=[dict(success=True,grounded=True,unauthorized=False,latency_ms=800,cost=.003) for _ in range(10)]
        self.assertEqual(code.agent_gate(cases),dict(decision='promote',success_rate=1.0,grounded_rate=1.0,p95_ms=800,total_cost=.03))
        cases[0]['unauthorized']=True;self.assertEqual(code.agent_gate(cases)['decision'],'block')
        cases[0]['unauthorized']=False;cases[0]['latency_ms']=3000;self.assertEqual(code.agent_gate(cases)['decision'],'block')
        cases[0]['latency_ms']=800;cases[0]['cost']=1;self.assertEqual(code.agent_gate(cases)['decision'],'block')
    def test_agents_boundaries(self):
        with self.assertRaises(ValueError):code.agent_gate([])
        cases=[dict(success=True,grounded=True,unauthorized=False,latency_ms=800,cost=.003) for _ in range(10)]
        cases[0]['grounded']=False;cases[1]['grounded']=False;self.assertEqual(code.agent_gate(cases)['decision'],'block')
    def test_canary(self):
        self.assertEqual(code.canary(1,1000,20,1000),'rollback')
        self.assertEqual(code.canary(1,1000,1,1000),'promote')
        self.assertEqual(code.canary(0,100,0,100),'hold')
        self.assertEqual(code.canary(1,1000,6,1000),'promote')
    def test_canary_boundaries(self):
        for args in [(1,0,0,1000),(1001,1000,0,1000),(0,1000,-1,1000)]:
            with self.assertRaises(ValueError):code.canary(*args)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('topic',nargs='?',default='all',choices=['all','correlation','capacity','seasonal','mlops','agents','canary']);parser.add_argument('--solution',action='store_true');args=parser.parse_args()
    code=importlib.import_module('solution' if args.solution else 'exercise')
    names=unittest.defaultTestLoader.getTestCaseNames(Checks)
    suite=unittest.TestSuite(Checks(n) for n in names if args.topic=='all' or n.startswith('test_'+args.topic))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
