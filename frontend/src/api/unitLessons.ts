import {request} from './client'
import type {UnitLesson} from '../data/curriculum'

export const fetchUnitLesson = (unitId:string) => request<UnitLesson>(`/units/${encodeURIComponent(unitId)}`)
