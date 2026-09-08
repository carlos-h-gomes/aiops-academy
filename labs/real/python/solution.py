"""Referência local. Leia depois da tentativa e explique cada limite."""
from collections import Counter

def normalize(events):
    seen=set();valid=[];invalid=0;duplicates=0
    for event in events:
        if not isinstance(event,dict) or not isinstance(event.get('id'),str) or not event['id'].strip() or type(event.get('status'))!=int or not 100<=event['status']<=599:
            invalid+=1;continue
        if event['id'] in seen:duplicates+=1;continue
        seen.add(event['id']);valid.append(event)
    return dict(unique_valid=len(valid),invalid=invalid,duplicates=duplicates,error_rate=100*sum(x['status']>=500 for x in valid)/len(valid) if valid else None)

def summarize(logs):
    return dict(Counter(x['service.name'] for x in logs if x.get('loglevel')=='ERROR'))

def z_score(observed,mean,std):
    if std<0:raise ValueError('Desvio negativo.')
    return (observed-mean)/std if std else None
