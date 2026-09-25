# AIOps Academy

**Aprenda. Teste. Explique.**

Última beta pública `1.2.0-beta.2`; candidata local `1.2.0-beta.3`, distribuída como código-fonte e pacote portátil para Windows após sua validação de release.

Um ambiente local de aprendizagem prática em infraestrutura, automação, observabilidade e IA. Para quem está começando ou quer consolidar fundamentos com exercícios e evidências — no próprio ritmo, sem depender de uma vaga ou empresa específica.

## Comece aqui

No Windows, com Python 3.12+ e Node LTS 22.12+ ou 24+ instalados:

1. [Baixe a beta para Windows](https://github.com/carlos-h-gomes/aiops-academy/releases/download/v1.2.0-beta.2/aiops-academy-1.2.0-beta.2-windows.zip) e extraia em uma pasta nova.
2. Execute **preparar.cmd** para instalar dependências isoladas, compilar a interface e gerar o kit.
3. Execute **iniciar.cmd**. O navegador abre em http://127.0.0.1:8765.
4. Faça o diagnóstico em **Simulados**, ajuste o calendário em **Preferências** e comece a primeira missão.

Na instalação já preparada, basta abrir iniciar.cmd. A sessão dura até 8 horas; depois, abra novamente. O progresso fica em seu computador. Aulas, simuladores e manuais funcionam sem internet após a preparação; fontes externas e serviços cloud precisam de acesso próprio.

## O que você encontra

| Recurso | Hoje |
| --- | --- |
| Trilhas | 50 aulas disponíveis: 30 de Infraestrutura, 6 de Dados, 6 de Segurança e 8 de Agentes/processos |
| Ritmo | De 30 min a 5h por dia, com calendário ajustável e progresso preservado |
| Bancadas | 11 simuladores com correção, pistas e soluções |
| Avaliações | Banco de 60 questões e seis configurações de simulado |
| Biblioteca | 12 manuais essenciais, 6 aprofundamentos e 7 guias de ferramentas |
| Continuidade | Revisão espaçada, notas, portfólio e backup v2 (compatível com v1) |
| Prática real | Exercícios Python, serviço HTTP e playbook Ansible |

O percurso cobre Linux, Windows, redes, Python, Git, Ansible/AAP, Dynatrace/DQL, OpenTelemetry, SLO, AWS S3/Lambda/OpenSearch, GCP, eventos, anomalias, RAG e resposta a incidentes.

## Um ciclo que gera evidência

**Aprender → praticar → explicar → revisar.**

Cada dia exige checkpoint com pelo menos 80%, laboratório resolvido e uma evidência escrita. Notas livres são autoavaliação; a pontuação não certifica senioridade. As bancadas são simulações explícitas com gramáticas limitadas. Roteiros de nuvem e ferramentas reais são opcionais e não executam recursos externos automaticamente.

Percurso essencial: 117,5 horas para as 50 aulas disponíveis, divisíveis em sessões de 30 min a 5h. Novos alunos começam com 1h/dia; preferências anteriores são mantidas. O calendário acompanha todas as trilhas e não bloqueia o acesso às aulas.

Em **Trilhas de estudo**, escolha Infraestrutura e AIOps, Dados/SQL/RAG, Segurança operacional ou Agentes/processos. As 50 aulas entram no calendário e no progresso local; as 20 aulas guiadas usam labs de decisões fechadas, sem executar SQL, arquivos, comandos, rede ou ferramentas externas do aluno. Guias complementares continuam disponíveis nas quatro trilhas.

## Construído para evoluir

FastAPI + React/TypeScript, API `/api/v1`, persistência SQLite e conteúdo versionado. Sem API de IA obrigatória, conta cloud ou telemetria externa. O suporte validado neste momento é Windows com Python 3.14 e Node 24.

- [Manual do usuário](docs/USER-MANUAL.md)
- [Arquitetura e operação](docs/TECHNICAL-DOCUMENTATION.md)
- [Roadmap incremental](ROADMAP.md)
- [Como contribuir](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Segurança](SECURITY.md)

## Estado do projeto

A última beta pública é `1.2.0-beta.2`; `1.2.0-beta.3` é a candidata local em validação. Código sob [MIT](LICENSE); conteúdo original sob [CC BY 4.0](CONTENT-LICENSE.md). A distribuição é para uso individual no Windows e não hospeda uma aplicação, não cria contas e não sincroniza dados por padrão. A preparação foi repetida em uma extração nova no mesmo computador; ainda não há prova de instalação em um segundo computador. A V1 mais ampla continua em implementação incremental; veja o [roadmap](ROADMAP.md) e as [Releases](https://github.com/carlos-h-gomes/aiops-academy/releases).
