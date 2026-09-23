# Dependências e licenças do piloto

Inventário revisto em 2026-09-08. O Compose usa tags de versão exatas e nunca `latest`. As imagens são baixadas pelo Docker no host; nenhum container possui egress em tempo de execução.

| Componente direto | Versão/imagem fixada | Uso | Licença principal | Fonte oficial |
| --- | --- | --- | --- | --- |
| Python runtime | `python:3.13.15-alpine3.24` | Aplicação, carga e controle; somente biblioteca padrão | Python Software Foundation License 2.0; empacotamento da Docker Official Image sob MIT | [Python 3.13 license](https://docs.python.org/3.13/license.html), [Docker Official Image](https://hub.docker.com/_/python), [empacotamento](https://github.com/docker-library/python) |
| Prometheus LTS | `prom/prometheus:v3.5.5` | Scrape e consulta local; retenção de 1 h/128 MB | Apache License 2.0 | [imagem](https://hub.docker.com/r/prom/prometheus/tags), [licença](https://prometheus.io/docs/introduction/faq/), [releases](https://github.com/prometheus/prometheus/releases) |
| Grafana OSS | `grafana/grafana-oss:13.0.2` | Dashboard local provisionado, Viewer anônimo | GNU AGPL v3 | [download/versão OSS](https://grafana.com/grafana/download?edition=oss), [imagem](https://hub.docker.com/r/grafana/grafana-oss/tags), [licenciamento](https://grafana.com/licensing/) |
| Docker Engine + Compose v2 | versão instalada pelo aluno | Executor local; não é distribuído pelo lab | Termos variam por produto/edição | [Docker Engine](https://docs.docker.com/engine/), [Docker Compose](https://docs.docker.com/compose/) |

Não há dependência Python instalada por `pip`, plugin Grafana adicional, Alertmanager, Loki, OpenTelemetry Collector, banco externo, SaaS, API paga ou serviço de IA. O datasource Prometheus é embutido no Grafana.

## Componentes transitivos e proveniência

As imagens incluem sistema base e bibliotecas transitivas mantidas pelos seus publicadores. Este arquivo é o inventário direto do lab, não um SBOM transitivo. Depois de uma execução autorizada com o Engine disponível, registre os identificadores imutáveis realmente resolvidos:

```powershell
docker image inspect python:3.13.15-alpine3.24 prom/prometheus:v3.5.5 grafana/grafana-oss:13.0.2 --format '{{.RepoTags}} {{.Id}} {{join .RepoDigests ","}}'
```

Se a sua instalação oferecer uma ferramenta SBOM local aprovada, exporte o resultado para evidência privada e revise licenças/vulnerabilidades antes de redistribuir imagens. Não acrescente uma extensão, conta ou scanner cloud apenas para este piloto.

Tags exatas impedem atualização acidental de versão, mas o registro pode mover uma tag. Para uma distribuição oficial futura, substitua as três referências por manifests multi-arquitetura fixados por digest depois de validar `amd64` e `arm64`, guarde SBOM/proveniência e defina atualização de segurança. Essa condição não transforma a configuração estática atual em prova de imagem executada.
