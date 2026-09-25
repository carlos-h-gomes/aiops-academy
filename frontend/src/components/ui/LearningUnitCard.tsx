import {ArrowUpRight} from 'lucide-react'
import type {LearningUnit} from '../../data/curriculum'
import {Badge,External} from './Common'

export function LearningUnitCard({unit,units,complete,scheduledDate}:{unit:LearningUnit;units:LearningUnit[];complete:boolean;scheduledDate?:string|null}) {
  return <article className="panel curriculum-unit" id={unit.id} aria-labelledby={`title-${unit.id}`}>
    <div className="curriculum-unit-heading"><span className="eyebrow">UNIDADE {String(unit.order).padStart(2,'0')}</span><Badge tone={complete?'lime-badge':''}>{complete?'Concluída':unit.status==='available'?'Disponível':'Em preparação'}</Badge></div>
    <h3 id={`title-${unit.id}`}>{unit.title}</h3>
    <p className="muted">{unit.summary}</p>
    {scheduledDate&&<p className="small">Início sugerido: <strong>{scheduledDate}</strong></p>}
    <ul className="curriculum-competencies">{unit.competencies.map(item=><li key={item}>{item}</li>)}</ul>
    {unit.duration_minutes?<p className="small">{unit.duration_minutes.essential/60}h no essencial · {unit.duration_minutes.complete/60}h no completo. Divida em sessões.</p>:<p className="small muted">Conteúdo e duração ainda em preparação.</p>}
    {unit.status==='available'&&<a className="primary" href={unit.lesson_day!==null?`#/day/${unit.lesson_day}`:`#/unit/${unit.id}`}>{complete?'Revisitar aula':'Abrir aula'}<span className="sr-only">: {unit.title}</span><ArrowUpRight size={16}/></a>}
    <details>
      <summary>Pré-requisitos e detalhes<span className="sr-only">: {unit.title}</span></summary>
      <p className="small">Bases recomendadas; você pode explorar as aulas disponíveis sem concluir a sequência.</p>
      {unit.prerequisites.length?<ul>{unit.prerequisites.map(id=>{const prerequisite=units.find(item=>item.id===id)!;return <li key={id}>{prerequisite.status==='available'?<a href={prerequisite.lesson_day!==null?`#/day/${prerequisite.lesson_day}`:`#/unit/${prerequisite.id}`}>{prerequisite.title}</a>:<span>{prerequisite.title} · em preparação</span>}</li>})}</ul>:<p className="small">Nenhum pré-requisito.</p>}
      {unit.practice&&<><p><strong>Prática: {unit.practice.kind==='simulation'?'simulação no navegador':'fixture local guiada'}</strong> · {unit.practice.title}</p><p className="small muted">{unit.practice.limitations}</p></>}
      {unit.sources.length>0&&<div aria-label="Fontes da unidade">{unit.sources.map(source=><External key={source.url} href={source.url}>{source.title}</External>)}</div>}
      <p className="small muted">{unit.content_version?`Conteúdo ${unit.content_version} · Português disponível. Inglês e espanhol em preparação.`:'Português, inglês e espanhol em preparação.'}</p>
      <p className="small muted">{unit.verified_tool_versions.length?unit.verified_tool_versions.join(' · '):'Versões de ferramentas reais não verificadas neste catálogo.'}</p>
    </details>
  </article>
}
