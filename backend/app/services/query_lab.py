"""Small exact parsers for documented DQL / OpenSearch teaching subsets."""
from collections import Counter
import json
import re
from app.models.catalog import LOGS

def dql(source):
    parts=[x.strip() for x in source.split('|')]
    if len(parts)>12 or parts[0]!='fetch logs': raise ValueError('Comece com fetch logs e use até 12 etapas.')
    rows=[dict(x) for x in LOGS]
    fields=set(LOGS[0])
    for part in parts[1:]:
        match=re.fullmatch(r'filter\s+([\w.]+)\s*(==|!=|>=|<=|>|<)\s*("[^"\n]{0,120}"|\d+(?:\.\d+)?)',part)
        if match:
            field,op,raw=match.groups()
            if field not in fields: raise ValueError(f'Campo desconhecido: {field}')
            value=json.loads(raw)
            def compare(r):
                actual=r.get(field)
                if type(actual)!=type(value) and not (type(actual) in (int,float) and type(value) in (int,float)): raise ValueError('Tipos incompatíveis na comparação.')
                return {'==':lambda:actual==value,'!=':lambda:actual!=value,'>=':lambda:actual>=value,'<=':lambda:actual<=value,'>':lambda:actual>value,'<':lambda:actual<value}[op]()
            rows=[r for r in rows if compare(r)];continue
        match=re.fullmatch(r'summarize\s+(\w+)\s*=\s*count\(\),\s*by\s*:\s*\{\s*([\w.]+)\s*\}',part)
        if match:
            alias,field=match.groups()
            if field not in fields or alias==field: raise ValueError('Campo ou alias de agregação inválido.')
            rows=[{field:k,alias:v} for k,v in Counter(r[field] for r in rows).items()];fields={field,alias};continue
        match=re.fullmatch(r'sort\s+([\w.]+)\s+(asc|desc)',part)
        if match:
            field,direction=match.groups()
            if field not in fields:raise ValueError('Campo de ordenação não existe neste resultado.')
            rows=sorted(rows,key=lambda r:r[field],reverse=direction=='desc');continue
        match=re.fullmatch(r'limit\s+(\d{1,3})',part)
        if match:
            limit=int(match[1])
            if not 1<=limit<=100:raise ValueError('limit deve ficar entre 1 e 100.')
            rows=rows[:limit];continue
        match=re.fullmatch(r'fields\s+([\w., ]+)',part)
        if match:
            selected=[s.strip() for s in match[1].split(',')]
            if not selected or any(f not in fields for f in selected):raise ValueError('Projeção contém campo desconhecido.')
            rows=[{f:r[f] for f in selected} for r in rows];fields=set(selected);continue
        raise ValueError('Etapa fora do subconjunto suportado. Consulte a referência ao lado do editor.')
    passed=sorted(rows,key=lambda r:str(r))==sorted([{'service.name':'quotes','total':3},{'service.name':'orders','total':1}],key=lambda r:str(r))
    return dict(rows=rows,passed=passed,message='Resultado correto: três erros em quotes e um em orders.' if passed else 'Consulta válida. O objetivo pede total de erros por service.name, com alias total.')

def opensearch(source):
    q=parse_json(source)
    if set(q)!={'size','query','aggs'} or q['size']!=0:raise ValueError('Use size:0, query e aggs. Consulte o exemplo de Query DSL.')
    if not isinstance(q['query'],dict) or set(q['query'])!={'term'}:raise ValueError('A bancada suporta query.term exato.')
    term=q['query']['term']
    if not isinstance(term,dict) or len(term)!=1:raise ValueError('Use um campo em term.')
    field,value=next(iter(term.items()))
    if field not in LOGS[0] or type(value) not in (str,int,float):raise ValueError('Campo/valor inválido.')
    if q['aggs']!={'por_servico':{'terms':{'field':'service.name'}}}:raise ValueError('Use agregação por_servico/terms/field service.name.')
    counts=Counter(r['service.name'] for r in LOGS if r[field]==value)
    rows=[dict(key=k,doc_count=v) for k,v in sorted(counts.items(),key=lambda x:-x[1])]
    passed=counts==Counter(quotes=3,orders=1)
    return dict(rows=rows,passed=passed,message='Agregação correta.' if passed else 'Query válida. Confira o filtro para contar ERROR.')

def parse_json(source):
    try: result=json.loads(source,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Número não finito.')))
    except (json.JSONDecodeError,RecursionError):raise ValueError('JSON inválido. Use aspas duplas e valores finitos.') from None
    if not isinstance(result,dict):raise ValueError('Envie um objeto JSON.')
    return result
