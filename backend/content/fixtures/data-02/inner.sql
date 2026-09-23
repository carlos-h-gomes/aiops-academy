SELECT i.incidente_id, e.evento_id, r.runbook_id
FROM incidentes AS i
INNER JOIN eventos AS e ON e.incidente_id = i.incidente_id
INNER JOIN runbooks AS r
  ON r.runbook_id = i.runbook_id AND r.servico_id = i.servico_id
WHERE i.servico_id = :servico
ORDER BY i.incidente_id, e.evento_id;
