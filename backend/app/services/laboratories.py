"""Lab orchestration and deterministic grading; authoritative outcomes live here."""
import math
import time
from app.models.catalog import LAB_MAP,LOGS,initial_hosts
from app.repositories import storage
from app.services import ansible_lab,query_lab

def lab_info(lab_id):
    if lab_id not in LAB_MAP:raise ValueError('Laboratório inexistente.')
    return LAB_MAP[lab_id]

def start(lab_id):
    lab_info(lab_id)
    state=dict(kind=lab_id,hosts=initial_hosts(),seen=[],fixed=False,approved=False,communicated=False,verified=False,closed=False,minutes=0,penalties=0,steps=0,created=time.time())
    sid=storage.session_create(state)
    return dict(id=sid,state=public_state(state),logs=LOGS if lab_id in ('dql','opensearch') else [])

def public_state(s):
    return {k:s[k] for k in ('hosts','seen','fixed','approved','communicated','verified','closed','minutes','penalties')}

def run(lab_id,request):
    lab_info(lab_id)
    def update(s):
        if s['kind']!=lab_id:raise ValueError('Sessão pertence a outro laboratório.')
        if time.time()-s['created']>8*3600:raise ValueError('Sessão expirou após 8h. Inicie outra.')
        if s['steps']>=250:raise ValueError('Limite de 250 ações nesta sessão. Inicie outra.')
        s['steps']+=1
        if lab_id.startswith('ansible'):
            result=ansible_lab.run(request.source,s['hosts'],request.check)
            if not request.check:s['hosts']=result['hosts']
            selected=[h for h in result['hosts'] if h['group']==('windows' if lab_id.endswith('windows') else 'webservers')]
            goal=all(h['services'].get('W3SVC' if h['os']=='windows' else 'nginx')=='started' and (h['os']=='windows' or 'nginx' in h['packages']) for h in selected)
            result['passed']=goal and result['changes']==0 and result['failed']==0 and not request.check
            result['message']='Convergência comprovada.' if result['passed'] else ('Check mode: nenhuma alteração persistida.' if request.check else 'Confira os estados e execute novamente para provar zero mudanças.')
        elif lab_id=='dql':result=query_lab.dql(request.source)
        elif lab_id=='opensearch':result=query_lab.opensearch(request.source)
        elif lab_id in ('linux','incident'):result=terminal(s,request.source.strip() if lab_id=='linux' else request.action,lab_id)
        else:result=grade(lab_id,query_lab.parse_json(request.source))
        result['state']=public_state(s)
        return result
    result=storage.session_update(request.session_id,update)
    if result['passed']:storage.update_progress(lambda p:p['labs'].__setitem__(lab_id,True))
    return result

def grade(lab_id,q):
    expected={'slo':dict(allowed_errors=1000,excess_errors=400,burn_rate=20),'events':dict(unique_valid=4,invalid=1,duplicates=1,error_rate=50),'anomaly':dict(z_score=4,precision=80,recall=200/3),'rag':dict(source='A',action='request_approval',execute=False)}
    if lab_id in expected:
        target=expected[lab_id]
        if set(q)!=set(target):raise ValueError('Mantenha exatamente os campos pedidos no enunciado.')
        checks=[]
        for key,val in target.items():
            actual=q[key]
            correct=(type(actual) in (int,float) and math.isfinite(actual) and abs(actual-val)<0.02) if type(val) in (int,float) else type(actual)==type(val) and actual==val
            checks.append(dict(name=key,passed=correct,message='Correto.' if correct else 'Revise a fórmula ou o controle correspondente no enunciado.'))
    elif lab_id=='workflow':
        required={'require_approval','deduplicate','allowed_targets','max_attempts','rollback','cooldown_seconds'}
        if set(q)!=required:raise ValueError('Mantenha os seis campos da política.')
        checks=[dict(name='Aprovação ausente bloqueia',passed=q['require_approval'] is True),dict(name='Duplicata não repete efeito',passed=q['deduplicate'] is True),dict(name='Alvo fora do escopo bloqueia',passed=q['allowed_targets']==['web-01']),dict(name='Tentativas limitadas',passed=type(q['max_attempts'])==int and 1<=q['max_attempts']<=3),dict(name='Rollback definido',passed=q['rollback'] is True),dict(name='Cooldown limita repetição',passed=type(q['cooldown_seconds'])==int and 60<=q['cooldown_seconds']<=3600)]
    else:raise ValueError('Corretor indisponível.')
    passed=all(x['passed'] for x in checks)
    return dict(passed=passed,checks=checks,score=round(100*sum(x['passed'] for x in checks)/len(checks)),message='Todos os critérios atendidos.' if passed else 'Ainda há critérios para corrigir. A tentativa foi preservada.')

def terminal(s,action,kind):
    if len(action)>160 or '\n' in action:raise ValueError('Execute uma ação por vez.')
    aliases={'df -h':'disk','journalctl -u quotes':'logs','free -m':'memory','systemctl status quotes':'status','help':'help'}
    action=aliases.get(action,action)
    supported={'help','disk','logs','memory','metrics','status','changes','rotate-logs','restart','traces','communicate','approve','rollback','verify','close'}
    if action not in supported:raise ValueError('Comando fora do simulador. Digite help para ver as ações aceitas.')
    if s['closed']:return dict(passed=True,message='Incidente encerrado. Inicie uma nova sessão para praticar.',score=max(0,100-s['penalties']))
    if action!='help':s['minutes']+=2
    if action in ('disk','logs','memory','metrics','changes','traces') and action not in s['seen']:s['seen'].append(action)
    if action=='help': message=('Comandos: df -h; free -m; journalctl -u quotes; metrics; status; changes; rotate-logs; restart. Um por vez. Ambiente sintético.' if kind=='linux' else 'Ações: metrics, logs, changes, traces, communicate, approve, rollback, verify, close.')
    elif action=='disk':message='Filesystem /var: 48GB / 50GB (96%). /var/log/quotes concentra crescimento.' if not s['fixed'] else 'Filesystem /var: 30GB / 50GB (60%). Rotação validada.'
    elif action=='memory':message='Memória 3.2GB / 8GB; swap 0. CPU 24%. Não há pressão de memória neste cenário.'
    elif action=='metrics':message='quotes: 100 req/s | erros 22% | p95 1800ms | pool 100% ocupado' if not s['fixed'] else 'quotes: 100 req/s | erros 0.1% | p95 110ms | pool 40% ocupado'
    elif action=='logs':message=('09:05 ERROR quotes: ENOSPC ao escrever /var/log/quotes; requests falham.' if kind=='linux' else '09:05 ERROR quotes: pool exhausted; downstream timeout; trace demo-0003.') if not s['fixed'] else '09:12 INFO requests concluídos; nenhum novo erro na amostra.'
    elif action=='changes':message='09:00: retenção de logs alterada sem limite.' if kind=='linux' else '09:00 deploy v2: pool_max caiu de 40 para 2. Regressão coincide com o início dos erros.'
    elif action=='traces':message='quotes → pricing-db: espera por conexão consome 92% do trace. Banco com latência normal.'
    elif action=='restart':s['penalties']+=15;message='Reinício sem remover a causa: erro retornou. +15 pontos de penalidade didática.'
    elif action=='rotate-logs':
        if kind!='linux':raise ValueError('Rotação não pertence a este incidente.')
        if not {'disk','logs','metrics'}.issubset(s['seen']):message='Colete disco, logs e métricas antes da ação. Nenhuma alteração feita.'
        else:s['fixed']=True;message='Rotação limitada à fixture quotes executada. Valide com status e metrics. Não houve acesso a arquivos reais.'
    elif action=='communicate':s['communicated']=True;message='Atualização registrada: serviço quotes degradado; investigação e próxima atualização em 10 minutos simulados.'
    elif action=='approve':
        if not {'metrics','logs','changes'}.issubset(s['seen']):message='Aprovação didática bloqueada: faltam métricas, logs ou mudanças.'
        else:s['approved']=True;message='Aprovado apenas rollback do canário quotes para v1 nesta sessão fictícia.'
    elif action=='rollback':
        if kind!='incident':raise ValueError('Use rotate-logs no incidente Linux.')
        if not s['approved'] or not s['communicated']:message='Bloqueado: comunique impacto e obtenha aprovação vinculada ao diagnóstico.'
        else:s['fixed']=True;message='Canário voltou para v1; pool_max=40. Valide a saúde antes de encerrar.'
    elif action in ('verify','status'):
        if s['fixed']:s['verified']=True;message='Verificação sintética: API funcional, erro 0.1%, p95 110ms, volume estável por 10 minutos simulados.';s['minutes']+=10
        else:message='Serviço ativo, mas função degradada. Processo rodando não prova saúde.'
    elif action=='close':
        if not s['verified'] or not s['communicated']:message='Não encerre sem validar recuperação e comunicar impacto.'
        else:s['closed']=True;message='Incidente encerrado com evidência. Escreva o postmortem no portfólio.'
    passed=s['fixed'] and s['verified'] and (kind=='linux' or s['closed'])
    return dict(passed=passed,message=message,score=max(0,100-s['penalties']) if passed else 0)
