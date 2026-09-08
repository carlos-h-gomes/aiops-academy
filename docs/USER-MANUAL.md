# AIOps Academy — User Manual

Status: public local-download beta
Version: 1.2.0-beta.1
Reviewed: 2026-09-07
Owner: local learner / root implementation

## Product purpose and prerequisites

Curso local para iniciante com 30 aulas e ritmo ajustável, foco na operação de infraestrutura com IA. Python 3.12+ e Node LTS22.12+/24 para preparar; app já preparado usa iniciar.cmd. Sem conta de IA ou cloud para bancadas.

## Access and first use

Abra iniciar.cmd. O navegador abre http://127.0.0.1:8765. Se solicitado, rode preparar.cmd primeiro. Faça Diagnóstico em Simulados e ajuste início/ritmo em Preferências. O primeiro acesso salva a data inicial; o fim do ciclo acompanha a data escolhida em Preferências.

## Navigation

Visão geral aponta a próxima missão. Trilha lista e busca 30 aulas. Laboratórios abre 11 bancadas. Simulados oferece diagnóstico, quatro checkpoints e final. Revisão usa recuperação espaçada. Portfólio reúne notas. Biblioteca inclui 25 conteúdos e kit. Preferências cuida de agenda e backup.

## Features and expected outcomes

Dia concluído exige checkpoint>=80%, bancada associada resolvida e nota salva com80 caracteres. Isso verifica participação nos exercícios, não qualidade semântica da nota ou senioridade. Soluções servem para estudar; refaça sem copiar para avaliar autonomia. Desafios de profundidade treinam decisões e limitações.

## Primary workflows

Abra dia, leia Aprender, siga Praticar, resolva bancada, volte para Comprovar, responda quiz e salve evidência. Conclua dia. No lab use pista depois de tentar; reset limpa sessão sintética e preserva conquistas. Simulado tem relógio do servidor; fora do tempo não aprova. Erros entram na revisão. Exporte portfólio e backup regularmente.

## Forms, validation, and feedback

Editor limita12.000 caracteres; YAML e consultas rejeitam sintaxe fora do subset. Notas limitam12.000 caracteres; rascunho fica local no navegador e deve ser salvo para backup. Radios exigem todas as respostas. Erro preserva campos. Botões ficam indisponíveis durante submissão. Restauração valida JSON antes de substituir.

## Roles, permissions, and restrictions

Usuário único local, sem contas. Não há integração com ambiente da empresa. Não use credenciais ou dados corporativos. Bancadas não executam shell. Roteiros de cloud exigem conta sandbox, orçamento e autorização; não são feitos automaticamente.

## Loading, empty, failure, degraded, and recovery states

Carregamento tem status. Lista vazia orienta próxima ação. Servidor indisponível oferece retry; reinicie iniciar.cmd. Backup restaura apenas após confirmar e permite desfazer. Sessão de laboratório expirada pede nova sessão. Porta ocupada preserva o outro processo. Sem internet, conteúdo local continua disponível com servidor aberto.

## Accessibility and supported interaction methods

Navegação por teclado, link pular conteúdo, foco visível, labels, mensagens de status e layout responsivo. Use Tab/Shift+Tab, Enter e Space. Editores e tabelas têm rolagem horizontal própria. Respeita reduced motion. A evidência de QA específica consta em docs/VALIDATION.md; não se afirma certificação WCAG por um scanner.

## Troubleshooting and frequently asked questions

O percurso completo tem 142h: até 5h por aula, com quatro revisões de 3h. O essencial tem 90h e pode ser dividido em sessões menores. Não precisa de cartão. Simulador não é Ansible/Dynatrace completo. Sessão encerra após 8h; reiniciar preserva progresso. Para preservar rascunho entre navegadores, salve e exporte backup.

## Support and escalation

Registre mensagem segura, página e sequência para reproduzir; nunca envie seu banco ou credenciais indiscriminadamente. Mudanças podem ser propostas conforme CONTRIBUTING.md. Questões de ferramentas corporativas devem ir ao owner do ambiente, com dados permitidos e limites claros.

## Version and release notes

1.2.0-beta.1: 30 aulas disponíveis, 20 unidades planejadas, 11 bancadas, seis configurações de simulado, 25 itens de biblioteca, revisão, portfólio, backup e kit. É uma beta local independente; não representa empresa nem certificação. Partes externas ou não verificadas são listadas no relatório de validação.
## Biblioteca ampliada — beta 1.2.0

Abra Biblioteca e escolha Todos, Manuais essenciais, Aprofundamentos AIOps ou Ferramentas e processos. A busca aceita nomes e conceitos sem exigir acentos; Limpar filtros recupera o catálogo. Selecione um título para ler. Fontes externas exigem internet. Em erro de carregamento, use Tentar novamente.

Os seis aprofundamentos acrescentam oito horas opcionais e exercícios Python no kit. Na pasta aiops_extensions, python check.py confere sua implementação; python check.py --solution confere a referência. Os sete guias de ferramentas e entrega incluem mapa de escolha, n8n, Apache NiFi e Power Automate, com exercícios de desenho, dados fictícios e solução comentada. Eles não instalam nem executam essas ferramentas. Nada disso altera a conclusão dos 30 dias ou apaga seu progresso.

A V1 pública foi aprovada, mas trilhas independentes, login, sincronização, PWA e idiomas adicionais continuam em construção. O funcionamento atual permanece individual e local em português.

Atualização posterior: as páginas independentes de trilha foram implementadas no incremento descrito abaixo; as aulas novas, contas, sincronização, PWA e traduções ainda permanecem pendentes.

Para praticar CI/CD sem GitHub, abra delivery no kit. Implemente exercise.py e execute python check.py; python check.py --solution verifica a referência em seis casos. ci-example.yml é um workflow inativo para estudo, não executado no GitHub.

## Ritmo flexível — beta 1.2.0

Em Preferências, escolha o início e a disponibilidade por dia. A previsão muda durante a edição; selecione Salvar preferências para atualizar o painel e a trilha. Novos usuários começam com 1h/dia. Quem já estudava mantém a preferência salva.

| Disponibilidade | Previsão de estudo diário |
| --- | --- |
| 30 minutos | 180 dias |
| 45 minutos | 120 dias |
| 1 hora | 90 dias |
| 1h30 | 60 dias |
| 2 horas | 45 dias |
| 3 horas | 30 dias, essencial |
| Até 5 horas | 30 dias, completo |

Uma aula pode ocupar várias sessões. A data na trilha indica quando começar a aula; a previsão final inclui sua última sessão. Com 2h/dia, uma sessão pode terminar uma aula e começar outra. A estimativa considera todos os dias corridos; folgas e pausas prolongam o prazo. Ainda não há escolha de dias da semana.

Mudar início ou ritmo não apaga notas, conclusões, resultados ou revisões, nem bloqueia aulas. Se salvar falhar, a edição permanece para tentar novamente. A data deve estar entre 01/01/2000 e 31/12/2100.

Backups v1 antigos continuam sendo aceitos. Os novos ritmos precisam desta versão atualizada do app. Para voltar ao aplicativo antigo, guarde seu backup atual e selecione 3h ou 5h antes de exportar outro arquivo compatível. Restaurar continua exigindo confirmação e permite desfazer.

## Trilhas e unidades — beta 1.2.0

Abra **Trilhas de estudo** no menu. Escolha entre Infraestrutura e AIOps, Dados/SQL/RAG, Segurança operacional e Agentes/processos. A página inicial separa aulas disponíveis de unidades em preparação. Atualmente existem 30 aulas disponíveis de infraestrutura e 20 unidades previstas nas outras trilhas (6, 6 e 8).

Em cada percurso, **Guias para estudar agora** abre o conteúdo correspondente na Biblioteca. Guias são complementares e não contam como conclusão das novas aulas. Links diretos para guias e trilhas podem ser reabertos no mesmo aplicativo.

Use **Buscar unidades** para encontrar temas e competências, inclusive sem acentos. O filtro **Disponibilidade** mostra todas, disponíveis ou em preparação. **Limpar filtros** recupera a lista. Em cada unidade disponível, **Abrir aula** leva à aula existente; **Revisitar aula** indica uma conclusão já registrada.

Expanda **Pré-requisitos e detalhes** para ver bases recomendadas, limites da simulação, referências e idiomas. As bases são sugestões: não bloqueiam as aulas disponíveis. A data de revisão do catálogo não significa que os produtos de terceiros foram novamente executados. As versões reais de ferramentas ainda não verificadas são identificadas; inglês e espanhol permanecem em preparação.

Unidades em preparação não têm aula, prática ou duração pronta e não podem ser concluídas. O calendário continua sendo o de Infraestrutura e AIOps; escolher outra página não muda datas, notas, revisões ou resultados. **Ver calendário das 30 aulas** abre a trilha anterior.

Se o catálogo falhar, use **Tentar novamente** ou **Abrir trilha de infraestrutura**. Um link desconhecido oferece retorno à lista. Nenhum desses caminhos altera o progresso ou restaura um backup.
