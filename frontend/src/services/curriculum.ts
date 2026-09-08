import type {LearningUnit} from '../data/curriculum'
import type {Progress} from '../data/types'

export type Availability = 'all'|'available'|'planned'
const normalize = (value:string) => value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('pt-BR')

export function trackUnits(units:LearningUnit[], track:string, query='', status:Availability='all') {
  const term=normalize(query.trim())
  return units.filter(unit=>unit.track_id===track && (status==='all'||unit.status===status)
    && normalize([unit.title,unit.summary,...unit.competencies].join(' ')).includes(term))
    .sort((a,b)=>a.order-b.order)
}

export function unitComplete(unit:LearningUnit, progress:Progress) {
  return unit.status==='available' && unit.lesson_day!==null && progress.completed.includes(unit.lesson_day)
}

export function trackSummary(units:LearningUnit[], progress:Progress) {
  const available=units.filter(unit=>unit.status==='available')
  return {available:available.length,planned:units.length-available.length,
    complete:available.filter(unit=>unitComplete(unit,progress)).length,
    essentialMinutes:available.reduce((total,unit)=>total+(unit.duration_minutes?.essential??0),0)}
}
