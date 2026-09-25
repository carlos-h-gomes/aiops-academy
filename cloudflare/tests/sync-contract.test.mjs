import assert from 'node:assert/strict'
import {applySyncOperations,emptySyncState} from '../src/sync.mjs'

const first=applySyncOperations(emptySyncState(),[{operation_id:'operation-001',type:'settings',payload:{settings:{start_date:'2026-09-24',daily_hours:1}}},{operation_id:'operation-002',type:'legacy_complete',payload:{day:1}},{operation_id:'operation-003',type:'legacy_quiz',payload:{day:1,score:80}},{operation_id:'operation-004',type:'legacy_lab',payload:{lab_id:'linux',passed:true}},{operation_id:'operation-005',type:'guided_progress',payload:{unit_id:'data-01',lab_passed:true,note:'Evidência local preservada para a aula guiada.'}}])
assert.deepEqual(first.conflict,null)
assert.deepEqual(first.state.completed,[1])
assert.equal(first.state.quizzes['1'],80)
assert.equal(first.state.labs.linux,true)
assert.equal(first.state.unit_progress['data-01'].lab_passed,true)

const monotonic=applySyncOperations(first.state,[{operation_id:'operation-006',type:'guided_progress',payload:{unit_id:'data-01',lab_passed:false,completed:true}}])
assert.equal(monotonic.state.unit_progress['data-01'].lab_passed,true)
assert.equal(monotonic.state.unit_progress['data-01'].completed,true)

const conflict=applySyncOperations(monotonic.state,[{operation_id:'operation-007',type:'guided_progress',payload:{unit_id:'data-01',note:'Outra evidência concorrente.'}}])
assert.deepEqual(conflict.conflict,{kind:'guided_note',id:'data-01'})
const resolved=applySyncOperations(monotonic.state,[{operation_id:'operation-008',type:'guided_progress',payload:{unit_id:'data-01',note:'Outra evidência concorrente.',replace:true}}])
assert.equal(resolved.state.unit_progress['data-01'].note,'Outra evidência concorrente.')
assert.throws(()=>applySyncOperations(emptySyncState(),[{operation_id:'short',type:'legacy_complete',payload:{day:99}}]))
assert.throws(()=>applySyncOperations(emptySyncState(),[{operation_id:'operation-009',type:'settings',payload:{settings:{start_date:'2026-02-31',daily_hours:1}}}]))
console.log('PASS local sync contract: bounded operations, complete progress and explicit conflicts')
