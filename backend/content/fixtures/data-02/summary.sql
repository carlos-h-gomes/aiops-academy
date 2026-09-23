-- Agregar antes de combinar relações um-para-muitos evita multiplicação.
WITH contagens AS (
  SELECT incidente_id, COUNT(*) AS total
  FROM eventos GROUP BY incidente_id
)
SELECT i.incidente_id, COALESCE(c.total, 0) AS eventos,
       r.runbook_id
FROM incidentes AS i
LEFT JOIN contagens AS c ON c.incidente_id = i.incidente_id
LEFT JOIN runbooks AS r
  ON r.runbook_id = i.runbook_id AND r.servico_id = i.servico_id
WHERE i.servico_id = :servico
ORDER BY i.incidente_id;
