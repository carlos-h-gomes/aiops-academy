export async function request<T=any>(path:string,method='GET',body?:unknown):Promise<T>{
  const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),15000)
  try{
    const response=await fetch('/api/v1'+path,{method,signal:controller.signal,headers:{'Content-Type':'application/json','X-Academy-Client':'local'},...(body!==undefined?{body:JSON.stringify(body)}:{})})
    const data=await response.json()
    if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Não foi possível concluir esta ação.')
    return data
  }catch(error){
    if(error instanceof TypeError||error instanceof DOMException)throw new Error('O app local não respondeu. Abra iniciar.cmd e tente novamente. Seu rascunho foi mantido.')
    throw error
  }finally{clearTimeout(timer)}
}
export async function textFile(path:string){const r=await fetch('/api/v1'+path);if(!r.ok)throw new Error('Não foi possível exportar.');return r.text()}
