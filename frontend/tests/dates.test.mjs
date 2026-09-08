import test from 'node:test';
import assert from 'node:assert/strict';
import {planEnd, dayDate, daysLeft, localDate, studyDays, validStudyStart} from '../src/utils/dates.ts';

test('30-day plan crosses year and leap-month boundaries', () => {
  assert.equal(planEnd('2035-12-15'), '2036-01-13');
  assert.equal(planEnd('2028-02-01'), '2028-03-01');
  assert.equal(dayDate('2035-12-15', 30), '13/01');
});

test('countdown is relative to the chosen target, without fixed hiring date', () => {
  assert.equal(daysLeft(localDate()), 0);
  assert.equal(daysLeft(planEnd(localDate())), 29);
});

test('lighter rates spread essential effort without shortening lessons', () => {
  assert.equal(studyDays(0.5),180);
  assert.equal(studyDays(0.75),120);
  assert.equal(studyDays(1),90);
  assert.equal(studyDays(1.5),60);
  assert.equal(studyDays(2),45);
  assert.equal(planEnd('2028-02-01',1),'2028-04-30');
  assert.equal(dayDate('2028-02-01',2,1),'04/02');
  assert.equal(dayDate('2028-02-01',30,1),'28/04');
});

test('legacy intensive rates keep original calendar', () => {
  for(const hours of [3,5]) assert.equal(planEnd('2035-12-15',hours),'2036-01-13');
});

test('partial sessions at 2h share calendar days and finish after the last lesson starts', () => {
  assert.equal(dayDate('2028-02-01',2,2),'02/02');
  assert.equal(dayDate('2028-02-01',3,2),'04/02');
  assert.equal(dayDate('2028-02-01',30,2),'15/03');
  assert.equal(planEnd('2028-02-01',2),'2028-03-16');
  assert.equal(planEnd('2035-12-15',0.5),'2036-06-11');
});

test('invalid and out-of-bounds dates never produce a form preview', () => {
  for(const iso of ['', '2028-02-30', '2027-02-29', '2000-13-01', '1999-12-31', '2101-01-01']) assert.equal(validStudyStart(iso),false,iso);
  for(const iso of ['2000-01-01', '2100-12-31', '2028-02-29']) assert.equal(validStudyStart(iso),true,iso);
});
