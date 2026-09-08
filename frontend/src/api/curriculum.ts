import {request} from './client'
import type {Curriculum} from '../data/curriculum'

export const fetchCurriculum = () => request<Curriculum>('/curriculum')
