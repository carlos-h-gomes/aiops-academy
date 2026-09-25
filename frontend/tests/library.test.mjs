// Isolated loopback UI checks. No personal browser profile or study database.
import {chromium, expect} from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import {spawn} from 'node:child_process'
import {mkdtemp, mkdir, writeFile, rm} from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import {fileURLToPath} from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const temporary = await mkdtemp(path.join(os.tmpdir(), 'academy-library-'))
const output = path.join(root, 'artifacts/library')
await mkdir(output, {recursive:true})
const python = path.join(root, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python')
const origin = 'http://127.0.0.1:8876'
const server = spawn(python, ['-m','uvicorn','app.main:app','--app-dir',path.join(root,'backend'),'--host','127.0.0.1','--port','8876','--no-access-log','--log-level','error'], {
  cwd:root, env:{...process.env, ACADEMY_DB:path.join(temporary,'test.sqlite3')}, stdio:'ignore'
})
let browser
const checks = []
try {
  for(let i=0;i<80;i++) {
    if(server.exitCode !== null) throw new Error('Isolated server exited; port may already be occupied.')
    try {if((await fetch(origin+'/api/v1/health')).ok) break} catch {}
    await new Promise(resolve=>setTimeout(resolve,100))
  }
  browser = await chromium.launch({channel:'chrome',headless:true})
  const context = await browser.newContext({reducedMotion:'reduce',serviceWorkers:'block'})
  const page = await context.newPage()
  page.setDefaultTimeout(8000)
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  for(const width of [1440,390,320]) {
    await page.setViewportSize({width,height:1000})
    // A distinct document URL resets SPA filters between viewport cases.
    await page.goto(origin+`/?audit=${width}#/library`)
    await expect(page.getByRole('status').filter({hasText:'25 conteúdos encontrados'})).toBeVisible()
    await page.getByRole('button',{name:'Ferramentas e processos',exact:true}).click()
    await expect(page.getByRole('status').filter({hasText:'7 conteúdos encontrados'})).toBeVisible()
    await page.getByRole('button',{name:'n8n: integrar processos com controle',exact:true}).click()
    if(width <= 390) {
      const button = await page.getByRole('button',{name:'n8n: integrar processos com controle',exact:true}).boundingBox()
      expect(button.width).toBeGreaterThan(width - 60)
    }
    await expect(page.getByRole('article')).toContainText('Não executa o produto real.')
    const results = await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze()
    const overflow = await page.evaluate(()=>document.documentElement.scrollWidth > window.innerWidth)
    checks.push({width,violations:results.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)})),overflow})
    await page.screenshot({path:path.join(output,`n8n-${width}.png`),fullPage:false})
    expect(results.violations).toEqual([])
    expect(overflow).toBe(false)
    await page.getByRole('textbox',{name:'Buscar na biblioteca',exact:true}).fill('termo-sem-resultado-xyz')
    await expect(page.getByRole('button',{name:'Limpar filtros'})).toBeVisible()
    await page.getByRole('button',{name:'Limpar filtros'}).click()
    await page.getByRole('button',{name:'Aprofundamentos AIOps',exact:true}).click()
    await expect(page.getByRole('status').filter({hasText:'6 conteúdos encontrados'})).toBeVisible()
    await page.getByRole('textbox',{name:'Buscar na biblioteca',exact:true}).fill('correlacao')
    await page.getByRole('button',{name:'Correlação de eventos e redução de ruído',exact:true}).click()
    await expect(page.getByRole('article')).toContainText('Python no computador')
    await page.getByRole('textbox',{name:'Buscar na biblioteca',exact:true}).focus()
    await page.keyboard.press('Tab')
    await expect(page.getByRole('button',{name:'Todos',exact:true})).toBeFocused()
    await page.keyboard.press('Enter')
    await expect(page.getByRole('button',{name:'Todos',exact:true})).toHaveAttribute('aria-pressed','true')
  }
  await page.route('**/api/v1/manuals', route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Falha sintética de catálogo'})}))
  await page.reload()
  await expect(page.getByRole('alert')).toContainText('Falha sintética')
  await page.screenshot({path:path.join(output,'error-320.png')})
  await page.unroute('**/api/v1/manuals')
  await page.getByRole('button',{name:'Tentar novamente'}).click()
  await expect(page.getByRole('status').filter({hasText:'25 conteúdos encontrados'})).toBeVisible()
  expect(errors).toEqual([])
  await writeFile(path.join(output,'checks.json'),JSON.stringify({checks,keyboard:'passed',empty:'passed',retry:'passed',pageErrors:errors},null,2))
  console.log('PASS: library 1440/390/320; axe, overflow, accented search, filters, keyboard, error and retry.')
} catch(error) {
  const detail = String(error.message).slice(0,3500)
  await writeFile(path.join(output,'failure.txt'),detail)
  console.error(detail)
  process.exitCode = 1
} finally {
  if(browser) await browser.close()
  server.kill()
  if(server.exitCode === null) await new Promise(resolve=>server.once('exit',resolve))
  if(path.dirname(temporary) !== path.resolve(os.tmpdir())) throw new Error('Temporary cleanup escaped its parent.')
  await rm(temporary,{recursive:true,force:true})
}
