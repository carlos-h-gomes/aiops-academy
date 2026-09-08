import{createContext,useContext,useState,useEffect,useCallback,type ReactNode}from'react'
import{request}from'../api/client'
import type{Course,Progress}from'../data/types'
type State={course:Course;progress:Progress;refresh:()=>Promise<void>}
const Context=createContext<State|null>(null)
export function AcademyProvider({children}:{children:ReactNode}){
 const[course,setCourse]=useState<Course>();const[progress,setProgress]=useState<Progress>();const[error,setError]=useState('');const[loading,setLoading]=useState(true)
 const refresh=useCallback(async()=>{setProgress(await request<Progress>('/progress'))},[])
 const load=useCallback(async()=>{setLoading(true);setError('');try{const[c,p]=await Promise.all([request<Course>('/course'),request<Progress>('/progress')]);setCourse(c);setProgress(p)}catch(e){setError((e as Error).message)}finally{setLoading(false)}},[])
 useEffect(()=>{void load()},[load])
 if(!course||!progress)return <main className="startup"><div className="brand-mark">A</div><h1>AIOps Academy</h1>{loading?<p role="status">Preparando sua missão…</p>:<><p role="alert">{error}</p><button className="primary" onClick={()=>void load()}>Tentar novamente</button></>}</main>
 return <Context.Provider value={{course,progress,refresh}}>{children}</Context.Provider>
}
export function useAcademy(){const ctx=useContext(Context);if(!ctx)throw new Error('AcademyProvider ausente');return ctx}
