import {request} from './client'
import type {UnitProgress} from '../data/types'

const unitPath=(unitId:string)=>`/units/${encodeURIComponent(unitId)}`
export const saveUnitNote=(unitId:string,text:string)=>request<UnitProgress>(`${unitPath(unitId)}/note`,'PUT',{text})
export const completeUnit=(unitId:string)=>request<UnitProgress>(`${unitPath(unitId)}/complete`,'POST',{})
export const reviewUnit=(unitId:string,rating:'again'|'hard'|'good'|'easy')=>request<UnitProgress>(`${unitPath(unitId)}/review`,'POST',{rating})
