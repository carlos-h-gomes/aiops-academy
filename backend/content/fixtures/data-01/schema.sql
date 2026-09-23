-- Fixture didática sintética. O verificador usa um banco temporário em memória.
CREATE TABLE servicos (
    servico_id VARCHAR(32) NOT NULL,
    nome VARCHAR(80) NOT NULL,
    criticidade VARCHAR(16) NOT NULL,
    CONSTRAINT servicos_pk PRIMARY KEY (servico_id),
    CONSTRAINT servicos_nome_uq UNIQUE (nome),
    CONSTRAINT servicos_criticidade_ck CHECK (criticidade IN ('baixa', 'media', 'alta'))
);

CREATE TABLE runbooks (
    runbook_id VARCHAR(32) NOT NULL,
    servico_id VARCHAR(32) NOT NULL,
    codigo VARCHAR(64) NOT NULL,
    versao INTEGER NOT NULL,
    titulo VARCHAR(120) NOT NULL,
    estado VARCHAR(16) NOT NULL,
    CONSTRAINT runbooks_pk PRIMARY KEY (runbook_id),
    CONSTRAINT runbooks_servico_fk FOREIGN KEY (servico_id)
        REFERENCES servicos (servico_id) ON DELETE RESTRICT,
    CONSTRAINT runbooks_versao_ck CHECK (versao > 0),
    CONSTRAINT runbooks_estado_ck CHECK (estado IN ('ativo', 'arquivado')),
    CONSTRAINT runbooks_servico_codigo_versao_uq UNIQUE (servico_id, codigo, versao),
    CONSTRAINT runbooks_identidade_servico_uq UNIQUE (runbook_id, servico_id)
);

CREATE TABLE incidentes (
    incidente_id VARCHAR(32) NOT NULL,
    servico_id VARCHAR(32) NOT NULL,
    aberto_em TIMESTAMP NOT NULL,
    severidade VARCHAR(8) NOT NULL,
    estado VARCHAR(16) NOT NULL,
    runbook_id VARCHAR(32),
    CONSTRAINT incidentes_pk PRIMARY KEY (incidente_id),
    CONSTRAINT incidentes_servico_fk FOREIGN KEY (servico_id)
        REFERENCES servicos (servico_id) ON DELETE RESTRICT,
    CONSTRAINT incidentes_runbook_servico_fk FOREIGN KEY (runbook_id, servico_id)
        REFERENCES runbooks (runbook_id, servico_id) ON DELETE RESTRICT,
    CONSTRAINT incidentes_severidade_ck CHECK (severidade IN ('sev1', 'sev2', 'sev3')),
    CONSTRAINT incidentes_estado_ck CHECK (estado IN ('aberto', 'mitigado', 'resolvido'))
);

CREATE TABLE eventos (
    evento_id VARCHAR(32) NOT NULL,
    incidente_id VARCHAR(32) NOT NULL,
    chave_origem VARCHAR(120) NOT NULL,
    ocorrido_em TIMESTAMP NOT NULL,
    tipo VARCHAR(16) NOT NULL,
    mensagem VARCHAR(240) NOT NULL,
    CONSTRAINT eventos_pk PRIMARY KEY (evento_id),
    CONSTRAINT eventos_incidente_fk FOREIGN KEY (incidente_id)
        REFERENCES incidentes (incidente_id) ON DELETE RESTRICT,
    CONSTRAINT eventos_chave_origem_uq UNIQUE (chave_origem),
    CONSTRAINT eventos_tipo_ck CHECK (tipo IN ('alerta', 'mudanca', 'anotacao', 'recuperacao'))
);
