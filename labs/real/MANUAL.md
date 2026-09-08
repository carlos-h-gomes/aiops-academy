# Kit AIOps Academy

Exercícios locais e roteiros opcionais. Leia cada escopo antes de executar.

# Como estudar aqui

## Seu ponto de partida
Este percurso parte do zero e apresenta IA para infraestrutura, com Ansible, Dynatrace, observabilidade, AWS (S3, Lambda, OpenSearch) e GCP. Este é material independente para qualquer pessoa interessada em AIOps. A prática usa dados sintéticos.

## Ritmo recomendado
Recomendação de planejamento: 5 horas líquidas nos dias comuns. Separe 60min para fundamentos, 180min para prática e 60min para revisão/evidência. Faça pausas de 10–15min entre blocos e um intervalo maior. Nos dias 7, 14, 21 e 28, use apenas 3h para consolidar. Total completo: 142h. O percurso essencial usa 3h/dia, total 90h: 40min de leitura, 100min de bancada e 40min de checkpoint/evidência. O conteúdo é o mesmo; deixe desafios de profundidade e parte dos roteiros externos para outro momento.

## Cada dia tem três etapas
1. Aprender: leia conceitos e execute os pequenos exemplos em ambiente próprio quando indicado.
2. Praticar: siga a missão. Tente por 20 minutos antes de abrir uma pista. A solução serve para destravar; refaça sem copiar.
3. Comprovar: responda o checkpoint e registre entrada, resultado, interpretação e limitação.

O servidor só marca o dia concluído quando o checkpoint tem pelo menos 80%, a bancada associada foi resolvida e há evidência com 80 caracteres ou mais. Esse tamanho é apenas um limite de formulário: não avalia a qualidade do seu texto. Use a rubrica. Bancadas compartilhadas reaparecem com tarefas de profundidade diferentes; o resultado salvo da bancada pode ser reutilizado, mas a evidência diária deve ser nova.

## Duas camadas de prática
As 11 bancadas são simulações ou corretores determinísticos. Nunca executam comandos na sua infraestrutura. O kit real traz Python, Ansible localhost, serviço HTTP e fixtures. Execute os arquivos separadamente e só na pasta de estudo. Roteiros Dynatrace, AWS e GCP dependem de tenant/sandbox próprio. O curso não cria contas ou paga serviços.

## Calendário e progresso
A data inicial é o dia do primeiro acesso e fica salva. Você pode alterá-la em Preferências; o app calcula o fim do ciclo de 30 dias. Programe o estudo conforme sua disponibilidade. Não comprima descanso ou esconda lacunas para marcar tudo. Priorize os checkpoints de Ansible, observabilidade e cloud.

## Como usar os simulados
Faça Diagnóstico antes de estudar; não precisa acertar para começar. Depois use os quatro checkpoints e o Final. Alternativas e seleção do banco variam. O servidor confere o tempo. Erros alimentam revisões; resultados finais da tentativa ficam na sessão do navegador e não são certificado. As revisões usam intervalos crescentes que você ajusta pela dificuldade lembrada.

# Preparação e recuperação

## Abrir no Windows
Na pasta aiops-academy, dê dois cliques em iniciar.cmd. Depois da preparação inicial, ele abre http://127.0.0.1:8765 no navegador. O servidor só escuta no próprio computador e encerra após 8h. Deixe sua janela aberta enquanto estuda; Ctrl+C encerra. Abrir outra vez preserva progresso.

Se a preparação ainda não foi feita, use preparar.cmd. É necessário Python 3.12 ou superior e Node.js 22.12 ou superior em uma linha LTS suportada. Esta entrega foi testada com Python 3.14 e Node 24. A instalação inicial baixa dependências públicas para .venv e frontend/node_modules, sem instalação global. Internet só é necessária nessa preparação e nos links externos.

## Se não abrir
1. Leia a mensagem da janela, sem fechá-la imediatamente.
2. Se Python ou Node estiver ausente, instale da fonte oficial e reabra o terminal.
3. Se a porta estiver ocupada por outro serviço, não encerre processos desconhecidos. Use python launcher.py --port 8766 e abra o endereço informado.
4. Se aparecer falha de interface não compilada, execute preparar.cmd e tente de novo.
5. Se o navegador perdeu conexão, reinicie o app e use Tentar novamente. Rascunhos de notas são guardados no navegador; salve a evidência para incluí-los no backup.

## Backup que você consegue restaurar
Em Preferências, exporte JSON. Guarde uma cópia fora da pasta do app. Para restaurar, selecione o arquivo ou cole seu conteúdo; confira quantas notas foram encontradas e confirme a substituição. O servidor valida versão, IDs e limites antes de gravar e preserva o estado anterior para Desfazer última restauração.

O backup contém preferências, notas salvas, conclusões, melhores checkpoints, bancadas resolvidas e revisões. Não contém rascunhos ainda não salvos nem sessões transitórias. O banco local fica em data/academy.sqlite3. Com o app parado, uma cópia desse arquivo também serve de recuperação técnica. Não edite SQLite com o app em execução.

## Privacidade
Não existe login nem isolamento entre processos que usam a mesma conta local. Não coloque dados internos da empresa no app. Somente o build da interface e artefatos explicitamente permitidos são servidos; arquivos de estudo não são publicados na internet. Nenhuma configuração substitui as políticas e controles da empresa.

# Python real · eventos

## Objetivo e requisitos
Python instalado; nenhum pacote externo é necessário. Edite labs/real/python/exercise.py. Há três funções para implementar: normalize, summarize e z_score. Os testes começam falhando por exercício incompleto; isso é intencional. A implementação de referência fica em solution.py. Tente antes de ler.

## Contrato
normalize recebe uma lista de objetos. Um evento válido tem id não vazio e status inteiro entre 100 e 599. bool não conta como inteiro HTTP. Valide antes de deduplicar; um registro inválido não reserva seu ID. Guarde o primeiro evento válido para cada ID. Retorne unique_valid, invalid, duplicates e error_rate em porcentagem; use None para taxa sem dados válidos.

summarize agrupa somente eventos ERROR por service.name e retorna contagens. z_score recebe observado, média e desvio; retorna None se desvio é zero e rejeita desvio negativo. Não use eval, rede ou arquivos globais. As funções devem ser puras.

```powershell
python labs/real/python/check.py
```

Na pasta extraída do kit, use python python/check.py. O verificador limita-se aos fixtures locais. Critério: todos os testes passam, e você consegue explicar o caso de evento inválido que reutiliza um ID válido mais tarde. Depois rode a solução de referência somente para comparar:

```powershell
python labs/real/python/check.py --solution
```

## Variação e evidência
Adicione um evento de erro novo; recalcule a taxa. Adicione duplicata e comprove que a taxa não muda. Troque status numérico por string e comprove que o registro vai para invalid. Explique o que precisaria mudar para duas instâncias concorrentes: o set local não é ledger distribuído, e efeitos precisam de armazenamento atômico.

## Falhas comuns
Usar len original como denominador inclui duplicatas. int('erro') lança exceção. isinstance(True, int) é verdadeiro em Python, por isso cheque o tipo exato quando o contrato rejeita booleanos. Retornar 0 para conjunto vazio inventa saúde. Registre uma dessas falhas e como seu teste a detectou.

# Ansible real · localhost

## Escopo local
Este roteiro usa Ansible de verdade dentro de Linux/WSL, em um diretório de estudo. Não instala pacotes do sistema, não usa sudo e não conecta a hosts remotos. O playbook só cria workspace ao lado de site.yml, renderiza agent.conf e verifica conteúdo. Não executamos a instalação de WSL nem habilitamos recursos do Windows por você.

## Preparar
Se já possui WSL Ubuntu configurado e de confiança, abra-o e copie a pasta ansible do kit para uma pasta sua. No WSL, /mnt/e corresponde à unidade E. Use caminhos entre aspas quando houver espaços. Caso o ambiente não tenha suporte a venv, prepare isso no seu Linux com a documentação da distribuição antes de continuar.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
ansible --version
```

Confira que inventory.ini contém apenas localhost com ansible_connection=local. Não reutilize um inventário corporativo.

```bash
ansible-playbook -i inventory.ini site.yml --syntax-check
ansible-playbook -i inventory.ini site.yml --list-hosts
ansible-playbook -i inventory.ini site.yml --check --diff
ansible-playbook -i inventory.ini site.yml
ansible-playbook -i inventory.ini site.yml
```

## Resultado esperado
A primeira execução cria o diretório e a configuração. A segunda termina com changed=0. O handler de mensagem roda quando o template muda. A verificação de conteúdo real roda em execução normal; em check mode ela é ignorada porque o arquivo pode não existir ainda. Isso ilustra uma limitação real de dry-run.

## Quebre e conserte
Mude a variável message e observe o diff e o handler. Provoque indentação inválida em uma cópia do arquivo e confirme que syntax-check falha antes de escrever. Altere o conteúdo manualmente em workspace/agent.conf e execute novamente para observar correção de drift. Restaure os fontes pelo kit original se precisar.

## Limpeza e limites
Workspace é o único efeito do playbook; .venv guarda dependências. Depois de revisar o caminho absoluto, você pode remover apenas essas pastas de estudo pelo explorador. Não há hosts remotos, WinRM, AAP ou permissões de produção neste teste. O lab Windows no app continua sintético; prática real requer VM própria e configuração segura do transporte.

# HTTP real · falha controlada

## Uma API de laboratório real
O kit inclui um servidor HTTP pequeno, limitado a loopback e ao tempo de execução. Você observa uma requisição de verdade, logs JSON e métricas Prometheus em texto. A fixture simula erro/latência; não é aplicação financeira, e não envia tráfego para terceiros.

```powershell
python labs/real/http_lab/bench.py
```

O bench inicia o servidor em uma porta dinâmica, faz um conjunto limitado de requisições, mede sucesso e falha nos cenários healthy e degraded, imprime resumo e encerra o processo filho. Tudo acontece no seu computador. Não gera carga ilimitada nem precisa de Docker.

## Investigar manualmente
Em um terminal execute o servidor, que encerra após dez minutos:

```powershell
python labs/real/http_lab/service.py --seconds 600 --port 8877
```

Em outro terminal, consulte:

```powershell
curl.exe --max-time 3 http://127.0.0.1:8877/quotes
curl.exe --max-time 3 http://127.0.0.1:8877/quotes?scenario=degraded
curl.exe --max-time 3 http://127.0.0.1:8877/metrics
```

## O que você precisa explicar
/health mede se o processo responde, mas /quotes pode retornar erro no cenário degradado. Os logs carregam cenário, caminho, status e duração em ms. /metrics expõe um contador de requisições e erros; esses contadores são da fixture e reiniciam com o processo. Calcular taxa requer janela e delta; dividir o acumulado de toda a vida pode esconder uma piora recente.

Compare o tempo healthy/degraded, encontre um evento e escreva uma hipótese. Não use essa fixture para testar internet, produção ou carga de terceiros. Ela mostra HTTP e telemetria básica; instrumentação OpenTelemetry completa e exportação para um backend são uma extensão posterior.

## Critério de aprovação
Bench termina sozinho, healthy tem zero erros, degraded tem os erros projetados, métricas batem com a contagem e nenhum processo permanece após o teste. Anexe o resumo ao portfólio e explique a diferença entre processo disponível e função saudável.

# Dynatrace real · roteiro

## Antes de começar
Use somente tenant de treinamento com permissão de leitura apropriada. A experiência e os nomes de menus variam por versão/perfil. A bancada DQL local é um preparatório; não comprova experiência no produto. Não é necessário criar trial para concluir o percurso local. Consulte condições atuais antes de qualquer conta ou licença.

## Missão 1 — navegação com uma pergunta
Escolha um serviço de demonstração conhecido. Ajuste janela de 30min e fuso. Registre nome da entidade, volume, erros e latência. Abra uma dependência e um trace com erro. Critério: explique qual span concentrou a duração e como ele se relaciona com um log permitido. Se não há dados, investigue coleta e permissão antes de concluir saúde.

## Missão 2 — DQL no produto
Abra uma área de consulta/notebook disponível no tenant. Use fetch logs com janela curta definida pela interface. Inspecione nomes e tipos dos campos antes de copiar os exemplos. Filtre severidade, agrupe por serviço e projete registros de um trace. Se service.name não existir no dataset, escolha o campo observado e documente a adaptação. Não invente resultados.

## Missão 3 — problema e topologia
Abra um problema de demonstração. Liste entidades afetadas, início, impacto e causa sugerida. Compare mudança recente e dependências. Escreva uma hipótese alternativa e a evidência que permitiria descartá-la. Critério: resumo de investigação com fatos separados de inferência.

## Missão 4 — automação sem execução
Desenhe evento → filtro → enriquecimento → aprovação → template Ansible → verificação. Confirme quais integrações e permissões existem no tenant; não crie token amplo nem workflow ativo. Critério: contrato de entrada, identidade executora, limite de alvos, cooldown, rollback e kill switch.

## Se houver sandbox com instalação autorizada
Antes de OneAgent: plataforma suportada, modo de monitoramento, privilégio, egress, dado coletado, custo e forma de remover. Use procedimento oficial e não desative verificações TLS. Evidência: host de estudo identificado e sinais chegando, sem dados pessoais. A instalação não foi executada por este curso e é uma mudança separada.

## Levar para o onboarding
Pergunte ao time: quais dashboards são autoritativos, qual naming/tagging, quem cuida da coleta, qual runbook de telemetria ausente e qual fluxo de aprovação de remediação. Não suponha que o ambiente da empresa coincide com o laboratório ou com screenshots de versões antigas.

# AWS real · S3 e Lambda

## Escopo e custo
Este é um roteiro opcional para conta sandbox sua e autorizada. Não será provisionado automaticamente. Defina região, prazo curto e teto de gasto antes de criar recursos; alertas de orçamento não são bloqueio rígido de cobrança. Use dados fictícios e uma conta de treinamento autorizada. O laboratório local de eventos oferece a alternativa sem cloud.

## Preparar um teste pequeno
1. Crie um bucket privado exclusivo do exercício, mantendo bloqueio de acesso público. Use prefixos input/ e output/.
2. Habilite proteções e política de retenção conforme o exercício, registrando seu efeito e custo. Se usar versionamento, lembre que versões antigas continuam ocupando espaço.
3. Prepare uma role de execução com leitura somente em input/, escrita somente em output/ e logs no grupo do exercício. Valide confiança da role separadamente das permissões.
4. Crie uma Lambda com runtime suportado, timeout curto e concorrência reservada pequena. Nunca use chave fixa no código.

## Implementar com contrato
No kit, normalize valida evento sintético. Para uma integração real, adapte o handler ao evento S3 observado: percorra Records, confirme origem, bucket/key e versão, decodifique key conforme o contrato e rejeite objeto fora do prefixo. Grave saída sob chave idempotente. Um ledger compartilhado precisa tratar concorrência e falha parcial; o set do exercício Python não é suficiente para produção.

## Testar sem loop
Configure notificação apenas para input/ e tipo de evento escolhido. Envie um arquivo com poucos eventos fictícios. Confirme uma saída, um registro de correlação sem segredo e as métricas da função. Reenvie a mesma identidade lógica e verifique que não duplica o efeito. Submeta conteúdo inválido e verifique a rota de erro. Não ligue output/ ao mesmo gatilho.

## Evidência e encerramento
Registre IDs não sensíveis do exercício, política conceitual, métricas de invocação/erro/duração, resultado de duplicata e invalid. Sem logs brutos com credenciais. Ao terminar: desative o gatilho, verifique execuções pendentes, remova exclusivamente recursos do exercício e todas as versões de objetos se sua intenção for apagar o bucket. Essa limpeza precisa de conferência do alvo e é executada por você na sandbox.

## Perguntas para se avaliar
O que acontece se a função grava a saída e falha antes de registrar conclusão? O que limita o custo de um loop? Qual permissão deixa de ser necessária se a função só lê? Como você reprocessa após corrigir um erro sem repetir o efeito? Registre respostas e o que não conseguiu verificar.

# OpenSearch real · ingestão

## Preparação
Use cluster local isolado ou domínio sandbox autorizado. O curso não inicia um domínio gerenciado, que pode gerar cobrança contínua. Confirme versão suportada, autenticação, limites de memória/disco, acesso de rede e prazo de limpeza. Nunca exponha uma instalação sem autenticação à internet. Os passos abaixo são entradas para Dev Tools de um ambiente de estudo; não são executados pelo app.

## Criar contrato do índice
Use um nome exclusivo: aiops-training-demo. Confira se não existe antes de criar. Mapping: timestamp como date; service.name e loglevel como keyword; duration_ms como double; content como text. Use poucos documentos sintéticos dos fixtures do kit. Não habilite ingestão contínua.

```json
PUT aiops-training-demo
{"mappings":{"properties":{"timestamp":{"type":"date"},"service.name":{"type":"keyword"},"loglevel":{"type":"keyword"},"duration_ms":{"type":"double"},"content":{"type":"text"}}}}
```

No Dev Tools, método/caminho ficam na primeira linha e o JSON abaixo. Em HTTP puro, método e corpo são enviados separadamente. Indexe um documento com ID estável de estudo:

```json
PUT aiops-training-demo/_doc/demo-1
{"timestamp":"2026-09-06T09:05:00Z","service.name":"quotes","loglevel":"ERROR","duration_ms":1200,"content":"upstream timeout"}
```

## Consultar e comparar
Espere a atualização de busca conforme o ambiente ou use refresh apenas para este pequeno exercício. Faça GET aiops-training-demo/_search com o corpo Query DSL da aula 20. Um documento ERROR deve gerar doc_count=1 em quotes. Adicione outro com ID diferente e observe 2; grave novamente demo-1 e explique substituição por identidade versus duplicação.

## Investigar falhas
Envie duration_ms como texto inválido em um documento de teste. Observe o erro de mapping sem alterar o mapping para aceitar qualquer coisa. Em bulk, inspecione erros por item. Não use volume alto ou teste de estresse. Verifique tamanho do índice e retenção; decida um prazo de remoção.

## Critério e limpeza
Evidência: mapping, dois documentos sintéticos, agregação esperada e erro de tipo compreendido. Depois de conferir nome e ausência de dados externos, remova apenas o índice de treinamento pela ferramenta do seu ambiente. Não confunda réplica com backup: o próximo exercício de profundidade é restaurar um snapshot em outro índice de sandbox e comparar a contagem.

# GCP real · identidade e eventos

## Antes de criar recursos
Use projeto exclusivo de treinamento com autorização e faturamento conscientemente configurado. Defina região, prazo e orçamento. Não exporte chave JSON por conveniência. Prefira identidade do ambiente ou federação suportada. Um alerta de custo não impede toda cobrança; limite instâncias, concorrência e volume do experimento.

## Missão de leitura
Selecione o projeto correto no console. Inspecione IAM e identifique principal, papel e recurso, sem mudar permissões. No Cloud Logging, encontre o tipo de recurso e severidade de um serviço de demonstração. No Monitoring, compare erro e latência na mesma janela. Critério: explicar o que uma permissão permite e em qual escopo.

## Missão de eventos
1. Crie tópico e assinatura Pub/Sub somente do exercício.
2. Defina envelope com event_id, occurred_at, resource_id e schema_version. Publique três mensagens fictícias, uma repetida logicamente e uma inválida.
3. Execute consumidor limitado que valida antes do efeito e confirma depois do resultado durável. Preserve ID lógico no replay.
4. Observe número de mensagens, ack e reentregas. Não assuma exactly-once sem verificar modo, região e condições documentadas.

## Missão Cloud Run
Prepare um serviço mínimo com endpoint autenticado, timeout curto, máximo de instâncias pequeno e identidade que só alcance o recurso necessário. Se integrar Pub/Sub push, configure identidade invocadora e a validação compatível com esse mecanismo. O código de teste local não implementa autenticação GCP; adaptar isso é parte explícita do laboratório real, nunca esconder a ausência.

## Cloud Storage
Armazene um arquivo sintético em bucket privado de estudo. Compare objeto/key com S3 e registre diferenças de evento, versão e IAM. Restrinja a identidade do consumidor ao bucket ou prefixo/condição apropriados conforme os recursos disponíveis. Não use nomes de projetos ou dados corporativos nas suas evidências pessoais.

## Verificar e limpar
Confirme processamento único do efeito, invalid separado e log com correlation_id. Simule falha de aplicação por entrada inválida, sem derrubar infraestrutura. Registre comportamento de retry, remova gatilhos e consumidores do exercício, confira mensagens pendentes e remova apenas os recursos verificados. Examine faturamento depois, respeitando a latência dos dados de custo.

# Docker e Kubernetes · extensão

## Objetivo
Aprender leitura de estado, não implantar um cluster corporativo. Você precisa de Docker/cluster local previamente configurado e confiável. Instalação de hypervisor, WSL ou Docker Desktop pode alterar o sistema e exigir termos; este curso não faz isso automaticamente. Se não tiver ambiente pronto, conclua o diagnóstico conceitual e marque a parte real pendente.

## Antes de qualquer kubectl
Liste o contexto atual e confirme que é o cluster local de estudo. Crie um namespace exclusivo com quota e limites. Use imagens de origem oficial, versão fixa e atualizada. Não monte o filesystem do host, socket Docker, credenciais ou diretórios corporativos no container de exercício. Não exponha portas em 0.0.0.0.

## Exercício de diagnóstico
Suba um serviço demonstrativo pequeno usando um tutorial oficial da sua versão. Observe pods, deployment e service. Compare readiness e liveness. Altere uma configuração em sandbox para produzir um erro de aplicação recuperável. Leia describe, eventos e logs; registre código de saída e relação com mudança. Restaure a configuração e valide rollout com prazo.

## Critério de aprovação
Você explica por que o pod não está pronto, qual evidência sustenta a hipótese e como recuperou sem apagar o namespace todo. Demonstre uma configuração de requests/limits, uma probe apropriada e um comando de leitura que seleciona namespace explicitamente. Não aumente réplicas antes de verificar limite da dependência.

## Limites e encerramento
Use prazo de 60 minutos e poucas réplicas. Limpeza atua só nos objetos do exercício após conferir contexto/namespace. Esse roteiro não foi executado como parte da validação do app. O HTTP lab real funciona sem containers e já permite estudar processo saudável versus função falhando.

# Runbooks e comunicação

## Modelo de runbook
Título e versão. Serviço/owner. Sintoma e impacto. Quando usar e quando não usar. Pré-condições: alvo, identidade, janela, backup e aprovação. Observações de leitura com janela/unidades. Hipóteses e como refutar. Ação mínima permitida. Resultado esperado. Validação funcional. Condição de parada. Retorno possível e seus limites. Escalonamento e evidência sanitizada.

## Exemplo de atualização de incidente
Desde 09:05, consultas do serviço fictício quotes apresentam 22% de falhas. A equipe identificou espera por conexão após uma alteração de configuração; a relação causal ainda está sendo confirmada. O rollback de um canário está em avaliação. Próxima atualização em 10 minutos. Sem evidência de perda de dados no exercício.

## Modelo de postmortem
Resumo. Janela e impacto. Como detectamos. Linha do tempo com fuso. Fatores contribuintes. Mitigação e como foi validada. O que ajudou. O que atrasou. Ações específicas com owner, prazo e indicador de conclusão. Questões ainda abertas. Fontes de evidência seguras.

## Modelo de decisão técnica
Problema e restrições. Opção escolhida. Alternativa viável. Consequências em operação, segurança, custo e manutenção. O que foi testado e o que não foi. Condição que faria revisar a escolha. Plano de retorno. Evite justificar escolha apenas pela popularidade de uma ferramenta.

## Checklist da automação
Entrada validada; alvo limitado; identidade mínima; autorização atual; deduplicação atômica; timeout; tentativas limitadas; backoff; cooldown; logs sem segredo; pré-condição; pós-condição; falha parcial; rollback; kill switch; owner e documentação. Cada item precisa de evidência quando for usado em um sistema real, não de uma caixa marcada sem teste.

## Fontes e priorização
A trilha reúne fundamentos de operação, Ansible/AAP, Python, Git, Linux/Windows, observabilidade, IA, APIs e documentação. Dynatrace, AWS e GCP aparecem como ferramentas de estudo; os conceitos devem ser transferidos para outras plataformas. As fontes oficiais estão disponíveis em cada aula. A trilha não representa uma vaga, empresa, certificação ou arquitetura específica.

## Complementos depois do essencial
Power Platform: faça um fluxo de aprovação com dados fictícios, entenda ambiente, conector, credencial e política de dados. Power BI: calcule indicadores com denominador e janela consistentes. SharePoint: pratique versionamento de documentação e controle de acesso. Certificações são opcionais; verifique catálogo e requisitos atuais, pois o HTML antigo não garante nomes ou disponibilidade de exames.

# Glossário de campo

## Leia o sintoma com precisão
Latência é tempo de resposta; throughput é quantidade por unidade de tempo. Erro é um resultado que viola o contrato. Saturação é a aproximação de um limite: CPU, memória, conexões ou fila. Percentil 95 indica que 95% das observações ficaram até aquele valor; não descreve os 5% restantes. Sempre registre janela, unidade, população e origem do dado.

## Diferencie os sinais
Métrica é uma medida numérica agregável. Log é um registro de evento. Trace acompanha uma operação distribuída; cada trecho é um span. Um trace ID permite correlacionar sinais. Alta cardinalidade significa muitos valores distintos de uma dimensão, como milhões de IDs de usuário: isso pode aumentar custo e dificultar a análise. Evite colocar dados pessoais em rótulos e exemplos.

## Entenda o compromisso operacional
SLI é o indicador observado; SLO é a meta para uma janela; SLA é um acordo com consequências contratuais. Error budget é a tolerância de falha derivada da meta. Para SLO de 99,9% em um milhão de requisições, o orçamento é mil requisições ruins. Burn rate compara a fração de erro observada com a fração permitida, usando o mesmo denominador. Um pico curto e uma degradação longa pedem janelas diferentes de investigação.

## Automatize de forma repetível
Idempotência significa que repetir a mesma intenção não produz novas mudanças após atingir o estado desejado. Retry é nova tentativa; backoff aumenta a espera; jitter distribui as tentativas. Deduplicação impede repetir um efeito para a mesma chave de evento. Timeout limita espera. Cooldown limita frequência de ações. Um circuit breaker interrompe temporariamente chamadas que estão falhando. Nenhum desses mecanismos substitui autorização.

## Reconheça os objetos de nuvem
Bucket armazena objetos; não se comporta como um disco compartilhado POSIX. Lambda executa uma função sob um contrato de evento. OpenSearch indexa documentos para busca e agregação. Pub/Sub separa publicação e consumo de mensagens. Cloud Run executa serviços ou jobs em contêineres. IAM determina qual identidade pode realizar qual ação em qual recurso; a existência de uma credencial não implica permissão universal.

## Separe evidência de hipótese em IA
Anomalia é desvio de um padrão; não prova incidente. Correlação não prova causalidade. Precisão mede quantos alertas positivos eram corretos; recall mede quantos casos relevantes foram encontrados. RAG recupera referências antes de gerar uma resposta. Grounding vincula afirmações a essas referências, mas não elimina erro. Avaliação usa casos com resultado esperado e critérios repetíveis. Prompt injection é conteúdo não confiável tentando mudar as instruções de um agente: referências e logs devem permanecer dados.

## Exercício de recuperação
Sem consultar, explique idempotência com um serviço parado e outro já iniciado. Depois explique por que um evento duplicado pode cobrar duas vezes mesmo quando o transporte está funcionando conforme o contrato. Finalmente escreva uma hipótese sobre latência e indique qual métrica, log e trace poderiam refutá-la. Compare sua resposta com os manuais de Ansible, AWS e observabilidade; registre a lacuna, não apenas a definição memorizada.

# Capacidade e FinOps

## Capacidade é um orçamento de recursos
Observe tráfego, filas, latência e saturação juntos. Uma instância pode estar com CPU baixa e ter esgotado as conexões do banco. O limite medido deve vir de um teste representativo, com latência e erro aceitáveis. Não extrapole indefinidamente uma medição pequena nem presuma que dobrar réplicas dobra capacidade: uma dependência compartilhada pode virar o gargalo.

Para este exercício, o serviço é horizontalmente escalável e cada réplica suporta 500 requisições por segundo no limite medido. A política didática permite operar até 60% desse limite e manter uma réplica extra. Esses valores são hipóteses de estudo, não uma recomendação universal de dimensionamento.

## Laboratório Python: número de réplicas
Implemente replicas(demand, capacity, utilization, spare). Use arredondamento para cima: ceil(demand / (capacity * utilization)) + spare. Demand é não negativa, capacity positiva, utilization está entre zero exclusivo e um inclusive, spare é inteiro não negativo. Entradas fora desses limites devem gerar ValueError.

```python
replicas(2400, 500, 0.60, 1)
# Esperado: 9 (8 para a demanda + 1 reserva)
```

Execute python check.py capacity na pasta aiops_extensions. Variação: demande 2401 rps; agora são 10 réplicas. Explique a descontinuidade do arredondamento e o efeito de trabalhar tão perto de um degrau de capacidade. Esse cálculo não provisiona nada e não mede um serviço real.

## Custo por unidade útil
Suponha custo fictício de 0,10 unidade monetária por réplica-hora. Nove réplicas por 720 horas custam 648 unidades. Com 1,2 milhão de operações bem-sucedidas no mês, isso equivale a 0,54 por mil operações bem-sucedidas. Esses números não são preços de AWS ou GCP; desconsideram rede, armazenamento, impostos e custos compartilhados.

Escolha o denominador que represente valor. Custo por tentativa pode parecer bom enquanto o número de falhas cresce. Compare custo por operação bem-sucedida, janela e escopo consistentes. Reduzir capacidade e violar o SLO pode deslocar custo para suporte e perda de serviço.

## Evidência e limite
Entregue a fórmula, dois cenários de demanda, política de reserva e custo unitário com exclusões explícitas. Proponha o próximo teste para validar a hipótese de escala linear. Compare previsão com observado periodicamente; uma estimativa não deve executar expansão automática sem quotas, autorização e verificação funcional.

# Correlação de eventos e redução de ruído

## Da tempestade de alertas à investigação
Dez notificações não significam dez incidentes. Deduplicação elimina a repetição de uma identidade de evento. Agrupamento reúne eventos relacionados para apresentação. Inibição evita notificar um sintoma quando uma condição mais abrangente já explica o contexto. Silenciamento tem escopo e prazo explícitos. Essas operações reduzem notificações; não devem apagar a evidência original.

Comece com uma chave que respeite fronteiras: ambiente, serviço e janela temporal. Acrescentar região pode separar falhas independentes. Retirar ambiente pode juntar homologação e produção. Topologia ajuda a formular relações, mas uma dependência compartilhada não prova que ela causou todos os erros. Compare horários, mudanças e traces antes de concluir causa raiz.

## Laboratório Python: agrupar eventos
Baixe o kit e abra aiops_extensions/exercise.py. Implemente correlate(events). Cada evento tem id, env, service e minute, um minuto inteiro não negativo desde o início do exercício. Eventos repetidos com a mesma dupla (env, id) são uma entrega duplicada: mantenha o primeiro. Agrupe os restantes pela tupla (env, service, minute // 5). Retorne um dicionário com contagens. Essas janelas fixas são uma simplificação; 4 e 5 pertencem a grupos diferentes mesmo estando próximos.

```python
events = [
    {'id':'a','env':'prod','service':'api','minute':1},
    {'id':'a','env':'prod','service':'api','minute':2},
    {'id':'b','env':'prod','service':'api','minute':4},
    {'id':'a','env':'test','service':'api','minute':1},
]
# Esperado: {('prod','api',0):2, ('test','api',0):1}
```

Execute python check.py correlation dentro da pasta. Depois crie um evento no minuto 5 e explique por que abre outro grupo. Troque service para worker sem alterar ambiente: continua um grupo diferente. O teste não usa Alertmanager real nem reproduz toda a sua política de roteamento.

## Evidência e critério
Registre quatro entradas, uma duplicata removida e dois grupos resultantes. Mostre um contraexemplo em que sua chave agrupa coisas demais. Reduzir quatro notificações para duas não prova melhor detecção: compare falsos agrupamentos, incidentes perdidos, tempo até diagnóstico e capacidade de abrir os eventos originais.

## Desafio de profundidade
Desenhe api → pool → banco e proponha como um alerta no banco poderia inibir sintomas da API com prazo e escopo. Defina quando desfazer a inibição. Nenhuma regra deve cruzar ambiente apenas porque os nomes dos serviços são iguais. Faça um runbook para quando a topologia estiver desatualizada.

# GitHub Actions: lendo e construindo pipelines

## De um evento a uma execução
GitHub Actions executa workflows em resposta a eventos. Um workflow contém jobs; um job roda em um runner e contém steps. Steps podem executar comandos ou usar actions. Jobs podem ter dependências explícitas; não suponha que a ordem no arquivo YAML impõe a ordem entre jobs. Revisão documental: 07/09/2026.

Um runner executa código e precisa de isolamento, limites e identidade apropriados. O notebook pessoal não deve virar runner permanente de contribuições públicas. A Academy não oferece runners aos alunos e este módulo não dispara execução no GitHub.

## Leia um pipeline antes de copiar
Observe gatilhos, permissões, ambiente, timeout, código executado e condições de falha. Pergunte se um pull request externo consegue alcançar credenciais. Inputs, nomes de branch e títulos de PR são dados não confiáveis: não os transforme diretamente em comandos.

Dependências e actions precisam de revisão e versões rastreáveis. Segredos devem ter menor privilégio e ficar fora do YAML e logs. Credenciais curtas por federação podem ser apropriadas para uma futura integração cloud, com relação de confiança restrita. Não há credencial cloud neste lab.

## Prática local no kit
Baixe o kit e abra delivery. O arquivo ci-example.yml é um workflow didático inativo: está no kit, não na pasta ativa .github/workflows do seu projeto. Ele descreve execução manual, permissão de leitura, limite de cinco minutos e testes de uma política sintética.

Leia cada seção. Identifique onde o código é obtido, qual diretório é testado e o que faz o job falhar. Não é necessário publicar o arquivo para praticar a lógica: execute na pasta delivery:
```text
python check.py --solution
```

Depois implemente exercise.py e execute python check.py. O teste local verifica uma política de promoção; não emula o runner inteiro nem comprova execução hospedada.

## Exercício de investigação
Considere três resultados: dependência não encontrada; teste falhou; credencial sem permissão. Para cada um, escreva a primeira evidência a consultar e quando repetir. Um retry não corrige teste determinístico errado. Um teste quebrado não deve ser ocultado com continue-on-error para permitir uma entrega.

Cache acelera trabalho repetível, enquanto artefato é um resultado que você quer transportar ou examinar. Não trate cache como a única cópia de uma entrega. Defina retenção, origem e conteúdo permitido; não arquive o diretório inteiro com arquivos de ambiente.

## Solução comentada
Workflow descreve o processo; job delimita ambiente de execução; step produz uma operação observável. A dependência entre testar e promover deve ser explícita. Um job de testes não precisa escrever no repositório para rodar checks locais. Falha deve produzir diagnóstico suficiente sem despejar segredos.

Na fixture, todos os testes da referência devem passar. A implementação incompleta do aluno deve falhar: isso indica trabalho a fazer, não que o curso está quebrado. Nenhum resultado deste exercício deve ser chamado de CI do GitHub executada até existir uma execução remota verificável.

## Critério de conclusão
Desenhe evento → job → steps, explique duas permissões desnecessárias e descreva como distinguir falha de infraestrutura de falha no código. Compare uma execução local com uma execução hospedada, indicando o que não foi validado. Aulas posteriores conectarão essa base a build, entrega e operação.

# CI/CD: do teste à entrega e ao rollback

## O que precisa acontecer entre editar e operar
Integração contínua verifica alterações frequentemente e oferece feedback sobre compatibilidade e testes. Entrega contínua mantém uma mudança pronta para ser implantada conforme a política. Implantação contínua automatiza essa passagem quando os critérios são satisfeitos. Uma organização pode escolher aprovação humana para etapas de maior impacto.

O pipeline didático será: mudança → revisão → testes → build → artefato identificado → ambiente de teste → aprovação → implantação → verificação operacional. Se o código muda depois dos testes, o resultado anterior não comprova a nova versão. Revisão documental: 07/09/2026.

## Artefato e ambiente
Um artefato deve ter origem, versão e integridade verificáveis. Usar o mesmo artefato validado na promoção reduz diferenças entre ambientes. Hash ajuda a comparar bytes com uma referência confiável; sozinho não autentica o publicador.

Configuração e segredos variam por ambiente e exigem controle próprio. Dados de produção não são fixture de laboratório. Mudanças de banco podem impedir retorno simples à versão anterior; planeje compatibilidade, recuperação e verificação antes de executar.

## Laboratório Python: decidir promoção
Na pasta delivery do kit, implemente decide(checks, approval, same_artifact) em exercise.py. Essa função é uma política didática, sem deploy ou acesso de rede.

checks deve conter exatamente unit, integration e security; valores permitidos: passed, failed ou missing. approval aceita approved, denied ou pending. same_artifact deve ser booleano.

A ordem da regra importa: qualquer check que não seja passed retorna block. Se os checks passaram, mas same_artifact é false, retorna block. Com evidência válida, aprovação denied retorna block e pending retorna hold. Somente approved retorna promote. Entrada fora do contrato deve lançar ValueError.
```python
checks = {"unit":"passed","integration":"passed","security":"passed"}
# decide(checks, "pending", True) -> "hold"
# decide(checks, "approved", True) -> "promote"
# decide(checks, "approved", False) -> "block"
```

Execute python check.py para conferir sua resposta, ou python check.py --solution para a referência. O teste inclui falhas, evidência ausente, recusa e troca de artefato. Esses estados são sintéticos: a função não verifica assinatura real nem autentica um aprovador.

## Variação de incidente
A implantação passou, mas os erros aumentam de 0,1% para 2% em uma janela comparável e o canário apresenta latência pior. Descreva observações, critério de interrupção, retorno e pós-condição. Não use pipeline verde como prova de saúde. Consulte o aprofundamento Resiliência e canário para comparar amostras e limites.

Rollback é voltar uma mudança quando existe caminho compatível. Roll forward é corrigir com outra mudança. Backup só ajuda quando há procedimento de restore testado. A escolha depende do estado dos dados e do impacto; reiniciar tudo sem evidência não é estratégia de recuperação.

## Solução e critério de conclusão
A solução exige contrato completo, falha segura e prioridade das verificações antes da aprovação. Um campo missing não significa sucesso. Um booleano textual como "true" não atende o contrato de same_artifact.

Entregue os resultados dos testes e um runbook curto: qual artefato promover, quais evidências consultar, quem autoriza, quando interromper e como validar retorno. Acrescente um indicador técnico e um indicador de impacto no serviço. Este lab exercita política de decisão; a futura implantação real precisa impor essas regras no ambiente autoritativo.

# Git e GitHub: versionamento e colaboração

## Git e GitHub têm papéis diferentes
Git registra versões de arquivos e permite trabalhar com histórico local. GitHub hospeda repositórios e acrescenta colaboração, issues, pull requests e outras funções. Um commit local não publica no GitHub; um arquivo salvo ainda pode não estar em um commit. Revisão documental: 07/09/2026.

Em infraestrutura, versionamos playbooks, configuração declarativa, dashboards e runbooks. O valor está em compreender o que mudou, por quê e como validar. Não coloque segredos, dumps de clientes ou backups pessoais no histórico. Adicionar um arquivo ao .gitignore não remove cópias já registradas.

## Vocabulário do primeiro dia
A árvore de trabalho contém os arquivos editáveis. A área de preparação seleciona mudanças para um commit. O commit registra uma versão com identidade e mensagem. Uma branch permite desenvolver uma linha de alterações; merge integra linhas. O remoto é uma referência a outro repositório, não uma cópia sempre atualizada.

Pull request é uma proposta de integrar alterações. Descreva o problema, a mudança, os testes e os riscos. Um reviewer precisa entender o comportamento sem ler uma conversa privada. Um status verde de CI informa o resultado daqueles checks; não substitui revisão do diff nem garante qualidade operacional.

## Exercício local — somente inspeção
Na pasta de um repositório de estudo, execute os comandos abaixo. Eles leem o estado. Não use saídas contendo dados privados em um portfólio público.
```text
git status --short
git diff
git diff --staged
git branch --show-current
git log -5 --oneline
```

Se o repositório ainda não tem commits, git log pode informar que não existe histórico. Isso é um estado inicial, não corrupção. Explique a diferença entre arquivo não rastreado, alteração não preparada e alteração preparada. Não faça commit ou push em um projeto compartilhado apenas para experimentar.

## Caso de revisão — configuração de timeout
Uma branch propõe trocar timeout de 30 para 300 segundos para reduzir erros visíveis. O incidente também mostra conexões ocupadas por mais tempo. Escreva uma descrição de PR com: sintoma, hipótese, alternativa, teste e retorno. Uma boa revisão pergunta se o aumento piora saturação e exige medir tempo de espera e impacto.

Agora imagine que outra branch alterou a mesma linha. Um conflito exige conciliar a intenção das duas mudanças. Escolher cegamente a versão mais nova pode eliminar uma correção. Resolva em uma cópia de estudo e execute os testes relevantes antes de integrar.

## Recuperação e colaboração
Em um histórico compartilhado, um novo commit que reverte uma mudança mantém rastreabilidade. Reescrever histórico e forçar envio pode afetar o trabalho de outras pessoas. Aprenda a diferença antes de usar essas operações; o exercício essencial não exige force push ou reset destrutivo.

Issue registra uma necessidade ou falha. PR contém uma mudança revisável. Tag identifica uma referência; release reúne notas e artefatos publicados. CODEOWNERS e regras de branch podem orientar revisão, mas precisam ser configurados e dependerão dos recursos disponíveis na conta/repositório.

## Critério de conclusão
Explique onde estão quatro estados: arquivo salvo, preparado, commit local e mudança publicada. Produza um PR fictício e duas observações de revisão técnica. Mostre como descobrir quais arquivos mudaram sem expor seu conteúdo. Na prática opcional no GitHub, use um repositório de laboratório próprio e revise sua visibilidade antes de publicar.

# LLMOps e operação de agentes

## Operar IA exige mais que uma resposta plausível
Uma resposta pode estar correta e chegar tarde demais. Pode citar um documento que não sustenta a conclusão. Pode recomendar uma ação fora da autorização. Avalie dimensões separadas: sucesso da tarefa, sustentação por evidência, latência, custo e efeitos das ferramentas. Mantenha versão do modelo, instruções, ferramentas e conjunto de avaliação junto dos resultados.

Telemetria de IA precisa preservar privacidade. Registre duração, contagens e IDs sintéticos de correlação; não habilite captura irrestrita de prompts, respostas, segredos ou dados de clientes. Convenções semânticas evoluem: confirme os nomes e a estabilidade no projeto OpenTelemetry antes de instrumentar um produto real.

## Laboratório Python: gate de uma versão
Implemente agent_gate(cases). Cada caso tem success, grounded e unauthorized como booleanos, latency_ms não negativo e cost não negativo em unidade monetária fictícia. Retorne decision, success_rate, grounded_rate, p95_ms e total_cost. Use p95 pelo método nearest-rank: posição ceil(0.95*n) na lista ordenada, contando a partir de 1.

A política didática permite promote apenas com: pelo menos 80% de sucesso, 90% de grounding, nenhuma ação não autorizada, p95 até 2000ms e custo total até 0,05. Todos os critérios precisam passar. Caso contrário, retorne block. Conjunto vazio gera ValueError.

```python
cases = [dict(success=True, grounded=True, unauthorized=False,
              latency_ms=800, cost=0.003) for _ in range(10)]
# decision='promote', success_rate=1.0, grounded_rate=1.0,
# p95_ms=800, total_cost=0.03
```

Execute python check.py agents. Mude apenas unauthorized para True em um caso: a versão bloqueia mesmo que todo o resto seja excelente. Mude apenas a latência de um caso para 3000: com dez casos, o p95 pelo método escolhido também bloqueia. Critérios e preços são fictícios; nenhuma API ou agente é chamado.

## Da avaliação ao controle de ferramentas
A autorização pertence ao código que executa a ação, não ao texto gerado. Separe leitura de escrita, limite alvos, número de passos, tentativas e duração. Uma aprovação precisa estar vinculada ao alvo e à ação; conteúdo de logs ou documentos não pode concedê-la. Tool outputs são dados não confiáveis. Uma boa nota em uma avaliação não elimina prompt injection ou abuso de ferramentas.

## Evidência
Entregue baseline aprovada e duas variações bloqueadas. Mostre qual critério falhou em cada uma. Grounded e success são rótulos de referência fornecidos no exercício; no mundo real exigem rubrica e revisão, não devem ser aceitos da autoavaliação do mesmo modelo. Inclua exemplos adversariais sintéticos e um plano de desativação segura do agente.

# MLOps e degradação de modelos

## AIOps e MLOps se encontram na operação
AIOps usa análise e IA para apoiar operações. MLOps trata da entrega e manutenção de sistemas de aprendizado de máquina. Um detector de incidentes precisa de ambos: boas decisões operacionais e um ciclo reproduzível para dados, modelo, avaliação e implantação. Registre versão do conjunto de dados, código, modelo e parâmetros para comparar tentativas.

Mudança na distribuição de entrada é data drift. Mudança na relação entre entrada e resultado é concept drift. Training-serving skew é uma diferença entre preparação dos dados em treinamento e uso. Drift não prova queda de qualidade. Para avaliar desempenho, frequentemente são necessários rótulos que chegam depois. Uma média agregada também pode esconder piora em um segmento pequeno.

## Laboratório Python: triagem de degradação
Implemente model_triage(missing_before, missing_now, accuracy_before, accuracy_now, labelled). Taxas estão entre zero e um; labelled é contagem inteira não negativa. A política didática tem esta ordem:

1. Com menos de 500 exemplos rotulados, retorne insufficient_evidence.
2. Se a proporção de valores ausentes aumentou pelo menos 0,05, retorne inspect_data.
3. Se a acurácia caiu pelo menos 0,05, retorne review_model.
4. Caso contrário, retorne monitor.

```python
model_triage(0.01, 0.12, 0.94, 0.93, 1000)
# 'inspect_data'
model_triage(0.01, 0.01, 0.94, 0.84, 1000)
# 'review_model'
```

Execute python check.py mlops. Depois reduza labelled para 40 e observe insufficient_evidence. A prioridade de investigar dados acima do modelo é uma escolha desta rubrica; não é regra universal. Ainda é possível investigar problemas de coleta com poucos rótulos, mas a função não decide qualidade do modelo nesse caso.

## O que fazer com a hipótese
Para inspect_data, compare schema, tipos, nulos, faixas, versão do pipeline e origem. Para review_model, revise segmentação, distribuição dos erros, comparação com uma baseline simples e impacto no usuário. Não retreine automaticamente com dados possivelmente corrompidos. Uma versão nova precisa de aprovação, critérios de avaliação e possibilidade de retorno.

## Evidência e limites
Entregue três cenários e explique por que a função não deve afirmar causa raiz. Acurácia é inadequada para alguns problemas desbalanceados: acrescente precisão, recall ou custo de erro conforme o caso. Quinhentos exemplos não garantem poder estatístico; o tamanho necessário depende da variabilidade, do efeito e da segmentação. Nenhum modelo é treinado por este exercício.

# Resiliência, game days e canários

## Uma falha planejada precisa de uma pergunta
Um game day ensaia resposta a falhas com cenário, participantes e critérios conhecidos. Um teste de resiliência deve começar com hipótese, estado saudável mensurável, escopo descartável, duração e condição de parada. Exemplos de perguntas: o timeout limita o atraso? O circuit breaker evita fila crescente? O runbook leva à verificação funcional?

Não confunda ensaio controlado com causar indisponibilidade em um ambiente compartilhado. Neste módulo todo o experimento é feito sobre números sintéticos. O laboratório HTTP do kit oferece uma alternativa real em loopback com estado healthy ou degraded e tempo limitado. Não envie tráfego de teste para sistemas externos por inferência.

## Laboratório Python: avaliação de canário
Implemente canary(control_errors, control_total, candidate_errors, candidate_total). Totais são inteiros positivos; erros inteiros entre zero e o total. A rubrica usa uma janela já encerrada e comparável para os dois grupos.

1. Se qualquer grupo tiver menos de 1000 requisições, retorne hold.
2. Calcule a taxa de erro de cada grupo.
3. Se candidate_rate - control_rate for maior que 0,005, retorne rollback.
4. Caso contrário, retorne promote.

```python
canary(1, 1000, 20, 1000)  # 'rollback'
canary(1, 1000, 1, 1000)   # 'promote'
canary(0, 100, 0, 100)     # 'hold'
```

Execute python check.py canary. Mude a candidata para 6 erros em 1000: diferença de 0,005, exatamente o limite didático, deve produzir promote. A função apenas recomenda; não realiza implantação ou rollback. Em uma operação real, critérios de latência, correção, saturação e erro budget também podem bloquear promoção.

## Por que uma comparação pode enganar
Se o controle recebe tráfego fácil e a candidata recebe um segmento mais pesado, a diferença não identifica o efeito da mudança. Compare janelas e populações, considere intervalos de confiança e dados insuficientes. Mil amostras são uma exigência do exercício, não garantia estatística. Um rollback também pode falhar por incompatibilidade de schema ou efeito irreversível já realizado.

## Evidência e revisão do ensaio
Entregue as três decisões, as duas taxas e uma hipótese alternativa. Escreva condição de parada, owner da decisão, forma de comunicar e verificação após retorno. Termine com um postmortem curto: o que foi observado, o que era esperado e uma ação com critério verificável. Incidentes sintéticos bem resolvidos demonstram raciocínio dentro daquele escopo, não imunidade a falhas reais.

# Anomalias e sazonalidade

## O normal depende do contexto
Um pico de tráfego toda segunda-feira pode ser esperado. Comparar esse horário com a madrugada gera alarmes ruins. Separe tendência, sazonalidade, mudanças de configuração e resíduos. Também verifique atrasos de coleta, relógios e unidades. Dados ausentes não significam zero; ausência de telemetria merece tratamento próprio.

A aula de anomalias apresenta uma linha de base simples. Aqui, escolha observações comparáveis: mesmo serviço, janela, horário e condições relevantes. Uma média ajuda a começar, mas é sensível a extremos. Mediana, quantis e medidas robustas podem ser alternativas. Escolha o método conforme o contrato do sinal e avalie em casos históricos, sem misturar futuro no treinamento.

## Laboratório Python: linha de base comparável
Implemente seasonal(values, current). Values contém pelo menos três valores positivos de períodos equivalentes, current é não negativo. Calcule baseline como a média. Deviation_pct é 100 * (current - baseline) / baseline, arredondado em duas casas. Flag é verdadeiro quando o módulo do desvio supera 20%. O limite é didático e estritamente maior, não maior ou igual.

```python
seasonal([100, 105, 95], 130)
# {'baseline':100.0, 'deviation_pct':30.0, 'flag':True}
seasonal([100, 105, 95], 120)
# {'baseline':100.0, 'deviation_pct':20.0, 'flag':False}
```

Execute python check.py seasonal. Insira um valor 900 na série e observe como a média pode esconder ou criar alertas. Não remova o extremo só porque atrapalha: investigue sua origem. O código não ajusta um modelo estatístico nem estima confiança.

## Avaliação temporal
Separe uma janela de desenvolvimento e uma janela posterior de teste. Evite escolher o limite olhando os incidentes que pretende usar para avaliar. Para um conjunto rotulado, conte verdadeiros positivos, falsos positivos e falsos negativos; calcule precisão e recall. Acrescente tempo de antecedência e falsos alertas por dia. Um modelo que alerta sempre pode ter recall alto e ser operacionalmente inútil.

## Evidência e aprofundamento
Entregue os dois resultados, a hipótese que tornou os períodos comparáveis e um caso em que ela deixa de valer. Explique como lidaria com um serviço novo sem histórico. Compare o mesmo volume de alertas antes e depois, preservando a possibilidade de investigar sinais descartados. Desvio estatístico é evidência para investigar, não autorização para remediar.

# Ferramentas de automação e Ops: como escolher

## Comece pelo problema
Uma ferramenta popular pode ser uma escolha ruim para um problema específico. Este mapa organiza capacidades documentadas, não um ranking de participação no mercado. Revisão documental: 07/09/2026. As versões dos futuros labs serão fixadas e medidas antes da distribuição.

Primeiro descreva gatilho, entrada, transformação, decisão, efeito e evidência. Depois anote volume, prazo, identidade, falha esperada e quem mantém a solução. Uma tarefa simples com regra conhecida pode precisar apenas de código pequeno e agendamento. Usar um agente não elimina esses requisitos.

## Integrações e processos
**n8n** conecta etapas e APIs em fluxos visuais. É um bom tema para estudar webhooks, transformação, ramificação e tratamento de falhas. A Community Edition pode ser auto-hospedada, mas tem termos próprios e diferenças de recursos. Não confunda código disponível com licença MIT.

**Power Automate** cobre fluxos de nuvem e desktop. Estude o ambiente Microsoft, conectores, aprovações e RPA. Uma ação disponível no editor pode exigir licença ou permissão que sua conta não possui. Evite construir a trilha essencial sobre um trial temporário.

## Dados e execução de processos
**Apache NiFi** trabalha com fluxos de dados, filas, roteamento e proveniência. Use-o como referência para ingestão, pressão de fila e rastreio de dados. O estado de uma fila não substitui controle transacional no destino.

**Apache Airflow** organiza workflows em lote e suas dependências. Um pipeline diário de consolidação é diferente de movimentar continuamente eventos individuais. Ensine reexecução por intervalo, dependência, atraso e dados atrasados.

**Temporal** permite modelar workflows duráveis em código e recuperar a execução. Isso não torna automaticamente idempotente uma chamada externa: uma Activity pode exigir nova tentativa e o destino ainda precisa controlar efeitos duplicados.

## Operação e infraestrutura
**Ansible / AAP**: estado e configuração de máquinas, inventário, playbooks e operação de automações. AAP é a plataforma empresarial; estudar Ansible local não reproduz todos os recursos de AAP.

**Rundeck**: execução de runbooks, seleção de alvos, permissões e auditoria. Uma tarefa operacional precisa de alvo limitado e condição de parada, mesmo quando tem um botão bonito.

**OpenTofu**: infraestrutura declarativa, planejamento e acompanhamento de recursos. Comparar plano com configuração desejada vem antes de aplicar. Um lab de leitura de plano não exige criar nuvem.

**Argo CD**: reconciliação GitOps para Kubernetes. Reconheça configuração desejada, diferença observada e política de sincronização. Não é um substituto de todo o pipeline de integração contínua.

## Observabilidade como base
OpenTelemetry fornece instrumentação e coleta de sinais. Prometheus e Alertmanager apoiam métricas e notificações; Grafana organiza visualização e investigação. Dynatrace reúne capacidades de observabilidade em uma plataforma comercial. Essas ferramentas dão evidências ao processo automatizado; um gráfico não concede permissão para reiniciar um serviço.

## Exercício de decisão — 25 minutos, sem instalação
1. Uma empresa fictícia recebe CSV diário e precisa reprocessar a data de ontem. Escolha uma categoria, a evidência de conclusão e o comportamento após falha.
2. Outra recebe dados contínuos de fontes diferentes, precisa rotear inválidos e acompanhar cada transformação.
3. Uma equipe precisa aprovar solicitações em seu ambiente Microsoft; outra precisa configurar cem servidores de laboratório.
4. Um processo leva horas, espera um retorno externo e precisa continuar após a queda do executor.
5. Para cada caso, proponha uma alternativa e escreva uma situação em que mudaria de escolha.

## Solução comentada
No caso 1, Airflow é uma opção para dependências por lote, mas um processo pequeno pode usar código simples. No caso 2, NiFi é candidato quando suas capacidades de dataflow são necessárias. No caso 3, Power Automate se encaixa no contexto Microsoft; Ansible na configuração de servidores. No caso 4, Temporal merece avaliação pela execução durável. n8n pode coordenar integrações, respeitando limites e mantendo regras autoritativas em código.

A resposta só é suficiente quando explica a entrega, a repetição e a falha. A mesma marca não é a resposta correta para todos os casos. Registre uma decisão com cinco campos: problema, escolha, alternativa, limite e teste. Compare custo operacional e capacidade da equipe, não apenas preço de licença.

## Próximo passo
Leia os guias específicos de n8n, NiFi e Power Automate nesta biblioteca. Eles oferecem exercícios de desenho com dados fictícios. Instalações reais desses três produtos ainda não fazem parte deste incremento. Os seis aprofundamentos AIOps têm exercícios Python no kit; o app distingue esses tipos de prática.

# n8n: integrar processos com controle

## O papel de uma integração
Um fluxo n8n pode receber uma entrada, transformar dados, consultar uma API e encaminhar trabalho. O fluxo também precisa lidar com duplicação, indisponibilidade e credenciais. A ferramenta integra etapas; código e sistemas de origem continuam responsáveis por autorização e estado autoritativo.

Neste exercício você desenha um fluxo. Não há n8n instalado pela Academy, API externa, credencial ou envio de mensagem. Revisão documental: 07/09/2026. A Community Edition auto-hospedada possui recursos e termos próprios; cloud e recursos empresariais precisam de avaliação separada.

## Vocabulário para começar
Um gatilho inicia uma execução. Nós transformam ou encaminham dados. Credenciais configuram uma identidade, mas a API de destino ainda decide permissões. Um webhook aberto não é evidência de que quem enviou o evento pode autorizar uma ação. Uma execução concluída no orquestrador não prova que o efeito correto aconteceu no sistema de destino.

Separe ambientes e mantenha os segredos fora do workflow exportado. Não cole tokens no corpo de um nó nem em uma captura de tela. Revisar código em um nó continua sendo necessário; arrastar blocos não elimina código executável.

## Cenário: triagem de incidente fictício
Uma API recebe dois avisos do mesmo evento. Você deve abrir uma única proposta de investigação e aguardar revisão antes de qualquer remediação. Dados de entrada:
```json
[
  {"event_id":"e-17","environment":"lab","service":"quotes","severity":"high"},
  {"event_id":"e-17","environment":"lab","service":"quotes","severity":"high"},
  {"event_id":"e-18","environment":"lab","service":"quotes","severity":"unknown"}
]
```

## Prática de desenho — 35 minutos
1. Desenhe: gatilho manual com fixture → validação → API de triagem → revisão humana → consulta do resultado.
2. Defina campos obrigatórios e valores permitidos. severity aceita low, medium ou high. Uma entrada inválida vai para revisão de dados, sem ação operacional.
3. Proponha uma chave de deduplicação que inclua ambiente e identidade do evento. Explique por que verificar existência e gravar em operações separadas cria uma corrida.
4. Defina o comportamento quando a chamada sofre timeout após o destino já registrar a proposta.
5. Defina no máximo duas novas tentativas para falhas transitórias e nenhuma repetição automática para autorização negada. Especifique prazo total e desligamento.
6. Faça uma tabela de evidências com entrada, resultado esperado, identidade usada e estado final.

## Resultado esperado e solução
O primeiro e-17 cria uma proposta; a repetição retorna a mesma proposta, sem novo efeito. e-18 é rejeitado pela validação. Com revisão negada, o estado final é negado e nenhuma remediação acontece. Com timeout, consultar a proposta pela mesma chave evita inventar um sucesso ou gerar outra solicitação.

A unicidade deve ser imposta atomicamente pelo destino. Uma memória temporária do workflow não basta quando há duas execuções concorrentes. A aprovação deve vincular a ação e seus parâmetros; se os parâmetros mudarem depois da aprovação, a autorização anterior não serve para a nova ação.

## Critério de conclusão
Entregue o desenho, os três resultados e dois testes adicionais: credencial sem permissão e retorno indisponível. Uma resposta que só diz usar retry é incompleta. Mostre limite de tentativa, evento auditável e condição de parada. O objetivo é reconhecer a fronteira entre orquestração e regra de negócio.

## Quando virar laboratório instalado
O pacote futuro deverá fixar versão, usar dados fictícios e API local permitida, limitar rede/recursos e trazer exportação sem segredos. Só então será marcado como execução real de n8n. Não importe fluxos de terceiros como se fossem configurações inofensivas.

# Apache NiFi: dados, filas e proveniência

## O que você vai aprender
NiFi organiza movimento e transformação de dados. Processors realizam operações; conexões mantêm filas; FlowFiles representam conteúdo e atributos; proveniência registra eventos sobre o caminho do dado. Em um lab futuro, você acompanhará um registro entre etapas e explicará onde ocorreu a falha.

Revisão documental: 07/09/2026. Este é um exercício de desenho e cálculo com fixtures, não uma instância NiFi em execução. Requisitos de Java, memória, autenticação e versão serão conferidos antes de distribuir o pacote real.

## Fluxo de um dado
Desenhe entrada → leitura de registro → validação → roteamento → destino. Abra uma ramificação de rejeição para registros inválidos. Uma política de retry não deve reenviar dados inválidos para sempre. Defina retenção e acesso tanto para dados válidos quanto para a fila de rejeição.

Back pressure controla a entrada na conexão quando o limite configurado é atingido. Isso não cria capacidade no destino. A fila precisa ser dimensionada junto com throughput, prazo e espaço disponível. Dados sensíveis também podem ficar em filas e registros de proveniência.

## Fixture da ingestão
```text
id,environment,service,value
r1,lab,quotes,18
r2,lab,quotes,21
r2,lab,quotes,21
r3,lab,quotes,invalid
```

Regra de negócio deste exercício: value deve ser número inteiro não negativo; (environment,id) identifica um registro no destino. Deduplicação transacional é responsabilidade do destino. O NiFi deve preservar essa chave e encaminhar os resultados.

## Prática — acompanhe cada registro
1. Escreva quais registros seguem ao destino e qual vai para rejeição. Diferencie registros recebidos de efeitos únicos.
2. Para cada etapa, anote atributo preservado, transformação e evidência necessária para investigar r2.
3. O destino confirma r2 e a conexão cai antes de o produtor receber a confirmação. Descreva o próximo envio e o comportamento idempotente esperado.
4. Considere fila vazia, entrada de 100 registros/s e saída de 60 registros/s por 30 segundos. Calcule o crescimento líquido sem back pressure; o limite didático de 1.000 registros seria alcançado quando?
5. Explique por que aumentar o limite da fila não resolve uma diferença permanente entre entrada e saída.

## Solução e evidência
São quatro registros recebidos: três válidos, incluindo a repetição; um inválido deve ser isolado. Há dois efeitos únicos esperados no destino, r1 e r2. A repetição de r2 após timeout deve confirmar o registro existente. Se o destino não implementa a regra, o fluxo não pode prometer ausência de duplicatas.

No modelo contínuo simplificado, a fila cresce 40 registros/s: 1.200 em 30 segundos. O limite de 1.000 seria alcançado em 25 segundos. Um NiFi real tem escalonamento, unidades de fila e configuração próprios; esse cálculo não é benchmark nem garantia de momento exato do bloqueio.

## Critério de conclusão
Entregue desenho com caminho de rejeição, as contagens, cálculo da fila e narrativa de replay. Inclua uma pergunta operacional: como localizar todas as transformações de r2 sem expor seu conteúdo sensível? A proveniência ajuda investigação; não torna correto o dado por si só.

## Variação
Agora dois ambientes usam r2. Refaça a chave e mostre que um ambiente não elimina o registro do outro. Se o atraso aceitável for menor que o tempo estimado de drenagem, proponha reduzir entrada, recuperar destino ou escalar capacidade com evidência.

# Power Automate: nuvem, desktop e aprovações

## Duas superfícies, problemas diferentes
Fluxos de nuvem podem reagir a eventos, comandos ou horários e integrar serviços por conectores. Fluxos de desktop automatizam tarefas na interface de aplicações. RPA é útil quando uma integração por API não está disponível, mas depende de elementos de tela, sessão e condições da aplicação.

Revisão documental: 07/09/2026. Contas, conectores, execução assistida/não assistida e ambientes possuem requisitos e licenças distintos. Não presuma que todos os recursos são gratuitos por existir Power Automate no Windows. O exercício abaixo não exige conta Microsoft nem trial.

## Antes de automatizar
Identifique o dono do processo, a fonte do dado e a autorização de cada etapa. Um conector usa uma identidade: permissões excessivas podem ampliar o alcance de um erro. Ambientes e políticas de dados ajudam a separar fluxos e controlar combinações de conectores; não substituem autorização na origem.

Se uma API oferece contrato estável e controles adequados, avalie essa integração antes de usar cliques. Quando só há interface, considere janela inesperada, elemento movido, sessão expirada e ação já executada antes de uma falha.

## Caso: solicitação fictícia de material
Uma equipe recebe um formulário com request_id, área e valor em centavos. O fluxo prepara uma solicitação, aguarda aprovação e registra a decisão. Não há pagamento, email enviado nem integração corporativa neste exercício.

```json
{"request_id":"req-42","area":"lab","amount_cents":12500}
```

As transições permitidas são recebida → pendente → aprovada ou recusada. Uma solicitação expirada não pode ser aprovada sem nova revisão. O sistema de registro impõe os estados e o vínculo entre solicitação e decisão.

## Prática — desenhe e teste no papel
1. Escolha cloud flow para o formulário integrado por API. Descreva quando um desktop flow seria necessário.
2. Valide request_id, área e centavos inteiros não negativos antes de registrar.
3. Descreva o que acontece se o gatilho entregar req-42 duas vezes.
4. Defina revisão recusada, expirada e indisponível. Não transforme silêncio em aprovação.
5. Imagine uma janela diferente da esperada no desktop. Defina uma checagem antes do clique e uma parada segura.
6. Registre quais evidências podem ser guardadas sem copiar dados pessoais para o histórico do fluxo.

## Solução comentada
Um gatilho duplicado deve apontar para a mesma solicitação. O sistema autoritativo impõe unicidade e transição válida. Recusa é estado final sem execução; expiração exige revisão renovada. Indisponibilidade exige retomada limitada e visível. O valor deve permanecer 12500 centavos, sem o modelo de IA recalcular ou autorizar despesas.

No desktop, confirmar aplicação e elemento esperado evita alguns erros, mas não todos. Após timeout, consultar o estado do processo é mais seguro do que repetir cegamente um clique que pode ter produzido efeito. API e RPA precisam de verificação da pós-condição.

## Critério de conclusão
Entregue duas opções de solução, o motivo da escolha e resultados de duplicação, recusa, expiração e janela inesperada. Explique qual identidade executa cada ação. Diferencie roteiro didático de validação real em um tenant.

## Caminho para prática real
No futuro lab, o aluno verificará sua modalidade de conta/licença antes de abrir um ambiente de teste. As ações usarão recursos fictícios dedicados e limpeza explícita. Se o requisito não estiver disponível gratuitamente, a Academy manterá o exercício equivalente sem assinatura.