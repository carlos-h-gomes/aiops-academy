# Directory ownership

Status: public local-download beta
Version: 1.2.0-beta.2
Reviewed: 2026-09-06
Owner: local learner / root implementation

## Python boundary

backend/app/controllers/ adapta HTTP. backend/app/services/ possui casos de uso, correção e segurança HTTP. backend/app/models/ contém catálogo/fixtures. backend/app/repositories/ possui SQLite e transações. backend/app/schemas/ define entrada. Controllers não consultam banco diretamente.

## React boundary

frontend/src/api/ transporta HTTP. frontend/src/services/ orquestra apresentação. pages/ compõe jornadas; components/layout e ui reusam visuais; context/ compartilha estado; hooks/ reusa React; utils/ é puro; data/ contém tipos; assets/ contém CSS. Sem fonte Python importada.

## Extensions

backend/content/ é conteúdo versionado lido por models/services; não é executado. labs/real/ é kit separado para execução consciente do aluno, sem endpoint de execução. scripts/ possui utilitários de build/teste. artifacts/ tem pacotes e evidências. data/ é estado local do aluno, excluído do pacote. frontend/tests/ contém harness QA, sem exposição no modo normal.

Catálogo de trilhas: schemas/curriculum valida metadados sem acessar estado; models/curriculum carrega e confere referências; services/curriculum serve o caso de leitura; controllers/api expõe /api/v1/curriculum. scripts/author_curriculum pode importar modelos/schemas para gerar metadados e schema JSON, mas nunca escreve progresso. Frontend mantém tipos em src/data/curriculum.ts, transporte em api/curriculum, filtro/projeção em services/curriculum, estado de leitura em hooks/useCurriculum e composição visual em TracksPage/LearningUnitCard. Não há nova camada de persistência ou execução externa.
