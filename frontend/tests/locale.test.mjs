import test from 'node:test'
import assert from 'node:assert/strict'
import {localeStatus,preferredLocale} from '../src/services/locale.ts'

test('locale preference accepts only declared locales and falls back safely to Portuguese',()=>{
  assert.equal(preferredLocale('pt-BR'),'pt-BR')
  assert.equal(preferredLocale('en'),'en')
  assert.equal(preferredLocale('es'),'es')
  assert.equal(preferredLocale('fr'),'pt-BR')
  assert.equal(preferredLocale(null),'pt-BR')
  assert.match(localeStatus('en'),/Portuguese remains active/)
  assert.match(localeStatus('es'),/portugués/)
})
