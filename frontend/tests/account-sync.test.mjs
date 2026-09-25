import {chromium,expect} from '@playwright/test'
import {localApp} from './support/local-app.mjs'
import path from 'node:path'
import {fileURLToPath} from 'node:url'

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..')
const app=await localApp(root)
let browser
try{
  browser=await chromium.launch({channel:'chrome',headless:true})
  const context=await browser.newContext({locale:'pt-BR',serviceWorkers:'block'})
  const page=await context.newPage()
  const remoteRequests=[]
  page.on('request',request=>{if(/\/(auth|sync)\//.test(new URL(request.url()).pathname))remoteRequests.push(request.url())})
  await page.goto(app.origin+'/#/settings')
  await expect(page.getByRole('heading',{name:'Conta e sincronização'})).toBeVisible()
  await expect(page.getByLabel('Endereço HTTPS do serviço')).toHaveValue('')
  await page.getByRole('tab',{name:'Criar conta'}).click()
  await page.getByLabel('Identificador').fill('estudante-local')
  await page.getByLabel('Credencial').fill('uma credencial de teste')
  await expect(page.getByRole('button',{name:'Criar conta'})).toBeDisabled()
  expect(remoteRequests).toEqual([])
  console.log('PASS optional account UI stays inert without an explicit endpoint')
}finally{if(browser)await browser.close();await app.close()}
