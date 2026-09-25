import{useEffect,useState}from'react'

export function useNetworkStatus(){
 const[available,setAvailable]=useState(()=>navigator.onLine)
 useEffect(()=>{
  let active=true
  const verify=async()=>{if(!navigator.onLine){setAvailable(false);return}try{const response=await fetch('/api/v1/health',{cache:'no-store'});if(active)setAvailable(response.ok)}catch{if(active)setAvailable(false)}}
  const connected=()=>void verify()
  const disconnected=()=>setAvailable(false)
  const reported=(event:Event)=>setAvailable((event as CustomEvent<boolean>).detail)
  const workerMessage=(event:MessageEvent)=>{if(event.data?.type==='academy-network-unavailable')setAvailable(false)}
  window.addEventListener('online',connected)
  window.addEventListener('offline',disconnected)
  window.addEventListener('academy-app-availability',reported)
  navigator.serviceWorker?.addEventListener('message',workerMessage)
  void verify()
  return()=>{active=false;window.removeEventListener('online',connected);window.removeEventListener('offline',disconnected);window.removeEventListener('academy-app-availability',reported);navigator.serviceWorker?.removeEventListener('message',workerMessage)}
 },[])
 return available
}
