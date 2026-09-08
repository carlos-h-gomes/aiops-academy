import {useState, useEffect} from 'react'
import {Download, Search, BookOpen} from 'lucide-react'
import {useAcademy} from '../context/AcademyContext'
import {request} from '../api/client'
import {PageTitle, Message, External} from '../components/ui/Common'
import {Markdown} from '../components/ui/Markdown'
import '../assets/library.css'

type Manual = {id:string; title:string; body:string; summary?:string; category?:string; minutes?:number; recommended_after?:number; sources?:{title:string; url:string}[]}
const searchable = (text:string) => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()

export function LibraryPage({manualId}:{manualId?:string}) {
  const {course} = useAcademy()
  const [manuals, setManuals] = useState<Manual[]>([])
  const [selected, setSelected] = useState(manualId??'start')
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('all')
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  async function load() {
    setLoading(true); setError('')
    try {setManuals(await request('/manuals'))}
    catch(e) {setError((e as Error).message)}
    finally {setLoading(false)}
  }
  useEffect(() => {void load()}, [])
  useEffect(() => {setSelected(manualId??'start')}, [manualId])
  const m = manuals.find(x => x.id === selected)
  const matches = manuals.filter(x => (category === 'all' || (x.category ?? 'core') === category) && searchable(`${x.title} ${x.summary ?? ''} ${x.body}`).includes(searchable(query)))
  const groups = [{id:'core', title:'Manuais essenciais'}, {id:'extension', title:'Aprofundamentos AIOps'}, {id:'tooling', title:'Ferramentas e processos'}]
  const extensions = manuals.filter(x => x.category === 'extension')
  const sources = [...new Map([...course.sources, ...manuals.flatMap(x => x.sources ?? [])].map(s => [s.url, s])).values()]
    .filter(s => searchable(s.title).includes(searchable(search)))
  return <>
    <PageTitle eyebrow="REFERÊNCIA PARA USAR, NÃO ACUMULAR" title="Seu manual de operações." description="Guias essenciais e aprofundamentos práticos para continuar evoluindo. Conteúdo disponível localmente." action={<a className="primary" href="/api/v1/kit"><Download size={17}/>Baixar kit de laboratórios</a>}/>
    <Message text={error} error/>
    {error && <button className="secondary" onClick={() => void load()}>Tentar novamente</button>}
    {extensions.length > 0 && <p className="library-extension-note">Além dos 30 dias · {extensions.length} aprofundamentos opcionais · {extensions.reduce((sum, x) => sum + (x.minutes ?? 0), 0) / 60} horas extras. Escolha após as bases; eles não alteram a conclusão da trilha.</p>}
    <label className="search"><Search size={18}/><input aria-label="Buscar na biblioteca" placeholder="Buscar tema, conceito ou exercício…" value={query} onChange={e => setQuery(e.target.value)}/></label>
    <div className="library-filters" role="group" aria-label="Filtrar manuais por categoria">
      {[{id:'all', title:'Todos'}, ...groups].map(group => <button className="secondary" key={group.id} aria-pressed={category === group.id} onClick={() => setCategory(group.id)}>{group.title}</button>)}
    </div>
    <p className="muted small" role="status">{loading ? 'Consultando catálogo…' : `${matches.length} conteúdos encontrados`}</p>
    <div className="library-layout">
      <nav className="manual-nav" aria-label="Manuais de estudo">
        {groups.map(category => {
          const group = matches.filter(x => (x.category ?? 'core') === category.id)
          return group.length > 0 && <div className="manual-group" key={category.id}>
            <h2>{category.title}</h2>
            {group.map(x => <button className={selected === x.id ? 'selected' : ''} aria-current={selected === x.id ? 'true' : undefined} onClick={() => setSelected(x.id)} key={x.id}><BookOpen size={16}/>{x.title}</button>)}
          </div>
        })}
        {!loading && matches.length === 0 && <div><p>Nenhum conteúdo para estes filtros.</p><button className="secondary" onClick={() => {setQuery(''); setCategory('all')}}>Limpar filtros</button></div>}
      </nav>
      <article className="panel manual-content" aria-label={m?.title ?? 'Leitura selecionada'}>
        {loading ? <p role="status">Carregando manuais…</p> : m ? <>
          {m.category === 'extension' && <div className="manual-meta"><p><strong>Aprofundamento opcional · {m.minutes} min</strong></p><p>{m.summary}</p><a href={`#/day/${m.recommended_after}`}>Base recomendada: concluir até o dia {m.recommended_after}</a><p>Prática no kit baixável, com Python no computador. O resultado não é enviado ao app.</p></div>}
          {m.category === 'tooling' && <div className="manual-meta"><p><strong>Ferramentas e processos · {m.minutes} min</strong></p><p>{m.summary}</p><p>Exercício de desenho e decisão com solução comentada. Não executa o produto real.</p><a href={`#/day/${m.recommended_after}`}>Base recomendada: concluir até o dia {m.recommended_after}</a></div>}
          <Markdown text={m.body}/>
          {!!m.sources?.length && <section className="manual-sources"><h2>Fontes deste conteúdo</h2>{m.sources.map(s => <External href={s.url} key={s.url}>{s.title}</External>)}</section>}
        </> : <div><p>Manual não encontrado. Selecione outro conteúdo na lista.</p><button className="secondary" onClick={()=>setSelected('start')}>Abrir guia de estudo</button></div>}
      </article>
    </div>
    <section className="sources-section">
      <div className="section-heading"><h2>Aprenda também com quem constrói.</h2><span className="muted">Fontes oficiais · exigem internet</span></div>
      <label className="search"><Search size={18}/><input aria-label="Buscar fontes" placeholder="Buscar Ansible, Dynatrace, AWS, GCP…" value={search} onChange={e => setSearch(e.target.value)}/></label>
      <div className="source-grid">{sources.map(s => <External href={s.url} key={s.url}>{s.title}</External>)}</div>
      {sources.length === 0 && <p className="muted">Nenhuma fonte para este termo.</p>}
    </section>
  </>
}
