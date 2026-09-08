export interface Question{question:string;options:string[]}
export interface Lesson{day:number;title:string;track:string;summary:string;objectives:string[];body:string;steps:string[];deliverable:string;senior:string;sources:string[];lab:string;quiz:Question[];minutes:number}
export interface Lab{id:string;title:string;category:string;kind:string;minutes:number;description:string;goal:string;starter:string;hint:string;limitations:string}
export interface Course{version:string;lessons:Lesson[];labs:Lab[];sources:{id:string;title:string;url:string}[]}
export interface Progress{settings:{start_date:string;daily_hours:0.5|0.75|1|1.5|2|3|5};notes:Record<string,string>;completed:number[];quizzes:Record<string,number>;labs:Record<string,boolean>;reviews:Record<string,{due:string;interval:number;last_score:number}>}
