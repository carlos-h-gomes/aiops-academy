# Dependências e recursos — piloto de Agentes/processos

Qualificação local em linux/amd64: 2026-09-15. Escopo: execução sintética privada, sem redistribuição. As imagens anteriores reprovadas permanecem no histórico privado.

## Artefato testado

- Python 3.14.7, somente biblioteca padrão; Alpine 3.24.
- Base oficial por manifest amd64: `python:3.14.7-alpine3.24@sha256:5e0ede45886712ce95b0e66232f743cc3d69ff6c2f62cc0d63778e1e894f8bd4`.
- Correção: `libuuid-2.42.3-r1.apk`, SHA-256 `8306e5bb577696c9069fe1dfd9e1dcc39d2d481c6a1b0e707fd03c3e21aa6aa2`, obtido do repositório oficial Alpine e instalado sem desativar a verificação de assinatura APK.
- `image/Dockerfile` fixa base e checksum, instala o APK sem rede no RUN e remove pip/ensurepip e componentes vendorizados. O estágio final copia o filesystem limpo para scratch, sem preservar bytes removidos em camadas inferiores.
- Imagem derivada local: `aiops-academy-agents-runtime:20260915-2`. ID usado no Compose e inspecionado: `sha256:a3ec1ef54271cf9640728b8ad52d6ca382649cc383ff473e2ccf7d5d3ff7e368`.

O script de remoção só pode executar no estágio Linux descartável, nunca no host. A imagem final é derivada localmente, não uma imagem oficial Python. Novo build pode produzir outro ID e exige nova avaliação; não substitua o ID do Compose apenas por uma tag. Não foi realizado segundo build para provar identidade binária reprodutível.

Build realizado na raiz da aplicação: `docker build --platform linux/amd64 --network none --provenance=mode=min --iidfile docs/ai/tasks/2026-09-15-agents-05-correction.final.image-id.txt --tag aiops-academy-agents-runtime:20260915-2 labs/agents-processes-pilot/image`. O build obtém base e APK fixados; o piloto executa sem rede.

## Inventário e licenças transitivas

Scout 1.23.1 produziu SPDX com 41 entradas, incluindo imagem, fontes e binários. Há 37 declarações de licença e quatro NOASSERTION: imagem agregada (sem licença única), `.python-rundeps` (metapacote virtual do Dockerfile oficial), tzdata (domínio público segundo IANA) e Python (PSF e termos históricos no aviso). O aviso Python final corresponde ao texto já revisado: SHA-256 `b0e25a78cffb43f4d92de8b61ccfa1f1f98ecbc22330b54b5251e7b6ba010231`.

O inventário contém GPL e outras licenças. A revisão cobre o ensaio local; redistribuição exige revisão própria de avisos e fontes correspondentes. O NOASSERTION não foi alterado e não foi atribuída uma licença única ao conjunto.

O scanner de severidades alta/crítica retornou exit 0, zero resultados, sobre o SPDX final. Nenhuma exceção foi criada ou aceita nesta tarefa; não foram usados filtros para ignorar base, componentes sem correção ou findings suprimidos. Isso não prova ausência de vulnerabilidades: outras severidades e alterações futuras da base CVE exigem avaliação antes de release. A correção r0 ainda tinha um alerta alto; r1 passou.

## Compatibilidade

Perfil medido: Desktop 4.82.0, Engine 29.6.1, Compose 5.3.0; Linux amd64. Os recursos e a jornada estão no [README](README.md). Identidade 65532, cgroups, rede ausente, mounts somente leitura, capabilities, limites de logs e encerramento foram verificados. Não há LLM, API paga ou serviço persistente. ARM64 e versões mínimas de executor não foram qualificados.

## Fontes oficiais

- [Imagem Python](https://hub.docker.com/_/python) e [Dockerfile Alpine](https://github.com/docker-library/python/blob/master/3.14/alpine3.24/Dockerfile).
- [Licença Python 3.14](https://docs.python.org/3.14/license.html) e [base de fusos IANA](https://www.iana.org/time-zones).
- [APK fixado](https://dl-cdn.alpinelinux.org/alpine/v3.24/main/x86_64/libuuid-2.42.3-r1.apk).
- [Dockerfile e checksums](https://docs.docker.com/reference/dockerfile/), [Scout CVEs](https://docs.docker.com/reference/cli/docker/scout/cves/) e [serviços Compose](https://docs.docker.com/reference/compose-file/services/).

Artefatos privados: prefixo `docs/ai/tasks/2026-09-15-agents-05-correction.final`, com SPDX, SARIF, ID, medições e validação. Mudança de base, APK, imagem ou arquitetura reinicia a qualificação.
