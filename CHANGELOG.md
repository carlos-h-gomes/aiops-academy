# Changelog

## 1.2.0-beta.3 — 2026-09-24

- As 50 aulas disponíveis passam a compartilhar um calendário coerente e progresso local por unidade, preservando os IDs e backups das 30 aulas legadas.
- A PWA local disponibiliza a interface e leituras de estudo já visitadas sem armazenar escritas, exportações ou filas de sincronização.
- Conta e sincronização são opt-in: não existe endpoint padrão, tráfego automático, domínio da empresa, conta de aluno, migração remota ou serviço hospedado nesta candidata.
- A fonte compatível com Cloudflare e sua migração D1 permanecem cobertas por testes locais; a prévia externa isolada não recebeu código do adaptador nem dados de aluno.

## 1.2.0-beta.2 — 2026-09-23

- As 20 aulas guiadas de Dados, Segurança e Agentes/processos passam a integrar o pacote local: são 50 aulas disponíveis no total.
- Cada aula guiada oferece um lab de escolhas fechadas, com feedback e reinício somente em memória; não há mudança de progresso, calendário, notas, quizzes, conclusão ou backup.
- O pacote inclui apenas os 20 corpos publicados das aulas guiadas. Fixtures, validadores, pilotos, dados do aluno, dependências instaladas, memória privada e arquivos sensíveis permanecem excluídos.
- A jornada de navegador cobre leitura, lab, respostas incompletas, feedback incorreto/correto, reinício, teclado, reflow e preservação do progresso legado.

## 1.2.0-beta.1 — 2026-09-07

- Quatro páginas de trilha, catálogo versionado, busca por competência e filtro de disponibilidade. As 30 aulas existentes estão disponíveis; as 20 novas unidades são planejamento identificado.
- IDs estáveis, pré-requisitos, duração, prática/limites, fontes e estado de traduções validados; detecção de duplicação, referências inválidas, ciclos e conteúdo desatualizado. Nenhuma migração de progresso ou mudança de backup.
- Links diretos para guias da Biblioteca; erros de catálogo preservam acesso à trilha anterior. Progresso de unidade reflete o dia já concluído.
- Exclusão de dados do aluno limitada à pasta raiz: arquivos de tipos em frontend/src/data passam a integrar Git e pacote portátil. Verificação de extração inclui o catálogo.

- Ritmo flexível: 30 min, 45 min, 1h, 1h30, 2h, 3h ou 5h por dia; previsão de 30 a 180 dias, conforme o percurso. Novos alunos começam com 1h; preferências existentes são preservadas.
- Calendário consistente entre prévia, painel, cabeçalho, trilha e aula; textos distinguem aula de sessão. Validação de data e controles indisponíveis durante o salvamento.
- Compatibilidade dos backups v1 mantida no app atualizado; testes cobrem preservação de progresso, restauração e desfazer com ritmos novos e antigos.

- Fundamentos adicionados a pedido do usuário: Git/GitHub, GitHub Actions e CI/CD. Biblioteca agora com 25 entradas; laboratório delivery offline com seis casos e exemplo de workflow inativo.


- V1 pública aprovada; código MIT e conteúdo original CC BY 4.0.
- Biblioteca: seis aprofundamentos AIOps integrados e quatro guias sobre ferramentas, n8n, NiFi e Power Automate; busca sem acentos e filtros por categoria.
- Validação de módulos antes da geração, preservando saída anterior quando há erro.
- Doze casos de referência dos aprofundamentos verificados e incluídos no kit.
- Guias de ferramentas são exercícios de desenho/decisão; produtos ainda não são instalados pela Academy.


Melhorias futuras estão no ROADMAP.md. Nenhuma funcionalidade planejada deve aparecer como entregue nesta versão.

## 1.1.0 — 2026-09-06

- Identidade geral, sem destinatário, empregador ou data de contratação fixa.
- Calendário calculado por pessoa; data inicial persistida no primeiro acesso.
- Datas existentes, notas, conclusões e backups v1 preservados.
- Base de contribuição, roadmap, CI preparada e exclusões Git para dados locais.
- Pacote de distribuição exclui evidências e memória privadas.

## 1.0.0 — 2026-09-06

- Primeira versão local: currículo de 30 dias, simuladores, provas, revisão espaçada, portfólio, backup e kit de exercícios.
