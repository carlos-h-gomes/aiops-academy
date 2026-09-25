import {ArrowLeft,FlaskConical,RotateCcw} from 'lucide-react'
import {useState} from 'react'
import {useUnitLab} from '../hooks/useUnitLab'
import {Message,PageTitle} from '../components/ui/Common'
import {useAcademy} from '../context/AcademyContext'

export function UnitLabPage({unitId}:{unitId:string}) {
  const {lab,error,loading,running,result,run,retry,clearResult}=useUnitLab(unitId)
  const {refresh}=useAcademy()
  const [answers,setAnswers]=useState<Record<string,string>>({})
  const reset=()=>{setAnswers({});clearResult()}
  if(loading)return <><PageTitle eyebrow="LAB GUIADO" title="Carregando lab" description="Preparando um cenário local…"/><p role="status">Carregando lab…</p></>
  if(error&&!lab)return <><PageTitle eyebrow="LAB GUIADO" title="Lab indisponível" description="Não foi possível carregar este cenário local."/><Message text={error} error/><button className="primary" onClick={retry}>Tentar novamente</button><a className="back-link" href={`#/unit/${unitId}`}>Voltar à aula</a></>
  if(!lab)return null
  const unanswered=lab.questions.filter(question=>!answers[question.id]).length
  async function submit(){const value=await run(answers);if(value?.correct)await refresh()}
  return <><a className="back-link" href={`#/unit/${unitId}`}><ArrowLeft size={16}/>Voltar à aula</a><PageTitle eyebrow={`LAB GUIADO · ${unitId.toUpperCase()}`} title={lab.title} description={lab.intro}/><div className="notice"><strong>Prática local com progresso</strong><p>{lab.limitations}</p><p>As escolhas somem ao reiniciar. Quando as decisões estiverem corretas, o resultado libera a conclusão da aula, sem executar comandos ou guardar suas respostas.</p></div><form className="unit-lab-form" onSubmit={event=>{event.preventDefault();if(!unanswered)void submit()}}><section className="lesson-paper"><div className="objectives"><p className="eyebrow">DECIDA COM BASE NA FIXTURE</p><p><FlaskConical size={16}/>Cenário fechado · feedback explicável</p></div>{lab.questions.map((question,index)=><fieldset key={question.id} className="unit-lab-question"><legend>{index+1}. {question.prompt}</legend>{question.options.map(option=><label key={option.value} className="answer"><input type="radio" name={question.id} value={option.value} checked={answers[question.id]===option.value} onChange={()=>{setAnswers(value=>({...value,[question.id]:option.value}));clearResult()}}/>{option.label}</label>)}</fieldset>)}<div className="action-row"><button className="primary" type="submit" disabled={running||unanswered>0}>{running?'Conferindo…':unanswered?`Responda ${unanswered} item(ns)`:'Conferir decisões'}</button><button className="secondary" type="button" onClick={reset}><RotateCcw size={16}/>Reiniciar escolhas</button></div>{error&&<Message text={error} error/>}{result&&<div className={result.correct?'notice unit-lab-result':'notice error unit-lab-result'} role="status"><strong>{result.correct?'Decisões conferidas':'Há decisões a revisar'}</strong><p>{result.feedback}</p>{result.correct&&<p>Volte à aula para salvar sua evidência e concluí-la.</p>}{!result.correct&&<p>Itens: {result.reviewed_fields.join(', ')}.</p>}</div>}</section></form></>
}
