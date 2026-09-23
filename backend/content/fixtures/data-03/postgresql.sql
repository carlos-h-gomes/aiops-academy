-- ROTEIRO NAO EXECUTADO. Somente em PostgreSQL descartavel qualificado.
-- Sem dados reais. Nao executar em conexao de producao.
-- O controlador futuro deve parar no primeiro erro e fechar a conexao.
BEGIN;
SET LOCAL statement_timeout = '5s';
SET LOCAL lock_timeout = '1s';
CREATE TEMP TABLE data03_eventos (
    evento_id integer PRIMARY KEY,
    incidente_id integer NOT NULL,
    ocorrido_em timestamp NOT NULL
) ON COMMIT DROP;
INSERT INTO pg_temp.data03_eventos
SELECT n, n % 100, timestamp '2026-09-16 00:00:00' + n * interval '1 second'
FROM generate_series(1, 20000) AS s(n);
ANALYZE pg_temp.data03_eventos;
-- Resultado esperado pela geracao: 10042, 10142, ... 10942 (dez IDs).
SELECT evento_id FROM pg_temp.data03_eventos
WHERE incidente_id = 42
  AND ocorrido_em >= timestamp '2026-09-16 00:00:00' + interval '10000 seconds'
  AND ocorrido_em < timestamp '2026-09-16 00:00:00' + interval '11000 seconds'
ORDER BY evento_id;
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT evento_id FROM pg_temp.data03_eventos
WHERE incidente_id = 42
  AND ocorrido_em >= timestamp '2026-09-16 00:00:00' + interval '10000 seconds'
  AND ocorrido_em < timestamp '2026-09-16 00:00:00' + interval '11000 seconds';
CREATE INDEX data03_incidente_tempo ON pg_temp.data03_eventos (incidente_id, ocorrido_em);
ANALYZE pg_temp.data03_eventos;
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT evento_id FROM pg_temp.data03_eventos
WHERE incidente_id = 42
  AND ocorrido_em >= timestamp '2026-09-16 00:00:00' + interval '10000 seconds'
  AND ocorrido_em < timestamp '2026-09-16 00:00:00' + interval '11000 seconds';
SELECT evento_id FROM pg_temp.data03_eventos
WHERE incidente_id = 42
  AND ocorrido_em >= timestamp '2026-09-16 00:00:00' + interval '10000 seconds'
  AND ocorrido_em < timestamp '2026-09-16 00:00:00' + interval '11000 seconds'
ORDER BY evento_id;
ROLLBACK;
