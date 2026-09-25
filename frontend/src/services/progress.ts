import type{Course,Progress}from'../data/types'
import{localDate}from'../utils/dates'
export function nextLesson(c:Course,p:Progress){return c.lessons.find(l=>!p.completed.includes(l.day))||c.lessons[29]}
export type ReviewItem={kind:'lesson'|'unit';id:string;due:string;interval:number;last_score:number}
export function reviewItems(p:Progress){return [...Object.entries(p.reviews).map(([id,review])=>({...review,kind:'lesson' as const,id})),...Object.entries(p.unit_progress).flatMap(([id,state])=>state.review?[{...state.review,kind:'unit' as const,id}]:[])].sort((left,right)=>left.due.localeCompare(right.due))}
export function dueReviews(p:Progress){return reviewItems(p).filter(item=>item.due<=localDate())}
export const stages=[{title:'Construa a base',range:[1,7],subtitle:'Linux · redes · Python · Git'},{title:'Automatize com Ansible',range:[8,14],subtitle:'Playbooks · roles · AAP · Windows'},{title:'Enxergue o sistema',range:[15,21],subtitle:'Dynatrace · DQL · SLO · AWS'},{title:'Conecte e resolva',range:[22,28],subtitle:'GCP · eventos · IA · incidentes'},{title:'Demonstre sua evolução',range:[29,30],subtitle:'Projeto final · próximos passos'}]
