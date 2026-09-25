"""v1 HTTP adapters; all grading and persistence live in services."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse,FileResponse
from app.schemas.requests import Note,Quiz,Settings,LabRun,Rating,Restore
from app.schemas.unit_labs import UnitLab, UnitLabRun, UnitLabResult
from app.services import learning,laboratories,files
from app.services import curriculum
from app.services import unit_lessons
from app.services import unit_labs
from app.schemas.curriculum import Curriculum, UnitLesson

router=APIRouter(prefix='/api/v1')

@router.get('/health')
def health():return dict(status='ok',product='aiops-academy',version='1.2.0-beta.2')

@router.get('/course')
def course():return learning.catalog()

@router.get('/curriculum', response_model=Curriculum)
def learning_units():return curriculum.catalog()

@router.get('/units/{unit_id}', response_model=UnitLesson)
def unit_lesson(unit_id: str):
    try:return unit_lessons.detail(unit_id)
    except RuntimeError as error:raise HTTPException(status_code=404, detail='Aula não encontrada.') from error

@router.get('/units/{unit_id}/lab', response_model=UnitLab)
def unit_lab(unit_id: str):
    try:return unit_labs.detail(unit_id)
    except (RuntimeError, ValueError) as error:raise HTTPException(status_code=404, detail='Lab não encontrado.') from error

@router.post('/units/{unit_id}/lab/run', response_model=UnitLabResult)
def unit_lab_run(unit_id: str, value: UnitLabRun):
    try:
        result=unit_labs.run(unit_id, value.answers)
        learning.record_unit_lab(unit_id,result.correct)
        return result
    except (RuntimeError, ValueError) as error:raise HTTPException(status_code=404, detail='Lab não encontrado.') from error

@router.get('/units/{unit_id}/progress')
def guided_unit_progress(unit_id: str):
    try:return learning.unit_progress(unit_id)
    except ValueError as error:raise HTTPException(status_code=404, detail='Aula não encontrada.') from error

@router.put('/units/{unit_id}/note')
def guided_unit_note(unit_id: str,value: Note):
    try:return learning.save_unit_note(unit_id,value.text)
    except ValueError as error:raise HTTPException(status_code=404, detail='Aula não encontrada.') from error

@router.post('/units/{unit_id}/complete')
def guided_unit_complete(unit_id: str):
    try:return learning.complete_unit(unit_id)
    except ValueError as error:raise HTTPException(status_code=422, detail=str(error)) from error

@router.post('/units/{unit_id}/review')
def guided_unit_review(unit_id: str,value: Rating):
    try:return learning.review_unit(unit_id,value.rating)
    except ValueError as error:raise HTTPException(status_code=422, detail=str(error)) from error

@router.get('/progress')
def progress():return learning.progress()

@router.put('/notes/{day}')
def note(day:int,value:Note):return learning.save_note(day,value.text)

@router.post('/quiz/{day}')
def quiz(day:int,value:Quiz):return learning.quiz(day,value.answers)

@router.post('/complete/{day}')
def complete(day:int):return learning.complete(day)

@router.put('/settings')
def settings(value:Settings):return learning.settings(value.model_dump(mode='json'))

@router.post('/reviews/{day}')
def review(day:int,value:Rating):return learning.review(day,value.rating)

@router.get('/reviews/{day}/card')
def review_card(day:int):return learning.review_card(day)

@router.post('/labs/{lab_id}/start')
def lab_start(lab_id:str):return laboratories.start(lab_id)

@router.post('/labs/{lab_id}/run')
def lab_run(lab_id:str,value:LabRun):return laboratories.run(lab_id,value)

@router.get('/labs/{lab_id}/solution')
def solution(lab_id:str):return dict(solution=laboratories.lab_info(lab_id)['solution'])

@router.post('/exams/{kind}/start')
def exam(kind:str):return learning.start_exam(kind)

@router.post('/exams/{sid}/submit')
def submit(sid:str,value:Quiz):return learning.submit_exam(sid,value.answers)

@router.get('/backup')
def backup():return learning.backup()

@router.post('/restore')
def restore(value:Restore):return learning.restore(value.model_dump(mode='json'))

@router.post('/restore/undo')
def undo():return learning.undo_restore()

@router.get('/portfolio',response_class=PlainTextResponse)
def portfolio():return learning.portfolio()

@router.get('/manuals')
def manuals():return files.manuals()

@router.get('/kit')
def kit():return FileResponse(files.kit(),filename='aiops-labs-reais.zip',media_type='application/zip')
