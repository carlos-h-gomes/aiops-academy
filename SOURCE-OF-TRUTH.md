# AIOps Academy — Source of Truth

Status: public local-download beta
Version: 1.2.0-beta.1
Reviewed: 2026-09-07
Owner: local learner / root implementation

## Project identity and release

AIOps Academy 1.2.0-beta.1: aprendizagem prática individual em português, independente de empresa ou processo seletivo. São 30 aulas disponíveis, 11 bancadas, seis configurações de simulado e 25 itens na biblioteca. A beta é publicada em https://github.com/carlos-h-gomes/aiops-academy como código-fonte e pacote portátil para uso local no Windows.

## Architecture profile

Python FastAPI em backend e React/TypeScript/Vite em frontend. As fronteiras estão descritas na documentação técnica. `docs/architecture/DIRECTORY-MAP.md` define responsabilidade. /api/v1 e artifacts/openapi.json (gerado) são o contrato.

## Authoritative source map

Conteúdo: backend/content/course.json e manuals.json, produzidos por scripts/author_course.py e author_manuals.py. Regras: backend/app/services. Dados: data/academy.sqlite3. Operação: launcher.py e `docs/TECHNICAL-DOCUMENTATION.md`. Uso: `docs/USER-MANUAL.md`. Evidência: docs/VALIDATION.md. Design público: docs/architecture/DIRECTORY-MAP.md.

Metadados das unidades/trilhas: backend/content/curriculum.json, gerado por scripts/author_curriculum.py. Contrato validado em backend/app/schemas/curriculum.py e exportado para schemas/curriculum.schema.json. GET /api/v1/curriculum não lê nem modifica progresso.

## Active work and decisions

Generalização iniciada na base local 1.1.0 e incorporada à beta 1.2.0-beta.1. Start_date é criado e persistido no primeiro acesso. Estado existente e backup v1 são preservados. ROADMAP.md descreve propostas futuras; CHANGELOG.md registra entregas.

Beta 1.2.0-beta.1: seis aprofundamentos integrados, sete guias de ferramentas e entrega e biblioteca filtrável; 25 itens no total. Exercícios Python de referência e catálogo validados; ver docs/VALIDATION.md para limites. A [pesquisa](docs/research/AIOPS-ACADEMY-ESTUDO-2026-09-07.md) e a [V1 pública proposta](docs/planning/V1-PROPOSTA.md) continuam sendo planejamento; demais entregas seguem no backlog. [Preparação do GitHub](docs/planning/GITHUB-SETUP.md) preserva o histórico anterior ao primeiro lançamento.

## Risks and unknowns

Incremento local de ritmo: 30 min a 5h/dia; padrão de 1h somente para novos alunos. O calendário distribui as 90h essenciais em 30–180 dias e mantém 30 dias para os ritmos legados 3h/5h. Banco e IDs existentes preservados. Backup v1 é aceito pelo app atualizado; versões anteriores podem rejeitar taxas novas. Agenda semanal ainda pendente. Regras e rollback em docs/TECHNICAL-DOCUMENTATION.md; uso em docs/USER-MANUAL.md.

Catálogo 2026.09.07.1/schema 1.0: quatro páginas independentes, 30 aulas disponíveis de infraestrutura e 20 unidades em preparação nas demais trilhas. Guias existentes podem ser abertos nas quatro páginas. Progresso projetado dos dias legados, sem migração nem conclusão fictícia. Traduções, práticas das novas unidades e versões reais de ferramentas não foram validadas por este incremento. Fontes, notas e backup antigos permanecem separados dos metadados.

Prática SaaS/cloud depende de sandbox externo. Sem autenticação multiusuário. MIT para software e CC BY 4.0 para conteúdo original. A publicação oferece download local; não ativa aplicação hospedada, contas ou serviços cloud. Consulte SECURITY.md e docs/VALIDATION.md.

## Last qualified evidence

Consulte docs/VALIDATION.md para escopo e limites. O candidato 1.2.0-beta.1 passou por preparação em extração nova no mesmo Windows, regressões, auditorias de dependências/segredos/SAST e empacotamento; a release exige workflow hospedado verde e publica revisão e SHA-256 próprios.

## Reconciliation rule

Confronte fontes, testes e conteúdo. Preserve dados de estudo. Alterações incompatíveis em IDs ou backups exigem migração testada.

## Delivery evidence

Validação local e documentação em docs/VALIDATION.md. O pacote pode ser gerado por scripts/package_app.py depois da preparação. Dados pessoais, bancos e memória privada ficam fora da distribuição.


## Local maintenance authority

No workspace de manutenção, `docs/ai/architecture-policy.json` registra a política de arquitetura e os gates locais. Essa memória operacional é privada e ignorada pelo Git; a arquitetura necessária para contribuir está descrita integralmente em docs/TECHNICAL-DOCUMENTATION.md e docs/architecture/DIRECTORY-MAP.md.
