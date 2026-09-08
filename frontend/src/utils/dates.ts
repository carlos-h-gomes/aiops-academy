export function localDate(d=new Date()){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
export function validStudyStart(iso:string){return /^\d{4}-\d{2}-\d{2}$/.test(iso)&&iso>='2000-01-01'&&iso<='2100-12-31'&&localDate(new Date(iso+'T12:00:00'))===iso}
export function studyDays(hours=3){return hours>=3?30:Math.ceil(90/hours)}
export function shortDate(iso:string){return new Date(iso+'T12:00:00').toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})}
export function dayDate(start:string,day:number,hours=3){const d=new Date(start+'T12:00:00');d.setDate(d.getDate()+(hours>=3?day-1:Math.floor((day-1)*3/hours)));return shortDate(localDate(d))}
export function planEnd(start:string,hours=3){const d=new Date(start+'T12:00:00');d.setDate(d.getDate()+studyDays(hours)-1);return localDate(d)}
export function daysLeft(target:string){return Math.round((Date.parse(target)-Date.parse(localDate()))/86400000)}
export function download(name:string,content:string,type='application/json'){const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
