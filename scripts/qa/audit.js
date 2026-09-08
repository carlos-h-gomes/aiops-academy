const frame=document.querySelector('#app'),output=document.querySelector('#report');
const wait=ms=>new Promise(r=>setTimeout(r,ms));
async function save(data){const r=await fetch('/_qa/evidence',{method:'POST',headers:{'Content-Type':'application/json','X-Academy-Client':'local'},body:JSON.stringify(data)});if(!r.ok)throw Error('Falha ao guardar evidência');}
document.querySelector('#run').onclick=async()=>{
 const results=[];document.querySelector('#run').disabled=true;
 try{for(const width of [1440,390,320])for(const route of ['','#/trail','#/day/1','#/lab/ansible','#/exams','#/reviews','#/portfolio','#/library','#/settings']){
  frame.width=width;frame.src='/?qa='+width+'-'+results.length+route;await new Promise(r=>frame.onload=r);await wait(200);
  const doc=frame.contentDocument;const script=doc.createElement('script');script.src='/_qa/axe.js';doc.head.appendChild(script);await new Promise((r,j)=>{script.onload=r;script.onerror=j});
  const audit=await frame.contentWindow.axe.run(doc,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
  results.push({width,route:route||'dashboard',title:doc.querySelector('h1')?.textContent,overflow:doc.documentElement.scrollWidth>width,violations:audit.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),incomplete:audit.incomplete.map(v=>v.id),passes:audit.passes.length});output.textContent=JSON.stringify(results,null,2);
 }await save({name:'a11y',report:results});output.textContent='CONCLUÍDO\n'+JSON.stringify(results,null,2);
 }catch(e){output.textContent='FALHA: '+e.message}finally{document.querySelector('#run').disabled=false}
};
document.querySelector('#save').onclick=async()=>{try{await save({name:document.querySelector('#image-name').value,image:document.querySelector('#image-data').value});output.textContent='Captura salva'}catch(e){output.textContent=e.message}};


document.querySelector('#preview').onclick=()=>{frame.width=Number(document.querySelector('#viewport').value);frame.src='/?preview=1#/';frame.scrollIntoView()};
