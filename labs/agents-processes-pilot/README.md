# Piloto de Agentes/processos

**Prática guiada:** siga [o roteiro de agents-05](GUIDE.md) para revisar o diff, negar ou aprovar explicitamente pelo hash e repetir o cenário. O comando padrão apresenta a revisão em português; cada execução limpa a área temporária. O [perfil local](runtime.env) contém apenas os limites qualificados.

Qualificação local em linux/amd64 concluída em 2026-09-15: imagem corrigida, scanner sem alertas altos/críticos e execução descartável verificada. A unidade agents-05 permanece `planned`, sem integração curricular ou publicação. Este estado substitui os bloqueios anteriores, preservados no histórico privado.

## Cenário

`development-v1` usa ticket, código, teste e proposta fictícios. O controlador lê quatro caminhos permitidos, produz candidato e unified diff em diretório temporário e exige aprovação humana sintética vinculada ao hash para registrar aceite.

O aceite é apenas um registro efêmero. A fixture não é alterada e não existe ferramenta para Git, commit, push, shell, subprocesso, rede, segredo, publicação ou escrita externa. Código e teste da fixture são evidências inertes. A aprovação sintética não autentica uma pessoa real.

## Perfil verificado

Docker Desktop 4.82.0, Engine 29.6.1 e Compose 5.3.0 no Windows com containers Linux amd64. Não se declara compatibilidade com versões anteriores ou ARM64.

| Parâmetro obrigatório | Valor testado |
|---|---|
| AGENTS_PLATFORM | linux/amd64 |
| AGENTS_UID / AGENTS_GID | 65532 / 65532 |
| AGENTS_CPU_LIMIT | 0.5 |
| AGENTS_MEMORY_LIMIT | 64m, sem swap adicional |
| AGENTS_PIDS_LIMIT | 16 |
| AGENTS_TMPFS_LIMIT | 8m |
| AGENTS_STOP_GRACE_PERIOD | 3s |
| AGENTS_LOG_MAX_SIZE / AGENTS_LOG_MAX_FILES | 1m / 1 |

Compose exige valores explícitos, usa a imagem local pelo ID e não faz pull. Filesystem e dois mounts são somente leitura; `/work` é temporário; rede desativada; capabilities removidas. Consulte [dependências e licenças transitivas](DEPENDENCIES.md) antes de reconstruir ou trocar a imagem.

## Jornada e evidência

1. Examine o ticket e os arquivos permitidos em `fixtures/development`.
2. Revise a proposta e o hash do diff na área temporária.
3. Compare aprovação ausente, hash divergente e aprovação sintética integral.
4. Faça reset e confirme o mesmo diff e a preservação das fixtures.

O ensaio com `tests/runtime_probe.py` confirmou essas situações, dois resets consecutivos e 100 ciclos determinísticos. Pico RSS do processo: 23.980 KiB; área temporária: 1.072 bytes; dois processos observados; 4,00 segundos no ensaio. São medições deste cenário, não dimensionamento universal de recursos. O comando padrão do Compose encerrou com `hold`, sem aceite e sem falta de memória. Os dois containers foram removidos.

O executor privado usa ambiente mínimo, arquivo de ambiente vazio, inspeção antes de iniciar, timeout e limpeza. Resultados e comandos: `docs/ai/tasks/2026-09-15-agents-05-correction.final.validation.md` no workspace de manutenção. A política de encerramento de três segundos foi inspecionada e a terminação natural medida; processo travado e rotação por saturação de logs não foram ensaiados.
