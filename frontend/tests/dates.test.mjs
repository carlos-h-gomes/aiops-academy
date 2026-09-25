import test from 'node:test';
import assert from 'node:assert/strict';
import {ESSENTIAL_STUDY_MINUTES,planEnd, dayDate, daysLeft, localDate, studyDays, validStudyStart} from '../src/utils/dates.ts';

test('50-lesson plan crosses year and leap-month boundaries', () => {
  assert.equal(ESSENTIAL_STUDY_MINUTES,7050);
  assert.equal(planEnd('2035-12-15'), '2036-01-23');
  assert.equal(planEnd('2028-02-01'), '2028-03-11');
  assert.equal(dayDate('2035-12-15', 30), '13/01');
});

test('countdown is relative to the chosen target, without fixed hiring date', () => {
  assert.equal(daysLeft(localDate()), 0);
  assert.equal(daysLeft(planEnd(localDate())), 39);
});

test('lighter rates spread essential effort without shortening lessons', () => {
  assert.equal(studyDays(0.5),235);
  assert.equal(studyDays(0.75),157);
  assert.equal(studyDays(1),118);
  assert.equal(studyDays(1.5),79);
  assert.equal(studyDays(2),59);
  assert.equal(planEnd('2028-02-01',1),'2028-05-28');
  assert.equal(dayDate('2028-02-01',2,1),'04/02');
  assert.equal(dayDate('2028-02-01',30,1),'28/04');
});

test('intensive rates cover the whole 50-lesson catalog', () => {
  assert.equal(planEnd('2035-12-15',3),'2036-01-23');
  assert.equal(planEnd('2035-12-15',5),'2036-01-07');
});

test('partial sessions at 2h share calendar days and finish after the last lesson starts', () => {
  assert.equal(dayDate('2028-02-01',2,2),'02/02');
  assert.equal(dayDate('2028-02-01',3,2),'04/02');
  assert.equal(dayDate('2028-02-01',30,2),'15/03');
  assert.equal(planEnd('2028-02-01',2),'2028-03-30');
  assert.equal(planEnd('2035-12-15',0.5),'2036-08-05');
});

test('invalid and out-of-bounds dates never produce a form preview', () => {
  for(const iso of ['', '2028-02-30', '2027-02-29', '2000-13-01', '1999-12-31', '2101-01-01']) assert.equal(validStudyStart(iso),false,iso);
  for(const iso of ['2000-01-01', '2100-12-31', '2028-02-29']) assert.equal(validStudyStart(iso),true,iso);
});
