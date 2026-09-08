import {useEffect, useState} from 'react'
import {fetchCurriculum} from '../api/curriculum'
import type {Curriculum} from '../data/curriculum'

export function useCurriculum() {
  const [catalog,setCatalog]=useState<Curriculum>()
  const [error,setError]=useState('')
  const [loading,setLoading]=useState(true)
  const [attempt,setAttempt]=useState(0)
  useEffect(()=>{
    let active=true
    setLoading(true);setError('')
    fetchCurriculum().then(value=>{if(active)setCatalog(value)})
      .catch(error=>{if(active)setError((error as Error).message)})
      .finally(()=>{if(active)setLoading(false)})
    return ()=>{active=false}
  },[attempt])
  return {catalog,error,loading,retry:()=>setAttempt(value=>value+1)}
}
