export type Translation = {locale:'pt-BR'|'en'|'es';status:'available'|'planned';content_version:string|null}
export type LearningUnit = {
  id:string;track_id:string;order:number;title:string;summary:string;status:'available'|'planned'
  content_version:string|null;lesson_day:number|null;competencies:string[];prerequisites:string[]
  duration_minutes:{essential:number;complete:number}|null
  practice:{kind:'simulation';lab_id:string;title:string;limitations:string}|null
  sources:{title:string;url:string}[];translations:Translation[];verified_tool_versions:string[]
}
export type LearningTrack = {id:string;title:string;summary:string;outcome:string;guides:{id:string;title:string}[]}
export type Curriculum = {schema_version:'1.0';version:string;metadata_reviewed_on:string;tracks:LearningTrack[];units:LearningUnit[]}
