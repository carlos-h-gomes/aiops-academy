import {useEffect, useState} from 'react'
import {Save} from 'lucide-react'
import {ESSENTIAL_STUDY_MINUTES,planEnd, studyDays, validStudyStart} from '../../utils/dates'
import type {Progress} from '../../data/types'

type Settings = Progress['settings']
const rates = [{hours:0.5,label:'Leve · 30 min'}, {hours:0.75,label:'Leve · 45 min'}, {hours:1,label:'Regular · 1h'}, {hours:1.5,label:'Regular · 1h30'}, {hours:2,label:'Dedicado · 2h'}, {hours:3,label:'Intensivo essencial · 3h'}, {hours:5,label:'Intensivo completo · 5h'}] as const

export function CalendarSettings({settings,busy,onSave}:{settings:Settings;busy:boolean;onSave:(value:Settings)=>void}) {
  const [start,setStart] = useState(settings.start_date)
  const [hours,setHours] = useState<Settings['daily_hours']>(settings.daily_hours)
  useEffect(()=>{setStart(settings.start_date);setHours(settings.daily_hours)},[settings.start_date,settings.daily_hours])
  const valid = validStudyStart(start)
  const end = valid ? new Date(planEnd(start,hours)+'T12:00:00').toLocaleDateString('pt-BR') : 'escolha uma data'
  return <section className="panel">
    <h2>Seu calendário</h2>
    <label className="form-label" htmlFor="start-date">Início do percurso</label>
    <input id="start-date" type="date" min="2000-01-01" max="2100-12-31" value={start} disabled={busy} aria-invalid={!valid} aria-describedby={!valid?'start-error':undefined} onChange={e=>setStart(e.target.value)}/>
    {!valid&&<p id="start-error" role="alert">Escolha uma data válida entre 01/01/2000 e 31/12/2100.</p>}
    <label className="form-label" htmlFor="daily-hours">Disponibilidade por dia</label>
    <select id="daily-hours" value={hours} disabled={busy} onChange={e=>setHours(Number(e.target.value) as Settings['daily_hours'])}>{rates.map(rate=><option key={rate.hours} value={rate.hours}>{rate.label}</option>)}</select>
    <p className="muted">Essencial: estimativa de {(ESSENTIAL_STUDY_MINUTES/60).toLocaleString('pt-BR')}h para as 50 aulas, prática e evidências. Divida cada aula em sessões; aprofundamentos são opcionais.</p>
    <p role="status" className="small">{busy?'Salvando preferências…':`Previsão de término: ${end} · ${studyDays(hours)} dias de estudo.`}</p>
    <div className="notice">Esta previsão considera estudo todos os dias, a partir da data escolhida. Uma aula pode ocupar várias sessões. Folgas e pausas prolongam o prazo; o calendário não bloqueia atividades nem apaga seu progresso.</div>
    <button className="primary" disabled={busy||!valid} onClick={()=>onSave({start_date:start,daily_hours:hours})}><Save size={17}/>Salvar preferências</button>
  </section>
}
