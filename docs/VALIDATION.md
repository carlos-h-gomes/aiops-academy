# Validação local

## Beta pública local 1.2.0-beta.1 — 2026-09-07

O candidato de distribuição passou, no Windows 11 com Python 3.14.6 e Node 24, pelos checks estruturais de arquitetura, documentação e UI; testes backend; testes Node de calendário/catálogo; build TypeScript/Vite; referências Python, HTTP e delivery; empacotamento determinístico; extração nova e smoke de API/UI/conteúdo/kit. A saúde da extração informou `1.2.0-beta.1`, com 30 aulas disponíveis, quatro trilhas e 20 unidades planejadas. Todos os comandos terminaram com saída 0.

A preparação completa (`scripts/prepare.py`, mesma lógica usada por `preparar.cmd`) também passou em uma pasta recém-extraída: criação de ambiente Python, instalação dos requisitos fixados, `npm ci --ignore-scripts`, build e geração do kit. Isso valida uma instalação limpa no mesmo computador; não comprova outro hardware, outra conta Windows, Linux ou macOS. O wrapper `.cmd` não foi automatizado porque contém uma pausa interativa, mas seu único passo de preparação chama o script testado.

Revisão de publicação: seleção Git e ZIP excluem `data/`, bancos, `.venv`, `node_modules`, `artifacts`, `docs/ai`, logs, chaves e arquivos `.env`. Busca heurística não encontrou padrões de credencial. `npm audit` encontrou 0 vulnerabilidades em 74 dependências resolvidas; `pip-audit 2.10.1` encontrou 0 nas 17 dependências Python; Bandit 1.9.4, limitado a achados de alta severidade e alta confiança, terminou com saída 0. Essas ferramentas têm cobertura limitada e não provam ausência de falhas.

O ZIP versionado contém 172 entradas, manifesto de hashes e o frontend compilado. A identidade SHA-256 final e a revisão Git são publicadas na release do GitHub depois da geração sobre o commit lançado. A release só deve ser criada se o workflow hospedado estiver verde; consulte [Actions](https://github.com/carlos-h-gomes/aiops-academy/actions) e [Releases](https://github.com/carlos-h-gomes/aiops-academy/releases).

Limites mantidos: sem leitor de tela dedicado, matriz de outros navegadores/sistemas, instalação em segundo computador, aplicação hospedada, contas, sincronização, PWA ou traduções. As 20 unidades novas são planejamento; os guias não equivalem a laboratórios Docker/VM/cloud completos.

Versão 1.1.0, verificada localmente em 2026-09-06.

- 23 testes de API: passaram, incluindo data inicial persistida, preservação do progresso anterior e restauração de backup v1.
- Dois testes de calendário: passaram, cobrindo virada de ano, ano bissexto e contagem relativa.
- Build TypeScript/Vite: passou. O campo de data atualiza a prévia durante a edição e salva o calendário escolhido.
- Seis casos do exercício Python de referência e 12 requisições do laboratório HTTP: passaram.
- 27 combinações de rota e largura (1440, 390 e 320): sem violações automáticas de acessibilidade e sem overflow horizontal do documento. Não equivale a certificação WCAG completa.
- Revisão manual: navegação, identidade geral, foco e calendário 15/12/2035 → 13/01/2036 conferidos. Menu móvel abriu e levou às preferências.
- Verificações locais de arquitetura e documentação passaram. O Git foi iniciado sem commit e sem remoto. Dados, ambientes e memória privada são ignorados.

A primeira tentativa de edição de data pela interface expôs uma prévia que não acompanhava o valor do campo; o evento de edição foi corrigido e o fluxo de salvar/navegar foi verificado novamente. Nenhuma migração ou limpeza de dados pessoais foi executada.

O ambiente de referência é Windows, Python 3.14 e Node 24. A CI em .github/workflows/ci.yml está preparada e ainda não foi executada no GitHub. Actions oficiais foram conferidas em 2026-09-06: [checkout](https://github.com/actions/checkout/releases), [setup-python](https://github.com/actions/setup-python/releases), [setup-node](https://github.com/actions/setup-node/releases), com versões exatas fixadas por SHA no workflow.

Não foram provisionados serviços de nuvem, tenant Dynatrace, AAP ou cluster Kubernetes. Ansible real exige um ambiente Linux/WSL separado. Não há certificação formal de acessibilidade nem avaliação de senioridade. Os testes usam dados sintéticos; evidências e bancos locais não integram o Git.

Comandos reproduzíveis estão em CONTRIBUTING.md. Execute-os antes de enviar alterações. IDs de dias/laboratórios e backup v1 são contratos que devem permanecer compatíveis.

## Incremento Unreleased — início da V1 aprovada

Verificado em 2026-09-07, sobre a base 1.1.0. Nenhuma publicação oficial foi realizada.

- 27 testes de backend/autoria passaram: os 23 existentes e quatro novos casos de catálogo, incluindo metadados inválidos, duplicação e preservação da saída em erro. API e backup usam banco temporário.
- 12 casos dos aprofundamentos Python passaram contra a solução de referência; o arquivo do aluno continua contendo exercícios a resolver.
- Build TypeScript/Vite passou. Biblioteca integra 25 entradas: 12 essenciais, seis aprofundamentos e sete guias de ferramentas e entrega.
- UI em 1440/390/320: zero violações automáticas axe nas tags WCAG verificadas, zero overflow e zero erros de página; busca com acentos, filtros, teclado, ausência de resultados e erro/retry passaram. Capturas revisadas visualmente. Não é certificação completa de acessibilidade; leitura com tecnologia assistiva dedicada não foi revalidada neste incremento.
- O teste inicialmente preservava filtro entre viewports por reutilizar a URL com hash. Corrigido o isolamento do documento. A revisão visual também encontrou colunas móveis excessivamente estreitas; CSS corrigido e largura mínima passou a ser verificada.
- Geração do kit verificou limites, caminhos, bytes e extração nova. O kit inclui fontes, manuais e licenças.

Comandos com saída 0: scripts/bounded.py envolvendo author_manuals.py, unittest discover -s backend/tests -v, aiops_extensions/check.py --solution, npm run build, node tests/library.test.mjs e package_kit.py. Checks estruturais de arquitetura e documentação passaram antes da execução.

Os guias n8n/NiFi/Power Automate são exercícios de decisão, sem instalação dos produtos. Não foram executados provedores cloud, inferência, login, sync ou PWA. A versão pública completa permanece no backlog aprovado.

Kit: 21 arquivos; SHA256 `2175db6a3534d3cc6bdc857ae28ccd03c84c29b2c552ecd80c5cae3c2b64ee48`. Evidências locais em artifacts/library/checks.json e kit-manifest.json; não integram o Git.

Após o adendo GitHub/CI/CD: catálogo regenerado com 25 entradas; 27 testes backend/autoria e UI repetidos com sucesso para o novo conteúdo; seis testes de referência de delivery passaram. Checks de documentação e UI em perfil dev passaram. O workflow didático permanece inativo e não foi executado remotamente.

## Incremento Unreleased — ritmo flexível (retomada em 2026-09-07)

Concluído localmente sobre o código já iniciado. Foram preservados os arquivos existentes; o repositório ainda não possui commit-base, portanto esta evidência identifica o estado por arquivos e hashes locais, sem alegar diff contra uma revisão Git.

| Verificação | Comando, a partir da pasta indicada | Resultado |
| --- | --- | --- |
| API, catálogo e backups (raiz do app) | `python scripts/bounded.py 90 .venv/Scripts/python.exe -m unittest discover -s backend/tests -v` | 30 testes, saída 0 |
| Calendário (frontend) | `python ../scripts/bounded.py 30 node --test tests/dates.test.mjs` | 6 testes, saída 0 |
| Compilação (frontend) | `python ../scripts/bounded.py 120 npm.cmd run build` | Saída 0 no estado final |
| Interface (frontend) | `python ../scripts/bounded.py 120 node tests/pace.test.mjs` | Saída 0 no estado final |

Cobertura de dados: taxas permitidas; rejeição de booleanos, strings, nulos e taxas não suportadas; datas inválidas; preferência inicial de 1h; preferências antigas preservadas; notas, conclusões, quizzes, labs e revisões conservados na mudança de ritmo. Todos os ritmos fazem roundtrip de backup, substituição e undo. Backup com taxa inválida não altera o progresso nem o ponto de recuperação. Testes usam exclusivamente SQLite temporário.

Cobertura de calendário: ano bissexto, virada de ano, 180/120/90/60/45/30 dias, aula compartilhando uma sessão no ritmo de 2h, data inicial válida e contagem relativa. As datas de 3h/5h permanecem iguais ao calendário legado.

Interface: Chrome isolado, data fixa de 01/02/2028, preferência sintética e larguras 1440/390/320. Testados carregamento, sete opções, prévia, data vazia, Tab/Enter/foco de salvar, salvamento, reload, coerência entre cabeçalho/painel/trilha/aula, erro HTTP, falha de rede, preservação da edição, retry e controles indisponíveis durante envio. Axe nas preferências: zero violações nas tags verificadas. Zero overflow nas preferências e na aula 2, zero erros JavaScript. Capturas finais revisadas visualmente em `artifacts/pace`; resultado em `artifacts/pace/checks.json`. Não representa auditoria integral de todas as aulas nem certificação WCAG.

Tentativas: compilação inicial falhou por importação malformada introduzida na edição, corrigida; a segunda compilação passou. A primeira execução de interface expirou ao identificar a linha de inicialização; teste delimitado com logs sem cor confirmou o servidor e a configuração foi corrigida. A segunda chegou à aula móvel e detectou overflow real no grid. A captura demonstrou a necessidade de `min-width:0` no conteúdo. O contrato registrou uma terceira e última compilação/execução de interface por essa nova evidência; ambas passaram. O arquivo failure.txt local é histórico das tentativas anteriores, não o resultado final.

Arquitetura e documentação foram verificadas antes da execução de código do app. Os gates finais e hashes do estado constam no registro local `artifacts/pace/manifest.json` e na memória operacional. Os processos de teste foram encerrados. Nenhum banco pessoal, perfil do navegador ou configuração de conta foi usado.

Fechamento: `architecture_check.py`, `documentation_check.py` e `ui_quality.py`, todos com `--root . --profile dev` via runner de 30s, passaram com saída 0. Os 11 JSONs de contrato/design/revisão passaram pelo validador dos schemas do Harness, saída 0. OpenAPI local regenerado com os sete ritmos, saída 0. Essas verificações estruturais complementam a revisão; não substituem os testes funcionais ou a aprovação de lançamento.

Limites: não executados CI hospedada, publicação, instalação de dependências, matriz Linux/macOS, auditoria dedicada com leitor de tela ou novo empacotamento de distribuição. Kit de exercícios não mudou neste incremento. Backups com taxas novas podem ser rejeitados pelo app antigo; procedimento de retorno documentado no manual e na documentação técnica. Não há alteração de dependências ou nova chamada externa. V1-02/03 completa, contas, idiomas, PWA e laboratórios de provedores permanecem no backlog.

## Incremento Unreleased — catálogo e trilhas (2026-09-07)

38 testes backend/autoria passaram (os 30 existentes e oito de currículo), com `python scripts/bounded.py 90 .venv/Scripts/python.exe -m unittest discover -s backend/tests -v`, saída 0. Cobertura nova: quatro trilhas, IDs estáveis, 30 disponíveis/20 planejadas, duração 90h/142h, grafo sem duplicação/ciclos/referência quebrada, tipos estritos, URLs, traduções, referências obsoletas, geração reproduzível e preservação da saída em erro. Leitura limitada de arquivo e erro seguro do catálogo testados. API mantém curso, todas as áreas do progresso e backup antigo idênticos após a leitura; não permite concluir uma aula inexistente.

Nove testes Node passaram, com `python ../scripts/bounded.py 30 node --test tests/dates.test.mjs tests/curriculum.test.mjs` em frontend, saída 0. Os três novos verificam busca sem acentos, filtro por disponibilidade, ordenação sem mutar entrada, projeção de conclusões antigas e ausência de progresso/duração fictícios nas trilhas planejadas. Build TypeScript/Vite passou na primeira execução, saída 0.

Autoria: `python scripts/bounded.py 30 .venv/Scripts/python.exe scripts/author_curriculum.py`, saída 0. Gera catálogo/schema e confere fontes internas; não acessa fontes remotas nem banco do aluno. Os testes comparam bytes gerados e schema exportado ao modelo atual.

UI: `python ../scripts/bounded.py 120 node tests/tracks.test.mjs`, saída final 0. Quinze combinações: catálogo e quatro detalhes, cada um em 1440/390/320. Zero violações axe nas tags verificadas, zero overflow e zero erros JavaScript. Carregamento, busca, filtros, vazio, teclado, progresso antigo, aula existente, guias diretos/reload, IDs desconhecidos, erro/retry e fallback para trilha legada passaram. Backup sintético permaneceu exatamente igual antes/depois. `library.test.mjs` foi repetido pela alteração de links e passou, saída 0.

Tentativas da interface: duas falhas de seletores do teste (espaço no nome acessível do link e texto de opções incluído no label nativo do select). Corrigidos os seletores sem alterar o produto para satisfazer o teste. A terceira rodada, registrada no contrato com as evidências das diferenças, passou. Capturas finais tracks-1440.png, tracks-320.png, infra-390.png e agents-1440.png foram abertas e inspecionadas: distinção entre pronto/planejado, leitura móvel, prática/limites e fontes legíveis. Evidência em artifacts/curriculum/checks.json; sem leitor de tela dedicado ou certificação WCAG integral.

Arquivos centrais: schemas/curriculum.schema.json; backend/app/schemas/curriculum.py, models/curriculum.py e services/curriculum.py; controllers/api.py; backend/content/curriculum.json; scripts/author_curriculum.py; frontend/src/{api,data,services}/curriculum.ts, hooks/useCurriculum.ts, pages/TracksPage.tsx, components/ui/LearningUnitCard.tsx e assets/curriculum.css. Navegação, Biblioteca, README, manuais, contribuição, índices e CI local atualizados. `.gitignore` e package_app.py agora distinguem dados do aluno em /data dos tipos de fonte em frontend/src/data.

Verificação de distribuição: package_app.py inclui assertions de tipos, catálogo e schema; valida hashes dos arquivos e extração nova, depois testa API legada, quatro trilhas/50 registros, arquivo da UI, kit e ausência da rota de QA com banco temporário. Registro de execução/identidade do artefato em artifacts/release-manifest.json; a documentação no pacote descreve limites e não anuncia uma V1 pública pronta. Instalação independente em outro computador e CI hospedada não foram executadas.

Limites deste incremento: unidades novas são registros editoriais, não aulas/labs finalizados; conteúdos legados não passaram por nova revisão externa. Sem alteração de dependências, modelos reais, autenticação, sincronização, PWA, conta, infraestrutura ou publicação. Mudanças de leitura não migraram dados. A nova API valida referências e falha de forma segura, mas isso não substitui revisão editorial das fontes.

Fechamento: a verificação final de arquitetura detectou importação de services pelo componente visual LearningUnitCard. A projeção foi mantida em TracksPage, que agora passa somente o booleano de conclusão ao componente. Nenhuma regra de arquitetura foi reduzida. Contrato registrou a rodada adicional por esse defeito novo; arquitetura, build e a quarta execução de trilhas passaram, saída 0. Documentação e ui_quality em perfil dev também passaram. Biblioteca não precisou de nova repetição depois desse ajuste restrito ao card. O pacote anterior ao ajuste foi regenerado a partir do build final; identidade final está no manifesto de distribuição local. OpenAPI atualizado inclui /api/v1/curriculum e seus modelos.
