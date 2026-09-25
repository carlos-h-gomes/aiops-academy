import assert from 'node:assert/strict'
import {mergeRemoteProgress,normalizeSyncEndpoint,planSync,takeSyncBatch} from '../src/services/sync.ts'

const local={settings:{start_date:'2026-01-01',daily_hours:1},completed:[1],notes:{'1':'Minha evidência local.'},quizzes:{'1':90},labs:{linux:true},reviews:{'1':{due:'2026-01-02',interval:1,last_score:90}},unit_progress:{'data-01':{lab_passed:true,completed:false,note:'Evidência da aula guiada.',review:null}}}
const remote={settings:null,completed:[2],notes:{'2':'Evidência do outro computador.'},quizzes:{'1':80},labs:{ansible:true},reviews:{'2':{due:'2026-01-03',interval:1,last_score:80}},unit_progress:{'data-01':{lab_passed:false,completed:true,note:'',review:null}}}
assert.equal(normalizeSyncEndpoint('https://sync.example.test/'),'https://sync.example.test')
assert.throws(()=>normalizeSyncEndpoint('http://sync.example.test'))
const planned=planSync(local,remote)
assert.equal(planned.conflicts.length,0)
assert.equal(planned.operations.length,7)
const merged=mergeRemoteProgress(local,remote)
assert.deepEqual(merged.progress.completed,[1,2])
assert.equal(merged.progress.notes['2'],'Evidência do outro computador.')
assert.equal(merged.progress.unit_progress['data-01'].completed,true)
assert.equal(merged.progress.quizzes['1'],90)
assert.equal(merged.progress.labs.linux,true)
assert.equal(merged.progress.labs.ansible,true)
assert.equal(merged.progress.reviews['2'].last_score,80)
const conflict=planSync(local,{...remote,notes:{'1':'Outra evidência','2':'Evidência do outro computador.'}})
assert.deepEqual(conflict.conflicts[0].kind,'legacy_note')
assert.equal(takeSyncBatch(0,planned.operations).operations.length,7)
const many=Array.from({length:51},(_,index)=>({operation_id:`operation-${String(index).padStart(3,'0')}`,type:'legacy_complete',payload:{day:1}}))
assert.equal(takeSyncBatch(0,many).operations.length,50)
console.log('PASS frontend sync planning: explicit endpoint, merge, conflict and bounded batch')
