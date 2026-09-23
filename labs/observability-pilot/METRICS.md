# Contrato de métricas sintéticas

Versão do contrato: 1.0 · revisão: 2026-09-08

A aplicação é a fonte de verdade do modo sintético e expõe texto Prometheus em `/metrics`. Prometheus consulta a cada 2 segundos e o Grafana lê somente Prometheus. Não há remote write, trace, dado pessoal, identificador empresarial ou série criada por entrada do aluno.

| Métrica | Tipo/unidade | Labels permitidos | Significado |
| --- | --- | --- | --- |
| `lab_http_requests_total` | counter / requisições | `route="/quotes"`, `status` em `200` ou `503`, `mode` em `healthy` ou `degraded` | Requisições concluídas, classificadas pelo modo no início da operação. |
| `lab_http_request_duration_seconds` | histogram / segundos | `route="/quotes"`, `mode` em `healthy` ou `degraded`, `le` fixo do histograma | Duração sintética observada. Buckets: 0,025; 0,05; 0,1; 0,25; 0,5; 1; +Inf. |
| `lab_mode` | gauge / booleano 0 ou 1 | `mode` em `healthy` ou `degraded` | Uma das duas séries vale 1 e indica o modo atual. |
| `lab_resets_total` | counter / comandos | sem labels | Resets aceitos. Não é apagado pelo reset para preservar monotonicidade. |
| `lab_process_start_time_seconds` | gauge / Unix seconds UTC | sem labels | Início do processo; ajuda a reconhecer reinício. |
| `up` | gauge / booleano 0 ou 1 | labels adicionados pelo Prometheus, incluindo `job="synthetic-app"` | Resultado do scrape; representa alcance do endpoint, não saúde da função. |

`request_id` existe somente no log estruturado. Ele é deliberadamente proibido como label para evitar cardinalidade crescente.

## Entrega, janela e falha

- O scrape é pull e best-effort. Uma amostra perdida não é repetida pela aplicação.
- Contadores ficam somente em memória e voltam ao início após reinício; reset limpa métricas de workload e preserva o contador de resets.
- O dashboard calcula taxas e p95 em uma janela móvel de 1 minuto. Durante aquecimento, ausência de série ou `NaN` não deve ser transformado em zero saudável.
- Prometheus guarda dados em tmpfs por no máximo 1 hora ou 128 MB. Encerrar o Compose elimina o armazenamento.
- Logs JSON ficam no driver local com rotação por tamanho/arquivo. Eles contêm somente modo, rota fixa, status, duração e ID sintético.
- Se Prometheus ou Grafana falhar, a aplicação continua; a investigação fica degradada. Se a aplicação falhar, `up` tende a 0 e a carga registra timeout, sem escolher outro alvo.

## Compatibilidade

O dashboard e `control evidence` são consumidores da versão 1.0. Renomear uma métrica, label ou unidade exige nova versão coordenada. Acrescentar labels provenientes de entrada, endpoints configuráveis, armazenamento persistente ou exportação externa está fora deste piloto e exige novo gate de arquitetura, dados, segurança e custo.
