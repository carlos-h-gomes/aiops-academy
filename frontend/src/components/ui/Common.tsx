import type{ReactNode}from'react'
import{ArrowUpRight,CheckCircle2,Clock3}from'lucide-react'
export function PageTitle({eyebrow,title,description,action}:{eyebrow:string;title:string;description:string;action?:ReactNode}){return <header className="page-heading"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="muted">{description}</p></div>{action}</header>}
export function Badge({children,tone=''}:{children:ReactNode;tone?:string}){return <span className={'badge '+tone}>{children}</span>}
export function Message({text,error=false}:{text:string;error?:boolean}){return text?<div className={'notice '+(error?'error':'')} role={error?'alert':'status'}>{text}</div>:null}
export function Time({minutes}:{minutes:number}){return <span className="time"><Clock3 size={14}/>{minutes>=60?`${minutes/60}h`:`${minutes} min`}</span>}
export function Check({done}:{done:boolean}){return done?<CheckCircle2 size={19} className="lime" aria-label="Concluído"/>:<span className="empty-check" role="img" aria-label="Pendente"/>}
export function External({href,children}:{href:string;children:ReactNode}){return <a className="source-link" href={href} target="_blank" rel="noopener noreferrer">{children}<ArrowUpRight size={16}/></a>}
export function Meter({value,label}:{value:number;label:string}){return <div className="meter" role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={value}><span style={{width:`${Math.min(100,Math.max(0,value))}%`}}/></div>}
