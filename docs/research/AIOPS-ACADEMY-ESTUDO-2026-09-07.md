# AIOps Academy — estudo de carreira, ferramentas e laboratórios

Pesquisa realizada em 7 de setembro de 2026. Estado: proposta para discussão, sem implementação, publicação, contratação ou provisionamento. Este documento não altera o currículo publicado nem declara novas funcionalidades entregues.

## 1. Conclusão e método

A arquitetura educacional recomendada combina conteúdo de todos os níveis disponível gratuitamente na web, exercícios leves executados no navegador e laboratórios completos executados pelo aluno em seu computador. Uma conta de nuvem pessoal seria uma alternativa opcional, não um requisito universal. Contas e sincronização online são uma decisão separada, sujeita a cotas de hospedagem.

O estudo cruzou documentação de fabricantes e projetos, um referencial de responsabilidade profissional e descrições públicas de funções. É uma amostra qualitativa para desenhar a Academy, não um levantamento estatístico do mercado. Não foram medidos salários, demanda, participação de ferramentas ou taxas de contratação. Produtos documentados não foram instalados ou comparados em benchmarks nesta pesquisa.

Os níveis abaixo são uma proposta curricular original. Títulos variam entre empresas: não existe nesta pesquisa evidência de uma régua universal que transforme determinada ferramenta, quantidade de anos ou conclusão de curso em cargo.

## 2. O campo de atuação

AIOps aplica técnicas de IA à operação de TI, incluindo tratamento de telemetria, identificação de eventos relevantes e apoio à investigação e resposta. MLOps trata do ciclo operacional de sistemas de aprendizado de máquina. Há interseção, mas são responsabilidades diferentes. [IBM: AIOps](https://www.ibm.com/think/topics/aiops), [IBM: AIOps e MLOps](https://www.ibm.com/think/topics/aiops-vs-mlops).

Para o currículo, proponho três frentes:

1. **Operar infraestrutura:** sistemas, redes, dados, cloud, automação, disponibilidade e segurança.
2. **Aplicar IA à operação:** correlação, anomalias, previsão, classificação de tickets, recuperação de conhecimento e recomendação de ações.
3. **Operar sistemas de IA:** modelos, inferência, avaliações, desempenho, qualidade, privacidade e custo.

O percurso completo atravessa as seguintes camadas. A ordem é didática; elas se comunicam durante um incidente real.

| Camada | Competência que a Academy deve desenvolver | Evidência prática proposta |
| --- | --- | --- |
| Sistemas e redes | Entender processos, memória, disco, DNS, HTTP e TLS | Localizar a origem de uma falha de acesso |
| Infraestrutura e entrega | Reproduzir configuração, controlar mudanças e reverter | Aplicar uma alteração e demonstrar convergência |
| Dados operacionais | Modelar, consultar, reter e proteger dados | Investigar locks e recuperar um backup |
| Telemetria | Instrumentar e correlacionar métricas, logs e traces | Rastrear uma requisição entre componentes |
| Confiabilidade | Relacionar sintomas ao impacto e aos objetivos do serviço | Definir alerta acionável e verificar recuperação |
| Análise e IA | Comparar regras, estatística e modelos com dados rotulados | Medir falsos positivos e incidentes não detectados |
| Conhecimento e agentes | Recuperar fontes e limitar ações de ferramentas | Responder com evidências e recusar ação não autorizada |
| Operação de IA | Acompanhar qualidade, latência, versões e consumo | Rejeitar uma versão que degrada o resultado |
| Governança e liderança | Priorizar riscos, investimento, manutenção e desenvolvimento de pessoas | Defender um plano de melhoria com critérios mensuráveis |

Segurança, comunicação e custo atravessam todas as camadas.

## 3. O que as fontes de carreira mostram

O SFIA distingue responsabilidade por autonomia, influência e complexidade, além do conhecimento. Uso essa ideia como referência de análise, sem estabelecer equivalência oficial entre seus níveis e os cargos brasileiros. [SFIA 9](https://sfia-online.org/en/sfia-9/responsibilities).

O handbook de SRE do GitLab apresenta evolução de Associate até Staff e considera execução, colaboração e influência, além da técnica. A descrição de gestão de infraestrutura enfatiza desenvolvimento da equipe e coordenação entre áreas. São exemplos de uma organização, não definições universais de AIOps. [Carreira técnica](https://handbook.gitlab.com/job-description-library/engineering/infrastructure/site-reliability-engineer/), [gestão](https://handbook.gitlab.com/job-description-library/engineering/infrastructure/engineering-management/).

Como sinais complementares, uma vaga brasileira de SRE/DevOps sênior da Verity reúne GCP/AWS, Ansible/Terraform, Kubernetes e observabilidade; uma vaga da Cognizant publicada em agosto de 2026 combina operação de Dynatrace, DQL, instrumentação e ajuste de alertas. A disponibilidade das vagas pode mudar. Elas comprovam exemplos de combinações de responsabilidades, não predominância no mercado. [Verity](https://verity.gupy.io/jobs/11711041), [Cognizant](https://careers.cognizant.com/apj-en/jobs/00070050331/dynatrace-observability-engineer-analyst/).

## 4. Matriz de funções e progressão proposta

| Função | Escopo típico a preparar | Entrega esperada na Academy |
| --- | --- | --- |
| Analista júnior | Investigar situações delimitadas com orientação, seguir procedimentos e escalar com evidências | Diagnóstico inicial, alteração simples revisável e relato claro |
| Analista pleno | Resolver problemas recorrentes com autonomia e manter automações e observabilidade de um serviço | Correção reproduzível, teste, reversão e acompanhamento |
| Analista sênior | Conduzir problemas ambíguos entre componentes e prevenir recorrência | Investigação completa e melhoria sustentada da confiabilidade |
| Especialista | Definir soluções e padrões técnicos que atendem múltiplos times | Arquitetura comparada, prova de conceito, avaliação e plano de adoção |
| Coordenador | Organizar pessoas, prioridades, capacidade e compromissos da operação | Plano de equipe, prioridades justificadas e acompanhamento de resultados |

Especialista e coordenador são ramificações. Coordenação não exige saber mais comandos que todos os especialistas. Uma pessoa também pode acumular responsabilidades em equipes menores. Comandar um incidente é um papel circunstancial, não sinônimo automático de cargo de coordenação.

### Percurso A — entrada e operação assistida

Conteúdo proposto: terminal Linux e PowerShell, Git, HTTP/DNS, leitura de logs, Python básico, JSON/YAML, SQL introdutório, permissões, backups e conceitos de métricas/alertas. Ansible entra com inventário e playbook pequeno; IA entra como apoio à explicação e ao exame de hipóteses.

Projeto: uma API deixa de responder. O aluno recebe um roteiro parcial, verifica serviço, rede e logs, registra o impacto e escolhe entre corrigir dentro de seu escopo ou escalar. Critério: distinguir evidência de hipótese e evitar uma alteração sem relação com o problema.

### Percurso B — operação autônoma

Conteúdo proposto: roles e testes de Ansible, containers, instrumentação, consultas de telemetria, SLO, SQL e PostgreSQL operacional, eventos duplicados, retries, filas de falha e fundamentos de AWS/GCP. Estatística aplicada vem antes da detecção de anomalias por ML.

Projeto: corrigir uma falha recorrente e automatizar a resposta com limites. Critério: comprovar resultado, segunda execução segura, falha controlada, recuperação e ausência de perda ou duplicação de dados.

### Percurso C — confiabilidade sistêmica

Conteúdo proposto: Kubernetes, GitOps, capacidade, cardinalidade e custo de telemetria, dependências distribuídas, SLOs entre serviços, anomalias sazonais, recuperação de desastres e avaliação de RAG/agentes.

Projeto: um deploy provoca lentidão, crescimento de fila e alerta excessivo. O aluno deve reduzir o impacto, identificar o mecanismo da falha e propor prevenção. Critério: uma solução que funciona também sob uma variação não vista durante o roteiro.

### Percurso D — especialização técnica

Especializações propostas: observabilidade/AIOps; automação e plataforma; dados e busca; segurança operacional; infraestrutura de IA/LLMOps. Não é necessário dominar todas simultaneamente.

Projeto: comparar duas arquiteturas com o mesmo conjunto de incidentes e orçamento de recursos. Critério: documentar limitações, custo, qualidade dos sinais, segurança, operação e migração. Incluir uma situação em que uma regra simples é melhor que um modelo.

### Percurso E — coordenação e liderança

Conteúdo proposto: priorização, escala de plantão sustentável, comunicação executiva, desenvolvimento de pessoas, orçamento, fornecedores, acompanhamento de incidentes, risco de mudanças e manutenção de conhecimento.

Projeto: exercício de mesa com equipe fictícia, orçamento limitado e incidentes concorrentes. O aluno decide prioridades, delega, comunica e prepara um plano de melhoria de 90 dias. A rubrica avalia justificativa e consequências; não há uma resposta única baseada só em menor custo.

Conclusão de trilha demonstra atividades realizadas e competências praticadas. Não certifica senioridade, capacidade de liderar pessoas ou experiência em produção. Casos de liderança precisam de revisão humana para avaliar nuances.

## 5. Ferramentas pesquisadas e seu lugar no currículo

Os itens são candidatos de ensino. A inclusão abaixo não aprova redistribuição, compatibilidade entre versões ou gratuidade de serviços hospedados. O catálogo final terá versão testada, licença, requisitos, custo de execução, alternativa e situação de manutenção.

| Área | Ferramentas propostas | Uso didático e prioridade |
| --- | --- | --- |
| Base operacional | Bash, PowerShell, Git, Python, curl, jq e SQL | Núcleo: reproduzir e explicar investigações pequenas |
| Automação | Ansible; Molecule; Event-Driven Ansible | Núcleo de Ansible, testes e eventos em aprofundamento. [Molecule](https://docs.ansible.com/projects/molecule/), [rulebooks](https://docs.ansible.com/projects/rulebook/en/latest/introduction.html) |
| Infraestrutura como código | OpenTofu; comparação com Terraform | Planejamento, estado, alterações e recuperação. [OpenTofu](https://opentofu.org/docs/v1.7/intro/) |
| Ambientes locais | Docker Compose; kind; VirtualBox | Três formatos conforme o objetivo do lab. [Compose](https://docs.docker.com/compose/intro/compose-application-model/), [kind](https://kind.sigs.k8s.io/) |
| Entrega em Kubernetes | kubectl, Helm e Argo CD | Ramificação de plataforma; comparar estado desejado e observado. [Argo CD](https://argo-cd.readthedocs.io/en/stable/) |
| Coleta de telemetria | OpenTelemetry Collector | Núcleo comum para receber, processar e exportar sinais. Componentes têm maturidades diferentes. [Collector](https://opentelemetry.io/docs/collector/) |
| Métricas, logs e traces | Prometheus, Alertmanager, Grafana, Loki, Tempo; Jaeger como alternativa | Começar com poucos componentes e acrescentar os demais por exercício. [Integrações de Tempo](https://grafana.com/docs/tempo/latest/), [demo oficial](https://opentelemetry.io/docs/demo/) |
| Bancos e busca | PostgreSQL, pgvector e OpenSearch | SQL, operação, similaridade e comparação de recuperação. [pgvector](https://github.com/pgvector/pgvector), [OpenSearch](https://docs.opensearch.org/latest/vector-search/) |
| Eventos e integrações | Kafka no cenário distribuído; APIs e webhooks em exemplos menores | Ensinar atraso, reprocessamento e duplicidade. Não exigir Kafka no perfil inicial. [Modos da demo](https://opentelemetry.io/docs/demo/docker-deployment/) |
| AWS local | AWS SAM CLI | Executar funções Lambda localmente com eventos controlados. Não comprova IAM ou toda a infraestrutura AWS. [SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli-local-invoke.html) |
| GCP local | Emulador Pub/Sub | Publicar e consumir mensagens; IAM não é suportado pelo emulador. [Google Cloud](https://docs.cloud.google.com/pubsub/docs/emulator?hl=en) |
| Análise e anomalias | Python e scikit-learn | Comparar baseline estatístico e Isolation Forest, com separação temporal de treino e avaliação. [Detecção de outliers](https://scikit-learn.org/stable/modules/outlier_detection.html) |
| Testes de desempenho e falha | k6 e Toxiproxy | Requisições limitadas e degradação de conexões no ambiente do lab. [k6](https://grafana.com/docs/k6/latest/get-started/), [Toxiproxy](https://github.com/shopify/toxiproxy) |
| Segurança de artefatos | Trivy | Investigar vulnerabilidades, segredos fictícios e configuração; examinar limites do scanner. [Trivy](https://trivy.dev/docs/latest/scanner/misconfiguration/) |
| Operação e qualidade de IA | MLflow, Langfuse e Promptfoo | Alternativas por exercício para experimentos, traces e avaliações. Não instalar todas no primeiro lab. [MLflow](https://www.mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/traces/), [Langfuse](https://langfuse.com/self-hosting), [Promptfoo](https://www.promptfoo.dev/docs/intro/) |
| Custo de infraestrutura | OpenCost | Entender alocação e consumo em Kubernetes; usar preços didáticos identificados quando não houver fatura real. [Especificação](https://opencost.io/docs/specification/) |
| Plataformas empresariais | Dynatrace como aprofundamento principal; Datadog como comparação citada nas vagas | Conceitos, consultas e roteiros com acesso próprio. Não apresentar produto comercial como incluído na Academy. [Exemplo de função Dynatrace](https://careers.cognizant.com/apj-en/jobs/00070050331/dynatrace-observability-engineer-analyst/) |

A proposta para o primeiro laboratório integrado é uma API pequena, PostgreSQL, OpenTelemetry Collector, Prometheus/Grafana e um gerador de carga limitado. Acrescentar busca, filas, agentes ou Kubernetes apenas quando o exercício exigir. A escolha final precisa de medição de recursos e revisão das licenças das versões selecionadas.

## 6. Módulo de modelos, assistentes e agentes

Antes de comparar produtos, ensinar as diferenças entre modelo, aplicativo assistente, agente com ferramentas, runtime de inferência e protocolo de integração. Eles ocupam camadas distintas.

| Opção | Papel e exercício proposto | Condição de acesso |
| --- | --- | --- |
| Codex | Trabalhar sobre um repositório de lab: explicar, propor correção, testar e revisar o diff | Acesso conforme conta/plano vigente; não obrigatório. [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) |
| Claude Cowork | Sintetizar evidências e preparar documentação operacional a partir de arquivos sintéticos | Produto distinto de um modelo; disponibilidade depende do plano/superfície. [Cowork](https://claude.com/product/cowork) |
| Gemini CLI | Investigar o mesmo repositório com outro agente e comparar evidências, permissões e resultado | Há modalidades gratuitas com cotas e modalidades pagas. [Cotas oficiais](https://geminicli.com/docs/resources/quota-and-pricing/) |
| Ollama | Executar um modelo local e observar consumo, latência e qualidade | Escolher explicitamente execução local; o produto também tem funções de cloud. [FAQ](https://docs.ollama.com/faq) |
| llama.cpp | Explorar inferência e quantização em hardware local | Verificar compatibilidade e licença do modelo escolhido. [Projeto](https://github.com/ggml-org/llama.cpp) |
| vLLM | Aprofundamento em serving, concorrência e benchmarks de inferência | Requisitos próprios; candidato a perfil avançado. [CLI e benchmarks](https://docs.vllm.ai/en/stable/cli/index.html) |
| Modelos locais | Comparar um modelo pequeno de geração e um de embeddings; Gemma/EmbeddingGemma são candidatos documentados | Fixar modelo, revisão, licença e requisitos após medição. [Catálogo Gemma](https://ai.google.dev/gemma/docs) |

Ollama não é o modelo; Codex e Cowork não são bancos vetoriais; um conector não é autorização para agir. A aula precisa tornar essas fronteiras visíveis.

Proponho seis exercícios: resumir um incidente sem inventar fatos; corrigir código com testes; recuperar um runbook com citações; reconhecer falta de evidência; resistir a uma instrução maliciosa inserida em documento; comparar qualidade, latência e consumo em um conjunto fixo de casos.

O caminho essencial não dependerá de assinatura ou API paga. Exemplos com respostas previamente registradas precisam ser identificados como demonstração; não serão anunciados como inferência real. Modelos locais também consomem memória, armazenamento, energia e tempo. Uma ferramenta local que chama um provedor remoto continua enviando dados para esse provedor.

Não há nesta pesquisa ranking de melhor modelo. Antes de recomendar uma versão para um lab, usar a mesma tarefa e critérios para medir as alternativas. Avaliações que chamam outro LLM também podem consumir API e não substituem testes determinísticos de autorização e estado.

## 7. Distribuição dos laboratórios

| Formato | Quando faz sentido | Decisão proposta |
| --- | --- | --- |
| Navegador | Leitura, consultas sobre fixtures, interpretação de sinais e decisões de incidentes | Acesso imediato e opção para equipamentos modestos |
| Docker Compose | API, banco, busca e observabilidade com serviços reproduzíveis | Formato principal para os primeiros labs reais |
| Kubernetes local com kind | Deploys, probes, scheduling, configuração e recuperação de workloads | Ramificação posterior; não pré-requisito para começar |
| Máquina virtual OVA/OVF | Serviços de sistema, boot, SSH, firewall e administração de Linux completo | Pacote opcional, com receita reproduzível para construí-lo |
| ISO | Instalação de sistema e recuperação por mídia | Só quando o próprio processo de instalação/recuperação for a aula |
| Nuvem do aluno | Recursos específicos de provedores e comportamento gerenciado | Opcional, com escopo, orçamento e encerramento explícitos |

Compose descreve aplicações com múltiplos serviços; kind oferece clusters locais com nós em containers. VirtualBox importa appliances OVF/OVA. A recomendação de privilegiar Compose e usar OVA para sistemas completos é uma decisão de projeto baseada nessas capacidades. [Compose](https://docs.docker.com/compose/intro/compose-application-model/), [kind](https://kind.sigs.k8s.io/), [importação VirtualBox](https://www.virtualbox.org/browser/vbox/trunk/doc/manual/en_US/man_VBoxManage-import.xml?rev=87075).

Containers não reproduzem todas as características de uma VM ou nuvem gerenciada. Um emulador de API não demonstra conformidade com IAM, cobrança ou disponibilidade real. O aluno deve conseguir consultar exatamente o que cada exercício reproduz.

Como referência concreta de viabilidade, a documentação consultada do OpenTelemetry Demo informa cerca de 6 GB de RAM para a aplicação completa, aproximadamente 3 GB no modo mínimo e 14 GB de disco. São números dessa demo, não requisitos já medidos para a Academy, e não incluem necessariamente toda a necessidade do sistema hospedeiro. [Requisitos e modos](https://opentelemetry.io/docs/demo/docker-deployment/).

Não publicar estimativas próprias como requisitos mínimos até testar os pacotes. Para cada lab, medir memória disponível, espaço após extração, tempo de inicialização, sistemas suportados e arquitetura de CPU. Um pacote x86-64 não deve ser anunciado como validado em ARM apenas porque usa containers.

### Contrato de um pacote pronto

Cada pacote deve conter objetivo, diagrama, versão, requisitos medidos, roteiro, dados sintéticos, falhas com intensidade limitada, verificador, dicas progressivas, solução explicada e procedimento de parada/restauração. Oferecer ações compreensíveis: verificar computador, preparar, iniciar, introduzir falha, conferir, parar e restaurar somente o lab.

Distribuir receitas e configurações pequenas no repositório; imagens e appliances como artefatos separados, após conferir cotas e permissões de redistribuição. Fixar versões e hashes, manter origem verificável e publicar a receita usada no build. Não incluir credenciais, licenças comerciais ou dados reais dentro das imagens.

O Docker Desktop tem condições de uso gratuito e de assinatura conforme o contexto; não anunciar gratuidade empresarial irrestrita. O Extension Pack do VirtualBox possui termos próprios, distintos do pacote base, e não deve ser uma dependência automática dos labs. [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/), [VirtualBox](https://www.virtualbox.org/wiki/Downloads?lang=en).

### Limites operacionais

Por padrão, interfaces acessíveis somente localmente, dados separados dos arquivos pessoais, recursos limitados e nenhum acesso automático à conta cloud do aluno. Labs comuns não precisam montar diretórios pessoais ou o socket de administração de containers. Quando um objetivo exigir privilégios elevados, preferir uma VM dedicada e explicar o requisito.

O site público não deve receber capacidade para executar comandos no computador. Uma primeira integração pode importar um relatório pequeno e sanitizado gerado pelo verificador local. Esse relatório prova participação declarada no exercício, não autoria inviolável: quem controla o computador pode alterá-lo. O projeto não emite certificação profissional.

## 8. Online gratuito e sustentabilidade

Conteúdo avançado também pode ficar online: a divisão deve ser pelo custo da execução, não pelo nível da pessoa. O aluno não precisa alugar um servidor para usar a modalidade local.

Para preservar um caminho sem gasto de infraestrutura, o catálogo estático pode funcionar com progresso no próprio navegador e exportação/importação. Login e sincronização entre dispositivos exigem serviço de dados ou arquitetura equivalente; planos gratuitos têm cotas e podem mudar. O servidor Python atual não roda no GitHub Pages. [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

Uma versão com Supabase ou outro serviço gratuito precisa de limite de retenção, monitoramento de cotas, plano de exportação e funcionamento degradado. Não garantir custo zero para qualquer número de usuários. O plano gratuito consultado do Supabase tem limites e pausa por inatividade. [Plano atual](https://supabase.com/pricing).

Os custos recorrentes a acompanhar incluem hospedagem de artefatos, tráfego de downloads, autenticação/email, banco de progresso, CI e eventual inferência. Não usar CI como hospedagem permanente de laboratórios. O custo de manutenção editorial e suporte também existe, mesmo quando não há fatura de cloud.

## 9. Atualização e qualidade editorial

Cada módulo deve guardar versão do conteúdo, ferramentas testadas, fontes, data de revisão, responsável e relação com traduções. A versão mais nova de uma ferramenta não deve entrar automaticamente em todos os labs: primeiro validar compatibilidade e exercício completo.

Proposta de rotina futura: conferir links e releases semanalmente; gerar uma fila de mudanças relevantes; revisar conteúdo; executar os verificadores; revisar traduções; publicar changelog. Rotinas precisam expor última execução e falhas. Nada foi agendado nesta pesquisa. [Condições dos agendamentos no GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

O levantamento encontrou exemplos de documentação legada em resultados de busca. Por isso, a curadoria deve verificar a versão e o suporte da página antes de recomendar seus comandos. Um link que responde não é prova de conteúdo atual.

Contribuições devem identificar aula, versão, ambiente e problema reproduzível, sem dados corporativos. Separar sugestão de tema, erro técnico, tradução e problema de acessibilidade. Conteúdo enviado por usuários passa por revisão antes da publicação.

## 10. Sugestões de diferenciação e ordem de execução

1. **Um sistema fictício que acompanha a formação:** o mesmo negócio ganha API, banco, fila, telemetria e automação ao longo das trilhas.
2. **Duas passagens pelo mesmo incidente:** primeiro com orientação; depois com uma variação e menos pistas.
3. **Registro de evidências:** hipóteses, consultas, alteração, resultado e prevenção; permitir exportação do portfólio.
4. **Critério de transferência:** resolver uma situação nova, não apenas repetir o roteiro conhecido.
5. **Visibilidade das limitações:** diferenciar leitura, simulação, ferramenta real e prática de provedor.
6. **Ritmo flexível e acessibilidade:** dividir etapas longas, salvar trabalho, oferecer dados de exemplo e conteúdo utilizável sem equipamento potente.
7. **Revisão por pessoas da área:** pilotos com iniciantes e profissionais para encontrar comandos ambíguos, pré-requisitos ocultos e critérios fracos.

Sequência recomendada de implementação futura: estrutura de trilhas/competências; um lab Compose completo e medido; teste com pequeno grupo; pacote VM para fundamentos de sistema; ramificações de Kubernetes e IA; só então ampliar o catálogo sistematicamente. Idiomas, manutenção de versões e acessibilidade devem nascer na estrutura, mesmo que a tradução integral venha por etapas.

Medir sucesso pelo aluno conseguir iniciar o lab, concluir uma investigação sem copiar, repetir a solução em outra situação e explicar os limites. Depoimentos espontâneos podem mostrar impacto; promessas de emprego, senioridade em prazo fixo ou equivalência acadêmica não são critérios de qualidade.

## 11. Estado e pendências após o estudo

Entregue: pesquisa documental, matriz curricular de cinco funções, catálogo de ferramentas candidatas, comparação de formatos de laboratório e proposta de evolução. As recomendações são de planejamento.

Não executado: instalação ou benchmark dos candidatos, criação de Docker/VM/ISO, alteração do app, publicação de repositório, contratação, login, sincronização ou monitoramento agendado.

Pendências para implementação: escolher o primeiro cenário; fixar versões/licenças; medir o pacote; definir suporte de sistemas; revisar o modelo de dados de múltiplas trilhas; testar a migração do progresso existente. As alterações de aprofundamentos iniciadas anteriormente permanecem uma entrega separada e ainda exigem integração e validação.
