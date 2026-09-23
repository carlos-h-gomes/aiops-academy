# AIOps Academy — Technical Documentation

Status: local release candidate pending public upload
Version: 1.2.0-beta.2
Reviewed: 2026-09-23
Owner: local learner / root implementation

## Purpose, scope, and users

App individual para estudo intensivo local. As bancadas não executam código enviado pelo navegador nem acessam sistemas da empresa. Fontes e currículo em português são originais, com referências oficiais.

## Architecture and runtime boundaries

Frontend build estático e backend HTTP na mesma origem 127.0.0.1:8765. Python serve apenas assets construídos e endpoints permitidos. Controller → service → repository/model. Composição em main.py/App.tsx. Não há imports de fonte entre frontend/backend.

## Module and directory responsibilities

backend/app/controllers: HTTP e arquivos estáticos permitidos. services: correção, progresso e políticas. repositories: transações SQLite. models: catálogo e fixtures. schemas: validação v1. frontend/src/api: fetch com timeout; context/hooks: estado e navegação; services: seleção de percurso; pages/components: UI; utils: funções puras. backend/content: dados do curso; labs/real: exercícios separados; scripts: preparação e validação; artifacts: kit e evidências.

## API contracts and integrations

/api/v1/course, progress, notes, quiz, complete, labs, exams, reviews, settings, backup, restore, portfolio, manuals e kit. OpenAPI em artifacts/openapi.json (gerado localmente) após build. Escritas JSON exigem X-Academy-Client:local e origem local compatível. Sem integrações externas de runtime; links oficiais abrem no navegador.

## Data ownership, schemas, and migrations

SQLite state(key,value JSON), transações BEGIN IMMEDIATE. Progress tem settings, notes, completed, quizzes, labs, reviews. Backup v1 é validado antes da substituição atômica; pre-restore preserva estado anterior. Sessões têm ID aleatório, expiram após 8h, limitam 250 ações e retenção total de 500. Mudança incompatível deve introduzir migração versionada. Não há migração automática silenciosa.

## Authentication, authorization, and security controls

Usuário único local, sem login. Bind loopback, Host/Origin guard, JSON com cabeçalho específico, sem CORS permissivo, CSP, limite 800KB por requisição e concorrência 32. YAML limita tamanho, plays/tasks e tokens; sem anchors, aliases, tags ou comandos arbitrários. DQL/OpenSearch aceitam gramática explícita sobre fixture. Sem eval, shell, SSH ou SDK cloud nas bancadas. Processos locais da mesma conta não são uma fronteira de segurança; não armazenar segredo.

## Configuration and environments

Launcher: --port, --seconds até 28800 e --no-browser. --qa usa artifacts/qa.sqlite3 e habilita somente recursos de teste isolados. ACADEMY_DB é override de teste. Ambiente de subprocessos minimizado. Python 3.14 e Node24 observados. requirements.txt e package-lock.json travam dependências. Sem APIs pagas.

## Local development, build, and tests

preparar.cmd chama scripts/prepare.py: cria .venv, instala requisitos binários e npm ci --ignore-scripts, compila TypeScript/Vite. scripts/bounded.py executa argumentos revisados via safe_exec com timeout e cleanup. Testes Python ficam em backend/tests; os comandos automatizados ficam no workflow `.github/workflows/ci.yml`.

## Deployment, compatibility, migration, and rollback

A beta é distribuída para execução local, não como serviço hospedado. iniciar.cmd abre o navegador; sessão limita-se a 8h. Porta ocupada não é encerrada. Para voltar uma versão, pare o app, exporte/preserve o backup e substitua somente os fontes/build por uma extração limpa da versão anterior; não extraia arquivos sobre `data/`. O pacote portátil não contém dados do aluno. Backups v1 continuam aceitos pela beta; um aplicativo antigo pode rejeitar os ritmos novos.

## Observability, alerts, and incident response

Health v1 identifica produto e versão. Sem telemetria externa, sem access log contendo notas. Exceções de aplicação têm mensagem segura. Não há monitor ou SLA de produção. Falha de banco: preserve rascunho e confira espaço/permissão antes de restaurar. Servidor de QA limitado por tempo.

## Backup, restore, and recovery

Exportar backup pela UI ou GET /api/v1/backup. Restaurar exige confirmação e validação de versão/campos/IDs/tamanhos; pre-restore permite desfazer. Com app parado, copie data/academy.sqlite3. Rascunhos ainda não salvos ficam no navegador e não entram no backup. A restauração não importa sessões temporárias. Validar roundtrip com fixtures antes de mudança de esquema.

## Operations, support, and troubleshooting

Porta padrão8765. Falha por ausência de build: preparar.cmd. Falha de dependência: examinar saída limitada e corrigir instalação sem privilégios globais. Outra aplicação na porta: --port8766. Sem internet: aulas locais funcionam após setup; links oficiais não. Não remova banco para resolver erro sem backup.

## Known limitations and residual risks

Simuladores não são ferramentas completas. SSH, WinRM, AAP, Dynatrace, AWS/GCP, OpenSearch real e Kubernetes têm pré-requisitos externos. Notas livres recebem rubrica humana, não avaliação semântica automática. Checkpoints usam 60 questões situacionais; final seleciona 30. Pistas e soluções disponíveis permitem estudar, portanto notas não certificam competência profissional. Pontuações importadas são confiadas ao backup do próprio usuário.

## Evidence and authoritative references

[Mapa de diretórios](architecture/DIRECTORY-MAP.md) registra decisões. Referências do curso ficam em backend/content/course.json. Dependências são identificadas pelos locks; proveniência e hashes acompanham o inventário local de artefatos, que não integra o pacote público.
## Beta 1.2.0 — biblioteca e autoria

O endpoint /api/v1/manuals serve 25 entradas: 12 essenciais, seis extension e sete tooling. Campos opcionais: summary, category, minutes, recommended_after e sources. Consumidores antigos continuam recebendo id/title/body; IDs da trilha e backup não mudaram. scripts/content_catalog.py valida tipos, identidade única, fontes HTTPS e limites antes de escrever atomicamente manuals.json. author_manuals.py mantém o núcleo e agrega módulos por nome. A biblioteca apresenta categorias, busca e limites de prática; não executa produtos de terceiros.

Os testes frontend/tests/library.test.mjs usam Chrome instalado em contexto isolado, serviço loopback temporário e banco sintético; nenhum perfil pessoal é acessado. Executar a partir de frontend com node tests/library.test.mjs através de scripts/bounded.py. A porta 8876 deve estar livre. Capturas e relatório ficam em artifacts/library, fora do Git. Esse cenário de navegador permanece local e não integra o workflow hospedado básico.

## Beta 1.2.0 — disponibilidade e calendário

`Settings.daily_hours` aceita somente os números 0.5, 0.75, 1, 1.5, 2, 3 e 5. Booleanos, strings e outros valores retornam 422, tanto em PUT /api/v1/settings quanto em POST /api/v1/restore. Data inicial permanece entre 2000-01-01 e 2100-12-31. Novo progresso usa 1h/dia; progresso já persistido não é migrado nem reescrito no primeiro acesso.

O formulário CalendarSettings possui a edição temporária e desabilita campos durante o salvamento. `utils/dates.ts` centraliza a estimativa de apresentação: abaixo de 3h/dia, `ceil(90/h)` dias corridos e início da aula n em `floor((n-1)*3/h)` dias após o início. As taxas legadas 3/5 mantêm 30 dias. Datas são civis locais, construídas ao meio-dia; o total não desconta fins de semana. A estimativa não autoriza conclusão nem modifica as regras de avaliação.

Backup conserva versão 1, IDs e namespaces. Leitor novo aceita arquivos antigos e novos; leitor antigo pode rejeitar taxas expandidas. Para rollback, preservar backup atual e exportar uma cópia com 3h/5h antes de substituir código e build. Não editar o JSON ou banco para forçar compatibilidade. Testes cobrem ida/volta, undo e rejeição sem substituir o estado/ponto de recuperação.

Verificação: testes de API em banco temporário, datas com Node e `frontend/tests/pace.test.mjs` após build. O teste de interface usa porta loopback efêmera identificada pela inicialização do próprio processo, contexto Chrome isolado, data sintética fixa e ambiente minimizado. Encerra o servidor e remove somente sua pasta temporária verificada. Relatório e capturas ficam em `artifacts/pace`, fora do pacote público; os limites aplicáveis permanecem descritos neste documento.

## Beta 1.2.0 — catálogo versionado

GET /api/v1/curriculum é somente leitura, com response_model `Curriculum`. O catálogo tem schema_version 1.0, quatro trilhas e 50 registros: 30 aulas legadas com dia do calendário e 20 aulas guiadas não legadas disponíveis por ID. `GET /api/v1/units/{unit_id}` só aceita IDs publicados e retorna conteúdo limitado; não lê nem escreve progresso. `GET /api/v1/units/{unit_id}/lab` e `POST /api/v1/units/{unit_id}/lab/run` atendem labs fechados das 20 aulas de Dados, Segurança e Agentes, com opções fechadas e avaliação determinística em memória. Não aceitam texto executável, SQL, caminhos, URLs, comandos ou persistência. `metadata_reviewed_on` é revisão dos metadados, não execução recente de cada fonte ou produto. Português disponível aponta para a revisão local; traduções en/es permanecem planejadas.

Autoria em scripts/author_curriculum.py gera backend/content/curriculum.json e schemas/curriculum.schema.json a partir do curso/biblioteca e do plano editorial. Pydantic estrito em backend/app/schemas/curriculum.py valida IDs, tipos, grafo acíclico, ordens, fontes HTTPS e consistência de disponibilidade/tradução. `validate_content_links` confronta título, resumo, objetivos, versão, duração, referências, labs e guias com os fontes reais antes de publicar o catálogo local. Falha de autoria não substitui a saída anterior. Não editar o JSON gerado isoladamente.

Models lê o catálogo até 1 MB e manuais até 2 MB; o serviço expõe o modelo validado. Leitura bem-sucedida é mantida em cache até reinício. Se arquivo estiver ausente/inconsistente, a API retorna erro interno seguro e rotas legadas continuam funcionando. Após regenerar conteúdo, reinicie o aplicativo.

IDs infra-01…infra-30 mapeiam explicitamente dias 1…30; data-01…06, security-01…06 e agents-01…08 preservam o planejamento aprovado. Os 20 IDs não legados estão publicados localmente; os labs fechados expostos ficam em `models/unit_labs.py`, `services/unit_labs.py` e schemas próprios. Renomear ou reutilizar esses IDs exigirá migração própria. Não houve alteração do SQLite, dos critérios de conclusão ou de backup v1. Frontend projeta `completed` pelos dias; não cria outro registro de conclusão. Guias não são aulas-base. Pré-requisitos são informativos.

Frontend usa api/curriculum para transporte, useCurriculum para loading/error/retry, services/curriculum para filtro/projeção e TracksPage/LearningUnitCard para apresentação. Novas rotas #/tracks, #/tracks/id e #/library/id preservam #/trail e #/day/n. URLs da biblioteca são identificadores validados, nunca caminhos de arquivo. Texto é renderizado por React; nenhuma entrada do catálogo concede execução de comandos.

Testes novos: backend/tests/test_curriculum.py, frontend/tests/curriculum.test.mjs e tracks.test.mjs. Este último usa helper support/local-app.mjs, Chrome isolado, porta efêmera e backup sintético. Env mínimo e cleanup ficam limitados ao processo e pasta criados pelo teste. Biblioteca antiga continua coberta por library.test.mjs.

`.gitignore` e package_app.py excluem `/data` do aluno, memória privada `docs/ai`, dependências instaladas, fixtures e validadores de manutenção, além dos dois laboratórios piloto. O pacote beta.2 inclui uma allowlist explícita dos 20 corpos de aulas guiadas em `backend/content/planned-units`; qualquer outro rascunho nessa pasta continua excluído. `frontend/src/data` (tipos de aplicação) continua no pacote. O pacote exige a presença desses tipos e do catálogo/schema; a extração nova verifica quatro trilhas, 50 registros e as rotas de aula guiada. A preparação completa também foi exercitada em uma pasta nova no mesmo Windows, mas isso não equivale à instalação em outro computador. O workflow hospedado cobre preparação, testes de API/progresso, calendário/catálogo, laboratórios de referência e reprodução de conteúdo; os cenários Chrome permanecem locais.

## Piloto local agents-05 — integração didática de 2026-09-15

No workspace de manutenção, a autoria PT-BR em backend/content/planned-units/agents-05.json aponta para o roteiro e a entrada guiada em labs/agents-processes-pilot. learning_session.py apresenta evidências e decisões; DevelopmentTriage mantém a autoridade sobre leitura, diff, aprovação sintética e arquivos temporários. As ações são finitas e a aprovação positiva exige SHA-256 explícito. Nenhum backend/frontend importa ou executa esse código.

O piloto usa a imagem local qualificada por ID e o perfil runtime.env com dez limites não secretos; o Compose padrão abre review. Não há serviço persistente, modelo, nova dependência ou migração. Cada invocação recria o cenário e limpa seus artefatos. A qualificação da imagem permanece separada da validação desta entrada. `agents-05` agora está disponível no catálogo por meio de um lab fechado do aplicativo; o piloto continua opcional, separado do runtime e não é iniciado pelo frontend ou backend. O piloto não foi acrescentado ao pacote distribuído.
