// Synthetic-only local UI verification. Run through scripts/bounded.py.
import {chromium, expect} from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import {spawn} from 'node:child_process'
import {once} from 'node:events'
import {mkdtemp, mkdir, writeFile, rm} from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import {fileURLToPath} from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const temporary = await mkdtemp(path.join(os.tmpdir(), 'academy-pace-'))
const output = path.join(root, 'artifacts/pace')
await mkdir(output, {recursive:true})
const keep = new Set(['PATH','SYSTEMROOT','WINDIR','TEMP','TMP','COMSPEC','PATHEXT','USERPROFILE','LOCALAPPDATA','APPDATA','PROGRAMFILES','PROGRAMFILES(X86)'])
const env = Object.fromEntries(Object.entries(process.env).filter(([key])=>keep.has(key.toUpperCase())))
const python = path.join(root, process.platform==='win32'?'.venv/Scripts/python.exe':'.venv/bin/python')
// Port 0 and the child's startup line identify our own server, never a learner session.
const server = spawn(python, ['-m','uvicorn','app.main:app','--app-dir',path.join(root,'backend'),'--host','127.0.0.1','--port','0','--no-access-log','--no-use-colors','--log-level','info'], {
  cwd:root, env:{...env, PYTHONUTF8:'1', ACADEMY_DB:path.join(temporary,'test.sqlite3')}, stdio:['ignore','ignore','pipe'], windowsHide:true
})
let browser
let startupTimer
const checks=[]
try {
  const origin = await new Promise((resolve,reject)=>{
    startupTimer=setTimeout(()=>reject(new Error('Isolated server startup timeout')),10000)
    server.once('error',()=>reject(new Error('Isolated server could not start')))
    server.once('exit',()=>reject(new Error('Isolated server exited')))
    let startup=''
    server.stderr.on('data',chunk=>{
      startup=(startup+chunk.toString()).slice(-2000)
      const match=startup.match(/Uvicorn running on (http:\/\/127\.0\.0\.1:\d+)/)
      if(match)resolve(match[1])
    })
  })
  clearTimeout(startupTimer)
  browser=await chromium.launch({channel:'chrome',headless:true})
  const context=await browser.newContext({reducedMotion:'reduce',locale:'pt-BR',timezoneId:'America/Sao_Paulo'})
  await context.addInitScript(()=>{
    const OriginalDate=Date
    window.Date=class extends OriginalDate {
      constructor(...args){super(...(args.length?args:['2028-02-01T12:00:00-03:00']))}
      static now(){return new OriginalDate('2028-02-01T12:00:00-03:00').getTime()}
    }
  })
  const page=await context.newPage()
  page.setDefaultTimeout(8000)
  const errors=[]
  page.on('pageerror',error=>errors.push(error.message))
  await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort())
  let releaseLoading
  const loading=new Promise(resolve=>{releaseLoading=resolve})
  await page.route('**/api/v1/progress',async route=>{await loading;await route.continue()})
  await page.goto(origin+'/#/settings',{waitUntil:'domcontentloaded'})
  await expect(page.getByRole('status')).toHaveText('Preparando sua missão…')
  releaseLoading()
  await expect(page.getByRole('heading',{name:'Seu calendário'})).toBeVisible()
  await page.unroute('**/api/v1/progress')
  await expect(page.getByLabel('Disponibilidade por dia')).toHaveValue('1')

  for(const width of [1440,390,320]) {
    await page.setViewportSize({width,height:1000})
    await page.goto(origin+`/?pace=${width}#/settings`)
    const start=page.getByLabel('Início do percurso')
    const rate=page.getByLabel('Disponibilidade por dia')
    const save=page.getByRole('button',{name:'Salvar preferências'})
    await start.fill('2028-02-01')
    for(const [hours,days] of [['0.5',180],['0.75',120],['1',90],['1.5',60],['2',45],['3',30],['5',30]]) {
      await rate.selectOption(hours)
      await expect(page.getByRole('status').filter({hasText:'Previsão de término'})).toContainText(`${days} dias de estudo`)
    }
    await rate.selectOption('1')
    await expect(page.getByRole('status').filter({hasText:'Previsão de término'})).toContainText('30/04/2028')
    await start.fill('')
    await expect(start).toHaveAttribute('aria-invalid','true')
    await expect(page.getByRole('alert')).toContainText('Escolha uma data válida')
    await expect(save).toBeDisabled()
    await start.fill('2028-02-01')
    await rate.focus()
    await page.keyboard.press('Tab')
    await expect(save).toBeFocused()
    await page.keyboard.press('Enter')
    await expect(page.getByRole('status').filter({hasText:'Preferências salvas'})).toBeVisible()
    await expect(page.locator('.target-date')).toHaveText('Previsão 30/04')
    const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze()
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)
    checks.push({width,violations:axe.violations.map(v=>({id:v.id,impact:v.impact,targets:v.nodes.map(n=>n.target)})),overflow})
    await page.screenshot({path:path.join(output,`settings-${width}.png`),fullPage:true})
    expect(axe.violations).toEqual([])
    expect(overflow).toBe(false)
    await page.reload()
    await expect(rate).toHaveValue('1')
    await expect(start).toHaveValue('2028-02-01')
    await page.goto(origin+'/#/')
    await expect(page.locator('.hero-foot')).toContainText('60 min por dia')
    await expect(page.locator('.stats-grid')).toContainText('Previsão: 30/04')
    await expect(page.locator('.stats-grid .stat').last().locator('strong')).toContainText('89')
    await page.goto(origin+'/#/trail')
    await expect(page.locator('a.lesson-row[href="#/day/2"] .date-label')).toHaveText('04/02')
    await page.locator('a.lesson-row[href="#/day/2"]').click()
    await expect(page.getByText('Início previsto: 04/02 · Disponibilidade: 60 min por dia.',{exact:false})).toBeVisible()
    await page.screenshot({path:path.join(output,`lesson-${width}.png`),fullPage:false})
    expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false)
  }

  await page.goto(origin+'/#/settings')
  const rate=page.getByLabel('Disponibilidade por dia')
  const save=page.getByRole('button',{name:'Salvar preferências'})
  await rate.selectOption('0.5')
  await page.route('**/api/v1/settings',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Falha sintética ao salvar'})}))
  await save.click()
  await expect(page.getByRole('alert')).toHaveText('Falha sintética ao salvar')
  await expect(rate).toHaveValue('0.5')
  await expect(page.locator('.target-date')).toHaveText('Previsão 30/04')
  await page.screenshot({path:path.join(output,'error-320.png'),fullPage:true})
  await page.unroute('**/api/v1/settings')
  await page.route('**/api/v1/settings',route=>route.abort())
  await save.click()
  await expect(page.getByRole('alert')).toContainText('O app local não respondeu')
  await expect(rate).toHaveValue('0.5')
  await page.unroute('**/api/v1/settings')
  let releaseSave
  const saving=new Promise(resolve=>{releaseSave=resolve})
  await page.route('**/api/v1/settings',async route=>{await saving;await route.continue()})
  await save.click()
  await expect(page.getByRole('status')).toHaveText('Salvando preferências…')
  await expect(save).toBeDisabled()
  await expect(rate).toBeDisabled()
  await expect(page.getByLabel('Início do percurso')).toBeDisabled()
  releaseSave()
  await expect(page.getByRole('status').filter({hasText:'Preferências salvas'})).toBeVisible()
  await page.unroute('**/api/v1/settings')
  // Old intensive rates retain the original thirty-day calendar after a light rate.
  for(const hours of ['3','5']) {
    await rate.selectOption(hours)
    await save.click()
    await expect(page.getByRole('status').filter({hasText:'Preferências salvas'})).toBeVisible()
    await expect(page.locator('.target-date')).toHaveText('Previsão 01/03')
  }
  expect(errors).toEqual([])
  await writeFile(path.join(output,'checks.json'),JSON.stringify({checks,loading:'passed',keyboard:'passed',invalid:'passed',persistence:'passed',crossRouteDates:'passed',failureAndRetry:'passed',busy:'passed',legacyDates:'passed',pageErrors:errors},null,2))
  console.log('PASS: pace settings, dates, loading, keyboard, invalid input, save/reload, failure/retry and legacy rates; 1440/390/320, axe and overflow.')
} catch(error) {
  const detail=String(error.message).slice(0,3500)
  await writeFile(path.join(output,'failure.txt'),detail)
  console.error(detail)
  process.exitCode=1
} finally {
  clearTimeout(startupTimer)
  if(browser)await browser.close()
  if(server.exitCode===null){const exited=once(server,'exit');server.kill();await exited}
  const resolved=path.resolve(temporary)
  if(path.dirname(resolved)!==path.resolve(os.tmpdir())||!path.basename(resolved).startsWith('academy-pace-'))throw new Error('Unsafe temporary cleanup path')
  await rm(resolved,{recursive:true,force:true})
}
