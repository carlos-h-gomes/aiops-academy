# Backlog da V1 pública

2026-09-07 · Aprovado; execução incremental iniciada. Referência: [desenho V1](V1-PROPOSTA.md).

Estes itens são locais; não foram publicados como issues ou milestones no GitHub. Nenhum item abaixo está concluído apenas por estar descrito.

| ID | Incremento | Entrega verificável | Depende de |
| --- | --- | --- | --- |
| V1-01 | Reconciliação | Inventariar fontes/artefatos da 1.1 e aprofundamentos incompletos; integrar sem perder dados e obter uma base validada | Aprovação do desenho |
| V1-02 | Conteúdo estruturado | Schema por unidade: IDs estáveis, competências, pré-requisitos, duração, práticas, fontes, versões e traduções; detectar inconsistências | V1-01 |
| V1-03 | Percursos e ritmo | Quatro trilhas, diagnóstico, agenda ajustável e mapas das cinco faixas; migração testada do progresso v1 | V1-02 |
| V1-04 | Idiomas e tour | Estrutura PT/EN/ES, navegação acessível, estados de tradução e tour opcional/repetível | V1-02 |
| V1-05 | Lab piloto | Observabilidade Compose com cenário completo, reset e requisitos medidos; piloto antes de multiplicar pacotes | V1-01 |
| V1-06 | Infraestrutura | Revisar as 30 aulas, integrar os seis aprofundamentos; pacote Linux/Ansible com receita e OVA validado | V1-02, V1-05 |
| V1-07 | Dados | Seis unidades, pacote PostgreSQL/pgvector/RAG, perfil NiFi e três cenários verificados | V1-02, V1-05 |
| V1-08 | Segurança | Seis unidades e práticas integradas aos pacotes; entradas sintéticas e isolamento comprovado | V1-02, V1-05 |
| V1-09 | Agentes e processos | Oito unidades, quatro processos, perfil n8n, roteiro opcional Power Automate, aprovação/estado em código e avaliações com falhas adversas | V1-02, V1-05, V1-08 |
| V1-10 | Progresso público | Adaptadores visitante/local/conta, contratos de dados, OAuth/RLS, exportação, exclusão e testes entre usuários | V1-03 |
| V1-11 | PWA | Instalação Android, download escolhido, retomada offline e sincronização com conflito visível | V1-04, V1-10 |
| V1-12 | Curadoria | Diretório de credenciais externas, templates, proposta semanal de atualização e revisão editorial | V1-02 |
| V1-13 | Tradução integral | Conteúdo-base e aprofundamentos em PT/EN/ES, com revisão técnica vinculada à versão original | V1-04, V1-06, V1-07, V1-08, V1-09 |
| V1-14 | Pronto para publicação | Piloto, gates aplicáveis, licenças aprovadas, documentação atual, CI validada, artefatos verificáveis e plano de recuperação | V1-06 a V1-13 |
| V1-15 | Publicação | Revisão dos arquivos e configurações finais pelo mantenedor; publicação e ativação dentro do escopo autorizado | V1-14 e autorização de publicação |

Milestones propostas: Base confiável (01–04), Prática real (05–09), Experiência pública (10–13), Validação e lançamento (14–15). São agrupamentos de entrega, sem datas prometidas. Abrir issues após reconciliar dependências e confirmar a implementação.

Regras: nenhuma mudança de ID sem migração; nenhuma ferramenta paga no caminho essencial; nenhum resultado de simulador anunciado como experiência real de provedor; nenhuma aula considerada pronta sem prática e revisão. Um bloqueio de provedor não impede o modo visitante, mas impede anunciar sincronização concluída.

Primeiro incremento local: biblioteca com 12 manuais essenciais, seis aprofundamentos integrados e sete guias de ferramentas e entrega. Validador de autoria e testes acrescentados. V1-01 parcialmente atendido; V1-02 iniciado pelos manuais. As 50 unidades, trilhas, contas e pacotes reais completos ainda não estão entregues.

Fundamentos solicitados durante a implementação: Git/GitHub, Actions e CI/CD entram em V1-06 ligados à aula 6 e às práticas de segurança/entrega. Três guias e um exercício de política de promoção já foram implementados localmente; execução hospedada e configuração de regras reais do GitHub continuam pendentes.

Incremento de ritmo em V1-03: disponibilidade diária de 30 min a 5h, prévia e datas coerentes, preservando o progresso v1. Não conclui V1-03: seleção semanal, pausas, quatro trilhas, diagnóstico adaptativo e mapas por faixa dependem da estrutura versionada de V1-02 e continuam pendentes.

Incremento seguinte concluído localmente: catálogo de unidades com schema, IDs, competências, pré-requisitos, duração, prática, fontes/revisões e traduções explícitas. Quatro páginas independentes de trilha, filtros e guias da biblioteca conectados; 30 unidades disponíveis e 20 planejadas. Projeção do progresso antigo verificada sem migração. V1-02 possui agora a estrutura de metadados; separar os corpos da autoria legada e concluir revisão das 50 aulas ainda são trabalhos editoriais. V1-03 ainda exige diagnóstico adaptativo, mapa de faixas e agenda semanal/pausas. Próximo incremento de conteúdo: unidades de Dados/SQL/RAG e prática verificável, antes de marcar essas aulas como disponíveis.
