const CACHE_NAME='aiops-academy-pwa-v2'
const ROOT_ASSETS=['/','/favicon.svg','/manifest.webmanifest']
const API_PREFIX='/api/v1/'
const CACHEABLE_API=new Set(['course','progress','curriculum','manuals'])

function isCacheableApi(pathname){
 if(!pathname.startsWith(API_PREFIX))return false
 const resource=pathname.slice(API_PREFIX.length)
 return CACHEABLE_API.has(resource)||/^units\/[^/]+(?:\/(?:lab|progress))?$/.test(resource)
}

async function cacheResponse(request,response){
 if(response.ok){try{const cache=await caches.open(CACHE_NAME);await cache.put(request,response.clone())}catch{}}
 return response
}

async function networkFirst(request){
 try{return await cacheResponse(request,await fetch(request))}
 catch{const cached=await caches.match(request);if(cached)return cached;throw new Error('Offline and uncached')}
}

async function cacheFirst(request){
 const cached=await caches.match(request)
 if(cached)return cached
 return cacheResponse(request,await fetch(request))
}

async function notifyUnavailable(){const clients=await self.clients.matchAll({type:'window'});for(const client of clients)client.postMessage({type:'academy-network-unavailable'})}

self.addEventListener('install',event=>{
 event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(ROOT_ASSETS)).then(()=>self.skipWaiting()))
})

self.addEventListener('activate',event=>{
 event.waitUntil(caches.keys().then(names=>Promise.all(names.filter(name=>name.startsWith('aiops-academy-pwa-')&&name!==CACHE_NAME).map(name=>caches.delete(name)))).then(()=>self.clients.claim()))
})

self.addEventListener('fetch',event=>{
 const request=event.request
 if(request.method!=='GET')return
 const url=new URL(request.url)
 if(url.origin!==self.location.origin)return
 if(url.pathname.startsWith(API_PREFIX)){
  if(isCacheableApi(url.pathname))event.respondWith(networkFirst(request))
  else event.respondWith(fetch(request).catch(async error=>{await notifyUnavailable();throw error}))
  return
 }
 if(request.mode==='navigate'){
  event.respondWith(networkFirst(request).catch(()=>caches.match('/')))
  return
 }
 if(url.pathname.startsWith('/assets/')||ROOT_ASSETS.includes(url.pathname))event.respondWith(cacheFirst(request))
})
