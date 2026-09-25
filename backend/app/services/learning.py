"""Course progress, assessment and scheduled retrieval practice."""
from datetime import date, timedelta
import math
import random
import time
from app.models.catalog import COURSE,LESSONS,LABS,LAB_MAP
from app.models.curriculum import load_curriculum
from app.repositories import storage

def catalog():
    lessons=[]
    for value in LESSONS.values():
        lessons.append({**value,'quiz':[{k:v for k,v in q.items() if k not in ('answer','explanation')} for q in value['quiz']]})
    return dict(version=COURSE['version'],lessons=lessons,sources=COURSE['sources'],labs=[{k:v for k,v in lab.items() if k!='solution'} for lab in LABS])

def get_lesson(day):
    if day not in LESSONS: raise ValueError('Dia inexistente.')
    return LESSONS[day]

def progress():return storage.progress()

def _guided_unit(unit_id):
    try:
        unit=next(item for item in load_curriculum().units if item.id==unit_id)
    except StopIteration as error:
        raise ValueError('Aula guiada inexistente.') from error
    if unit.status!='available' or unit.lesson_day is not None:
        raise ValueError('Aula guiada inexistente.')
    return unit

def _unit_state(progress,unit_id):
    return progress['unit_progress'].setdefault(unit_id,dict(lab_passed=False,completed=False,note='',review=None))

def unit_progress(unit_id):
    _guided_unit(unit_id)
    return storage.progress()['unit_progress'].get(unit_id,dict(lab_passed=False,completed=False,note='',review=None))

def record_unit_lab(unit_id,passed):
    _guided_unit(unit_id)
    if not passed:
        return unit_progress(unit_id)
    def update(value):
        _unit_state(value,unit_id)['lab_passed']=True
        return _unit_state(value,unit_id)
    return storage.update_progress(update)

def save_unit_note(unit_id,text):
    _guided_unit(unit_id)
    def update(value):
        state=_unit_state(value,unit_id)
        state['note']=text
        return state
    return storage.update_progress(update)

def complete_unit(unit_id):
    _guided_unit(unit_id)
    def update(value):
        state=_unit_state(value,unit_id)
        if not state['lab_passed']:
            raise ValueError('Resolva o lab guiado antes de concluir a aula.')
        if len(state['note'].strip())<80:
            raise ValueError('Registre uma evidência de pelo menos 80 caracteres antes de concluir a aula.')
        state['completed']=True
        state['review']=dict(due=(date.today()+timedelta(days=1)).isoformat(),interval=1,last_score=100)
        return state
    return storage.update_progress(update)

def review_unit(unit_id,rating):
    _guided_unit(unit_id)
    def update(value):
        state=_unit_state(value,unit_id)
        if not state['completed']:
            raise ValueError('Conclua a aula antes de registrar uma revisão.')
        previous=state.get('review') or dict(interval=0,last_score=100)
        old=previous.get('interval',0)
        interval={'again':0,'hard':1,'good':min(14,max(1,old*2+1)),'easy':min(21,max(3,old*3+1))}[rating]
        state['review']=dict(due=(date.today()+timedelta(days=interval)).isoformat(),interval=interval,last_score=previous.get('last_score',100))
        return state
    return storage.update_progress(update)

def review_card(day):
    q=get_lesson(day)['quiz'][0]
    return dict(answer=q['options'][q['answer']],explanation=q['explanation'])

def quiz(day,answers):
    lesson=get_lesson(day)
    if len(answers)!=len(lesson['quiz']) or any(type(x)!=int or not 0<=x<3 for x in answers):
        raise ValueError('Responda todas as questões com uma alternativa válida.')
    feedback=[dict(correct=a==q['answer'],answer=q['answer'],explanation=q['explanation']) for a,q in zip(answers,lesson['quiz'])]
    score=round(100*sum(x['correct'] for x in feedback)/len(feedback))
    def update(p):
        p['quizzes'][str(day)]=max(score,p['quizzes'].get(str(day),0))
        p['reviews'][str(day)]=dict(due=(date.today()+timedelta(days=1 if score>=80 else 0)).isoformat(),interval=1,last_score=score)
    storage.update_progress(update)
    return dict(score=score,feedback=feedback,passed=score>=80)

def save_note(day,text):
    get_lesson(day)
    storage.update_progress(lambda p:p['notes'].__setitem__(str(day),text))
    return dict(saved=True)

def complete(day):
    lesson=get_lesson(day)
    def update(p):
        if p['quizzes'].get(str(day),0)<80: raise ValueError('Passe no checkpoint com pelo menos 80%.')
        if not p['labs'].get(lesson['lab']): raise ValueError('Resolva o laboratório associado primeiro.')
        if len(p['notes'].get(str(day),'').strip())<80: raise ValueError('Registre uma evidência de pelo menos 80 caracteres com resultado e interpretação.')
        if day not in p['completed']: p['completed'].append(day)
    return storage.update_progress(update)

def settings(value):
    start=value['start_date']
    if not date(2000,1,1)<=date.fromisoformat(start)<=date(2100,12,31): raise ValueError('Use data entre 2000 e 2100.')
    return storage.update_progress(lambda p:p.__setitem__('settings',value))

def review(day,rating):
    get_lesson(day)
    def update(p):
        previous=p['reviews'].get(str(day),dict(interval=0))
        old=previous.get('interval',0)
        interval={'again':0,'hard':1,'good':min(14,max(1,old*2+1)),'easy':min(21,max(3,old*3+1))}[rating]
        p['reviews'][str(day)]=dict(due=(date.today()+timedelta(days=interval)).isoformat(),interval=interval,last_score=previous.get('last_score',0))
    return storage.update_progress(update)

def backup(): return dict(version=2,**storage.progress())

def restore(value):
    value=dict(value)
    value.pop('confirm');value.pop('version')
    for key in ('notes','quizzes','reviews'):
        if any(k not in {str(x) for x in LESSONS} for k in value[key]): raise ValueError('Backup contém dias inválidos.')
    if any(x not in LESSONS for x in value['completed']): raise ValueError('Dias concluídos inválidos.')
    if any(k not in LAB_MAP for k in value['labs']): raise ValueError('Laboratório inválido no backup.')
    guided={unit.id for unit in load_curriculum().units if unit.status=='available' and unit.lesson_day is None}
    if any(unit_id not in guided for unit_id in value['unit_progress']): raise ValueError('Aula guiada inválida no backup.')
    if any(len(v)>12000 for v in value['notes'].values()): raise ValueError('Nota excede o limite.')
    if any(not math.isfinite(v) or not 0<=v<=100 for v in value['quizzes'].values()): raise ValueError('Pontuação inválida.')
    for r in value['reviews'].values():
        if set(r)!={'due','interval','last_score'}: raise ValueError('Revisão inválida.')
        date.fromisoformat(r['due'])
        if type(r['interval'])!=int or not 0<=r['interval']<=21 or type(r['last_score']) not in (int,float) or not 0<=r['last_score']<=100: raise ValueError('Intervalo inválido.')
    for state in value['unit_progress'].values():
        if set(state)-{'lab_passed','completed','note','review'}: raise ValueError('Progresso da aula guiada inválido.')
        if type(state.get('lab_passed',False)) is not bool or type(state.get('completed',False)) is not bool or type(state.get('note','')) is not str or len(state.get('note',''))>12000: raise ValueError('Progresso da aula guiada inválido.')
        review=state.get('review')
        if review is not None:
            if set(review)!={'due','interval','last_score'}: raise ValueError('Revisão da aula guiada inválida.')
            date.fromisoformat(review['due'])
            if type(review['interval'])!=int or not 0<=review['interval']<=21 or type(review['last_score']) not in (int,float) or not 0<=review['last_score']<=100: raise ValueError('Revisão da aula guiada inválida.')
    if not date(2000,1,1)<=date.fromisoformat(value['settings']['start_date'])<=date(2100,12,31): raise ValueError('Data de backup inválida.')
    value['completed']=sorted(set(value['completed']))
    with storage.transaction() as db:
        storage.write(db,'pre-restore',storage.read(db,'progress',storage.default_progress()))
        storage.write(db,'progress',storage.hydrate_progress(value))
    return value

def undo_restore():
    with storage.transaction() as db:
        previous=storage.read(db,'pre-restore')
        if previous is None: raise ValueError('Não há restauração para desfazer.')
        current=storage.read(db,'progress',storage.default_progress())
        storage.write(db,'progress',previous);storage.write(db,'pre-restore',current)
    return previous

EXAMS={'diagnostic':(list(range(1,31,3)),20),'foundations':(list(range(1,8)),15),'ansible':(list(range(8,15)),15),'observability':(list(range(15,22)),15),'ai':(list(range(22,29)),15),'final':(list(range(1,31)),50)}

def start_exam(kind):
    if kind not in EXAMS: raise ValueError('Simulado inexistente.')
    days,minutes=EXAMS[kind]
    questions=[]
    rng=random.SystemRandom()
    for day in days:
        q=dict(rng.choice(LESSONS[day]['quiz']))
        order=list(range(3));rng.shuffle(order)
        questions.append(dict(day=day,question=q['question'],options=[q['options'][i] for i in order],answer=order.index(q['answer']),explanation=q['explanation']))
    rng.shuffle(questions)
    expires=time.time()+minutes*60
    sid=storage.session_create(dict(kind='exam',exam=kind,questions=questions,expires=expires,submitted=False))
    return dict(id=sid,minutes=minutes,expires=expires,questions=[{k:v for k,v in q.items() if k not in ('answer','explanation')} for q in questions])

def submit_exam(sid,answers):
    def update(s):
        if s['kind']!='exam': raise ValueError('Sessão não corresponde a simulado.')
        if s['submitted']: return s['result']
        if len(answers)!=len(s['questions']) or any(type(a)!=int or not 0<=a<3 for a in answers): raise ValueError('Responda todas as questões.')
        feedback=[dict(day=q['day'],question=q['question'],correct=a==q['answer'],answer=q['options'][q['answer']],explanation=q['explanation']) for a,q in zip(answers,s['questions'])]
        expired=time.time()>s['expires']
        result=dict(score=round(100*sum(x['correct'] for x in feedback)/len(feedback)),feedback=feedback,expired=expired)
        result['passed']=result['score']>=80 and not expired
        s.update(submitted=True,result=result)
        return result
    result=storage.session_update(sid,update)
    def save(p):
        for f in result['feedback']:
            if not f['correct']: p['reviews'][str(f['day'])]=dict(due=date.today().isoformat(),interval=0,last_score=0)
    storage.update_progress(save)
    return result

def portfolio():
    p=storage.progress()
    lines=['# Meu portfólio AIOps','',f'Exportado em {date.today().isoformat()} · conteúdo 1.1.0','', 'Resultados de exercícios didáticos; não são certificação de senioridade. Revise antes de compartilhar.','']
    for day,lesson in LESSONS.items():
        note=p['notes'].get(str(day),'').strip()
        if note:
            lines.extend([f'## Dia {day:02d} — {lesson["title"]}',f'Checkpoint: {p["quizzes"].get(str(day),0)}% | Concluído: {"sim" if day in p["completed"] else "não"}', '',note,''])
    guided={unit.id:unit for unit in load_curriculum().units if unit.status=='available' and unit.lesson_day is None}
    for unit_id,state in p['unit_progress'].items():
        if state.get('note','').strip() and unit_id in guided:
            lines.extend([f'## {guided[unit_id].title}',f'Lab guiado: {"resolvido" if state.get("lab_passed") else "pendente"} | Concluída: {"sim" if state.get("completed") else "não"}', '',state['note'].strip(),''])
    return '\n'.join(lines)
