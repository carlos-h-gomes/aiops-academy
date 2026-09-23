# agents-05 — Prática guiada de triagem de bugs

Este roteiro acompanha a autoria PT-BR de agents-05 no workspace de manutenção. A aula permanece **em preparação no aplicativo**: esta prática não marca conclusão, não salva notas no curso e ainda não faz parte do pacote distribuído.

Objetivo: explicar por que o ticket pede 169 centavos, revisar o diff e distinguir proposta, decisão e aplicação. A aprovação é sintética; mesmo um aceite não modifica o código da fixture. Não use dados ou repositórios pessoais.

## Preparar uma vez

Use o Docker já aberto, com containers Linux amd64, e a imagem local qualificada descrita em [DEPENDENCIES.md](DEPENDENCIES.md). O perfil [runtime.env](runtime.env) contém somente os limites medidos, sem credenciais. O Compose não baixa nem reconstrói imagens. Em outra máquina, a imagem precisa ser construída e qualificada antes de seguir.

Abra PowerShell na raiz `aiops-academy` e entre na pasta do piloto:

```powershell
Set-Location labs/agents-processes-pilot
```

Os comandos abaixo usam explicitamente o mesmo Compose e perfil. Cada execução encerra sozinha, limpa seus arquivos temporários e remove seu container. O limite interno é 20 segundos. Não altere os parâmetros AGENTS_* nem monte outros diretórios para contornar uma falha.

## 1. Ler o ticket, as evidências e o diff

```powershell
docker compose --env-file runtime.env -f compose.yaml run --rm -T --no-deps --pull never development-triage
```

O comando padrão é `review`. Leia as cinco partes: ticket/evidências, hipótese, diff, decisão e limpeza. Código e teste são exibidos como texto, sem execução. Identifique a linha que trunca o desconto e compare o caso 199 × 15% com o caso exato 200 × 15%.

Resultado esperado: `hold / approval_missing`, seguido da confirmação de limpeza. Anote o SHA-256 exibido **depois de revisar o diff**. A proposta é reconstruída de forma determinística em cada comando; não existe sessão ou arquivo de aprovação persistente entre eles.

## 2. Conferir as recusas de leitura

```powershell
docker compose --env-file runtime.env -f compose.yaml run --rm -T --no-deps --pull never development-triage python -B /opt/lab/src/learning_session.py check-paths
```

Resultado esperado: três recusas — caminho relativo para fora da lista, caminho absoluto e arquivo não listado. Os nomes são fixos no exercício; o comando não aceita caminhos arbitrários do aluno.

## 3. Negar a proposta

```powershell
docker compose --env-file runtime.env -f compose.yaml run --rm -T --no-deps --pull never development-triage python -B /opt/lab/src/learning_session.py reject
```

Resultado esperado: `block / approval_denied`. Não há registro de aceite. Negar uma proposta válida é uma decisão permitida da pessoa revisora.

## 4. Comparar vínculo errado e vínculo revisado

Primeiro, simule um hash diferente do diff:

```powershell
docker compose --env-file runtime.env -f compose.yaml run --rm -T --no-deps --pull never development-triage python -B /opt/lab/src/learning_session.py approve --reviewed-hash ('0' * 64)
```

Resultado esperado: `block / approval_not_bound_to_diff`. Depois, copie o hash que você revisou na etapa 1 para a variável abaixo, substituindo o texto entre aspas. Não use um hash de exemplo como aprovação automática.

```powershell
$reviewedDiffHash = 'SUBSTITUA_PELO_SHA256_REVISADO'
docker compose --env-file runtime.env -f compose.yaml run --rm -T --no-deps --pull never development-triage python -B /opt/lab/src/learning_session.py approve --reviewed-hash $reviewedDiffHash
```

Resultado esperado com o hash correto: `accepted / human_approval_bound_to_diff`. O único efeito adicional foi `acceptance.json` na área temporária, removido antes do encerramento. Nenhum patch foi aplicado. Sem `--reviewed-hash`, o comando retorna erro de uso (exit 2) e nem abre a área de trabalho.

## 5. Repetir e comprovar a limpeza

```powershell
docker compose --env-file runtime.env -f compose.yaml run --rm -T --no-deps --pull never development-triage python -B /opt/lab/src/learning_session.py reset
```

Resultado esperado: dois resets consecutivos, mesmo hash ao gerar a proposta novamente, fixtures preservadas e diretório temporário removido. O comando também limpa a proposta recriada. Para repetir a prática, volte à etapa 1.

## Evidência de aprendizagem

Registre por conta própria, usando apenas dados fictícios:

- comportamento observado e esperado, hipótese e duas referências de código/teste;
- o que o diff muda e os três testes propostos;
- diferença entre hold, block e accepted, incluindo o vínculo ao hash;
- recusas de leitura, repetição do hash e limites do aceite temporário.

O hash e os testes automatizados verificam comportamento do piloto, não sua compreensão. Explique por que 199 com 15% resulta em 169 e por que o aceite não equivale a executar testes ou publicar uma correção.

## Recuperação

Imagem ausente ou incompatível: pare e confira [dependências](DEPENDENCIES.md); não troque a referência por latest. Docker indisponível: abra o Desktop e aguarde o Engine, então repita review. Hash inválido: confira os 64 caracteres minúsculos. Hash divergente: revise a proposta atual novamente. Falha de fixture, limite ou filesystem: preserve a configuração e registre a mensagem segura; não libere rede ou escrita. Comandos retornam 0 para cenários didáticos completos, inclusive hold/block, 2 para uso inválido e 1 para falha operacional. O timeout interno encerra o processo sem sucesso.

Para verificações automatizadas, as ações aceitam `--json`. Essa opção mantém os mesmos limites e decisões; não cria uma capacidade adicional.
