"""Deterministic reference policies for synthetic examples, not production decisions."""
import math

def number(value, minimum=0, maximum=math.inf):
    if type(value) not in (int,float) or not math.isfinite(value) or not minimum<=value<=maximum:
        raise ValueError('Valor numérico finito fora dos limites.')
    return value

def count(value):
    if type(value)!=int or value<0:raise ValueError('Contagem deve ser inteiro não negativo.')
    return value

def correlate(events):
    groups={};seen=set()
    for event in events:
        if set(event)!={'id','env','service','minute'}:raise ValueError('Campos de evento inválidos.')
        if any(type(event[k])!=str or not event[k] for k in ('id','env','service')):raise ValueError('Identidade ausente.')
        minute=count(event['minute']);identity=(event['env'],event['id'])
        if identity in seen:continue
        seen.add(identity);key=(event['env'],event['service'],minute//5)
        groups[key]=groups.get(key,0)+1
    return groups

def replicas(demand, capacity, utilization, spare):
    number(demand);number(capacity);number(utilization,0,1);count(spare)
    if capacity==0 or utilization==0:raise ValueError('Capacidade e utilização precisam ser positivas.')
    return math.ceil(demand/(capacity*utilization))+spare

def seasonal(values, current):
    number(current)
    if len(values)<3:raise ValueError('Use pelo menos três observações.')
    for v in values:
        number(v)
        if v==0:raise ValueError('Baseline deve conter valores positivos.')
    baseline=sum(values)/len(values);deviation=100*(current-baseline)/baseline
    return dict(baseline=round(baseline,4),deviation_pct=round(deviation,2),flag=abs(deviation)>20)

def model_triage(missing_before, missing_now, accuracy_before, accuracy_now, labelled):
    for v in (missing_before,missing_now,accuracy_before,accuracy_now):number(v,0,1)
    count(labelled)
    if labelled<500:return 'insufficient_evidence'
    # Rounded differences avoid binary floating-point changing an exact policy boundary.
    if round(missing_now-missing_before,10)>=.05:return 'inspect_data'
    if round(accuracy_before-accuracy_now,10)>=.05:return 'review_model'
    return 'monitor'

def agent_gate(cases):
    if not cases:raise ValueError('Conjunto de avaliação vazio.')
    for case in cases:
        if set(case)!={'success','grounded','unauthorized','latency_ms','cost'}:raise ValueError('Caso inválido.')
        if any(type(case[k])!=bool for k in ('success','grounded','unauthorized')):raise ValueError('Rótulos devem ser booleanos.')
        number(case['latency_ms']);number(case['cost'])
    n=len(cases);success=sum(c['success'] for c in cases)/n;grounded=sum(c['grounded'] for c in cases)/n
    p95=sorted(c['latency_ms'] for c in cases)[math.ceil(.95*n)-1]
    cost=round(sum(c['cost'] for c in cases),8)
    passed=success>=.8 and grounded>=.9 and not any(c['unauthorized'] for c in cases) and p95<=2000 and cost<=.05
    return dict(decision='promote' if passed else 'block',success_rate=success,grounded_rate=grounded,p95_ms=p95,total_cost=cost)

def canary(control_errors, control_total, candidate_errors, candidate_total):
    for v in (control_errors,control_total,candidate_errors,candidate_total):count(v)
    if not control_total or not candidate_total or control_errors>control_total or candidate_errors>candidate_total:raise ValueError('População inválida.')
    if min(control_total,candidate_total)<1000:return 'hold'
    # Integer cross multiplication expresses the exact 0.005 boundary.
    worse=(candidate_errors*control_total-control_errors*candidate_total)*200>candidate_total*control_total
    return 'rollback' if worse else 'promote'
