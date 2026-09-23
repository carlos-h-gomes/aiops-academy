import {useEffect, useState} from 'react'
import {fetchUnitLesson} from '../api/unitLessons'
import type {UnitLesson} from '../data/curriculum'

export function useUnitLesson(unitId:string) {
  const [lesson,setLesson]=useState<UnitLesson>()
  const [error,setError]=useState('')
  const [loading,setLoading]=useState(true)
  const [attempt,setAttempt]=useState(0)
  useEffect(()=>{
    let active=true
    setLoading(true);setError('')
    fetchUnitLesson(unitId).then(value=>{if(active)setLesson(value)}).catch(reason=>{if(active)setError((reason as Error).message)}).finally(()=>{if(active)setLoading(false)})
    return ()=>{active=false}
  },[unitId,attempt])
  return {lesson,error,loading,retry:()=>setAttempt(value=>value+1)}
}
