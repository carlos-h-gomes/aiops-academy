import {chromium,expect} from '@playwright/test'
import path from 'node:path'
import {fileURLToPath} from 'node:url'
import {localApp} from './support/local-app.mjs'

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..')
const app=await localApp(root)
let browser
try {
  browser=await chromium.launch({channel:'chrome',headless:true})
  const context=await browser.newContext({locale:'pt-BR'})
  const page=await context.newPage()
  page.setDefaultTimeout(10000)
  await page.goto(app.origin+'/#/tracks')
  await expect(page.getByRole('heading',{name:'Escolha o que quer construir.'})).toBeVisible()
  const manifest=await page.evaluate(async()=>{
    const response=await fetch('/manifest.webmanifest')
    return {status:response.status,value:await response.json()}
  })
  expect(manifest.status).toBe(200)
  expect(manifest.value).toMatchObject({start_url:'/',display:'standalone',lang:'pt-BR'})
  await page.evaluate(async()=>{await navigator.serviceWorker.ready})
  const backupCached=await page.evaluate(async()=>{await fetch('/api/v1/backup');return Boolean(await caches.match('/api/v1/backup'))})
  expect(backupCached).toBe(false)

  await page.reload()
  await expect(page.getByRole('heading',{name:'Escolha o que quer construir.'})).toBeVisible()
  await context.setOffline(true)
  await page.reload({waitUntil:'domcontentloaded'})
  await expect(page.getByRole('heading',{name:'Escolha o que quer construir.'})).toBeVisible()
  await page.evaluate(()=>window.dispatchEvent(new Event('offline')))
  await expect(page.locator('.network-status')).toContainText(/Você está sem conexão.|O app local não respondeu./)
  await context.setOffline(false)
  console.log('PASS pwa offline shell and cached curriculum')
} finally {
  if(browser)await browser.close()
  await app.close()
}
