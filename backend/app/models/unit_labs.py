"""Fixed local lab definitions. They never load learner files or execute input."""
from app.schemas.unit_labs import UnitLab, UnitLabOption, UnitLabQuestion, UnitLabResult


def _options(*values):
    return [UnitLabOption(value=value, label=label) for value, label in values]


def _question(identity, prompt, *options):
    return UnitLabQuestion(id=identity, prompt=prompt, options=_options(*options))


# The expected values remain server-side. Browser clients receive only the question text
# and fixed options, never an arbitrary file, command, URL, SQL statement or evaluator.
DATA_LABS = {
    'data-01': {
        'title': 'Lab local: integridade relacional',
        'intro': 'Classifique o resultado da fixture relacional sintética. Nenhuma resposta executa SQL.',
        'limitations': 'Usa somente uma matriz de resultados conhecida; não abre bancos, arquivos ou conexões externas.',
        'expected': {'services': '2', 'incidents': '2', 'foreign_key': 'rejeitada', 'duplicate': 'rejeitada', 'check': 'rejeitada'},
        'questions': [
            _question('services', 'Quantos serviços a carga válida contém?', ('1', 'Um'), ('2', 'Dois'), ('4', 'Quatro')),
            _question('incidents', 'Quantos incidentes a carga válida contém?', ('1', 'Um'), ('2', 'Dois'), ('4', 'Quatro')),
            _question('foreign-key', 'Um incidente com serviço inexistente deve ser…', ('rejeitada', 'rejeitado pela FK'), ('aceita', 'aceito como pendente')),
            _question('duplicate', 'Um evento com chave de origem repetida deve ser…', ('rejeitada', 'rejeitado pela unicidade'), ('aceita', 'aceito como novo evento')),
            _question('check', 'Uma severidade fora do domínio deve ser…', ('rejeitada', 'rejeitada pelo CHECK'), ('aceita', 'aceita para correção posterior')),
        ],
        'aliases': {'foreign-key': 'foreign_key'},
    },
    'data-02': {
        'title': 'Lab local: joins e contagens',
        'intro': 'Preveja os resultados das consultas versionadas contra uma base descartável.',
        'limitations': 'Nenhuma consulta digitada é executada; o lab avalia apenas escolhas fechadas da fixture SQLite.',
        'expected': {'quotes_inner': '4', 'quotes_left': '5', 'quotes_summary': '2', 'fanout': '8', 'missing_event_count': '0'},
        'questions': [
            _question('quotes-inner', 'Para quotes, o INNER JOIN retorna quantas linhas?', ('0', '0'), ('4', '4'), ('5', '5')),
            _question('quotes-left', 'Para quotes, o LEFT JOIN retorna quantas linhas?', ('2', '2'), ('4', '4'), ('5', '5')),
            _question('quotes-summary', 'Para quotes, o resumo retorna quantos incidentes?', ('1', '1'), ('2', '2'), ('5', '5')),
            _question('fanout', 'Juntar todos os runbooks do serviço infla inc-100 para quantas linhas?', ('4', '4'), ('5', '5'), ('8', '8')),
            _question('missing-event-count', 'COUNT(evento_id) para inc-300 vale…', ('0', '0'), ('1', '1'), ('nulo', 'NULL')),
        ],
        'aliases': {'quotes-inner': 'quotes_inner', 'quotes-left': 'quotes_left', 'quotes-summary': 'quotes_summary', 'missing-event-count': 'missing_event_count'},
    },
    'data-03': {
        'title': 'Lab local: plano e índice',
        'intro': 'Interprete um plano simplificado desenhado para o exercício, sem medir um PostgreSQL.',
        'limitations': 'Não há servidor, SQL executável, tempo ou buffer real neste lab.',
        'expected': {'estimate_factor': '10', 'repeated_total': '12', 'index_columns': 'incidente_id,ocorrido_em', 'speedup_proven': 'false', 'write_overhead': 'true'},
        'questions': [
            _question('estimate-factor', 'A estimativa 100 dividida por 10 linhas reais é…', ('1', '1'), ('10', '10'), ('100', '100')),
            _question('repeated-total', 'Três linhas por quatro loops totalizam…', ('3', '3'), ('7', '7'), ('12', '12')),
            _question('index-columns', 'Para igualdade em incidente e faixa de tempo, escolha…', ('incidente_id,ocorrido_em', 'incidente_id, depois ocorrido_em'), ('ocorrido_em,incidente_id', 'ocorrido_em, depois incidente_id')),
            _question('speedup-proven', 'O cenário comprova aceleração em runtime?', ('false', 'Não; é uma simulação'), ('true', 'Sim; o nome do nó basta')),
            _question('write-overhead', 'Índices acrescentam trabalho às escritas?', ('true', 'Sim'), ('false', 'Não')),
        ],
        'aliases': {'estimate-factor': 'estimate_factor', 'repeated-total': 'repeated_total', 'index-columns': 'index_columns', 'speedup-proven': 'speedup_proven', 'write-overhead': 'write_overhead'},
    },
    'data-04': {
        'title': 'Lab local: rollback e restauração',
        'intro': 'Decida o estado esperado de uma transação sintética que falha e de uma cópia em destino novo.',
        'limitations': 'Não usa dump, arquivo de backup, banco PostgreSQL ou origem do aluno.',
        'expected': {'after_rollback': 'aberto', 'backup_destination': 'nova_conexao', 'source_unchanged': 'true', 'foreign_keys_valid': 'true', 'postgresql_verified': 'false'},
        'questions': [
            _question('after-rollback', 'Após rollback explícito, inc-100 fica…', ('aberto', 'aberto'), ('resolvido', 'resolvido')),
            _question('backup-destination', 'O backup vai para…', ('nova_conexao', 'uma conexão nova e vazia'), ('origem', 'a própria origem')),
            _question('source-unchanged', 'Após alterar o destino, a origem permanece inalterada?', ('true', 'Sim'), ('false', 'Não')),
            _question('foreign-keys-valid', 'A cópia de referência termina com FKs válidas?', ('true', 'Sim'), ('false', 'Não')),
            _question('postgresql-verified', 'O exercício qualificou PostgreSQL?', ('false', 'Não'), ('true', 'Sim')),
        ],
        'aliases': {'after-rollback': 'after_rollback', 'backup-destination': 'backup_destination', 'source-unchanged': 'source_unchanged', 'foreign-keys-valid': 'foreign_keys_valid', 'postgresql-verified': 'postgresql_verified'},
    },
    'data-05': {
        'title': 'Lab local: busca com filtro',
        'intro': 'Aplique audiência e versão antes de ordenar vetores bidimensionais desenhados à mão.',
        'limitations': 'Não chama modelo, embeddings, pgvector, banco ou rede.',
        'expected': {'ranking': 'rb-a,rb-b,rb-c', 'restricted_returned': 'false', 'stale_returned': 'false', 'filter_stage': 'antes_do_ranking', 'similarity_proves_truth': 'false'},
        'questions': [
            _question('ranking', 'Qual é o ranking permitido?', ('rb-a,rb-b,rb-c', 'rb-a, rb-b, rb-c'), ('rb-admin,rb-a,rb-b', 'rb-admin, rb-a, rb-b')),
            _question('restricted-returned', 'O documento de instrutor pode retornar ao aluno?', ('false', 'Não'), ('true', 'Sim')),
            _question('stale-returned', 'Documento descontinuado pode retornar?', ('false', 'Não'), ('true', 'Sim')),
            _question('filter-stage', 'Em que etapa se aplica audiência e atualidade?', ('antes_do_ranking', 'antes do ranking'), ('depois_do_ranking', 'depois do ranking')),
            _question('similarity-proves-truth', 'Similaridade prova que uma alegação é verdadeira?', ('false', 'Não'), ('true', 'Sim')),
        ],
        'aliases': {'similarity-proves-truth': 'similarity_proves_truth'},
    },
    'data-06': {
        'title': 'Lab local: evidência e acesso',
        'intro': 'Decida responder ou abster-se usando citações pré-vinculadas a alegações.',
        'limitations': 'Não interpreta linguagem natural nem segue instruções presentes nos documentos sintéticos.',
        'expected': {'supported': 'responder', 'no_evidence': 'abster', 'stale': 'abster', 'forbidden': 'abster', 'injection': 'abster', 'wrong_version': 'abster'},
        'questions': [
            _question('supported', 'Citação atual da audiência certa sustenta a alegação?', ('responder', 'Responder'), ('abster', 'Abster-se')),
            _question('no-evidence', 'Sem evidência disponível, a decisão é…', ('abster', 'Abster-se'), ('responder', 'Responder')),
            _question('stale', 'Citação descontinuada permite responder?', ('abster', 'Abster-se'), ('responder', 'Responder')),
            _question('forbidden', 'Documento de instrutor pode sustentar resposta de aluno?', ('abster', 'Abster-se'), ('responder', 'Responder')),
            _question('injection', 'Texto que manda ignorar regras altera o avaliador?', ('abster', 'Não; abster-se'), ('responder', 'Sim; responder')),
            _question('wrong-version', 'Citação da versão errada permite responder?', ('abster', 'Abster-se'), ('responder', 'Responder')),
        ],
        'aliases': {'no-evidence': 'no_evidence', 'wrong-version': 'wrong_version'},
    },
}

SECURITY_LABS = {
    'security-01': {
        'title': 'Lab local: menor privilégio',
        'intro': 'Classifique decisões fixas de uma política sintética, sem criar identidade, credencial, conta ou regra externa.',
        'limitations': 'O lab avalia somente escolhas fechadas sobre sujeitos e recursos fictícios; não autentica, autoriza, altera IAM, chama rede ou persiste uma decisão.',
        'expected': {'allowed': '1', 'denied': '3', 'read_change': 'separadas', 'external_actions': '0'},
        'questions': [
            _question('allowed', 'Quantos cenários da fixture recebem allow?', ('1', 'um'), ('3', 'três')),
            _question('denied', 'Quantos cenários da fixture recebem deny?', ('1', 'um'), ('3', 'três')),
            _question('read-change', 'Ler e alterar um mesmo runbook exigem permissões…', ('separadas', 'separadas e explícitas'), ('herdadas', 'herdadas pela leitura')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'read-change': 'read_change', 'external-actions': 'external_actions'},
    },
    'security-02': {
        'title': 'Lab local: evidência mínima e redação',
        'intro': 'Classifique decisões de proteção em uma fixture inteiramente sintética e fechada.',
        'limitations': 'Não recebe, reconhece, testa, armazena ou transmite credenciais, dados reais ou valores livres.',
        'expected': {'allowed_fields': '5', 'secret_marker': 'redigido', 'study_record': 'redigido', 'runtime_mode': 'excluido', 'secret_leak': 'rejeitada'},
        'questions': [
            _question('allowed-fields', 'A evidência aceita contém quantos campos permitidos?', ('4', 'Quatro'), ('5', 'Cinco'), ('7', 'Sete')),
            _question('secret-marker', 'O marcador semelhante a segredo deve aparecer como…', ('redigido', '[REDIGIDO]'), ('texto_original', 'texto original')),
            _question('study-record', 'O registro sintético de estudo deve aparecer como…', ('redigido', '[REDIGIDO]'), ('texto_original', 'texto original')),
            _question('runtime-mode', 'A configuração runtime_mode deve ser…', ('excluido', 'excluída da evidência'), ('incluido', 'incluída na evidência')),
            _question('secret-leak', 'Uma saída com valor protegido em claro deve ser…', ('rejeitada', 'rejeitada'), ('aceita', 'aceita')),
        ],
        'aliases': {'allowed-fields': 'allowed_fields', 'secret-marker': 'secret_marker', 'study-record': 'study_record', 'runtime-mode': 'runtime_mode', 'secret-leak': 'secret_leak'},
    },
    'security-03': {
        'title': 'Lab local: topologia e hardening',
        'intro': 'Classifique decisões da topologia sintética sem iniciar container, rede ou processo.',
        'limitations': 'O lab só avalia escolhas fechadas; não aplica manifesto, abre porta, monta volume ou acessa Docker.',
        'expected': {'valid_topology': 'accept', 'publisher': 'loopback', 'egress': 'fixa', 'daemon_socket': 'deny', 'external_actions': '0'},
        'questions': [
            _question('valid-topology', 'A topologia sintética que satisfaz a policy recebe…', ('accept', 'aceitação'), ('deny', 'negação')),
            _question('publisher', 'Quando há publisher de recuperação, ele deve usar…', ('loopback', 'somente loopback'), ('publico', 'um bind público')),
            _question('egress', 'A rota de saída permitida é…', ('fixa', 'fixa e não configurável'), ('livre', 'livremente escolhida')),
            _question('daemon-socket', 'Um socket do daemon no manifesto sintético deve ser…', ('deny', 'negado'), ('accept', 'aceito')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'valid-topology': 'valid_topology', 'daemon-socket': 'daemon_socket', 'external-actions': 'external_actions'},
    },
    'security-04': {
        'title': 'Lab local: evidência de suprimento',
        'intro': 'Classifique registros de artefatos fictícios sem baixar imagem, consultar registry ou executar scanner.',
        'limitations': 'O lab avalia decisões fechadas da fixture; digest, SBOM e proveniência não representam um artefato real.',
        'expected': {'approved': '1', 'blocked': '4', 'review': '1', 'latest': 'block', 'external_actions': '0'},
        'questions': [
            _question('approved', 'Quantos cenários sintéticos recebem approve?', ('1', 'um'), ('4', 'quatro')),
            _question('blocked', 'Quantos cenários sintéticos recebem block?', ('1', 'um'), ('4', 'quatro')),
            _question('review', 'Quantos cenários sintéticos recebem review?', ('0', 'zero'), ('1', 'um')),
            _question('latest', 'Uma tag latest na fixture deve resultar em…', ('block', 'block'), ('approve', 'approve')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'external-actions': 'external_actions'},
    },
    'security-05': {
        'title': 'Lab local: resposta e recuperação',
        'intro': 'Classifique a resposta a incidente da fixture em memória sem alterar uma origem ou restaurar recurso real.',
        'limitations': 'O lab não toca arquivos, banco, volumes, serviços, rede ou processos; o reset é somente didático.',
        'expected': {'completed': '1', 'rejected': '5', 'origin': 'inalterada', 'destination': 'separado', 'external_actions': '0'},
        'questions': [
            _question('completed', 'Quantos cenários alcançam complete?', ('1', 'um'), ('5', 'cinco')),
            _question('rejected', 'Quantos cenários são rejeitados antes de mudar estado?', ('1', 'um'), ('5', 'cinco')),
            _question('origin', 'A origem sintética após o cenário aceito fica…', ('inalterada', 'inalterada'), ('sobrescrita', 'sobrescrita')),
            _question('destination', 'O destino de recuperação deve ser…', ('separado', 'separado da origem'), ('origem', 'a própria origem')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'external-actions': 'external_actions'},
    },
    'security-06': {
        'title': 'Lab local: autoridade fora do texto',
        'intro': 'Classifique decisões de policy estática sem chamar modelo, ferramenta, rede, processo ou aprovação real.',
        'limitations': 'O lab só avalia escolhas fechadas; textos hostis da fixture não são executados nem retornados ao navegador.',
        'expected': {'allowed': '1', 'denied': '14', 'extra_field': 'deny', 'authority': 'externa', 'external_actions': '0'},
        'questions': [
            _question('allowed', 'Quantos pedidos da fixture recebem allow?', ('1', 'um'), ('14', 'quatorze')),
            _question('denied', 'Quantos pedidos da fixture recebem deny?', ('1', 'um'), ('14', 'quatorze')),
            _question('extra-field', 'Um campo extra no pedido fechado deve resultar em…', ('deny', 'negação de schema'), ('allow', 'permissão')),
            _question('authority', 'A autorização que permite a fixture vem de registro…', ('externa', 'externo e vinculado'), ('texto', 'de texto não confiável')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'extra-field': 'extra_field', 'external-actions': 'external_actions'},
    },
}

AGENT_LABS = {
    'agents-01': {
        'title': 'Lab local: processos e limites',
        'intro': 'Classifique decisões predefinidas sobre processos sintéticos, sem chamar um modelo ou ferramenta.',
        'limitations': 'O lab avalia somente escolhas fechadas; não interpreta texto livre, chama rede, cria estado ou executa ações externas.',
        'expected': {'routine': 'regra', 'high_impact': 'recusa', 'external_actions': '0'},
        'questions': [
            _question('routine', 'Um processo de baixo risco com entradas completas usa…', ('regra', 'regra determinística'), ('agente', 'agente autônomo')),
            _question('high-impact', 'Um processo de alto impacto deve receber…', ('recusa', 'recusa e revisão humana'), ('automacao', 'automação imediata')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'high-impact': 'high_impact', 'external-actions': 'external_actions'},
    },
    'agents-02': {
        'title': 'Lab local: camadas e autoridade',
        'intro': 'Diferencie componentes do cenário didático e mantenha a decisão de capacidade fora de uma resposta plausível.',
        'limitations': 'O lab avalia somente escolhas fechadas; não chama modelo, provider, rede, processo, arquivo ou aprovação externa.',
        'expected': {'authority': 'policy', 'state': 'efemero', 'external_actions': '0'},
        'questions': [
            _question('authority', 'A capacidade de uma ação vem da…', ('policy', 'policy e aprovação vinculada'), ('resposta', 'resposta plausível do assistente')),
            _question('state', 'O estado do controlador didático é…', ('efemero', 'efêmero, em memória'), ('persistente', 'persistente em serviço externo')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'external-actions': 'external_actions'},
    },
    'agents-03': {
        'title': 'Lab local: contratos fechados',
        'intro': 'Escolha como um controlador de exemplo reage a contratos e ferramentas previamente delimitados.',
        'limitations': 'Não recebe comandos, caminhos, URLs, SQL ou texto livre; cada decisão é uma escolha fechada em memória.',
        'expected': {'extra_field': 'bloquear', 'shell': 'bloquear', 'external_actions': '0'},
        'questions': [
            _question('extra-field', 'Um campo extra fora do schema deve…', ('bloquear', 'ser bloqueado antes da policy'), ('aceitar', 'ser aceito para conversão')),
            _question('shell', 'Uma ferramenta shell fora da allowlist deve…', ('bloquear', 'ser bloqueada'), ('executar', 'ser executada em modo limitado')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'extra-field': 'extra_field', 'external-actions': 'external_actions'},
    },
    'agents-04': {
        'title': 'Lab local: estado e aprovação',
        'intro': 'Avalie transições predefinidas de espera, aprovação vinculada e repetição idempotente.',
        'limitations': 'O cenário usa somente estado efêmero e escolhas fechadas; não cria aprovações, persiste dados ou executa ferramentas externas.',
        'expected': {'missing_approval': 'hold', 'replay': 'idempotente', 'external_actions': '0'},
        'questions': [
            _question('missing-approval', 'Um pedido que exige aprovação, mas não a recebeu, fica em…', ('hold', 'hold para retomada segura'), ('completed', 'completed automaticamente')),
            _question('replay', 'Uma repetição com a mesma intenção concluída deve ser…', ('idempotente', 'idempotente, sem novo efeito'), ('duplicada', 'executada novamente')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'missing-approval': 'missing_approval', 'external-actions': 'external_actions'},
    },
    'agents-05': {
        'title': 'Lab local: triagem revisável',
        'intro': 'Classifique limites de uma proposta de correção sintética sem acessar repositório, container ou serviço externo.',
        'limitations': 'O lab não abre arquivos, inicia Docker, gera commit, envia alteração ou executa comandos; avalia apenas decisões fechadas.',
        'expected': {'workspace': 'efemero', 'publication': 'bloquear', 'external_actions': '0'},
        'questions': [
            _question('workspace', 'Uma proposta de diff didática deve ficar em área…', ('efemero', 'efêmera e revisável'), ('producao', 'de produção compartilhada')),
            _question('publication', 'Commit ou push automático está…', ('bloquear', 'bloqueado fora da prática'), ('permitir', 'permitido após rascunho')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'external-actions': 'external_actions'},
    },
    'agents-06': {
        'title': 'Lab local: chamados com evidência',
        'intro': 'Classifique encaminhamentos de chamados fictícios usando runbooks e decisões pré-vinculados.',
        'limitations': 'O lab não envia mensagens, modifica contas, executa runbooks, chama modelo ou acessa rede.',
        'expected': {'missing_evidence': 'hold', 'send': 'bloquear', 'external_actions': '0'},
        'questions': [
            _question('missing-evidence', 'Um chamado sem evidência aplicável deve ficar em…', ('hold', 'hold para revisão'), ('rascunho', 'rascunho sem citação')),
            _question('send', 'A ação de enviar uma mensagem está…', ('bloquear', 'bloqueada fora do contrato'), ('permitir', 'permitida pelo runbook')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'missing-evidence': 'missing_evidence', 'external-actions': 'external_actions'},
    },
    'agents-07': {
        'title': 'Lab local: briefing e revisão',
        'intro': 'Classifique fatos, revisão vinculada e publicação em um briefing inteiramente sintético.',
        'limitations': 'O lab não publica, envia conteúdo, chama modelo, acessa plataforma social ou recebe texto livre.',
        'expected': {'unsupported_claim': 'bloquear', 'publication': 'bloquear', 'external_actions': '0'},
        'questions': [
            _question('unsupported-claim', 'Uma afirmação sem fato fornecido deve…', ('bloquear', 'ser bloqueada'), ('inventar', 'ser completada pelo assistente')),
            _question('publication', 'Uma revisão válida concede publicação externa?', ('bloquear', 'Não; publicação continua bloqueada'), ('permitir', 'Sim; revisão cria permissão')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'unsupported-claim': 'unsupported_claim', 'external-actions': 'external_actions'},
    },
    'agents-08': {
        'title': 'Lab local: conciliação sintética',
        'intro': 'Classifique correspondências e exceções de registros fictícios sem importar arquivos ou mover valores.',
        'limitations': 'O lab não lê CSV, conecta banco, faz pagamento, transfere valores ou acessa rede; avalia escolhas fechadas.',
        'expected': {'duplicate': 'revisar', 'payment': 'bloquear', 'external_actions': '0'},
        'questions': [
            _question('duplicate', 'Uma chave duplicada na conciliação deve…', ('revisar', 'seguir para revisão'), ('somar', 'ser somada automaticamente')),
            _question('payment', 'Um pedido de pagamento está…', ('bloquear', 'bloqueado fora da capacidade'), ('permitir', 'permitido após conciliar')),
            _question('external-actions', 'Quantas ações externas este lab executa?', ('0', 'zero'), ('1', 'uma')),
        ],
        'aliases': {'external-actions': 'external_actions'},
    },
}

LABS = {**DATA_LABS, **SECURITY_LABS, **AGENT_LABS}


def load_unit_lab(unit_id: str) -> UnitLab:
    try:
        lab = LABS[unit_id]
        return UnitLab(unit_id=unit_id, title=lab['title'], intro=lab['intro'], limitations=lab['limitations'], questions=lab['questions'])
    except KeyError as error:
        raise ValueError('Lab unavailable.') from error


def grade_unit_lab(unit_id: str, answers: dict[str, str]) -> UnitLabResult:
    try:
        lab = LABS[unit_id]
        aliases = lab.get('aliases', {})
        normalized = {aliases.get(key, key): value for key, value in answers.items()}
        expected = lab['expected']
        reviewed = sorted(key for key, value in expected.items() if normalized.get(key) != value)
        reviewed.extend(sorted(key for key in normalized if key not in expected))
        correct = not reviewed and len(normalized) == len(expected)
        return UnitLabResult(
            unit_id=unit_id,
            correct=correct,
            reviewed_fields=reviewed,
            feedback='Todas as decisões coincidem com a fixture local.' if correct else 'Revise as decisões marcadas e compare com a explicação da aula. Nenhuma resposta foi gravada.',
        )
    except KeyError as error:
        raise ValueError('Lab unavailable.') from error
