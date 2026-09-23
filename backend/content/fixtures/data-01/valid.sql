INSERT INTO servicos (servico_id, nome, criticidade) VALUES
    ('svc-quotes', 'quotes', 'alta'),
    ('svc-ledger-demo', 'ledger-demo', 'media');

INSERT INTO runbooks (runbook_id, servico_id, codigo, versao, titulo, estado) VALUES
    ('rb-quotes-01', 'svc-quotes', 'pool-esgotado', 3, 'Investigar esgotamento do pool', 'ativo'),
    ('rb-ledger-01', 'svc-ledger-demo', 'fila-lancamentos', 1, 'Conferir fila de lançamentos', 'arquivado');

INSERT INTO incidentes (incidente_id, servico_id, aberto_em, severidade, estado, runbook_id) VALUES
    ('inc-100', 'svc-quotes', '2026-09-09 09:05:00', 'sev2', 'mitigado', 'rb-quotes-01'),
    ('inc-200', 'svc-ledger-demo', '2026-09-09 10:15:00', 'sev3', 'resolvido', NULL);

INSERT INTO eventos (evento_id, incidente_id, chave_origem, ocorrido_em, tipo, mensagem) VALUES
    ('evt-001', 'inc-100', 'monitor-demo:evt-001', '2026-09-09 09:05:00', 'alerta', 'Taxa de erros acima da linha de base'),
    ('evt-002', 'inc-100', 'change-demo:evt-002', '2026-09-09 09:02:00', 'mudanca', 'Ajuste sintético do pool aplicado'),
    ('evt-003', 'inc-100', 'operator-demo:evt-003', '2026-09-09 09:18:00', 'anotacao', 'Mitigação limitada confirmada'),
    ('evt-004', 'inc-200', 'monitor-demo:evt-004', '2026-09-09 10:31:00', 'recuperacao', 'Fila sintética retornou ao normal');
