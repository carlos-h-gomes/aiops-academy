# AIOps Academy — User Manual

Status: public beta
Version: 1.2.0-beta.3 candidate
Reviewed: 2026-09-24
Owner: local learner / root implementation

## Product purpose and prerequisites

Curso local para iniciante com 50 aulas e ritmo ajustável, foco na operação de infraestrutura com IA. Python 3.12+ e Node LTS22.12+/24 para preparar; app já preparado usa iniciar.cmd. Sem conta de IA ou cloud para bancadas.

## Access and first use

Abra iniciar.cmd. O navegador abre http://127.0.0.1:8765. Se solicitado, rode preparar.cmd primeiro. Faça Diagnóstico em Simulados e ajuste início/ritmo em Preferências. O primeiro acesso salva a data inicial; o fim do ciclo acompanha a data escolhida em Preferências.

## Navigation

Visão geral aponta a próxima missão. Trilhas lista e busca 50 aulas. Laboratórios abre 11 bancadas legadas. Simulados oferece diagnóstico, quatro checkpoints e final. Revisão usa recuperação espaçada. Portfólio reúne notas. Biblioteca inclui 25 conteúdos e kit. Preferências cuida de agenda e backup.

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

Navegação por teclado, link pular conteúdo, foco visível, labels, mensagens de status e layout responsivo. Use Tab/Shift+Tab, Enter e Space. Editores e tabelas têm rolagem horizontal própria. Respeita reduced motion. Os limites públicos aplicáveis constam neste manual e em [Segurança](../SECURITY.md); não se afirma certificação WCAG por um scanner.

## Troubleshooting and frequently asked questions

O percurso essencial das 50 aulas tem 117,5h e pode ser dividido em sessões menores. Não precisa de cartão. Simulador não é Ansible/Dynatrace completo. Sessão encerra após 8h; reiniciar preserva progresso. Rascunhos ficam neste navegador; para levá-los a outro dispositivo, salve a evidência e exporte backup.

## Support and escalation

Registre mensagem segura, página e sequência para reproduzir; nunca envie seu banco ou credenciais indiscriminadamente. Mudanças podem ser propostas conforme CONTRIBUTING.md. Questões de ferramentas corporativas devem ir ao owner do ambiente, com dados permitidos e limites claros.

## Version and release notes

1.2.0-beta.3 candidate: mantém as 50 aulas, 11 bancadas legadas, seis configurações de simulado, 25 itens de biblioteca, revisão, portfólio, backup e kit. As 20 aulas guiadas agora registram seu próprio resultado de lab, evidência, conclusão e revisão no progresso local, sem mudar IDs nem o histórico das 30 aulas legadas. A PWA pode reabrir conteúdo seguro já visitado quando o app estiver offline; conta e sincronização só são opcionais após a pessoa salvar explicitamente um endpoint HTTPS compatível. É uma beta local independente; não representa empresa nem certificação, e nenhum serviço hospedado é parte desta candidata.
## Biblioteca ampliada — beta 1.2.0

Abra Biblioteca e escolha Todos, Manuais essenciais, Aprofundamentos AIOps ou Ferramentas e processos. A busca aceita nomes e conceitos sem exigir acentos; Limpar filtros recupera o catálogo. Selecione um título para ler. Fontes externas exigem internet. Em erro de carregamento, use Tentar novamente.

Os seis aprofundamentos acrescentam oito horas opcionais e exercícios Python no kit. Na pasta aiops_extensions, python check.py confere sua implementação; python check.py --solution confere a referência. Os sete guias de ferramentas e entrega incluem mapa de escolha, n8n, Apache NiFi e Power Automate, com exercícios de desenho, dados fictícios e solução comentada. Eles não instalam nem executam essas ferramentas. Nada disso altera a conclusão dos 30 dias ou apaga seu progresso.

A V1 pública foi aprovada, mas trilhas independentes, login, sincronização, PWA e idiomas adicionais continuam em construção. O funcionamento atual permanece individual e local em português.

Atualização posterior: as páginas independentes de trilha, o progresso das 50 aulas e a PWA local foram implementados no incremento de trabalho atual. Ajustes agora também contém um controle opcional de conta e sincronização: ele exige que você informe e salve explicitamente um endpoint HTTPS compatível, e não faz conexão por padrão. A publicação beta.2 continua sendo o último pacote público qualificado; não há serviço hospedado configurado.

Em Ajustes, **Preferência de idioma** permite escolher Português, English ou Español. Português continua ativo enquanto inglês e espanhol aguardam revisão editorial humana: a escolha nunca mostra uma aula parcialmente traduzida, não envia dados e fica somente neste navegador.

Para praticar CI/CD sem GitHub, abra delivery no kit. Implemente exercise.py e execute python check.py; python check.py --solution verifica a referência em seis casos. ci-example.yml é um workflow inativo para estudo, não executado no GitHub.

## Ritmo flexível — beta 1.2.0

Em Preferências, escolha o início e a disponibilidade por dia. A previsão muda durante a edição; selecione Salvar preferências para atualizar o painel e a trilha. Novos usuários começam com 1h/dia. Quem já estudava mantém a preferência salva.

| Disponibilidade | Previsão de estudo diário |
| --- | --- |
| 30 minutos | 235 dias |
| 45 minutos | 157 dias |
| 1 hora | 118 dias |
| 1h30 | 79 dias |
| 2 horas | 59 dias |
| 3 horas | 40 dias, essencial |
| Até 5 horas | 24 dias, essencial |

Uma aula pode ocupar várias sessões. A data na trilha indica quando começar a aula; a previsão final inclui sua última sessão. Com 2h/dia, uma sessão pode terminar uma aula e começar outra. A estimativa considera todos os dias corridos; folgas e pausas prolongam o prazo. Ainda não há escolha de dias da semana.

Mudar início ou ritmo não apaga notas, conclusões, resultados ou revisões, nem bloqueia aulas. Se salvar falhar, a edição permanece para tentar novamente. A data deve estar entre 01/01/2000 e 31/12/2100.

Backups v1 antigos continuam sendo aceitos. O aplicativo atual exporta backup v2, que preserva também o progresso das aulas guiadas. Uma versão antiga pode rejeitar esse arquivo; para voltar, preserve o backup v2, substitua somente o app e não tente editar o JSON ou banco para forçar compatibilidade. Restaurar continua exigindo confirmação e permite desfazer.

## Trilhas e unidades — beta 1.2.0

Abra **Trilhas de estudo** no menu. Escolha entre Infraestrutura e AIOps, Dados/SQL/RAG, Segurança operacional e Agentes/processos. Existem 30 aulas do calendário de infraestrutura, seis aulas guiadas de Dados, seis de Segurança e oito de Agentes/processos: 50 no total. As 20 aulas guiadas são acessadas pelo ID da unidade e entram no mesmo calendário pessoal, preservando os IDs e a conclusão dos 30 dias originais.

Em cada percurso, **Guias para estudar agora** abre o conteúdo correspondente na Biblioteca. Guias são complementares e não contam como conclusão das novas aulas. Links diretos para guias e trilhas podem ser reabertos no mesmo aplicativo.

Use **Buscar unidades** para encontrar temas e competências, inclusive sem acentos. O filtro **Disponibilidade** mostra todas, disponíveis ou em preparação. **Limpar filtros** recupera a lista. Em cada unidade disponível, **Abrir aula** leva à aula existente; **Revisitar aula** indica uma conclusão já registrada.

Expanda **Pré-requisitos e detalhes** para ver bases recomendadas, limites da simulação, referências e idiomas. As bases são sugestões: não bloqueiam as aulas disponíveis. A data de revisão do catálogo não significa que os produtos de terceiros foram novamente executados. As versões reais de ferramentas ainda não verificadas são identificadas; inglês e espanhol permanecem em preparação.

As aulas guiadas abrem em uma página própria e usam somente conteúdo e exemplos sintéticos locais. As seis aulas de Dados, seis de Segurança e oito de Agentes/processos têm o botão **Abrir lab guiado**: escolha respostas fechadas, confira o feedback e use **Reiniciar escolhas** para limpar a tela. O lab não executa texto, SQL, arquivos, comandos, URLs, rede ou ferramentas externas. Quando o resultado está correto, ele libera a etapa de evidência: descreva o que verificou e use **Concluir aula**. A conclusão, o resultado correto, a evidência e a revisão entram no progresso e no backup v2 dessa unidade, sem alterar quiz ou conclusão das aulas legadas. O calendário considera todas as 50 aulas disponíveis conforme o ritmo salvo. **Ver calendário das 30 aulas** preserva o atalho da trilha anterior.

Se o catálogo falhar, use **Tentar novamente** ou **Abrir trilha de infraestrutura**. Um link desconhecido oferece retorno à lista. Nenhum desses caminhos altera o progresso ou restaura um backup.

## Uso sem conexão e PWA local

Após abrir o aplicativo uma vez, o navegador pode oferecer a instalação da AIOps Academy como aplicativo. A PWA mantém a interface e as páginas de estudo que já foram abertas neste dispositivo. Se o navegador ficar sem conexão, uma faixa informa a condição; o conteúdo já cacheado pode reabrir, mas salvar, restaurar, exportar ou abrir conteúdo inédito depende de o aplicativo local responder novamente. A PWA não cria conta nem sincroniza automaticamente. Se você configurar um serviço compatível nos Ajustes, a sincronização acontece somente depois de entrar e clicar em **Sincronizar agora**; nenhuma alteração de estudo é enviada sem essa escolha.

## Conteúdo em manutenção

O pacote beta.2 inclui as 20 aulas guiadas e seus conteúdos de leitura. Fixtures de autoria, validadores e laboratórios piloto permanecem fora do download; não tente instalar Docker ou alterar isolamento para acessá-los. A implementação local em evolução adiciona calendário, progresso e PWA para essas aulas, mas ainda não foi empacotada ou publicada como uma nova versão.
