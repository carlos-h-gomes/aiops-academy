-- Complemento sintético; carregar após data-01/schema.sql e valid.sql.
INSERT INTO incidentes VALUES
 ('inc-300', 'svc-quotes', '2026-09-16 10:00:00', 'sev3', 'aberto', NULL);
INSERT INTO runbooks VALUES
 ('rb-quotes-02', 'svc-quotes', 'pool-esgotado', 4, 'Revisar pool', 'ativo');
-- Mesmo texto, identidade distinta: não é duplicação da chave de origem.
INSERT INTO eventos VALUES
 ('evt-005', 'inc-100', 'monitor-demo:evt-005', '2026-09-16 10:01:00',
  'alerta', 'Taxa de erros acima da linha de base');
