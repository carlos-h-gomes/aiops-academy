import type {LearningUnit} from '../data/curriculum'
import type {Progress} from '../data/types'
import {minutesDate} from '../utils/dates.ts'

export type Availability = 'all'|'available'|'planned'
const normalize = (value:string) => value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('pt-BR')

export function trackUnits(units:LearningUnit[], track:string, query='', status:Availability='all') {
  const term=normalize(query.trim())
  return units.filter(unit=>unit.track_id===track && (status==='all'||unit.status===status)
    && normalize([unit.title,unit.summary,...unit.competencies].join(' ')).includes(term))
    .sort((a,b)=>a.order-b.order)
}

export function unitComplete(unit:LearningUnit, progress:Progress) {
  return unit.status==='available' && (unit.lesson_day!==null?progress.completed.includes(unit.lesson_day):progress.unit_progress[unit.id]?.completed===true)
}

export function trackSummary(units:LearningUnit[], progress:Progress) {
  const available=units.filter(unit=>unit.status==='available')
  const trackable=available
  return {available:available.length,planned:units.length-available.length,trackable:trackable.length,
    complete:available.filter(unit=>unitComplete(unit,progress)).length,
    essentialMinutes:available.reduce((total,unit)=>total+(unit.duration_minutes?.essential??0),0)}
}

export function scheduledUnitDate(unit:LearningUnit, allUnits:LearningUnit[], progress:Progress) {
  const ordered=allUnits.filter(item=>item.status==='available')
  const position=ordered.findIndex(item=>item.id===unit.id)
  if(position<0)return null
  const previous=ordered.slice(0,position).reduce((total,item)=>total+(item.duration_minutes?.essential??0),0)
  return minutesDate(progress.settings.start_date,previous,progress.settings.daily_hours)
}
