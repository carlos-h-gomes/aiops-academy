"""Explicit QA launch only. Fixed synthetic evidence files, no arbitrary paths."""
import base64
import json
from pathlib import Path
from fastapi import Request, HTTPException
from fastapi.responses import FileResponse
from app.main import app as academy

ROOT=Path(__file__).resolve().parents[1]
@academy.get('/_qa/{name}')
def qa_file(name:str):
    paths={'audit.html':ROOT/'scripts/qa/audit.html','audit.js':ROOT/'scripts/qa/audit.js','axe.js':ROOT/'frontend/node_modules/axe-core/axe.min.js'}
    if name not in paths:raise HTTPException(404)
    return FileResponse(paths[name])

@academy.post('/_qa/evidence')
async def evidence(request:Request):
    data=await request.json()
    name=data.get('name')
    if name=='a11y':
        report=data.get('report')
        if not isinstance(report,list) or len(report)>50:raise HTTPException(422)
        (ROOT/'artifacts/a11y.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    elif name in ('desktop','mobile','lesson'):
        try:blob=base64.b64decode(data.get('image',''),validate=True)
        except Exception:raise HTTPException(422)
        ext='png' if blob.startswith(b'\x89PNG\r\n\x1a\n') else 'jpg' if blob.startswith(b'\xff\xd8\xff') else None
        if ext is None or len(blob)>590000:raise HTTPException(422)
        (ROOT/f'artifacts/{name}.{ext}').write_bytes(blob)
    else:raise HTTPException(422)
    return {'saved':True}

class QAFrames:
    def __init__(self,app):self.inner=app
    async def __call__(self,scope,receive,send):
        async def headers(message):
            if message['type']=='http.response.start':
                message['headers']=[(k,v.replace(b"frame-ancestors 'none'",b"frame-ancestors 'self'")) if k==b'content-security-policy' else (k,v) for k,v in message['headers']]
            await send(message)
        await self.inner(scope,receive,headers)
app=QAFrames(academy)
