# Laboratório piloto de observabilidade

Ambiente opcional, local e descartável para investigar um serviço **inteiramente sintético**. Você vai observar saúde, ativar uma degradação controlada, confrontar métricas e logs, recuperar o serviço, salvar evidência e limpar o ambiente.

> **Correção de arquitetura aprovada em 2026-09-08.** Aplicação, Prometheus e Grafana permanecem somente na rede `internal`. Um gateway local de destinos fixos publica as três interfaces apenas em `127.0.0.1`; sua segunda bridge desabilita masquerade e não oferece proxy configurável. A qualificação deve confirmar publishers, ausência de acesso pela LAN/egress e cleanup antes de considerar o lab concluído.

Este lab não se conecta ao aplicativo principal da AIOps Academy, à nuvem, a APIs de IA, à rede da empresa ou a qualquer alvo configurável. Os serviços observados ficam em uma rede Docker interna; somente o gateway local encaminha TCP para três destinos codificados no próprio lab.

## Requisitos e limites

- Docker Desktop ou Docker Engine já instalado, em execução com containers Linux, e Docker Compose v2. O lab não instala nem inicia essas ferramentas.
- Acesso à internet somente para o Docker baixar as três imagens versionadas na primeira preparação. Depois de iniciados, os containers não têm rota de saída.
- Recomendado: 2 CPUs livres, 2 GB de memória livre, 2,5 GB de disco para imagens/cache e cerca de 45 minutos.
- Portas locais livres: `13000` (Grafana), `18080` (aplicação sintética) e `19090` (Prometheus). Não encerre um processo desconhecido para liberar porta.
- Limite total configurado: 1,55 CPU, 1.024 MiB de RAM, 320 MiB de armazenamento temporário, logs rotacionados. A carga envia no máximo 2 requisições/s por 30 minutos; a aplicação encerra em 40 minutos. Prometheus retém no máximo 1 hora ou 128 MB.

Dependências, versões, licenças e fontes estão em [DEPENDENCIES.md](DEPENDENCIES.md); o contrato das métricas está em [METRICS.md](METRICS.md). O lab não usa credenciais e não monta o Docker socket nem dados fora desta pasta.

## 1. Verifique antes de iniciar

Abra o PowerShell nesta pasta e confirme que o resultado de `docker version` mostra as seções **Client** e **Server**. Se a seção Server faltar ou houver erro de conexão, pare aqui: inicie o Docker Desktop manualmente conforme a política do seu computador ou use outra máquina autorizada. Não instale nem altere o sistema apenas para concluir a aula.

```powershell
docker version
docker compose version
docker compose config --quiet
```

`docker compose config --quiet` sem mensagem e com saída 0 confirma somente a forma do Compose; ainda não prova que imagens ou containers funcionam.

## 2. Prepare e inicie

```powershell
docker compose build
docker compose up -d
docker compose ps --all
```

Espere até `app`, `prometheus`, `grafana` e `gateway` aparecerem como `healthy`. `loadgen` deve estar em execução; ele termina sozinho após 30 minutos. Se algum serviço não ficar saudável em até dois minutos, não repita indefinidamente:

```powershell
docker compose logs --tail 80 app prometheus grafana gateway
docker compose down --volumes --remove-orphans
```

Leia a última causa, corrija somente se estiver dentro deste lab e faça no máximo uma nova tentativa.

## 3. Observe o estado saudável

Abra o dashboard provisionado:

- Grafana: <http://127.0.0.1:13000/d/aiops-observability-pilot>
- Estado da aplicação: <http://127.0.0.1:18080/state>
- Prometheus, para consulta opcional: <http://127.0.0.1:19090>

Não há login: o Grafana está em modo anônimo **Viewer**, preso ao loopback e sem edição. Aguarde de 60 a 90 segundos. O esperado é:

- **Scenario state** = `HEALTHY`;
- liveness = `PROCESS UP`;
- taxa próxima de 2 req/s;
- erro próximo de zero;
- p95 de latência abaixo de 0,1 s depois que a janela estiver preenchida.

Um painel vazio nos primeiros segundos é estado de aquecimento, não falha. Confirme o intervalo **Last 10 minutes** e aguarde pelo menos dois scrapes.

## 4. Ative a degradação sintética

```powershell
docker compose --profile tools run --rm control degrade
```

O único efeito é mudar o estado em memória da aplicação do lab. A carga passa a receber, de forma determinística, aproximadamente 75% de respostas HTTP 503 com cerca de 350 ms. Aguarde 60 segundos e observe:

- **Scenario state** = `DEGRADED`;
- error ratio crescendo;
- p95 acima de 0,3 s;
- liveness continuando `PROCESS UP`.

Essa diferença é central: processo disponível não significa função saudável.

## 5. Investigue com duas fontes

Primeiro consulte uma evidência agregada e limitada:

```powershell
docker compose --profile tools run --rm control evidence
```

Depois veja somente os logs recentes da aplicação:

```powershell
docker compose logs --since 2m --tail 160 app
```

Nos logs JSON, compare `mode`, `status` e `duration_ms`. `request_id` serve apenas para localizar uma requisição no log e não entra como label de métrica. Formule uma hipótese: “o processo segue respondendo, mas a função de cotações entrou no modo degradado, elevando 503 e duração”.

Para conferir no Prometheus, use as consultas já empregadas no dashboard:

```promql
sum(rate(lab_http_requests_total{route="/quotes",status=~"5.."}[1m]))
  / clamp_min(sum(rate(lab_http_requests_total{route="/quotes"}[1m])), 0.001)
```

```promql
histogram_quantile(0.95,
  sum by (le) (rate(lab_http_request_duration_seconds_bucket{route="/quotes"}[1m])))
```

Taxas e percentis precisam de uma janela. Os contadores acumulados, sozinhos, podem esconder quando a mudança ocorreu.

## 6. Recupere e registre evidência

```powershell
docker compose --profile tools run --rm control recover
```

Aguarde pelo menos 60 segundos. O estado volta a `HEALTHY`; a janela ainda pode misturar amostras degradadas até envelhecer. Isso é esperado. Salve duas evidências pequenas, sem dados pessoais:

```powershell
New-Item -ItemType Directory -Force evidence | Out-Null
docker compose --profile tools run --rm control evidence | Tee-Object -FilePath evidence\recovered.json
docker compose logs --since 5m --tail 320 app | Set-Content -Encoding utf8 evidence\app-recent.log
```

O diretório `evidence/` é ignorado pelo Git. Um bom registro inclui horário, estado, taxa, erro, p95, hipótese, ação de recuperação e limitação da janela. Uma captura do dashboard pode complementar, mas não substitui a consulta reproduzível.

## 7. Reset idempotente

`reset` sempre seleciona o modo saudável e limpa contadores/histogramas de requisição. O contador de resets permanece monotônico para mostrar quantas vezes o comando foi recebido. Repetir é seguro:

```powershell
docker compose --profile tools run --rm control reset
docker compose --profile tools run --rm control reset
curl.exe --max-time 2 http://127.0.0.1:18080/state
```

O resultado deve mostrar `mode` igual a `healthy`, zero requisições/erros logo após o reset (a carga pode adicionar novas requisições imediatamente) e `resets_total` incrementado. Se a carga já terminou, `docker compose restart loadgen` inicia outra janela máxima de 30 minutos.

## 8. Limpeza explícita

Na pasta deste lab:

```powershell
docker compose down --volumes --remove-orphans
docker image rm aiops-academy-observability-pilot-python:local
```

O primeiro comando remove somente containers, rede e armazenamento temporário nomeados pelo projeto `aiops-academy-observability-pilot`. O segundo remove somente a imagem construída por este lab; se outro container seu ainda a usa, o Docker recusará sem forçar. Imagens-base versionadas permanecem no cache porque podem ser compartilhadas. Não use `docker system prune` como parte deste roteiro.

Se quiser remover a evidência, revise a pasta `evidence/` no Explorador e apague-a manualmente. Não há recurso cloud, conta, credencial ou estado no aplicativo principal para limpar.

## Problemas conhecidos e recuperação

- **Docker Engine indisponível:** não há execução funcional. Faça apenas validação estática ou inicie o Docker manualmente conforme sua autorização.
- **Portas ausentes:** confirme se `gateway` está saudável. Somente ele pode publicar `127.0.0.1:13000`, `18080` e `19090`; os serviços internos não publicam portas. Não troque `internal: true`, não habilite masquerade e não conecte os serviços observados à bridge de acesso.
- **Porta ocupada:** pare o lab e escolha portas diferentes apenas no lado esquerdo dos três mapeamentos `127.0.0.1` em `compose.yaml`; atualize os endereços usados no roteiro. Nunca publique em `0.0.0.0`.
- **Dashboard sem dados:** confirme `docker compose ps --all`, abra Prometheus → Status → Targets e verifique `synthetic-app` como UP. Depois aguarde a janela de um minuto.
- **Loadgen encerrado:** esse é o limite de 30 minutos, não um crash. Reinicie apenas se ainda estiver estudando.
- **Aplicação encerrada:** a sessão atingiu 40 minutos. Execute a limpeza e inicie uma nova sessão; não altere o limite para deixar carga esquecida.
- **Após reset ainda aparece degradação:** consultas `rate(...[1m])` preservam amostras recentes. Aguarde a janela ou diminua o intervalo visual apenas para investigar, sem confundir isso com apagamento dos dados do Prometheus.

## Critério de conclusão

Você concluiu quando consegue mostrar, com dados do próprio lab:

1. liveness permaneceu disponível durante a falha funcional;
2. 503 e p95 cresceram depois da degradação;
3. logs e métricas sustentam a mesma hipótese;
4. a recuperação voltou a gerar respostas saudáveis;
5. reset foi repetível e cleanup removeu os recursos do projeto.

Configuração válida ou testes unitários não substituem esse cenário executado em containers.
