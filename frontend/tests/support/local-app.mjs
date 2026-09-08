// Scoped test harness, never attaches to a learner server or browser profile.
import {spawn} from 'node:child_process'
import {once} from 'node:events'
import {mkdtemp,rm} from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'

export async function localApp(root) {
  const temporary=await mkdtemp(path.join(os.tmpdir(),'academy-curriculum-'))
  const keep=new Set(['PATH','SYSTEMROOT','WINDIR','TEMP','TMP','COMSPEC','PATHEXT','USERPROFILE','LOCALAPPDATA','APPDATA','PROGRAMFILES','PROGRAMFILES(X86)'])
  const env=Object.fromEntries(Object.entries(process.env).filter(([key])=>keep.has(key.toUpperCase())))
  const python=path.join(root,process.platform==='win32'?'.venv/Scripts/python.exe':'.venv/bin/python')
  const server=spawn(python,['-m','uvicorn','app.main:app','--app-dir',path.join(root,'backend'),'--host','127.0.0.1','--port','0','--no-access-log','--no-use-colors','--log-level','info'],{
    cwd:root,env:{...env,PYTHONUTF8:'1',ACADEMY_DB:path.join(temporary,'test.sqlite3')},stdio:['ignore','ignore','pipe'],windowsHide:true
  })
  let timer
  async function close(){
    clearTimeout(timer)
    if(server.exitCode===null){const exited=once(server,'exit');server.kill();await exited}
    const resolved=path.resolve(temporary)
    if(path.dirname(resolved)!==path.resolve(os.tmpdir())||!path.basename(resolved).startsWith('academy-curriculum-'))throw new Error('Unsafe test cleanup path')
    await rm(resolved,{recursive:true,force:true})
  }
  try {
    const origin=await new Promise((resolve,reject)=>{
      timer=setTimeout(()=>reject(new Error('Isolated startup timeout')),10000)
      server.once('error',()=>reject(new Error('Isolated server could not start')))
      server.once('exit',()=>reject(new Error('Isolated server exited')))
      let startup=''
      server.stderr.on('data',chunk=>{
        startup=(startup+chunk.toString()).slice(-2000)
        const match=startup.match(/Uvicorn running on (http:\/\/127\.0\.0\.1:\d+)/)
        if(match)resolve(match[1])
      })
    })
    clearTimeout(timer)
    return {origin,close}
  } catch(error){await close();throw error}
}
