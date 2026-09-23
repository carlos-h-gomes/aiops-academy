import {request} from './client'
import type {UnitLab,UnitLabResult} from '../data/curriculum'

export const fetchUnitLab = (unitId:string) => request<UnitLab>(`/units/${encodeURIComponent(unitId)}/lab`)
export const runUnitLab = (unitId:string,answers:Record<string,string>) => request<UnitLabResult>(`/units/${encodeURIComponent(unitId)}/lab/run`,'POST',{answers})
