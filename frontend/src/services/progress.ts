import type{Course,Progress}from'../data/types'
import{localDate}from'../utils/dates'
export function nextLesson(c:Course,p:Progress){return c.lessons.find(l=>!p.completed.includes(l.day))||c.lessons[29]}
export function dueReviews(p:Progress){return Object.entries(p.reviews).filter(([,r])=>r.due<=localDate()).map(([id])=>Number(id))}
export const stages=[{title:'Construa a base',range:[1,7],subtitle:'Linux · redes · Python · Git'},{title:'Automatize com Ansible',range:[8,14],subtitle:'Playbooks · roles · AAP · Windows'},{title:'Enxergue o sistema',range:[15,21],subtitle:'Dynatrace · DQL · SLO · AWS'},{title:'Conecte e resolva',range:[22,28],subtitle:'GCP · eventos · IA · incidentes'},{title:'Demonstre sua evolução',range:[29,30],subtitle:'Projeto final · próximos passos'}]
