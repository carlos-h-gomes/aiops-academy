import type {Progress,UnitProgress} from '../data/types'

const ENDPOINT_KEY='academy-sync-endpoint',TOKEN_KEY='academy-sync-session-token',DEVICE_KEY='academy-sync-device-id',PENDING_KEY='academy-sync-pending'
const LABS=new Set(['linux','ansible','ansible-windows','dql','opensearch','slo','events','workflow','anomaly','rag','incident'])
export const MAX_SYNC_OPERATIONS=50
export const MAX_SYNC_BYTES=64*1024
type Review={due:string;interval:number;last_score:number}
type Settings=Progress['settings']
export type SyncState={settings:Settings|null;completed:number[];notes:Record<string,string>;quizzes:Record<string,number>;labs:Record<string,boolean>;reviews:Record<string,Review>;unit_progress:Record<string,Pick<UnitProgress,'lab_passed'|'completed'|'note'|'review'>>}
export type SyncOperation={operation_id:string;type:'settings'|'legacy_complete'|'legacy_note'|'legacy_quiz'|'legacy_lab'|'legacy_review'|'guided_progress';payload:Record<string,unknown>}
export type SyncConflict={kind:'settings'|'legacy_note'|'legacy_review'|'guided_note'|'guided_review';id:string;local:string;remote:string}
export type PendingSync={revision:number;operations:SyncOperation[]}
type SyncResponse={revision:number;state:SyncState;idempotent?:boolean}
type AccountResponse={session_token:string;handle?:string;recovery_codes?:string[]}

function browserStorage(kind:'localStorage'|'sessionStorage'){try{return window[kind]}catch{return null}}
function newId(){try{return crypto.randomUUID()}catch{return `sync-${Date.now()}-${Math.random().toString(36).slice(2,10)}`}}
function same(left:unknown,right:unknown){return JSON.stringify(left)===JSON.stringify(right)}
function byteLength(value:unknown){return new TextEncoder().encode(JSON.stringify(value)).byteLength}
function label(value:unknown){return typeof value==='string'?value:JSON.stringify(value)}
function blankState():SyncState{return {settings:null,completed:[],notes:{},quizzes:{},labs:{},reviews:{},unit_progress:{}}}
function validState(value:unknown):value is SyncState{const state=value as Partial<SyncState>;return !!value&&typeof value==='object'&&Array.isArray(state.completed)&&typeof state.notes==='object'&&typeof state.quizzes==='object'&&typeof state.labs==='object'&&typeof state.reviews==='object'&&typeof state.unit_progress==='object'&&('settings'in state)}

export function normalizeSyncEndpoint(value:string){let url:URL;try{url=new URL(value.trim())}catch{throw new Error('Informe um endereço HTTPS válido para a sincronização.')}if(url.protocol!=='https:'||url.username||url.password||url.search||url.hash)throw new Error('Use somente a origem HTTPS do serviço de sincronização, sem senha, consulta ou fragmento.');return `${url.origin}${url.pathname.replace(/\/$/,'')}`}
export function savedSyncEndpoint(){return browserStorage('localStorage')?.getItem(ENDPOINT_KEY)||''}
export function saveSyncEndpoint(value:string){browserStorage('localStorage')?.setItem(ENDPOINT_KEY,normalizeSyncEndpoint(value))}
export function clearSyncEndpoint(){browserStorage('localStorage')?.removeItem(ENDPOINT_KEY)}
export function hasSession(){return !!browserStorage('sessionStorage')?.getItem(TOKEN_KEY)}
function sessionToken(){return browserStorage('sessionStorage')?.getItem(TOKEN_KEY)||''}
function saveToken(value:string){browserStorage('sessionStorage')?.setItem(TOKEN_KEY,value)}
export function clearSession(){browserStorage('sessionStorage')?.removeItem(TOKEN_KEY)}
function deviceId(){const store=browserStorage('localStorage');let value=store?.getItem(DEVICE_KEY)||'';if(!/^[a-z0-9][a-z0-9_-]{7,63}$/i.test(value)){value=`device-${newId()}`.replace(/[^a-z0-9_-]/gi,'').slice(0,64);store?.setItem(DEVICE_KEY,value)}return value}
async function remote<T>(endpoint:string,path:string,body:unknown,token=sessionToken()):Promise<T>{const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);try{const response=await fetch(`${endpoint}${path}`,{method:'POST',headers:{'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`}:{})},body:JSON.stringify(body),signal:controller.signal});const data=await response.json().catch(()=>({}));if(!response.ok){const error=new Error(typeof data.detail==='string'?data.detail:'Não foi possível falar com o serviço de sincronização.');Object.assign(error,{status:response.status,data});throw error}return data as T}catch(error){if(error instanceof DOMException||error instanceof TypeError)throw new Error('Não foi possível alcançar o serviço de sincronização. Confira o endereço e a conexão.');throw error}finally{clearTimeout(timer)}}
export async function registerSyncAccount(endpoint:string,handle:string,password:string){const data=await remote<AccountResponse>(endpoint,'/auth/register',{handle,password},'');saveToken(data.session_token);return data}
export async function loginSyncAccount(endpoint:string,handle:string,password:string){const data=await remote<AccountResponse>(endpoint,'/auth/login',{handle,password},'');saveToken(data.session_token);return data}
export async function recoverSyncAccount(endpoint:string,handle:string,recovery_code:string,new_password:string){const data=await remote<AccountResponse>(endpoint,'/auth/recover',{handle,recovery_code,new_password},'');saveToken(data.session_token);return data}
export async function logoutSyncAccount(endpoint:string){try{await remote<{signed_out:boolean}>(endpoint,'/auth/logout',{})}finally{clearSession()}}
export async function pullSync(endpoint:string){return remote<SyncResponse>(endpoint,'/sync/pull',{})}
export async function pushSync(endpoint:string,pending:PendingSync){return remote<SyncResponse>(endpoint,'/sync/push',{base_revision:pending.revision,device_id:deviceId(),operations:pending.operations})}
function operation(type:SyncOperation['type'],payload:Record<string,unknown>):SyncOperation{return {operation_id:newId(),type,payload}}
function conflict(kind:SyncConflict['kind'],id:string,local:unknown,remote:unknown){return {kind,id,local:label(local),remote:label(remote)}}
export function planSync(local:Progress,remoteInput:SyncState,preference:'ask'|'local'='ask'){
  const remote={...blankState(),...remoteInput},operations:SyncOperation[]=[];const conflicts:SyncConflict[]=[]
  if(!remote.settings)operations.push(operation('settings',{settings:local.settings}));else if(!same(local.settings,remote.settings)){if(preference==='local')operations.push(operation('settings',{settings:local.settings,replace:true}));else conflicts.push(conflict('settings','preferências',local.settings,remote.settings))}
  for(const day of local.completed)if(!remote.completed.includes(day))operations.push(operation('legacy_complete',{day}))
  for(const [day,text] of Object.entries(local.notes))if(text){const other=remote.notes[day]||'';if(other&&other!==text){if(preference==='local')operations.push(operation('legacy_note',{day:Number(day),text,replace:true}));else conflicts.push(conflict('legacy_note',day,text,other))}else if(!other)operations.push(operation('legacy_note',{day:Number(day),text}))}
  for(const [day,score] of Object.entries(local.quizzes))if(score>(remote.quizzes[day]||0))operations.push(operation('legacy_quiz',{day:Number(day),score}))
  for(const [id,passed] of Object.entries(local.labs))if(passed&&LABS.has(id)&&!remote.labs[id])operations.push(operation('legacy_lab',{lab_id:id,passed:true}))
  for(const [day,review] of Object.entries(local.reviews)){const other=remote.reviews[day];if(!other)operations.push(operation('legacy_review',{day:Number(day),review}));else if(!same(review,other)){if(preference==='local')operations.push(operation('legacy_review',{day:Number(day),review,replace:true}));else conflicts.push(conflict('legacy_review',day,review,other))}}
  for(const [unit_id,state] of Object.entries(local.unit_progress)){const other=remote.unit_progress[unit_id]||{lab_passed:false,completed:false,note:'',review:null};const payload:Record<string,unknown>={unit_id};if(state.lab_passed&&!other.lab_passed)payload.lab_passed=true;if(state.completed&&!other.completed)payload.completed=true;if(state.note){if(other.note&&other.note!==state.note){if(preference==='local')payload.note=state.note,payload.replace=true;else conflicts.push(conflict('guided_note',unit_id,state.note,other.note))}else if(!other.note)payload.note=state.note}if(state.review){if(other.review&&!same(state.review,other.review)){if(preference==='local')payload.review=state.review,payload.replace=true;else conflicts.push(conflict('guided_review',unit_id,state.review,other.review))}else if(!other.review)payload.review=state.review}if(Object.keys(payload).length>1)operations.push(operation('guided_progress',payload))}
  return {operations,conflicts}
}
export function mergeRemoteProgress(local:Progress,remoteInput:SyncState,preference:'local'|'remote'='local'){
  const remote={...blankState(),...remoteInput};const next:Progress=structuredClone(local),conflicts:SyncConflict[]=[]
  if(remote.settings&&!same(next.settings,remote.settings)){conflicts.push(conflict('settings','preferências',next.settings,remote.settings));if(preference==='remote')next.settings=remote.settings}
  next.completed=[...new Set([...next.completed,...remote.completed])].sort((a,b)=>a-b)
  for(const [day,text] of Object.entries(remote.notes)){const current=next.notes[day]||'';if(current&&current!==text){conflicts.push(conflict('legacy_note',day,current,text));if(preference==='remote')next.notes[day]=text}else if(!current)next.notes[day]=text}
  for(const [day,score] of Object.entries(remote.quizzes))next.quizzes[day]=Math.max(next.quizzes[day]||0,score)
  for(const [id,passed] of Object.entries(remote.labs))if(passed)next.labs[id]=true
  for(const [day,review] of Object.entries(remote.reviews)){const current=next.reviews[day];if(current&&!same(current,review)){conflicts.push(conflict('legacy_review',day,current,review));if(preference==='remote')next.reviews[day]=review}else if(!current)next.reviews[day]=review}
  for(const [id,other] of Object.entries(remote.unit_progress)){const current=next.unit_progress[id]||{lab_passed:false,completed:false,note:'',review:null};if(current.note&&other.note&&current.note!==other.note){conflicts.push(conflict('guided_note',id,current.note,other.note));if(preference==='remote')current.note=other.note}else if(!current.note)current.note=other.note;if(current.review&&other.review&&!same(current.review,other.review)){conflicts.push(conflict('guided_review',id,current.review,other.review));if(preference==='remote')current.review=other.review}else if(!current.review)current.review=other.review;next.unit_progress[id]={...current,lab_passed:current.lab_passed||other.lab_passed,completed:current.completed||other.completed}}
  return {progress:next,conflicts}
}
export function takeSyncBatch(revision:number,operations:SyncOperation[]){const batch:SyncOperation[]=[];for(const item of operations){if(batch.length===MAX_SYNC_OPERATIONS||byteLength([...batch,item])>MAX_SYNC_BYTES)break;batch.push(item)}return {revision,operations:batch}}
export function loadPendingSync():PendingSync|null{try{const value=JSON.parse(browserStorage('localStorage')?.getItem(PENDING_KEY)||'null');return value&&Number.isInteger(value.revision)&&value.revision>=0&&Array.isArray(value.operations)?value:null}catch{return null}}
export function savePendingSync(value:PendingSync|null){const store=browserStorage('localStorage');if(!value){store?.removeItem(PENDING_KEY);return}const batch=takeSyncBatch(value.revision,value.operations);if(batch.operations.length!==value.operations.length)throw new Error('A fila local excede o limite de sincronização.');store?.setItem(PENDING_KEY,JSON.stringify(value))}
export function pendingCount(){return loadPendingSync()?.operations.length||0}
export function isSyncState(value:unknown){return validState(value)}
