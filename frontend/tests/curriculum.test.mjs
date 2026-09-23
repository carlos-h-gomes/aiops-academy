import test from 'node:test'
import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {trackUnits,trackSummary,unitComplete} from '../src/services/curriculum.ts'

const catalog=JSON.parse(readFileSync(new URL('../../backend/content/curriculum.json',import.meta.url),'utf8'))
const progress={settings:{start_date:'2035-12-15',daily_hours:0.75},completed:[1,2],notes:{'1':'Synthetic note'},quizzes:{'1':100},labs:{linux:true},reviews:{}}

test('track filtering respects accents, status, ordering and input immutability',()=>{
  const before=JSON.stringify(catalog)
  assert.equal(trackUnits(catalog.units,'data','','available').length,6)
  assert.equal(trackUnits(catalog.units,'data','','planned').length,0)
  assert.equal(trackUnits(catalog.units,'data','transacoes')[0].id,'data-04')
  assert.equal(trackUnits(catalog.units,'infra','NAO-EXISTE').length,0)
  assert.equal(trackUnits([...catalog.units].reverse(),'infra')[0].id,'infra-01')
  assert.equal(JSON.stringify(catalog),before)
})

test('legacy completed days project once without modifying study state',()=>{
  const before=JSON.stringify(progress)
  const summary=trackSummary(trackUnits(catalog.units,'infra'),progress)
  assert.deepEqual(summary,{available:30,planned:0,trackable:30,complete:2,essentialMinutes:5400})
  assert.equal(unitComplete(catalog.units.find(unit=>unit.id==='infra-01'),progress),true)
  assert.equal(unitComplete(catalog.units.find(unit=>unit.id==='infra-03'),progress),false)
  assert.equal(JSON.stringify(progress),before)
})

test('guided nonlegacy lessons do not project into legacy progress',()=>{
  const units=trackUnits(catalog.units,'agents')
  assert.deepEqual(trackSummary(units,progress),{available:8,planned:0,trackable:0,complete:0,essentialMinutes:645})
  assert.equal(unitComplete(units[0],progress),false)
})
