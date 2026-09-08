import{useEffect,useState}from'react'
export function useRoute(){const[route,setRoute]=useState(location.hash.slice(1)||'/');useEffect(()=>{const cb=()=>{setRoute(location.hash.slice(1)||'/');window.scrollTo(0,0)};window.addEventListener('hashchange',cb);return()=>window.removeEventListener('hashchange',cb)},[]);return route}
