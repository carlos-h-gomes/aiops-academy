import {useEffect,useState} from 'react'
import {fetchUnitLab,runUnitLab} from '../api/unitLabs'
import type {UnitLab,UnitLabResult} from '../data/curriculum'

export function useUnitLab(unitId:string) {
  const [lab,setLab]=useState<UnitLab>()
  const [error,setError]=useState('')
  const [loading,setLoading]=useState(true)
  const [running,setRunning]=useState(false)
  const [attempt,setAttempt]=useState(0)
  const [result,setResult]=useState<UnitLabResult>()
  useEffect(()=>{
    let active=true
    setLoading(true);setError('');setResult(undefined)
    fetchUnitLab(unitId).then(value=>{if(active)setLab(value)}).catch(reason=>{if(active)setError((reason as Error).message)}).finally(()=>{if(active)setLoading(false)})
    return ()=>{active=false}
  },[unitId,attempt])
  async function run(answers:Record<string,string>) {
    setRunning(true);setError('')
    try {const value=await runUnitLab(unitId,answers);setResult(value);return value}
    catch(reason) {setError((reason as Error).message);return undefined}
    finally {setRunning(false)}
  }
  return {lab,error,loading,running,result,run,retry:()=>setAttempt(value=>value+1),clearResult:()=>setResult(undefined)}
}
