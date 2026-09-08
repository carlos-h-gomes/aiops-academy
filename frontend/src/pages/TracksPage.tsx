import {useState} from 'react'
import {ArrowLeft,ArrowUpRight,BookOpen,Search} from 'lucide-react'
import {useAcademy} from '../context/AcademyContext'
import {useCurriculum} from '../hooks/useCurriculum'
import {trackUnits,trackSummary,unitComplete,type Availability} from '../services/curriculum'
import {PageTitle,Message,Meter} from '../components/ui/Common'
import {LearningUnitCard} from '../components/ui/LearningUnitCard'
import '../assets/curriculum.css'

export function TracksPage({trackId}:{trackId?:string}) {
  const {progress}=useAcademy()
  const {catalog,error,loading,retry}=useCurriculum()
  const [query,setQuery]=useState('')
  const [status,setStatus]=useState<Availability>('all')
  if(loading)return <><PageTitle eyebrow="ESCOLHA SEU PERCURSO" title="Trilhas de estudo" description="Aprenda por objetivo e retome no seu ritmo."/><p role="status">Carregando trilhas…</p></>
  if(error||!catalog)return <><PageTitle eyebrow="ESCOLHA SEU PERCURSO" title="Trilhas de estudo" description="Não foi possível carregar o catálogo."/><Message text={error||'Catálogo indisponível.'} error/><button className="primary" onClick={retry}>Tentar novamente</button><a className="back-link" href="#/trail">Abrir trilha de infraestrutura</a></>
  const track=catalog.tracks.find(item=>item.id===trackId)
  if(trackId&&!track)return <div className="empty-state"><h1>Trilha não encontrada</h1><a className="secondary" href="#/tracks">Voltar às trilhas</a></div>
  if(!track)return <>
    <PageTitle eyebrow="UMA BASE. VÁRIOS CAMINHOS." title="Escolha o que quer construir." description="Infraestrutura, dados, segurança e agentes. Veja o que já pode estudar e o que está em preparação."/>
    <div className="notice">{catalog.units.filter(unit=>unit.status==='available').length} aulas disponíveis · {catalog.units.filter(unit=>unit.status==='planned').length} unidades em preparação. Guias complementares já podem ser estudados nas quatro trilhas.</div>
    <div className="curriculum-tracks">{catalog.tracks.map(item=>{const summary=trackSummary(trackUnits(catalog.units,item.id),progress);return <article className="panel curriculum-track" key={item.id}>
      <BookOpen size={24} aria-hidden="true"/><h2>{item.title}</h2><p className="muted">{item.summary}</p>
      <p className="small">{summary.available} aulas disponíveis · {summary.planned} em preparação</p>
      {summary.available>0?<><p className="small">{summary.complete}/{summary.available} aulas concluídas · {summary.essentialMinutes/60}h essenciais</p><Meter value={summary.complete/summary.available*100} label={`Progresso: ${item.title}`}/></>:<p className="small">Comece pelos {item.guides.length} guias complementares.</p>}
      <a className="primary" href={`#/tracks/${item.id}`}>Explorar trilha<span className="sr-only">: {item.title}</span><ArrowUpRight size={17}/></a>
    </article>})}</div>
    <p className="small muted curriculum-footnote">O calendário em Preferências acompanha o percurso de Infraestrutura e AIOps. Trocar de página não altera suas notas, datas ou conclusões.</p>
  </>
  const all=trackUnits(catalog.units,track.id)
  const matches=trackUnits(catalog.units,track.id,query,status)
  const summary=trackSummary(all,progress)
  return <>
    <a className="back-link" href="#/tracks"><ArrowLeft size={16}/>Todas as trilhas</a>
    <PageTitle eyebrow="APRENDER, PRATICAR, EXPLICAR" title={track.title} description={track.summary}/>
    <div className="notice"><strong>Ao longo deste percurso</strong><p>{track.outcome}</p><p>{summary.available} aulas disponíveis · {summary.planned} em preparação.{summary.available>0?` ${summary.complete}/${summary.available} aulas concluídas.`:' As novas aulas ainda não podem ser iniciadas; explore os guias abaixo.'}</p></div>
    {track.id==='infra'&&<a className="secondary" href="#/trail">Ver calendário das 30 aulas</a>}
    <section className="curriculum-guides" aria-labelledby="guides-title"><h2 id="guides-title">Guias para estudar agora</h2><p className="muted small">Conteúdos complementares da Biblioteca. Eles não substituem as novas aulas nem contam como sua conclusão.</p><ul>{track.guides.map(guide=><li key={guide.id}><a href={`#/library/${guide.id}`}>{guide.title}<ArrowUpRight size={15}/></a></li>)}</ul></section>
    <h2>Unidades do percurso</h2>
    <div className="toolbar"><label className="search"><Search size={18}/><input aria-label="Buscar unidades" placeholder="Buscar tema ou competência…" value={query} onChange={event=>setQuery(event.target.value)}/></label><label className="filter-label">Disponibilidade<select value={status} onChange={event=>setStatus(event.target.value as Availability)}><option value="all">Todas</option><option value="available">Disponíveis</option><option value="planned">Em preparação</option></select></label></div>
    <p className="small muted" role="status">{matches.length} unidades encontradas</p>
    {matches.length?<div className="curriculum-units">{matches.map(unit=><LearningUnitCard unit={unit} units={catalog.units} complete={unitComplete(unit,progress)} key={unit.id}/>)}</div>:<div className="empty-state"><h3>Nenhuma unidade para estes filtros</h3><button className="secondary" onClick={()=>{setQuery('');setStatus('all')}}>Limpar filtros</button></div>}
  </>
}
