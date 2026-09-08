"""Strict, bounded YAML state interpreter. No external execution or ignored syntax."""
from copy import deepcopy
import yaml
from yaml.tokens import AliasToken,AnchorToken,TagToken

def run(source,hosts,check=False):
    try:
        tokens=list(yaml.scan(source))
        if len(tokens)>1800 or any(isinstance(t,(AliasToken,AnchorToken,TagToken)) for t in tokens):
            raise ValueError('Aliases, anchors, tags e documentos extensos não são suportados.')
        plays=yaml.safe_load(source)
    except yaml.YAMLError:
        raise ValueError('YAML inválido. Confira espaços, dois-pontos e indentação.') from None
    if not isinstance(plays,list) or not 1<=len(plays)<=5: raise ValueError('Use uma lista YAML com 1 a 5 plays.')
    plans=[]
    modules={'ansible.builtin.package':'package','ansible.builtin.apt':'package','package':'package','apt':'package','ansible.builtin.service':'service','service':'service','ansible.windows.win_service':'windows'}
    for play in plays:
        if not isinstance(play,dict) or set(play)-{'name','hosts','tasks'}: raise ValueError('Play suporta apenas name, hosts e tasks. Variáveis/handlers ficam no kit real.')
        selector=play.get('hosts')
        if type(selector)!=str: raise ValueError('hosts deve ser um nome ou grupo sintético.')
        targets=[h['name'] for h in hosts if selector in (h['name'],h['group'],'all')]
        if not targets: raise ValueError('Nenhum alvo encontrado. Use webservers, windows, web-01 ou web-02.')
        tasks=play.get('tasks')
        if not isinstance(tasks,list) or not 1<=len(tasks)<=30: raise ValueError('Use entre 1 e 30 tarefas por play.')
        for task in tasks:
            if not isinstance(task,dict): raise ValueError('Cada tarefa deve ser um mapeamento.')
            names=[k for k in task if k!='name']
            if len(names)!=1 or names[0] not in modules: raise ValueError('Use um único módulo suportado por tarefa; nenhum campo será ignorado.')
            module=modules[names[0]]; args=task[names[0]]
            if not isinstance(args,dict) or set(args)!={'name','state'}: raise ValueError('O módulo deste lab exige apenas name e state explícitos.')
            name=args['name']; state=args['state']
            if not isinstance(name,str) or not name or len(name)>80: raise ValueError('Nome inválido (máximo 80 caracteres).')
            allowed={'present','absent'} if module=='package' else {'started','stopped','restarted'}
            if type(state)!=str or state not in allowed: raise ValueError('state não suportado para este módulo.')
            plans.append((targets,module,name,state,str(task.get('name',name))[:160]))
    updated=deepcopy(hosts); events=[]; failed=set()
    for targets,module,name,state,label in plans:
        for h in updated:
            if h['name'] not in targets or h['name'] in failed: continue
            if (module=='windows') != (h['os']=='windows'):
                events.append(dict(host=h['name'],task=label,status='failed',message='Módulo incompatível com a plataforma.'))
                failed.add(h['name']);continue
            if module=='package':
                exists=name in h['packages']; changed=exists!=(state=='present')
                if state=='present' and not exists:h['packages'].append(name)
                elif state=='absent' and exists:h['packages'].remove(name)
            else:
                if name not in h['services']:
                    events.append(dict(host=h['name'],task=label,status='failed',message='Serviço não existe nesta fixture.'))
                    failed.add(h['name']);continue
                final='started' if state=='restarted' else state
                changed=h['services'][name]!=final or state=='restarted'
                h['services'][name]=final
            events.append(dict(host=h['name'],task=label,status='changed' if changed else 'ok',message=f'{name}: {state}'))
    return dict(hosts=updated,events=events,changes=sum(e['status']=='changed' for e in events),failed=len(failed),check=check)
