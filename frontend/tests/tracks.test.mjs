import {chromium,expect} from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import {mkdir,writeFile} from 'node:fs/promises'
import path from 'node:path'
import {fileURLToPath} from 'node:url'
import {localApp} from './support/local-app.mjs'

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..')
const output=path.join(root,'artifacts/curriculum')
await mkdir(output,{recursive:true})
const app=await localApp(root)
let browser
try {
  const {origin}=app
  // Only our temporary database receives this synthetic legacy fixture.
  const fixture={version:1,confirm:true,settings:{start_date:'2035-12-15',daily_hours:0.75},notes:{'1':'Evidência sintética para verificar a preservação do estudo existente.'},completed:[1],quizzes:{'1':100},labs:{linux:true},reviews:{'1':{due:'2035-12-16',interval:1,last_score:100}}}
  const seeded=await fetch(origin+'/api/v1/restore',{method:'POST',headers:{'Content-Type':'application/json','X-Academy-Client':'local'},body:JSON.stringify(fixture)})
  expect(seeded.status).toBe(200)
  const backup=await (await fetch(origin+'/api/v1/backup')).json()
  browser=await chromium.launch({channel:'chrome',headless:true})
  const context=await browser.newContext({locale:'pt-BR',timezoneId:'America/Sao_Paulo',reducedMotion:'reduce'})
  await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort())
  const page=await context.newPage()
  page.setDefaultTimeout(8000)
  const errors=[],checks=[]
  page.on('pageerror',error=>errors.push(error.message))
  async function audit(name,width){
    const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze()
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)
    const violations=result.violations.map(item=>({id:item.id,impact:item.impact,targets:item.nodes.map(node=>node.target)}))
    checks.push({name,width,overflow,violations})
    await page.screenshot({path:path.join(output,`${name}-${width}.png`),fullPage:name==='tracks'})
    expect(violations,`${name} ${width} axe`).toEqual([])
    expect(overflow,`${name} ${width} overflow`).toBe(false)
  }
  let releaseLoading
  const loading=new Promise(resolve=>{releaseLoading=resolve})
  await page.route('**/api/v1/curriculum',async route=>{await loading;await route.continue()})
  await page.goto(origin+'/#/tracks',{waitUntil:'domcontentloaded'})
  await expect(page.getByRole('status')).toHaveText('Carregando trilhas…')
  releaseLoading()
  await expect(page.getByRole('heading',{name:'Escolha o que quer construir.'})).toBeVisible()
  await page.unroute('**/api/v1/curriculum')
  for(const width of [1440,390,320]){
    await page.setViewportSize({width,height:1000})
    await page.goto(origin+`/?tracks=${width}#/tracks`)
    await expect(page.locator('.curriculum-track')).toHaveCount(4)
    await expect(page.locator('.notice')).toContainText('30 aulas disponíveis · 20 unidades em preparação')
    await expect(page.locator('.curriculum-track').first()).toContainText('1/30 aulas concluídas')
    await audit('tracks',width)
    const explore=page.getByRole('link',{name:/Explorar trilha.*Infraestrutura e AIOps/})
    await explore.focus();await page.keyboard.press('Enter')
    await expect(page.getByRole('heading',{name:'Infraestrutura e AIOps',exact:true})).toBeVisible()
    await expect(page.getByRole('status')).toHaveText('30 unidades encontradas')
    await expect(page.locator('#infra-01')).toContainText('Concluída')
    await page.locator('#infra-01 summary').click()
    await expect(page.locator('#infra-01')).toContainText('Prática: simulação no navegador')
    await expect(page.locator('#infra-01')).toContainText('Não é shell Linux')
    await audit('infra',width)
    await page.getByLabel('Buscar unidades').fill('observabilidade')
    expect(await page.locator('.curriculum-unit').count()).toBeGreaterThan(0)
    await page.getByLabel('Buscar unidades').fill('sem-resultado-xyz')
    await expect(page.getByRole('status')).toHaveText('0 unidades encontradas')
    await page.getByRole('button',{name:'Limpar filtros'}).click()
    await expect(page.getByRole('status')).toHaveText('30 unidades encontradas')
    await expect(page.getByRole('combobox')).toHaveAccessibleName(/Disponibilidade/)
    await page.getByRole('combobox').selectOption('planned')
    await expect(page.getByRole('status')).toHaveText('0 unidades encontradas')
    await page.getByRole('button',{name:'Limpar filtros'}).click()
    await page.locator('#infra-01').getByRole('link',{name:/Revisitar aula/}).click()
    await expect(page.getByRole('heading',{name:'Seu primeiro plantão começa aqui'})).toBeVisible()
    for(const [id,title,count] of [['data','Dados, SQL e RAG',6],['security','Segurança operacional',6],['agents','Agentes e processos',8]]){
      await page.goto(origin+`/#/tracks/${id}`)
      await expect(page.getByRole('heading',{name:title,exact:true})).toBeVisible()
      await expect(page.getByRole('status')).toHaveText(`${count} unidades encontradas`)
      await expect(page.locator('.curriculum-unit .primary')).toHaveCount(0)
      await expect(page.locator('.curriculum-guides a').first()).toBeVisible()
      await audit(id,width)
    }
    await page.getByRole('link',{name:'n8n: integrar processos com controle',exact:true}).click()
    await expect(page.getByRole('article',{name:'n8n: integrar processos com controle'})).toContainText('Não executa o produto real.')
    await page.reload()
    await expect(page.getByRole('article',{name:'n8n: integrar processos com controle'})).toBeVisible()
    await page.goto(origin+'/#/tracks/data')
    await page.getByLabel('Buscar unidades').fill('transacoes')
    await expect(page.getByRole('status')).toHaveText('1 unidades encontradas')
    await expect(page.getByRole('heading',{name:'Transações, backup e restauração'})).toBeVisible()
  }
  await page.goto(origin+'/#/tracks/unknown')
  await expect(page.getByRole('heading',{name:'Trilha não encontrada'})).toBeVisible()
  await page.getByRole('link',{name:'Voltar às trilhas'}).click()
  await expect(page.locator('.curriculum-track')).toHaveCount(4)
  await page.route('**/api/v1/curriculum',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Falha sintética de catálogo'})}))
  await page.reload()
  await expect(page.getByRole('alert')).toHaveText('Falha sintética de catálogo')
  await page.screenshot({path:path.join(output,'error-320.png')})
  await page.unroute('**/api/v1/curriculum')
  await page.getByRole('button',{name:'Tentar novamente'}).click()
  await expect(page.locator('.curriculum-track')).toHaveCount(4)
  await page.route('**/api/v1/curriculum',route=>route.abort())
  await page.reload()
  await expect(page.getByRole('alert')).toContainText('O app local não respondeu')
  await page.getByRole('link',{name:'Abrir trilha de infraestrutura'}).click()
  await expect(page.getByRole('heading',{name:'Sua trilha de 30 aulas'})).toBeVisible()
  await page.unroute('**/api/v1/curriculum')
  await page.goto(origin+'/#/library/not-found')
  await expect(page.getByText('Manual não encontrado. Selecione outro conteúdo na lista.')).toBeVisible()
  await page.getByRole('button',{name:'Abrir guia de estudo'}).click()
  await expect(page.getByRole('article',{name:'Como estudar aqui'})).toBeVisible()
  expect(await (await fetch(origin+'/api/v1/backup')).json()).toEqual(backup)
  expect(errors).toEqual([])
  await writeFile(path.join(output,'checks.json'),JSON.stringify({checks,loading:'passed',keyboard:'passed',filter:'passed',guideDeepLinks:'passed',unknownIds:'passed',errorRetry:'passed',offlineFallback:'passed',legacyProgressPreserved:'passed',pageErrors:errors},null,2))
  console.log('PASS: 15 track/viewport audits, search, status, legacy progress, deep links, errors and retry.')
} catch(error){
  const detail=String(error.message).slice(0,3500)
  await writeFile(path.join(output,'failure.txt'),detail)
  console.error(detail);process.exitCode=1
} finally {
  if(browser)await browser.close()
  await app.close()
}
