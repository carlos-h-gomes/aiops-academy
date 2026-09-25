import {webcrypto} from 'node:crypto'
import assert from 'node:assert/strict'

globalThis.crypto??=webcrypto
const {default:worker}=await import('../src/worker.mjs')
const LOGIN_FAILURE_LIMIT=5

class MemoryD1{
 constructor(){this.accounts=new Map();this.credentials=new Map();this.codes=[];this.sessions=[];this.throttles=new Map();this.snapshots=new Map();this.operations=new Map()}
 prepare(sql){return new Statement(this,sql)}
 async batch(statements){return Promise.all(statements.map(statement=>statement.run()))}
 first(sql,args){
  if(sql.startsWith('SELECT user_id FROM accounts WHERE handle')){const userId=this.accounts.get(args[0]);return userId?{user_id:userId}:null}
  if(sql.startsWith('SELECT a.user_id')){const userId=this.accounts.get(args[0]);return userId?{user_id:userId,verifier:this.credentials.get(userId)}:null}
  if(sql.startsWith('SELECT failures'))return this.throttles.get(args[0])||null
  if(sql.startsWith('SELECT revision,state_json FROM progress_snapshots'))return this.snapshots.get(args[0])||null
  if(sql.startsWith('SELECT operation_id FROM progress_operations'))return this.operations.has(`${args[0]}:${args[1]}`)?{operation_id:args[1]}:null
  if(sql.startsWith('SELECT user_id FROM sessions')){const session=this.sessions.find(item=>item.hash===args[0]&&!item.revoked&&item.expires>args[1]);return session?{user_id:session.userId}:null}
  return null
 }
 all(sql,args){if(sql.startsWith('SELECT code_hash FROM recovery_codes'))return {results:this.codes.filter(item=>item.userId===args[0]&&!item.used).map(item=>({code_hash:item.hash}))};return {results:[]}}
 run(sql,args){
  if(sql.startsWith('INSERT INTO accounts'))this.accounts.set(args[1],args[0])
  else if(sql.startsWith('INSERT INTO credential_verifiers'))this.credentials.set(args[0],args[1])
  else if(sql.startsWith('INSERT INTO recovery_codes'))this.codes.push({userId:args[0],hash:args[1],used:false})
  else if(sql.startsWith('INSERT INTO sessions'))this.sessions.push({hash:args[0],userId:args[1],expires:args[3],revoked:false})
  else if(sql.startsWith('UPDATE recovery_codes')){const row=this.codes.find(item=>item.userId===args[1]&&item.hash===args[2]&&!item.used);if(row){row.used=true;return {success:true,meta:{changes:1}}}return {success:true,meta:{changes:0}}}
  else if(sql.startsWith('UPDATE credential_verifiers'))this.credentials.set(args[2],args[0])
  else if(sql.startsWith('UPDATE sessions')){for(const row of this.sessions)if(row.userId===args[1])row.revoked=true}
  else if(sql.startsWith('INSERT INTO login_throttles'))this.throttles.set(args[0],{failures:args[1],window_started_at:args[2],blocked_until:args[3]})
  else if(sql.startsWith('INSERT INTO progress_operations'))this.operations.set(`${args[0]}:${args[1]}`,true)
  else if(sql.startsWith('INSERT INTO progress_snapshots'))this.snapshots.set(args[0],{revision:args[1],state_json:args[2]})
  else if(sql.startsWith('DELETE FROM login_throttles'))this.throttles.delete(args[0])
  return {success:true,meta:{changes:1}}
 }
}
class Statement{constructor(db,sql){this.db=db;this.sql=sql;this.args=[]}bind(...args){this.args=args;return this}first(){return this.db.first(this.sql,this.args)}all(){return this.db.all(this.sql,this.args)}run(){return this.db.run(this.sql,this.args)}}
function request(path,value,token){return new Request('https://sync.example'+path,{method:'POST',headers:{'content-type':'application/json',...(token?{authorization:`Bearer ${token}`}:{})},body:JSON.stringify(value)})}

const db=new MemoryD1()
const registration=await worker.fetch(request('/auth/register',{handle:'aluna_aiops',password:'uma senha local longa'}),{DB:db})
assert.equal(registration.status,200)
const account=await registration.json()
assert.equal(account.handle,'aluna_aiops')
assert.equal(account.recovery_codes.length,8)
assert.equal(db.credentials.size,1)
assert.equal(JSON.stringify([...db.credentials.values()]).includes('uma senha local longa'),false)
const login=await worker.fetch(request('/auth/login',{handle:'ALUNA_AIOPS',password:'uma senha local longa'}),{DB:db})
assert.equal(login.status,200)
const session=(await login.json()).session_token
const push=await worker.fetch(request('/sync/push',{device_id:'device-local-01',base_revision:0,operations:[{operation_id:'sync-op-001',type:'legacy_complete',payload:{day:1}}]},session),{DB:db})
assert.equal(push.status,200)
assert.equal((await push.json()).revision,1)
const replay=await worker.fetch(request('/sync/push',{device_id:'device-local-01',base_revision:0,operations:[{operation_id:'sync-op-001',type:'legacy_complete',payload:{day:1}}]},session),{DB:db})
assert.equal((await replay.json()).idempotent,true)
const secondDevice=await worker.fetch(request('/sync/push',{device_id:'device-local-02',base_revision:0,operations:[{operation_id:'sync-op-002',type:'legacy_quiz',payload:{day:1,score:90}}]},session),{DB:db})
assert.equal((await secondDevice.json()).revision,2)
const pulled=await worker.fetch(request('/sync/pull',{},session),{DB:db})
const state=(await pulled.json()).state
assert.equal(state.completed.includes(1),true)
assert.equal(state.quizzes['1'],90)
const savedNote=await worker.fetch(request('/sync/push',{device_id:'device-local-01',base_revision:2,operations:[{operation_id:'sync-op-003',type:'legacy_note',payload:{day:1,text:'Evidência do primeiro dispositivo.'}}]},session),{DB:db})
assert.equal(savedNote.status,200)
const competingNote=await worker.fetch(request('/sync/push',{device_id:'device-local-02',base_revision:2,operations:[{operation_id:'sync-op-004',type:'legacy_note',payload:{day:1,text:'Evidência concorrente.'}}]},session),{DB:db})
assert.equal(competingNote.status,409)
const foreign=await worker.fetch(request('/sync/pull',{},undefined),{DB:db})
assert.equal(foreign.status,401)
const preflight=await worker.fetch(new Request('https://sync.example/sync/pull',{method:'OPTIONS',headers:{origin:'https://app.example.test','access-control-request-method':'POST','access-control-request-headers':'authorization, content-type'}}),{DB:db,ALLOWED_ORIGINS:'https://app.example.test'})
assert.equal(preflight.status,204)
assert.equal(preflight.headers.get('access-control-allow-origin'),'https://app.example.test')
const deniedOrigin=await worker.fetch(new Request('https://sync.example/sync/pull',{method:'OPTIONS',headers:{origin:'https://other.example.test','access-control-request-method':'POST','access-control-request-headers':'authorization'}}),{DB:db,ALLOWED_ORIGINS:'https://app.example.test'})
assert.equal(deniedOrigin.status,403)
for(let attempt=1;attempt<LOGIN_FAILURE_LIMIT;attempt++){const rejected=await worker.fetch(request('/auth/login',{handle:'aluna_aiops',password:'senha errada longa'}),{DB:db});assert.equal(rejected.status,401)}
const blocked=await worker.fetch(request('/auth/login',{handle:'aluna_aiops',password:'senha errada longa'}),{DB:db})
assert.equal(blocked.status,429)
const blockedCorrect=await worker.fetch(request('/auth/login',{handle:'aluna_aiops',password:'uma senha local longa'}),{DB:db})
assert.equal(blockedCorrect.status,429)
const recovery=await worker.fetch(request('/auth/recover',{handle:'aluna_aiops',recovery_code:account.recovery_codes[0],new_password:'nova senha local longa'}),{DB:db})
assert.equal(recovery.status,200)
const used=await worker.fetch(request('/auth/recover',{handle:'aluna_aiops',recovery_code:account.recovery_codes[0],new_password:'outra senha local longa'}),{DB:db})
assert.equal(used.status,401)
const renewed=await worker.fetch(request('/auth/login',{handle:'aluna_aiops',password:'nova senha local longa'}),{DB:db})
assert.equal(renewed.status,200)
const malformed=await worker.fetch(new Request('https://sync.example/auth/login',{method:'POST',headers:{'content-type':'application/json'},body:'{'}),{DB:db})
assert.equal(malformed.status,422)
console.log('PASS local Worker auth flow with recovery-code consumption')
