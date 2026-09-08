"""Loopback/same-origin request guards with bounded body and safe errors."""
import json
import re
from starlette.responses import JSONResponse

class LocalOnlyMiddleware:
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        if scope['type']!='http':return await self.app(scope,receive,send)
        headers={k.decode('latin1').lower():v.decode('latin1') for k,v in scope.get('headers',[])}
        host=headers.get('host','')
        origin=headers.get('origin')
        if not re.fullmatch(r'(127\.0\.0\.1|localhost)(:\d{1,5})?',host) or (origin is not None and origin!=f'http://{host}'):
            return await JSONResponse({'detail':'Acesso permitido apenas pela origem local do app.'},403)(scope,receive,send)
        if scope['method'] not in ('GET','HEAD','OPTIONS'):
            if headers.get('x-academy-client')!='local':return await JSONResponse({'detail':'Cabeçalho local obrigatório.'},403)(scope,receive,send)
            if headers.get('content-type','').split(';')[0]!='application/json':return await JSONResponse({'detail':'Envie application/json.'},415)(scope,receive,send)
        body=b''
        while True:
            message=await receive()
            if message['type']=='http.disconnect':return
            body+=message.get('body',b'')
            if len(body)>800_000:return await JSONResponse({'detail':'Entrada excede 800 KB.'},413)(scope,receive,send)
            if not message.get('more_body',False):break
        sent=False
        async def replay():
            nonlocal sent
            if sent:return await receive()
            sent=True
            return {'type':'http.request','body':body,'more_body':False}
        async def secure_send(message):
            if message['type']=='http.response.start':
                message.setdefault('headers',[]).extend([(b'x-content-type-options',b'nosniff'),(b'cache-control',b'no-store'),(b'referrer-policy',b'no-referrer'),(b'content-security-policy',b"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")])
            await send(message)
        await self.app(scope,replay,secure_send)

async def value_error(request,error):return JSONResponse({'detail':str(error)[:350]},422)

async def validation_error(request,error):return JSONResponse({'detail':'Entrada inválida. Confira campos, tipos, tamanho e limites.'},422)

async def internal_error(request,error):return JSONResponse({'detail':'Não foi possível concluir. Seu rascunho permanece no navegador; tente novamente e confira espaço em disco.'},500)
