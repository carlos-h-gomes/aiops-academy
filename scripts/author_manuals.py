"""Original operating guides and optional vendor sandbox exercises."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANUALS=[]
def manual(id,title,body):MANUALS.append(dict(id=id,title=title,body=body.strip()))

manual('start','Como estudar aqui',r'''
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
''')

manual('setup','Preparação e recuperação',r'''
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
''')

manual('python','Python real · eventos',r'''
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
''')

manual('ansible','Ansible real · localhost',r'''
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
''')

manual('http','HTTP real · falha controlada',r'''
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
''')

manual('dynatrace','Dynatrace real · roteiro',r'''
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
''')

manual('aws','AWS real · S3 e Lambda',r'''
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
''')

manual('search','OpenSearch real · ingestão',r'''
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
''')

manual('gcp','GCP real · identidade e eventos',r'''
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
''')

manual('kubernetes','Docker e Kubernetes · extensão',r'''
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
''')

manual('templates','Runbooks e comunicação',r'''
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
''')

manual('glossary','Glossário de campo',r'''
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
''')

if __name__=='__main__':
    from content_catalog import write_catalog
    path=ROOT/'backend/content/manuals.json'
    write_catalog(MANUALS, ROOT/'backend/content/modules', path)
    print(f'{len(json.loads(path.read_text(encoding="utf-8")))} original manuals')
